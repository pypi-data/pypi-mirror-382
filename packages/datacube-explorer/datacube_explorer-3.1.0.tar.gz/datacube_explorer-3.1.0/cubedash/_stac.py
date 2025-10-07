import json
import uuid
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timedelta, timezone
from datetime import time as dt_time
from functools import partial
from typing import Any, TypeAlias

import flask
import pystac
import structlog
from datacube.model import Range
from datacube.utils import DocReader, parse_time
from eodatasets3 import serialise
from eodatasets3 import stac as eo3stac
from eodatasets3.model import AccessoryDoc, DatasetDoc, MeasurementDoc, ProductDoc
from eodatasets3.properties import Eo3Dict
from eodatasets3.utils import is_doc_eo3
from flask import abort, current_app, request
from pystac import Catalog, Collection, Extent, Item, ItemCollection, Link, STACObject
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry
from toolz import dicttoolz
from werkzeug.datastructures import ImmutableMultiDict, TypeConversionDict
from werkzeug.exceptions import BadRequest, HTTPException

from cubedash.summary._stores import CollectionItem, DatasetItem

from . import _model, _utils
from .summary import ItemSort

_LOG = structlog.stdlib.get_logger()
bp = flask.Blueprint("stac", __name__, url_prefix="/stac")

DEFAULT_PAGE_SIZE_LIMIT = 1000
DEFAULT_PAGE_SIZE = 20
DEFAULT_CATALOG_SIZE = 500

# Should we force all URLs to include the full hostname?
DEFAULT_FORCE_ABSOLUTE_LINKS = True

# Should searches return the full properties for every stac item by default?
# These searches are much slower we're forced us to use ODC's own metadata table.
DEFAULT_RETURN_FULL_ITEMS = True

STAC_VERSION = "1.1.0"

ItemLike: TypeAlias = pystac.Item | dict

############################
#  Helpers
############################


def get_default_limit() -> int:
    return current_app.config.get("STAC_DEFAULT_PAGE_SIZE", DEFAULT_PAGE_SIZE)


def check_page_limit(limit: int) -> None:
    page_size_limit = current_app.config.get(
        "STAC_PAGE_SIZE_LIMIT", DEFAULT_PAGE_SIZE_LIMIT
    )
    if limit > page_size_limit:
        abort(
            400,
            f"Max page size is {page_size_limit}. "
            "Use the next links instead of a large limit.",
        )


def dissoc_in(d: dict, key: str):
    # like dicttoolz.dissoc but with support for nested keys
    split = key.split(".")

    # if nested
    if len(split) > 1 and dicttoolz.get_in(split, d) is not None:
        outer = dicttoolz.get_in(split[:-1], d)
        return dicttoolz.update_in(
            d=d, keys=split[:-1], func=lambda _: dicttoolz.dissoc(outer, split[-1])
        )
    return dicttoolz.dissoc(d, key)


# Time-related


def utc(d: datetime):
    if d.tzinfo is None:
        return d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def _parse_time_range(time: str) -> tuple[datetime, datetime] | None:
    """
    >>> _parse_time_range('1986-04-16T01:12:16/2097-05-10T00:24:21')
    (datetime.datetime(1986, 4, 16, 1, 12, 16), datetime.datetime(2097, 5, 10, 0, 24, 21))
    >>> _parse_time_range('1986-04-16T01:12:16')
    (datetime.datetime(1986, 4, 16, 1, 12, 16), datetime.datetime(1986, 4, 16, 1, 12, 17))
    >>> # Time is optional:
    >>> _parse_time_range('2019-01-01/2019-01-01')
    (datetime.datetime(2019, 1, 1, 0, 0), datetime.datetime(2019, 1, 1, 0, 0))
    >>> _parse_time_range('1986-04-16')
    (datetime.datetime(1986, 4, 16, 0, 0), datetime.datetime(1986, 4, 17, 0, 0))
    >>> # Open ranges:
    >>> _parse_time_range('2019-01-01/..')[0]
    datetime.datetime(2019, 1, 1, 0, 0)
    >>> _parse_time_range('2019-01-01/..')[1] > datetime.now()
    True
    >>> _parse_time_range('../2019-01-01')
    (datetime.datetime(1971, 1, 1, 0, 0), datetime.datetime(2019, 1, 1, 0, 0))
    >>> # Unbounded time is the same as no time filter. ("None")
    >>> _parse_time_range('../..')
    >>>
    """
    time_period = time.split("/")
    if len(time_period) == 2:
        start: str | datetime
        end: str | datetime
        start, end = time_period
        if start == "..":
            start = datetime(1971, 1, 1, 0, 0)
        elif end == "..":
            end = datetime.now() + timedelta(days=2)
        # Were they both open? Treat it as no date filter.
        if end == "..":
            return None

        return parse_time(start), parse_time(end)
    if len(time_period) == 1:
        t: datetime = parse_time(time_period[0])
        if t.time() == dt_time():
            return t, t + timedelta(days=1)
        return t, t + timedelta(seconds=1)
    return None


def _unparse_time_range(time: tuple[datetime, datetime]) -> str:
    """
    >>> _unparse_time_range((
    ...     datetime(1986, 4, 16, 1, 12, 16),
    ...     datetime(2097, 5, 10, 0, 24, 21)
    ... ))
    '1986-04-16T01:12:16/2097-05-10T00:24:21'
    """
    start_time, end_time = time
    return f"{start_time.isoformat()}/{end_time.isoformat()}"


# URL-related


def url_for(*args, **kwargs):
    force_absolute_links = current_app.config.get(
        "STAC_ABSOLUTE_HREFS", DEFAULT_FORCE_ABSOLUTE_LINKS
    )
    if force_absolute_links:
        kwargs["_external"] = True
    return flask.url_for(*args, **kwargs)


# Conversions


def _band_to_measurement(band: Mapping[str, Any]) -> MeasurementDoc:
    """Create EO3 measurement from an EO1 band dict"""
    return MeasurementDoc(
        path=band.get("path", "Unknown"),
        band=band.get("band"),
        layer=band.get("layer"),
        name=band.get("name"),  # type: ignore[arg-type]
        alias=band.get("label"),  # type: ignore[arg-type]
    )


def as_stac_item(dataset: DatasetItem) -> pystac.Item:
    """
    Get a dict corresponding to a stac item
    """
    ds = dataset.odc_dataset

    if ds is not None and is_doc_eo3(ds.metadata_doc):
        dataset_doc = serialise.from_doc(ds.metadata_doc, skip_validation=True)
        dataset_doc.locations = None if ds.uri is None else [ds.uri]

        # Geometry is optional in eo3, and needs to be calculated from grids if missing.
        # We can use ODC's own calculation that happens on index.
        if dataset_doc.geometry is None:
            fallback_extent = ds.extent
            if fallback_extent is not None:
                dataset_doc.geometry = fallback_extent.geom
                dataset_doc.crs = str(ds.crs)

        if ds.sources:
            dataset_doc.lineage = {
                classifier: [d.id] for classifier, d in ds.sources.items()
            }
        # Does ODC still put legacy lineage into indexed documents?
        elif ("source_datasets" in dataset_doc.lineage) and len(
            dataset_doc.lineage
        ) == 1:
            # From old to new lineage type.
            # FIXME: remove type ignores and fix the issues.
            dataset_doc.lineage = {  # type: ignore[misc]
                classifier: [dataset["id"]]  # type: ignore[has-type]
                for classifier, dataset in dataset_doc.lineage["source_datasets"]
            }

    else:
        # eo1 to eo3

        dataset_doc = DatasetDoc(
            id=dataset.dataset_id,
            # Filled-in below.
            label=None,
            product=ProductDoc(dataset.product_name),
            locations=None if ds is None or ds.uri is None else [ds.uri],
            crs=str(dataset.geometry.crs) if dataset.geometry is not None else None,
            geometry=dataset.geometry.geom if dataset.geometry is not None else None,
            grids=None,
            # TODO: Convert these from stac to eo3
            properties=Eo3Dict(
                {
                    "datetime": utc(dataset.center_time),
                    **(dict(_build_properties(ds.metadata)) if ds else {}),
                    "odc:processing_datetime": utc(dataset.creation_time),
                }
            ),
            measurements=(
                {name: _band_to_measurement(b) for name, b in ds.measurements.items()}
                if ds is not None
                else {}
            ),
            accessories=(
                _accessories_from_eo1(ds.metadata_doc) if ds is not None else {}
            ),
            # TODO: Fill in lineage. The datacube API only gives us full datasets, which is
            #       expensive. We only need a list of IDs here.
            lineage={},
        )

    if dataset_doc.label is None and ds is not None:
        dataset_doc.label = _utils.dataset_label(ds)

    item = eo3stac.to_pystac_item(
        dataset=dataset_doc,
        stac_item_destination_url=url_for(
            ".item", collection=dataset.product_name, dataset_id=dataset.dataset_id
        ),
        odc_dataset_metadata_url=url_for("dataset.raw_doc", id_=dataset.dataset_id),
        explorer_base_url=url_for("pages.default_redirect"),
    )

    # Add the region code that Explorer inferred.
    # (Explorer's region codes predate ODC's and support
    #  many more products.
    item.properties["cubedash:region_code"] = dataset.region_code

    # add canonical ref pointing to the JSON file on s3
    if ds is not None and ds.uri:
        media_type = "application/json" if ds.uri.endswith("json") else "text/yaml"
        item.links.append(
            Link(
                rel="canonical",
                media_type=media_type,
                target=_utils.as_resolved_remote_url(None, ds.uri),
            )
        )

    return item


def as_stac_collection(res: CollectionItem) -> pystac.Collection:
    stac_collection = Collection(
        id=res.name,
        title=res.title,
        description=res.description or "",
        license=res.definition.get(
            "license",
            flask.current_app.config.get("CUBEDASH_DEFAULT_LICENSE", "Unknown"),
        ),
        providers=[],
        extent=Extent(
            pystac.SpatialExtent(
                # TODO: Find a nicer way to make the typechecker happier
                # pystac is too specific in wanting a list[float | int]
                # odc-geo BoundingBox class is a Sequence[float]
                bboxes=[list(res.bbox) if res.bbox else [-180.0, -90.0, 180.0, 90.0]]
            ),
            temporal=pystac.TemporalExtent(
                intervals=[
                    [
                        utc(res.time_earliest) if res.time_earliest else None,
                        utc(res.time_latest) if res.time_latest else None,
                    ]
                ]
            ),
        ),
    )

    stac_collection.set_root(root_catalog())

    stac_collection.links.extend(
        [
            Link(rel="self", target=request.url),
            Link(rel="items", target=url_for(".collection_items", collection=res.name)),
            Link(
                rel="http://www.opengis.net/def/rel/ogc/1.0/queryables",
                target=url_for(".collection_queryables", collection=res.name),
            ),
        ]
    )

    return stac_collection


def _accessories_from_eo1(metadata_doc: dict) -> dict[str, AccessoryDoc]:
    """Create and EO3 accessories section from an EO1 document"""
    accessories = {}

    # Browse image -> thumbnail
    if "browse" in metadata_doc:
        for name, browse in metadata_doc["browse"].items():
            accessories[f"thumbnail:{name}"] = AccessoryDoc(
                path=browse["path"], name=name
            )

    # Checksum
    if "checksum_path" in metadata_doc:
        accessories["checksum:sha1"] = AccessoryDoc(
            path=metadata_doc["checksum_path"], name="checksum:sha1"
        )
    return accessories


def field_platform(key, value):
    yield "eo:platform", value.lower().replace("_", "-")


def field_instrument(key, value):
    yield "eo:instrument", value


def field_path_row(key, value):
    # Path/Row fields are ranges in datacube but 99% of the time
    # they are a single value
    # (they are ranges in telemetry products)
    # Stac doesn't accept a range here, so we'll skip it in those products,
    # but we can handle the 99% case when lower==higher.
    if key == "sat_path":
        kind = "landsat:wrs_path"
    elif key == "sat_row":
        kind = "landsat:wrs_row"
    else:
        raise ValueError(f"Path/row kind {key!r}")

    # If there's only one value in the range, return it.
    if isinstance(value, Range):
        if value.end is None or value.begin == value.end:
            # Standard stac
            yield kind, int(value.begin)
        else:
            # Our questionable output. Only present in telemetry products?
            yield f"odc:{key}", [value.begin, value.end]


# Other Property examples:
# collection	"landsat-8-l1"
# eo:gsd	15
# eo:platform	"landsat-8"
# eo:instrument	"OLI_TIRS"
# eo:off_nadir	0
# datetime	"2019-02-12T19:26:08.449265+00:00"
# eo:sun_azimuth	-172.29462212
# eo:sun_elevation	-6.62176054
# eo:cloud_cover	-1
# eo:row	"135"
# eo:column	"044"
# landsat:product_id	"LC08_L1GT_044135_20190212_20190212_01_RT"
# landsat:scene_id	"LC80441352019043LGN00"
# landsat:processing_level	"L1GT"
# landsat:tier	"RT"

_STAC_PROPERTY_MAP = {
    "platform": field_platform,
    "instrument": field_instrument,
    # "measurements": field_bands,
    "sat_path": field_path_row,
    "sat_row": field_path_row,
}


def _build_properties(d: DocReader):
    for key, val in d.fields.items():
        if val is None:
            continue
        converter = _STAC_PROPERTY_MAP.get(key)
        if converter:
            yield from converter(key, val)


# Search arguments


def _remove_prefixes(arg: str):
    # remove potential 'item.', 'properties.', or 'item.properties.' prefixes for ease of handling
    arg = arg.replace("item.", "")
    return arg.replace("properties.", "")


def _array_arg(arg: str | list[str | float], expect_type=str, expect_size=None) -> list:
    """
    Parse an argument that should be a simple list.
    """
    if isinstance(arg, list):
        return arg

    # Make invalid arguments loud. The default ValueError behaviour is to quietly forget the param.
    try:
        if not isinstance(arg, str):
            raise ValueError
        arg = arg.strip()
        # Legacy json-like format. This is what sat-api seems to do too.
        if arg.startswith("["):
            value = json.loads(arg)
        else:
            # Otherwise OpenAPI non-exploded form style.
            # Eg. "1, 2, 3" or "string1,string2" or "string1"
            args = [a.strip() for a in arg.split(",")]
            value = [expect_type(a.strip()) for a in args if a]
    except ValueError:
        raise BadRequest(
            f"Invalid argument syntax. Expected comma-separated list, got: {arg!r}"
        ) from None

    if not isinstance(value, list):
        raise BadRequest(f"Invalid argument syntax. Expected json list, got: {value!r}")

    if expect_size is not None and len(value) != expect_size:
        raise BadRequest(
            f"Expected size {expect_size}, got {len(value)} elements in {arg!r}"
        )

    return value


def _geojson_arg(arg: dict) -> BaseGeometry:
    if not isinstance(arg, dict):
        raise BadRequest(
            "The 'intersects' argument must be a JSON object (and sent over a POST request)"
        )

    try:
        return shape(arg)
    except ValueError:
        raise BadRequest(
            "The 'intersects' argument must be valid GeoJSON geometry."
        ) from None


def _bool_argument(s: str | bool):
    """
    Parse an argument that should be a bool
    """
    if isinstance(s, bool):
        return s
    # Copying FastAPI booleans:
    # https://fastapi.tiangolo.com/tutorial/query-params
    return s.strip().lower() in ("1", "true", "on", "yes")


def _dict_arg(arg: str | dict[str, Any]) -> dict[str, Any]:
    """
    Parse stac extension arguments as dicts
    """
    if isinstance(arg, str):
        return json.loads(arg.replace("'", '"'))
    return arg


def _field_arg(arg: str | list[str] | dict) -> dict[str, list[str]]:
    """
    Parse field argument into a dict
    """
    if isinstance(arg, dict):
        return _dict_arg(arg)
    if isinstance(arg, str):
        if arg.startswith("{"):
            return _dict_arg(arg)
        arg = arg.split(",")
    include = []
    exclude = []
    if isinstance(arg, list):
        for a in arg:
            if a.startswith("-"):
                exclude.append(a[1:])
            else:
                # account for '+' showing up as a space if not encoded
                include.append(a[1:] if a.startswith("+") else a.strip())
    return {"include": include, "exclude": exclude}


def _sort_arg(arg: str | list[str] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Parse sortby argument into a list of dicts
    """

    def _format(val: str) -> dict[str, str]:
        val = _remove_prefixes(val)
        if val.startswith("-"):
            return {"field": val[1:], "direction": "desc"}
        if val.startswith("+"):
            return {"field": val[1:], "direction": "asc"}
        # default is ascending
        return {"field": val.strip(), "direction": "asc"}

    arg_work = arg.split(",") if isinstance(arg, str) else arg
    if len(arg_work):
        if isinstance(arg_work[0], str):
            return [_format(a) for a in arg_work]  # type: ignore[arg-type]
        if isinstance(arg_work[0], dict):
            for a in arg_work:
                assert isinstance(a, dict)
                a["field"] = _remove_prefixes(a["field"])

    return arg_work  # type: ignore[return-value]


def _filter_arg(arg: str | dict) -> str:
    # convert dict to arg to more easily remove prefixes
    if isinstance(arg, dict):
        arg = json.dumps(arg)
    return _remove_prefixes(arg)


def _validate_filter(filter_lang: str, cql: str) -> None:
    # check filter-lang and actual cql format are aligned
    is_json = True
    try:
        json.loads(cql)
    except json.decoder.JSONDecodeError:
        is_json = False

    if filter_lang == "cql2-text" and is_json:
        abort(400, "Expected filter to be cql2-text, but received cql2-json")
    if filter_lang == "cql2-json" and not is_json:
        abort(400, "Expected filter to be cql2-json, but received cql2-text")


# Search


def _handle_search_request(
    method: str,
    request_args: TypeConversionDict,
    product_names: list[str],
    include_total_count: bool,
) -> ItemCollection:
    bbox = request_args.get(
        "bbox", type=partial(_array_arg, expect_size=4, expect_type=float)
    )
    if bbox is not None and len(bbox) != 4:
        abort(400, "Expected bbox of size 4. [min lon, min lat, max lon, max lat]")

    time = request_args.get("datetime")

    limit = request_args.get("limit", default=get_default_limit(), type=int)
    check_page_limit(limit)

    ids = request_args.get(
        "ids", default=None, type=partial(_array_arg, expect_type=uuid.UUID)
    )

    offset = request_args.get("_o", default=0, type=int)

    # Request the full Item information. This forces us to go to the
    # ODC dataset table for every record, which can be extremely slow.
    default_full_items = current_app.config.get(
        "STAC_DEFAULT_FULL_ITEM_INFORMATION", DEFAULT_RETURN_FULL_ITEMS
    )
    full_information = request_args.get(
        "_full", default=default_full_items, type=_bool_argument
    )

    intersects = request_args.get("intersects", default=None, type=_geojson_arg)

    fields = request_args.get("fields", default=None, type=_field_arg)

    sortby = request_args.get("sortby", default=None, type=_sort_arg)
    # not sure if there's a neater way to check sortable attribute type in _stores
    # but the handling logic (i.e. 400 status code) would still need to live in here
    if sortby:
        for s in sortby:
            field = s.get("field")
            if field in [
                "type",
                "stac_version",
                "properties",
                "geometry",
                "links",
                "assets",
                "bbox",
                "stac_extensions",
            ]:
                abort(
                    400,
                    f"Cannot sort by {field}. "
                    "Only 'id', 'collection', and Item properties can be used to sort results.",
                )

    # Make sure users know that the query extension isn't implemented
    if request_args.get("query") is not None:
        abort(
            400,
            "The Query extension is no longer supported. Please use the Filter extension instead.",
        )

    filter_lang = request_args.get("filter-lang", default=None, type=str)
    filter_cql = request_args.get("filter", default=None, type=_filter_arg)
    filter_crs = request_args.get("filter-crs", default=None)
    if filter_crs and filter_crs != "https://www.opengis.net/def/crs/OGC/1.3/CRS84":
        abort(
            400,
            "filter-crs only accepts 'https://www.opengis.net/def/crs/OGC/1.3/CRS84' as a valid value.",
        )
    if filter_lang is None and filter_cql is not None:
        # If undefined, defaults to cql2-text for a GET request and cql2-json for a POST request.
        filter_lang = "cql2-text" if method == "GET" else "cql2-json"
    if filter_cql:
        assert filter_lang is not None
        _validate_filter(filter_lang, filter_cql)

    if time is not None:
        time = _parse_time_range(time)

    def next_page_url(next_offset):
        return url_for(
            ".stac_search",
            collections=",".join(product_names),
            bbox="{},{},{},{}".format(*bbox) if bbox else None,
            datetime=_unparse_time_range(time) if time else None,
            ids=",".join(map(str, ids)) if ids else None,
            limit=limit,
            _o=next_offset,
            _full=full_information,
            intersects=intersects,
            fields=fields,
            sortby=sortby,
            # so that it doesn't get named 'filter_lang'
            **{"filter-lang": filter_lang},
            filter=filter_cql,
        )

    feature_collection = search_stac_items(
        product_names=product_names,
        bbox=None if bbox is None else tuple(bbox),
        time=time,
        dataset_ids=ids,
        limit=limit,
        offset=offset,
        intersects=intersects,
        # The /stac/search api only supports intersects over post requests.
        use_post_request=method == "POST" or intersects is not None,
        get_next_url=next_page_url,
        full_information=full_information,
        include_total_count=include_total_count,
        fields=fields,
        sortby=sortby,
        filter_lang=filter_lang,
        filter_cql=filter_cql,
    )

    feature_collection.extra_fields["links"].extend(
        (
            {
                "href": url_for(".stac_search"),
                "rel": "search",
                "title": "Search",
                "type": "application/geo+json",
                "method": "GET",
            },
            {
                "href": url_for(".stac_search"),
                "rel": "search",
                "title": "Search",
                "type": "application/geo+json",
                "method": "POST",
            },
        )
    )
    return feature_collection


def _handle_collection_search(
    request_args: TypeConversionDict,
) -> tuple[list[Collection], dict[str, Any]]:
    bbox = request_args.get(
        "bbox", type=partial(_array_arg, expect_size=4, expect_type=float)
    )
    if bbox is not None and len(bbox) != 4:
        abort(400, "Expected bbox of size 4. [min lon, min lat, max lon, max lat]")

    time = request_args.get("datetime")

    q = request_args.get("q", default=None, type=partial(_array_arg, expect_type=str))

    limit = request_args.get("limit", default=get_default_limit(), type=int)
    check_page_limit(limit)

    offset = request_args.get("_o", default=0, type=int)

    if time is not None:
        time = _parse_time_range(time)

    def next_page_url(next_offset):
        return url_for(
            ".collections",
            bbox="{},{},{},{}".format(*bbox) if bbox else None,
            time=_unparse_time_range(time) if time else None,
            q=",".join(map(str, q)) if q else None,
            limit=limit,
            _o=next_offset,
        )

    return search_stac_collections(
        bbox=None if bbox is None else tuple(bbox),
        time=time,
        q=q,
        limit=limit,
        offset=offset,
        get_next_url=next_page_url,
    )


# Item search extensions


def _get_property(prop: str, item: Item, no_default: bool = False):
    """So that we don't have to keep using this bulky expression"""
    return dicttoolz.get_in(prop.split("."), item.to_dict(), no_default=no_default)


def _handle_fields_extension(items: Sequence[Item], fields: dict) -> Sequence[ItemLike]:
    """
    Implementation of fields extension (https://github.com/stac-api-extensions/fields/blob/main/README.md)
    This implementation differs slightly from the documented semantics in that the default fields will always
    be included regardless of `include` or `exclude` values so as to ensure valid stac items.

    fields = {'include': [...], 'exclude': [...]}
    """
    res = []

    for item in items:
        # minimum fields needed for a valid stac item
        default_fields = [
            "id",
            "type",
            "geometry",
            "bbox",
            "links",
            "assets",
            "stac_version",
            # while not necessary for a valid stac item, we still want them included
            "stac_extensions",
            "collection",
        ]

        # datetime is one of the default fields, but might be included as start_datetime/end_datetime instead
        if _get_property("properties.start_datetime", item) is None:
            dt_field = ["properties.start_datetime", "properties.end_datetime"]
        else:
            dt_field = ["properties.datetime"]

        try:
            # if 'include' is present at all, start with default fields to add to or extract from
            include = fields["include"]
            if include is None:
                include = []

            filtered_item = {k: _get_property(k, item) for k in default_fields}
            # handle datetime separately due to nested keys
            for f in dt_field:
                filtered_item = dicttoolz.assoc_in(
                    filtered_item, f.split("."), _get_property(f, item)
                )
        except KeyError:
            # if 'include' wasn't provided, remove 'exclude' fields from set of all available fields
            filtered_item = item.to_dict()
            include = []

        # add datetime field names to list of defaults for easy access
        default_fields.extend(dt_field)
        include = list(set(include + default_fields))

        for exc in fields.get("exclude", []):
            if exc not in default_fields:
                filtered_item = dissoc_in(filtered_item, exc)

        # include takes precedence over exclude, plus account for a nested field of an excluded field
        for inc in include:
            # we don't want to insert None values if a field doesn't exist, but we also don't want to error
            try:
                filtered_item = dicttoolz.update_in(
                    d=filtered_item,
                    keys=inc.split("."),
                    func=lambda _: _get_property(inc, item, no_default=True),
                )
            except KeyError:
                continue

        res.append(filtered_item)

    return res


def search_stac_items(
    get_next_url: Callable[[int], str],
    limit: int,
    offset: int,
    dataset_ids: Sequence[uuid.UUID] | None = None,
    product_names: list[str] | None = None,
    bbox: tuple[float, float, float, float] | None = None,
    intersects: BaseGeometry | None = None,
    time: tuple[datetime, datetime] | None = None,
    full_information: bool = False,
    order: ItemSort = ItemSort.DEFAULT_SORT,
    include_total_count: bool = False,
    use_post_request: bool = False,
    fields: dict | None = None,
    sortby: list[dict] | None = None,
    filter_lang: str | None = None,
    filter_cql: str | dict | None = None,
) -> ItemCollection:
    """
    Perform a search, returning a FeatureCollection of stac Item results.

    :param get_next_url: A function that calculates a page url for the given offset.
    """
    if limit < 1:
        limit = get_default_limit()

    offset = offset or 0
    items = list(
        _model.STORE.search_items(
            product_names=product_names,
            time=time,
            bbox=bbox,
            limit=limit + 1,
            dataset_ids=dataset_ids,
            intersects=intersects,
            offset=offset,
            full_dataset=full_information,
            filter_lang=filter_lang,
            filter_cql=filter_cql,
            order=sortby if sortby is not None else order,
        )
    )
    returned = items[:limit]
    there_are_more = len(items) == limit + 1

    extra_properties = {"links": [], "numberReturned": len(returned)}
    if include_total_count:
        count_matching = _model.STORE.get_count(
            product_names=product_names,
            time=time,
            bbox=bbox,
            intersects=intersects,
            dataset_ids=dataset_ids,
            filter_lang=filter_lang,
            filter_cql=filter_cql,
        )
        extra_properties["numberMatched"] = count_matching

    items = [as_stac_item(f) for f in returned]
    items = _handle_fields_extension(items, fields) if fields else items

    result = ItemCollection(items, extra_fields=extra_properties)

    if there_are_more:
        next_link: dict[str, str | bool | dict] = {
            "rel": "next",
            "title": "Next page of Items",
            "type": "application/geo+json",
        }
        if use_post_request:
            next_link.update(
                {
                    "method": "POST",
                    "merge": True,
                    # Unlike GET requests, we can tell them to repeat their same request args
                    # themselves.
                    #
                    # Same URL:
                    "href": flask.request.url,
                    # ... with a new offset.
                    "body": {"_o": offset + limit},
                }
            )
        else:
            # Otherwise, let the route create the next url.
            next_link.update({"method": "GET", "href": get_next_url(offset + limit)})

        result.extra_fields["links"].append(next_link)

    return result


def search_stac_collections(
    get_next_url: Callable[[int], str],
    limit: int,
    offset: int,
    bbox: tuple[float, float, float, float] | None,
    time: tuple[datetime, datetime] | None,
    q: list[str] | None,
) -> tuple[list[Collection], dict[str, Any]]:
    if limit < 1:
        limit = get_default_limit()

    collections = list(
        _model.STORE.search_collections(
            time=time, bbox=bbox, q=q, limit=limit + 1, offset=offset
        )
    )
    returned = collections[:limit]
    there_are_more = len(collections) == limit + 1

    count_matching = len(
        list(_model.STORE.search_collections(time=time, bbox=bbox, q=q))
    )

    extra_properties: dict[str, int | list[dict]] = {
        "links": [],
        "numberReturned": len(returned),
        "numberMatched": count_matching,
    }

    result = [as_stac_collection(r) for r in returned]

    if there_are_more:
        next_link = {
            "rel": "next",
            "title": "Next page of Collections",
            "type": "application/json",
            "method": "GET",
            "href": get_next_url(offset + limit),
        }
        assert not isinstance(extra_properties["links"], int)
        extra_properties["links"].append(next_link)

    return result, extra_properties


# Response helpers


def _stac_response(
    doc: STACObject | ItemCollection, content_type="application/json"
) -> flask.Response:
    """Return a stac document as the flask response"""
    if isinstance(doc, STACObject):
        doc.set_root(root_catalog())
    return _utils.as_json(doc.to_dict(), content_type=content_type)


def _geojson_stac_response(doc: STACObject | ItemCollection) -> flask.Response:
    """Return a stac item"""
    return _stac_response(doc, content_type="application/geo+json")


# Root setup


def stac_endpoint_information() -> dict:
    config = current_app.config
    o = {
        "id": config.get("STAC_ENDPOINT_ID", "odc-explorer"),
        "title": config.get("STAC_ENDPOINT_TITLE", "Default ODC Explorer instance"),
    }
    description = config.get(
        "STAC_ENDPOINT_DESCRIPTION",
        "Configure stac endpoint information in your Explorer `settings.env.py` file",
    )
    if description:
        o["description"] = description
    return o


def root_catalog():
    c = Catalog(**stac_endpoint_information())
    c.set_self_href(url_for(".root"))
    return c


##########################
# ENDPOINTS
##########################

CONFORMANCE_CLASSES = [
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
    "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
    "https://api.stacspec.org/v1.0.0/core",
    "https://api.stacspec.org/v1.0.0/item-search",
    "https://api.stacspec.org/v1.0.0/ogcapi-features",
    "https://api.stacspec.org/v1.0.0/item-search#fields",
    "https://api.stacspec.org/v1.1.0/item-search#sort",
    "https://api.stacspec.org/v1.0.0/item-search#filter",
    "http://www.opengis.net/spec/cql2/1.0/conf/cql2-text",
    "http://www.opengis.net/spec/cql2/1.0/conf/cql2-json",
    "http://www.opengis.net/spec/cql2/1.0/conf/basic-cql2",
    "http://www.opengis.net/spec/cql2/1.0/conf/advanced-comparison-operators",
    "http://www.opengis.net/spec/cql2/1.0/conf/spatial-operators",
    "http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/filter",
    "https://api.stacspec.org/v1.0.0/collections",
    "https://api.stacspec.org/v1.0.0-rc.1/collection-search",
    "https://api.stacspec.org/v1.0.0-rc.1/collection-search#free-text",
    "http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/simple-query",
]


@bp.route("", strict_slashes=False)
def root():
    """
    The root stac page links to each collection (product) catalog
    """
    c = root_catalog()
    c.links.extend(
        [
            Link(
                title="Collections",
                # description="All product collections",
                rel="data",
                media_type="application/json",
                target=url_for(".collections"),
            ),
            Link(
                title="Arrivals",
                # description="Most recently added items",
                rel="child",
                media_type="application/json",
                target=url_for(".arrivals"),
            ),
            Link(
                title="Item Search",
                rel="search",
                media_type="application/json",
                target=url_for(".stac_search"),
            ),
            Link(
                title="Queryables",
                rel="http://www.opengis.net/def/rel/ogc/1.0/queryables",
                media_type="application/json",
                target=url_for(".queryables"),
            ),
            # Individual Product Collections
            *(
                Link(
                    title=product.name,
                    # description=product.definition.get("description"),
                    rel="child",
                    media_type="application/json",
                    target=url_for(".collection", collection=product.name),
                )
                for product, _ in _model.get_products_with_summaries()
            ),
        ]
    )
    c.extra_fields = {"conformsTo": CONFORMANCE_CLASSES}

    return _stac_response(c)


@bp.route("/conformance")
def conformance():
    return _utils.as_json({"conformsTo": CONFORMANCE_CLASSES})


@bp.route("/search", methods=["GET", "POST"])
def stac_search():
    """
    Search api for stac items.
    """
    if request.method == "GET":
        args: ImmutableMultiDict | TypeConversionDict = request.args
    else:
        args = TypeConversionDict(request.get_json())

    products: list = args.get("collections", default=[], type=_array_arg)

    if "collection" in args:
        products.append(args.get("collection"))

    return _geojson_stac_response(
        _handle_search_request(request.method, args, products, True)
    )


# Collections


@bp.route("/collections", methods=["GET"])
def collections():
    """
    This is like the root "/", but has full information for each collection in
     an array (instead of just a link to each collection).
    """
    if request.args:
        results, props = _handle_collection_search(request.args)
    else:
        props = {"links": []}
        results = [as_stac_collection(r) for r in _model.STORE.search_collections()]

    props["links"].extend(
        [
            {"rel": "self", "type": "application/json", "href": request.url},
            {"rel": "root", "type": "application/json", "href": url_for(".root")},
            {"rel": "parent", "type": "application/json", "href": url_for(".root")},
        ]
    )

    return _utils.as_json(
        dict(**props, collections=[collection.to_dict() for collection in results])
    )


@bp.route("/queryables")
def queryables():
    """
    Define what terms are available for use when writing filter expressions for the entire catalog
    Part of basic CQL2 conformance for stac-api filter implementation.
    See: https://github.com/stac-api-extensions/filter#queryables
    """
    return _utils.as_json(
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": flask.request.base_url,
            "type": "object",
            "title": "",
            "properties": {
                "id": {
                    "title": "Item ID",
                    "description": "Item identifier",
                    "$ref": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/"
                    "item.json#/definitions/core/allOf/2/properties/id",
                },
                "collection": {
                    "description": "Collection",
                    "$ref": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/"
                    "item.json#/collection",
                },
                "geometry": {
                    "description": "Geometry",
                    "$ref": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json#/geometry",
                },
                "datetime": {
                    "description": "Datetime",
                    "$ref": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/"
                    "datetime.json#/properties/datetime",
                },
            },
            "additionalProperties": True,
        }
    )


@bp.route("/collections/<collection>/queryables")
def collection_queryables(collection: str):
    """
    The queryables resources for a given collection (barebones implementation)
    """
    try:
        product = _model.STORE.get_product(collection)
    except KeyError:
        abort(404, f"Unknown collection {collection!r}")

    collection_title = product.definition.get("description")
    return _utils.as_json(
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": flask.request.base_url,
            "type": "object",
            "title": f"Queryables for {collection_title}",
            "properties": {
                "id": {
                    "title": "Item ID",
                    "description": "Item identifier",
                    "$ref": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/"
                    "item.json#/definitions/core/allOf/2/properties/id",
                },
                "collection": {
                    "description": "Collection",
                    "$ref": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/"
                    "item.json#/collection",
                },
                "geometry": {
                    "description": "Geometry",
                    "$ref": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json#/geometry",
                },
                "datetime": {
                    "description": "Datetime",
                    "$ref": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/"
                    "datetime.json#/properties/datetime",
                },
            },
            "additionalProperties": True,
        }
    )


@bp.route("/collections/<collection>")
def collection(collection: str):
    """
    Overview of a WFS Collection (a datacube product)
    """
    try:
        _model.STORE.get_product(collection)
    except KeyError:
        abort(404, f"Collection {collection!r} not found")
    # The preceding get_product ensures collection exists.
    c = _model.STORE.get_collection(collection)
    assert c is not None
    return _stac_response(as_stac_collection(c))


@bp.route("/collections/<collection>/items")
def collection_items(collection: str):
    """
    We no longer have one 'items' link. Redirect them to a stac search that implements the
    same FeatureCollection result.
    """
    try:
        _model.STORE.get_product(collection)
    except KeyError:
        abort(404, f"Collection {collection!r} not found")

    return flask.redirect(
        url_for(".stac_search", collection=collection, **request.args)
    )


@bp.route("/collections/<collection>/items/<uuid:dataset_id>")
def item(collection: str, dataset_id: uuid.UUID):
    dataset = _model.STORE.get_item(dataset_id)
    if not dataset:
        abort(404, f"No dataset found with id {dataset_id!r}")

    actual_product_name = dataset.product_name
    if collection != actual_product_name:
        # We're not doing a redirect as we don't want people to rely on wrong urls
        # (and we're unkind)
        actual_url = url_for(
            ".item", collection=actual_product_name, dataset_id=dataset_id
        )
        abort(
            404,
            "No such dataset in collection.\n"
            f"Perhaps you meant collection {actual_product_name}: {actual_url})",
        )

    return _geojson_stac_response(as_stac_item(dataset))


# Catalogs


@bp.route("/catalogs/<collection>/<int:year>-<int:month>")
def collection_month(collection: str, year: int, month: int):
    """ """
    all_time_summary = _model.get_time_summary(collection, year, month)
    if not all_time_summary:
        abort(404, f"No data for {collection!r} {year} {month}")

    default_catalog_size = current_app.config.get(
        "STAC_DEFAULT_CATALOG_SIZE", DEFAULT_CATALOG_SIZE
    )
    request_args = request.args
    limit = request_args.get("limit", default=default_catalog_size, type=int)
    offset = request_args.get("_o", default=0, type=int)

    items = list(
        _model.STORE.search_items(
            product_names=[collection],
            time=_utils.as_time_range(year, month),
            limit=limit + 1,
            offset=offset,
            # We need the full dataset to get dataset labels.
            full_dataset=True,
        )
    )
    returned = items[:limit]
    there_are_more = len(items) == limit + 1

    optional_links: list[Link] = []
    if there_are_more:
        next_url = url_for(
            ".collection_month",
            collection=collection,
            year=year,
            month=month,
            _o=offset + limit,
        )
        optional_links.append(Link(rel="next", target=next_url))

    date = datetime(year, month, 1).date()
    c = Catalog(
        f"{collection}-{year}-{month}",
        description=f"{collection} for {date.strftime('%B %Y')}",
    )

    c.links.extend(
        [
            Link(rel="self", target=request.url),
            # dict(rel='parent', href= catalog?,
            # Each item.
            *(
                Link(
                    title="Unknown"
                    if item_summary.odc_dataset is None
                    else _utils.dataset_label(item_summary.odc_dataset),
                    rel="item",
                    target=url_for(
                        ".item",
                        collection=item_summary.product_name,
                        dataset_id=item_summary.dataset_id,
                    ),
                )
                for item_summary in items
            ),
            *optional_links,
        ]
    )

    # ????
    c.extra_fields["numberReturned"] = len(returned)
    c.extra_fields["numberMatched"] = all_time_summary.dataset_count

    return _stac_response(c)


@bp.route("/catalogs/arrivals")
def arrivals():
    """
    Virtual catalog of the items most recently indexed into this index
    """
    c = Catalog(
        id="arrivals",
        title="Dataset Arrivals",
        description="The most recently added Items to this index",
    )

    c.links.extend(
        [
            Link(rel="self", target=request.url),
            Link(rel="items", target=url_for(".arrivals_items")),
        ]
    )
    return _stac_response(c)


@bp.route("/catalogs/arrivals/items")
def arrivals_items():
    """
    Get the Items most recently indexed into this Open Data Cube instance.

    This returns a Stac FeatureCollection of complete Stac Items, with paging links.
    """
    limit = request.args.get("limit", default=get_default_limit(), type=int)
    offset = request.args.get("_o", default=0, type=int)
    check_page_limit(limit)

    def next_page_url(next_offset):
        return url_for(".arrivals_items", limit=limit, _o=next_offset)

    return _geojson_stac_response(
        search_stac_items(
            limit=limit,
            offset=offset,
            get_next_url=next_page_url,
            full_information=True,
            order=ItemSort.RECENTLY_ADDED,
            include_total_count=False,
        )
    )


@bp.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = json.dumps(
        {"code": e.code, "name": e.name, "description": e.description}
    )
    response.content_type = "application/json"
    return response
