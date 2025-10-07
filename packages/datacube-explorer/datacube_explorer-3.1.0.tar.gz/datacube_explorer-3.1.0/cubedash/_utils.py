"""
Common global filters and util methods.
"""

from __future__ import annotations

import csv
import difflib
import functools
import io
import itertools
import re
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import datetime, timedelta, timezone
from datetime import tzinfo as e_tzinfo
from io import StringIO
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin, urlparse

import eodatasets3.serialise
import flask
import shapely.geometry
import shapely.validation
import structlog
from affine import Affine
from datacube import utils as dc_utils
from datacube.index.eo3 import is_doc_eo3
from datacube.index.fields import Field
from datacube.model import Dataset, MetadataType, Product, Range
from datacube.utils import InvalidDocException, jsonify_document
from eodatasets3 import serialise
from flask_themer import render_template
from odc.geo import Geometry, geom
from odc.geo.crs import CRS
from orjson.orjson import OPT_INDENT_2, dumps
from pyproj import CRS as PJCRS
from ruamel.yaml.comments import CommentedMap
from shapely.geometry import Polygon, shape
from sqlalchemy import TIMESTAMP, func
from werkzeug.datastructures import MultiDict

if TYPE_CHECKING:
    from cubedash._model import ProductWithSummary

_TARGET_CRS = "EPSG:4326"

NEAR_ANTIMERIDIAN = shape(
    {
        "coordinates": [((175, -90), (175, 90), (185, 90), (185, -90), (175, -90))],
        "type": "Polygon",
    }
)

# CRS's we use as inference results
DEFAULT_CRS_INFERENCES = [
    PJCRS.from_epsg(4283).to_wkt(),
    PJCRS.from_epsg(4326).to_wkt(),
]
MATCH_CUTOFF = 0.38

_LOG = structlog.stdlib.get_logger()


def infer_crs(crs_str: str) -> str | None:
    plausible_list = [
        code
        for code in DEFAULT_CRS_INFERENCES
        if difflib.SequenceMatcher(None, code.lower(), crs_str.lower()).ratio() >= 0.2
    ]

    def chars_in_common(s: str):
        return sum(
            b.size
            for b in difflib.SequenceMatcher(
                None, s.lower(), crs_str.lower()
            ).get_matching_blocks()
        )

    sorted_closest_wkt = sorted(plausible_list, key=chars_in_common, reverse=False)

    if len(sorted_closest_wkt) == 0:
        return None

    epsg = PJCRS.from_wkt(sorted_closest_wkt[-1]).to_epsg()
    return f"epsg:{epsg}"


def render(template, **context):
    return render_template(template, **context)


def expects_eo3_metadata_type(md: MetadataType) -> bool:
    """
    Does the given metadata type expect EO3 datasets?
    """
    try:
        MetadataType.validate_eo3(md.definition)
        return True
    except InvalidDocException:
        return False


def jsonb_doc_expression(md: MetadataType):
    return md.dataset_fields["metadata_doc"].alchemy_expression  # type: ignore[attr-defined]


def datetime_expression(md_type: MetadataType):
    """
    Get an Alchemy expression for a timestamp of datasets of the given metadata type.
    There is another function sharing the same logic but is for flask template
    in file: _utils.py function datetime_from_metadata
    """
    # If EO3+Stac formats, there's already has a plain 'datetime' field,
    # So we can use it directly.
    if expects_eo3_metadata_type(md_type):
        props = jsonb_doc_expression(md_type)["properties"]

        # .... but in newer Stac, datetime is optional.
        # .... in which case we fall back to the start time.
        #      (which I think makes more sense in large ranges than a calculated center time)
        return (
            func.coalesce(props["datetime"].astext, props["dtr:start_datetime"].astext)
            .cast(TIMESTAMP(timezone=True))
            .label("center_time")
        )

    # On older EO datasets, there's only a time range, so we take the center time.
    # (This matches the logic in ODC's Dataset.center_time)
    time = md_type.dataset_fields["time"].alchemy_expression  # type: ignore[attr-defined]
    return (func.lower(time) + (func.upper(time) - func.lower(time)) / 2).label(
        "center_time"
    )


def get_dataset_file_offsets(dataset: Dataset) -> dict[str, str]:
    """
    Get (usually relative) paths for all known files of a dataset.

    Returns {name, url}
    """

    # Get paths to measurements (usually relative, but may not be)
    uri_list = {
        name: m["path"] for name, m in dataset.measurements.items() if m.get("path")
    }

    # Add accessories too, if possible
    if is_doc_eo3(dataset.metadata_doc):
        dataset_doc = serialise.from_doc(dataset.metadata_doc, skip_validation=True)
        uri_list.update({name: a.path for name, a in dataset_doc.accessories.items()})

    return uri_list


def as_resolved_remote_url(location: str | None, offset: str) -> str:
    """
    Convert a dataset location and file offset to a full remote URL.
    """
    return as_external_url(
        urljoin(location or "", offset),
        flask.current_app.config.get("CUBEDASH_DATA_S3_REGION", "ap-southeast-2"),
        location is None,
    )


def as_external_url(
    url: str, s3_region: str | None = None, is_base: bool = False
) -> str:
    """
    Convert a URL to an externally-visible one.

    >>> import pytest; pytest.skip() # doctests aren't working outside flask context :(
    >>> # Converts s3 to http
    >>> as_external_url('s3://some-data/L2/S2A_OPER_MSI_ARD__A030100_T56LNQ_N02.09/ARD-METADATA.yaml', "ap-southeast-2")
    'https://some-data.s3.ap-southeast-2.amazonaws.com/L2/S2A_OPER_MSI_ARD__A030100_T56LNQ_N02.09/ARD-METADATA.yaml'
    >>> # Other URLs are left as-is
    >>> unconvertible_url = 'file:///g/data/xu18/ga_ls8c_ard_3-1-0_095073_2019-03-22_final.odc-metadata.yaml'
    >>> unconvertible_url == as_external_url(unconvertible_url)
    True
    >>> as_external_url('some/relative/path.txt')
    'some/relative/path.txt'
    >>> # if base uri was none, we may want to return the s3 location instead of the metadata yaml
    """
    parsed = urlparse(url)

    if s3_region and parsed.scheme == "s3":
        # get buckets for which link should be to data location instead of s3 link
        data_location = flask.current_app.config.get("SHOW_DATA_LOCATION", {})
        if parsed.netloc in data_location:
            # remove the first '/'
            path = parsed.path[1:]
            if is_base:
                # if it's the folder url, get the directory path
                path = path[: path.rindex("/") + 1]
                path = f"?prefix={path}"
            return f"https://{data_location.get(parsed.netloc)}/{path}"

        return f"https://{parsed.netloc}.s3.{s3_region}.amazonaws.com{parsed.path}"

    return url


def group_field_names(request: dict) -> dict:
    """
    In a request, a dash separates field names from a classifier (eg: begin/end).

    Group the query classifiers by field names.

    >>> group_field_names({'lat-begin': '1', 'lat-end': '2', 'orbit': 3})
    {'lat': {'begin': '1', 'end': '2'}, 'orbit': {'val': 3}}
    """
    out: dict = defaultdict(dict)

    for field_expr, val in request.items():
        comps = field_expr.split("-")
        field_name = comps[0]

        if len(comps) == 1:
            constraint = "val"
        elif len(comps) == 2:
            constraint = comps[1]
        else:
            raise ValueError("Corrupt field name " + field_expr)

        # Skip empty values
        if val is None or val == "":
            continue

        out[field_name][constraint] = val
    return dict(out)


def get_sorted_product_summaries(
    product_summaries: Sequence[ProductWithSummary], key: Callable[[Any], Any]
) -> list[tuple[str, list]]:
    return sorted(
        (
            (name or "", list(items))
            for (name, items) in itertools.groupby(
                sorted(product_summaries, key=key), key=key
            )
        ),
        # Show largest groups first
        key=lambda k: len(k[1]),
        reverse=True,
    )


def query_to_search(request: MultiDict, product: Product) -> dict:
    args = _parse_url_query_args(request, product)

    # If their range is backwards (high, low), let's reverse it.
    # (the intention is "between these two numbers")
    for key in args:
        value = args[key]
        if (
            isinstance(value, Range)
            and value.begin is not None
            and value.end is not None
            and value.end < value.begin
        ):
            args[key] = Range(value.end, value.begin)

    return args


def dataset_label(dataset: Dataset) -> str:
    """
    Get a human-readable label for the dataset
    """
    # Identify by label if they have one
    label = dataset.metadata.fields.get("label")
    if label is not None:
        return label

    # Otherwise try to get a file/folder name for the dataset's location.
    if dataset.uri:
        name = _get_reasonable_file_label(dataset.uri)
        if name:
            return name

    # TODO: Otherwise try to build a label from the available fields?
    return str(dataset.id)


def _get_reasonable_file_label(uri: str) -> str | None:
    """
    Get a label for the dataset from a URI.... if we can.

    >>> uri = '/tmp/some/ls7_wofs_1234.nc'
    >>> _get_reasonable_file_label(uri)
    'ls7_wofs_1234.nc'
    >>> uri = 'file:///g/data/rs0/datacube/002/LS7_ETM_NBAR/10_-24/LS7_ETM_NBAR_3577_10_-24_1999_v1496652530.nc#part=0'
    >>> _get_reasonable_file_label(uri)
    'LS7_ETM_NBAR_3577_10_-24_1999_v1496652530.nc#part=0'
    >>> uri = 'file:///tmp/ls7_nbar_20120403_c1/ga-metadata.yaml'
    >>> _get_reasonable_file_label(uri)
    'ls7_nbar_20120403_c1'
    >>> uri = 's3://deafrica-data/jaxa/alos_palsar_mosaic/2017/N05E040/N05E040_2017.yaml'
    >>> _get_reasonable_file_label(uri)
    'N05E040_2017'
    >>> uri = 'file:///g/data/if87/S2A_OPER_MSI_ARD_TL_EPAE_20180820T020800_A016501_T53HQA_N02.06/ARD-METADATA.yaml'
    >>> _get_reasonable_file_label(uri)
    'S2A_OPER_MSI_ARD_TL_EPAE_20180820T020800_A016501_T53HQA_N02.06'
    >>> uri = 'https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/2020/S2B_36PTU_20200101_0_L2A/'
    >>> _get_reasonable_file_label(uri)
    'S2B_36PTU_20200101_0_L2A'
    >>> _get_reasonable_file_label('ga-metadata.yaml')
    """
    for component in reversed(uri.rsplit("/", maxsplit=3)):
        # If it's a default yaml document name, we want the folder name instead.
        if component and component not in (
            "ga-metadata.yaml",
            "agdc-metadata.yaml",
            "ARD-METADATA.yaml",
        ):
            suffixes = component.rsplit(".", maxsplit=1)
            # Remove the yaml/json suffix if we have one now.
            if suffixes[-1] in ("yaml", "json"):
                return ".".join(suffixes[:-1])
            return component
    return None


def product_license(product: Product) -> str | None:
    """
    What is the license to display for this product?

    The return format should match the stac collection spec
    - Either a SPDX License identifier
    - 'various'
    -  or 'proprietary'

    Example value: "CC-BY-SA-4.0"
    """
    # Does the metadata type has a 'license' field defined?
    if "license" in product.metadata.fields:
        return product.metadata.fields["license"]

    # Otherwise, look in a default location in the document, matching stac collections.
    # (Note that datacube > 1.8.0b6 is required to allow licenses in products).
    if "license" in product.definition:
        return product.definition["license"]

    # Otherwise is there a global default?
    return flask.current_app.config.get("CUBEDASH_DEFAULT_LICENSE", None)


def _next_month(date: datetime) -> datetime:
    if date.month == 12:
        return datetime(date.year + 1, 1, 1)

    return datetime(date.year, date.month + 1, 1)


def as_time_range(
    year: int | None,
    month: int | None = None,
    day: int | None = None,
    tzinfo: e_tzinfo | None = None,
) -> Range | None:
    """
    >>> as_time_range(2018)
    Range(begin=datetime.datetime(2018, 1, 1, 0, 0), end=datetime.datetime(2019, 1, 1, 0, 0))
    >>> as_time_range(2018, 2)
    Range(begin=datetime.datetime(2018, 2, 1, 0, 0), end=datetime.datetime(2018, 3, 1, 0, 0))
    >>> as_time_range(2018, 8, 3)
    Range(begin=datetime.datetime(2018, 8, 3, 0, 0), end=datetime.datetime(2018, 8, 4, 0, 0))
    """
    if year and month and day:
        start = datetime(year, month, day)
        end = start + timedelta(days=1)
    elif year and month:
        start = datetime(year, month, 1)
        end = _next_month(start)
    elif year:
        start = datetime(year, 1, 1)
        end = datetime(year + 1, 1, 1)
    else:
        return None

    return Range(start.replace(tzinfo=tzinfo), end.replace(tzinfo=tzinfo))


def _parse_url_query_args(request: MultiDict, product: Product) -> dict[str, Any]:
    """
    Convert search arguments from url query args into datacube index search parameters
    """
    query = {}

    field_groups = group_field_names(request)

    for field_name, field_vals in field_groups.items():
        field = product.metadata_type.dataset_fields.get(field_name)
        if not field:
            raise ValueError(f"No field {field_name!r} for product {product.name!r}")

        parser = _field_parser(field)

        if "val" in field_vals:
            query[field_name] = parser(field_vals["val"])
        elif "begin" in field_vals or "end" in field_vals:
            begin, end = field_vals.get("begin"), field_vals.get("end")
            query[field_name] = Range(
                parser(begin) if begin else None, parser(end) if end else None
            )
        else:
            raise ValueError(f"Unknown field classifier: {field_vals!r}")

    return query


def _field_parser(field: Field):
    if field.type_name.endswith("-range"):
        field = field.lower  # type: ignore[attr-defined]

    try:
        parser = field.parse_value  # type: ignore[attr-defined]
    except AttributeError:
        parser = _unchanged_value
    return parser


def _unchanged_value(a):
    return a


def default_utc(d: datetime) -> datetime:
    if d.tzinfo is None:
        return d.replace(tzinfo=timezone.utc)
    return d


def now_utc() -> datetime:
    return default_utc(datetime.now(timezone.utc))


def dataset_created(dataset: Dataset) -> datetime | None:
    if "created" in dataset.metadata.fields:
        return dataset.metadata.created

    value = dataset.metadata.creation_dt
    if value:
        try:
            return default_utc(dc_utils.parse_time(value))
        except ValueError:
            _LOG.warning(
                "invalid_dataset.creation_dt", dataset_id=dataset.id, value=value
            )
    # like in _dataset_creation_expression, if there's no creation time
    # then we fall back to indexed time (if it exists)
    if dataset.indexed_time:
        return default_utc(dc_utils.parse_time(dataset.indexed_time))
    return None


def datetime_from_metadata(dataset: Dataset) -> datetime:
    """
    This function shares similar logic to datetime_expression (above),
    but retrieves values for the flask template.
    Get datetime info from metadata_doc rather than Dataset.center_time for EO3
    """
    # seems to be a misleading name...
    md_type = dataset.metadata_type
    if expects_eo3_metadata_type(md_type):
        # prefer using datetime or start_datetime directly
        properties = dataset.metadata_doc["properties"]
        t = properties.get("datetime") or properties.get("dtr:start_datetime")
        return default_utc(dc_utils.parse_time(t))
    # stick with center time for EO datasets
    return default_utc(dataset.center_time)


def as_rich_json(o):
    """
    Use datacube's method of simplifying objects before serialising to json

    (Primarily useful for serialising datacube models reliably)

    Much slower than as_json()
    """
    return as_json(jsonify_document(o))


def as_json(
    o, content_type="application/json", downloadable_filename_prefix: str | None = None
) -> flask.Response:
    """
    Serialise an object into a json flask response.

    Optionally provide a filename, to tell web-browsers to download
    it on click with that filename.
    """
    # Indent if they're loading directly in a browser.
    #   (Flask's Accept parsing is too smart, and sees html-acceptance in
    #    default ajax requests "accept: */*". So we do it raw.)
    prefer_formatted = "text/html" in flask.request.headers.get("Accept", ())

    response = flask.Response(
        dumps(
            o, option=OPT_INDENT_2 if prefer_formatted else 0, default=_json_fallback
        ),
        content_type=content_type,
    )

    if downloadable_filename_prefix:
        suggest_download_filename(response, downloadable_filename_prefix, ".json")

    return response


def _json_fallback(o, *args, **kwargs):
    if isinstance(o, (geom.BoundingBox, Affine)):
        return tuple(o)

    # I think orjson swallows our nicer error message?
    raise TypeError(
        "Cannot (yet) serialise object type to json: "
        f"{o.__module__}.{type(o).__qualname__}"
    )


def as_geojson(o, downloadable_filename_prefix: str | None):
    """
    Serialise the given object into a GeoJSON flask response.

    Optionally provide a filename, to tell web-browsers to download
    it on click with that filename.
    """
    response = as_json(o, content_type="application/geo+json")

    if downloadable_filename_prefix:
        suggest_download_filename(response, downloadable_filename_prefix, ".geojson")
    return response


def common_uri_prefix(uris: Sequence[str]):
    """
    This is like `os.path.commonpath()`, but always expects URL paths.
    (i.e. forward slashes in all environments, and will not strip double slashes '//')

    >>> common_uri_prefix(['file:///a/thing-1.txt'])
    'file:///a/thing-1.txt'
    >>> common_uri_prefix(['file:///a/1.txt', 'file:///a/2.txt', 'file:///a/3.txt'])
    'file:///a/'
    >>> # Returns the common directory, not a partial filename:
    >>> common_uri_prefix(['file:///a/thing-1.txt', 'file:///a/thing-2.txt', 'file:///a/thing-3.txt'])
    'file:///a/'
    >>> common_uri_prefix(['http://example.com/things/'])
    'http://example.com/things/'
    >>> common_uri_prefix(['http://example.com/things/'] * 4)
    'http://example.com/things/'
    >>> common_uri_prefix(['http://example.com/things/', 'http://example.com/others/'])
    'http://example.com/'
    >>> common_uri_prefix([])
    ''
    """
    if not uris:
        return ""
    first_possibility = min(uris)
    last_possibility = max(uris)

    if first_possibility == last_possibility:
        # All are the same
        return first_possibility

    for i, c in enumerate(first_possibility):
        if c != last_possibility[i]:
            result = first_possibility[:i]
            break
    else:
        result = first_possibility

    return result[: result.rfind("/") + 1]


def suggest_download_filename(
    response: flask.Response, prefix: str, suffix: str
) -> None:
    """
    Give the Browser a hint to download the file with the given filename
    (rather than display it in-line).
    """
    explorer_id = only_alphanumeric(
        flask.current_app.config.get("STAC_ENDPOINT_ID", "")
    )
    if explorer_id:
        prefix += f"-{explorer_id.lower()}"

    response.headers["Content-Disposition"] = f"attachment; filename={prefix}{suffix}"


def as_yaml(
    *o, content_type: str = "text/yaml", downloadable_filename_prefix: str | None = None
) -> flask.Response:
    """
    Return a yaml response.

    Multiple args will return a multi-doc yaml file.
    """
    stream = StringIO()
    eodatasets3.serialise.dumps_yaml(stream, *o)
    response = flask.Response(stream.getvalue(), content_type=content_type)
    if downloadable_filename_prefix:
        suggest_download_filename(response, downloadable_filename_prefix, ".yaml")

    return response


_ALNUM_PATTERN = re.compile("[^0-9a-zA-Z]+")


def only_alphanumeric(s: str) -> str:
    """
    Strip any chars that aren't simple alphanumeric.

    Useful for using strings as still-slightly-human-readbale identifiers.

    >>> only_alphanumeric("Guitar o'clock")
    'guitar-o-clock'
    """
    return _ALNUM_PATTERN.sub("-", s).lower()


def as_csv(
    *,
    filename_prefix: str,
    headers: tuple[str, ...],
    rows: Iterable[tuple[object, ...]],
):
    """Return a CSV Flask response."""
    out = io.StringIO()
    cw = csv.writer(out)
    cw.writerow(headers)
    cw.writerows(rows)
    response = flask.make_response(out.getvalue())
    suggest_download_filename(response, filename_prefix, ".csv")
    response.headers["Content-type"] = "text/csv"
    return response


def prepare_dataset_formatting(
    dataset: Dataset, include_source_url=False, include_locations=False
) -> CommentedMap:
    """
    Try to format a raw Dataset document for readability.

    This will change property order, add comments on the type & source url.
    """
    doc = dict(dataset.metadata_doc)

    if include_locations:
        doc["location"] = dataset.uri

    # If it's EO3, use eodatasets's formatting. It's better.
    if is_doc_eo3(doc):
        doc = eodatasets3.serialise.prepare_formatting(doc)
        if include_source_url:
            doc.yaml_set_comment_before_after_key(
                "$schema", before=f"url: {flask.request.url}"
            )
        # Strip EO-legacy fields.
        undo_eo3_compatibility(doc)
        return doc
    return prepare_document_formatting(
        doc,
        # Label old-style datasets as old-style datasets.
        doc_friendly_label="EO1 Dataset",
        include_source_url=include_source_url,
    )


def prepare_document_formatting(
    metadata_doc: Mapping,
    doc_friendly_label: str = "",
    include_source_url: bool | str = False,
):
    """
    Try to format a raw document for readability.

    This will change property order, add comments on the type & source url.
    """

    def get_property_priority(ordered_properties: list, keyval):
        key, _ = keyval
        if key not in ordered_properties:
            return 999
        return ordered_properties.index(key)

    header_comments = []
    if doc_friendly_label:
        header_comments.append(doc_friendly_label)
    if include_source_url:
        if include_source_url is True:
            include_source_url = flask.request.url
        header_comments.append(f"url: {include_source_url}")

    # Give the document the same order as eo-datasets. It's far more readable (ID/names first, sources last etc.)
    ordered_metadata = CommentedMap(
        sorted(
            metadata_doc.items(),
            key=functools.partial(get_property_priority, EODATASETS_PROPERTY_ORDER),
        )
    )

    # Order any embedded ones too.
    if "lineage" in ordered_metadata:
        ordered_metadata["lineage"] = dict(
            sorted(
                ordered_metadata["lineage"].items(),
                key=functools.partial(
                    get_property_priority, EODATASETS_LINEAGE_PROPERTY_ORDER
                ),
            )
        )

        if "source_datasets" in ordered_metadata["lineage"]:
            for type_, source_dataset_doc in ordered_metadata["lineage"][
                "source_datasets"
            ].items():
                ordered_metadata["lineage"]["source_datasets"][type_] = (
                    prepare_document_formatting(source_dataset_doc)
                )

    # Products have an embedded metadata doc (subset of dataset metadata)
    if "metadata" in ordered_metadata:
        ordered_metadata["metadata"] = prepare_document_formatting(
            ordered_metadata["metadata"]
        )

    if header_comments:
        # Add comments above the first key of the document.
        ordered_metadata.yaml_set_comment_before_after_key(
            next(iter(metadata_doc.keys())), before="\n".join(header_comments)
        )
    return ordered_metadata


def api_path_as_filename_prefix():
    """
    Get a usable filename prefix for the given API offset.

    Eg:

        "/api/datasets/ls7_albers/2017"

    Becomes filename:

        "ls7_albers-2017-datasets.geojson"

    (the suffix is added by the response)
    """
    stem = flask.request.path.split(".")[0]
    _, kind, *period = stem.strip("/").split("/")
    return "-".join([*period, kind])


def undo_eo3_compatibility(doc) -> None:
    """
    In-place removal and undo-ing of the EO-compatibility fields added by ODC to EO3
     documents on index.
    """
    if "grid_spatial" in doc:
        del doc["grid_spatial"]
    if "extent" in doc:
        del doc["extent"]

    lineage = doc.get("lineage", {})
    # If old EO1-style lineage was built (as it is on dataset.get(include_sources=True),
    # flatten to EO3-style ID lists.

    # TODO: It's incredibly inefficient that the whole source-dataset tree has been loaded by ODC
    #       and we're now throwing it all away except the top-level ids.

    if "source_datasets" in lineage:
        new_lineage: dict = {}
        for classifier, dataset_doc in lineage["source_datasets"].items():
            new_lineage.setdefault(classifier, []).append(dataset_doc["id"])
        doc["lineage"] = new_lineage


EODATASETS_PROPERTY_ORDER = [
    "$schema",
    # Products / Types
    "name",
    "license",
    "metadata_type",
    "description",
    "metadata",
    # EO3
    "id",
    "label",
    "product",
    "locations",
    "crs",
    "geometry",
    "grids",
    "properties",
    "measurements",
    "accessories",
    # EO
    "ga_label",
    "product_type",
    "product_level",
    "product_doi",
    "creation_dt",
    "size_bytes",
    "checksum_path",
    "platform",
    "instrument",
    "format",
    "usgs",
    "rms_string",
    "acquisition",
    "extent",
    "grid_spatial",
    "gqa",
    "browse",
    "image",
    "lineage",
    "product_flags",
]
EODATASETS_LINEAGE_PROPERTY_ORDER = [
    "algorithm",
    "machine",
    "ancillary_quality",
    "ancillary",
    "source_datasets",
]


def dataset_shape(ds: Dataset) -> tuple[Polygon | None, bool]:
    """
    Get a usable extent from the dataset (if possible), and return
    whether the original was valid.
    """
    log = _LOG.bind(dataset_id=ds.id)
    try:
        extent = ds.extent
    except AttributeError:
        # `ds.extent` throws an exception on telemetry datasets,
        # as they have no grid_spatial. It probably shouldn't.
        return None, False

    if extent is None:
        log.warning("invalid_dataset.empty_extent")
        return None, False
    ds_geom = shape(extent.to_crs(CRS(_TARGET_CRS)))

    if not ds_geom.is_valid:
        log.warning(
            "invalid_dataset.invalid_extent",
            reason_text=shapely.validation.explain_validity(ds_geom),
        )
        # A zero distance may be used to “tidy” a polygon.
        clean = ds_geom.buffer(0.0)
        assert clean.geom_type in ("Polygon", "MultiPolygon"), (
            f"got {clean.geom_type} for cleaned {ds.id}"
        )
        assert clean.is_valid
        return clean, False

    if ds_geom.is_empty:
        _LOG.warning("invalid_dataset.empty_extent_geom", dataset_id=ds.id)
        return None, False

    return ds_geom, True


def bbox_as_geom(dataset: Dataset) -> Geometry | None:
    """Get dataset bounds as to Geometry object projected to target CRS"""
    if dataset.crs is None:
        return None
    bounds = dataset.bounds
    if bounds is None:
        return None
    return geom.box(*bounds.bbox, crs=dataset.crs).to_crs(CRS(_TARGET_CRS))
