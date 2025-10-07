"""
Tests that load pages and check the contained text.
"""

from datetime import datetime, timezone
from io import StringIO
from zoneinfo import ZoneInfo

import flask
import pytest
from flask.testing import FlaskClient
from ruamel.yaml import YAML, YAMLError

from cubedash import _model
from cubedash.summary import SummaryStore, _extents, show
from cubedash.summary._stores import explorer_index
from integration_tests.asserts import (
    assert_text_contains,
    assert_text_equals,
    check_area,
    check_dataset_count,
    check_last_processed,
    get_geojson,
    get_html,
    get_json,
    get_normalized_text,
    get_text_response,
)

DEFAULT_TZ = ZoneInfo("Australia/Darwin")

METADATA_TYPES = [
    "metadata/eo3_landsat_ard.odc-type.yaml",
    "metadata/eo3_landsat_l1.odc-type.yaml",
    "metadata/eo3_metadata.yaml",
    "metadata/eo_metadata.yaml",
    "metadata/eo_plus.yaml",
    "metadata/landsat_l1_scene.yaml",
    "metadata/qga_eo.yaml",
]
PRODUCTS = [
    "products/dsm1sv10.odc-product.yaml",
    "products/ga_ls8c_ard_3.odc-product.yaml",
    "products/ga_ls9c_ard_3.odc-product.yaml",
    "products/ga_ls_fc_3.odc-product.yaml",
    "products/ga_ls_wo_fq_nov_mar_3.odc-product.yaml",
    "products/hltc.odc-product.yaml",
    "products/l1_ls8_ga.odc-product.yaml",
    "products/l1_ls5.odc-product.yaml",
    "products/ls5_fc_albers.odc-product.yaml",
    "products/ls5_nbart_albers.odc-product.yaml",
    "products/ls5_nbart_tmad_annual.odc-product.yaml",
    "products/ls5_scenes.odc-product.yaml",
    "products/ls7_nbart_tmad_annual.odc-product.yaml",
    "products/ls7_nbar_albers.odc-product.yaml",
    "products/ls7_nbart_albers.odc-product.yaml",
    "products/ls7_scenes.odc-product.yaml",
    "products/ls8_nbar_albers.odc-product.yaml",
    "products/ls8_nbart_albers.odc-product.yaml",
    "products/ls8_scenes.odc-product.yaml",
    "products/pq_count_summary.odc-product.yaml",
    "products/usgs_ls7e_level1_1.odc-product.yaml",
    "products/wofs_albers.yaml",
    "products/wofs_summary.odc-product.yaml",
]
DATASETS = [
    "datasets/ga_ls8c_ard_3-sample.yaml",
    "datasets/ga_ls9c_ard_3-sample.yaml",
    "datasets/usgs_ls7e_level1_1-sample.yaml",
    "datasets/ga_ls_wo_fq_nov_mar_3-sample.yaml",
    "datasets/ga_ls_fc_3-sample.yaml",
    "datasets/high_tide_comp_20p.yaml.gz",
    # These have very large footprints, as they were unioned from many almost-identical
    # polygons and not simplified. They will trip up postgis if used naively.
    # (postgis gist index has max record size of 8k per entry)
    "datasets/pq_count_summary.yaml.gz",
    "datasets/wofs-albers-sample.yaml.gz",
]


# Use the 'auto_odc_db' fixture to populate the database with sample data.
pytestmark = pytest.mark.usefixtures("auto_odc_db")


@pytest.fixture()
def sentry_client(client: FlaskClient) -> FlaskClient:
    flask.current_app.config["SENTRY_CONFIG"] = {
        "dsn": "https://githash@number.sentry.opendatacube.org/123456",
        "include_paths": ["cubedash"],
    }
    return client


def _script(html):
    return html.css("script")


@pytest.mark.xfail()
def test_prometheus(sentry_client: FlaskClient) -> None:
    """
    Ensure Prometheus metrics endpoint exists
    """
    resp = sentry_client.get("/metrics")
    assert b"flask_exporter_info" in resp.data


def test_default_redirect(client: FlaskClient) -> None:
    rv = client.get("/", follow_redirects=False)
    # The products page is the default.
    assert rv.location.endswith("/products")


def test_get_overview(client: FlaskClient) -> None:
    html = get_html(client, "/ga_ls9c_ard_3")
    check_dataset_count(html, 11)
    check_last_processed(html, "2024-05-20T20:49:02")
    assert "ga_ls9c_ard_3 whole collection" in _h1_text(html)
    # check_area("61,...km2", html)

    html = get_html(client, "/ga_ls9c_ard_3/2021")
    check_dataset_count(html, 5)
    check_last_processed(html, "2024-05-20T20:48:14")
    assert "ga_ls9c_ard_3 across 2021" in _h1_text(html)

    html = get_html(client, "/ga_ls9c_ard_3/2022/01")
    check_dataset_count(html, 6)
    check_last_processed(html, "2024-05-20T20:49:02")
    assert "ga_ls9c_ard_3 across January 2022" in _h1_text(html)
    # check_area("30,...km2", html)


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_invalid_footprint_wofs_summary_load(client: FlaskClient) -> None:
    # This all-time overview has a valid footprint that becomes invalid
    # when reprojected to wgs84 by shapely.
    from .data_wofs_summary import wofs_time_summary

    _model.STORE._put(wofs_time_summary)
    html = get_html(client, "/wofs_summary")
    check_dataset_count(html, 1244)


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_all_products_are_shown(client: FlaskClient) -> None:
    """
    After all the complicated grouping logic, there should still be one header link for each product.
    """
    html = get_html(client, "/ls7_nbar_scene")

    # We use a sorted array instead of a Set to detect duplicates too.
    found_product_names = sorted(
        a.text(strip=True)
        for a in html.css(".product-selection-header .option-menu-link")
    )
    indexed_product_names = sorted(p.name for p in _model.STORE.all_products())
    assert found_product_names == indexed_product_names, (
        "Product shown in menu don't match the indexed products"
    )


def test_get_overview_product_links(client: FlaskClient) -> None:
    """
    Are the source and derived product lists being displayed?
    """
    html = get_html(client, "/ga_ls_fc_3/2022")

    product_links = html.css(".source-product a")
    assert [p.text(strip=True) for p in product_links] == ["ga_ls8c_ard_3"]
    assert [p.attributes["href"] for p in product_links] == [
        "/products/ga_ls8c_ard_3/2022"
    ]

    html = get_html(client, "/ga_ls8c_ard_3/2022")
    product_links = html.css(".derived-product a")
    assert [p.text(strip=True) for p in product_links] == ["ga_ls_fc_3"]
    assert [p.attributes["href"] for p in product_links] == [
        "/products/ga_ls_fc_3/2022"
    ]


def test_get_day_overviews(client: FlaskClient) -> None:
    # Individual days are computed on-the-fly rather than from summaries, so can
    # have their own issues.

    # With a dataset
    html = get_html(client, "/ga_ls8c_ard_3/2022/5/03")
    check_dataset_count(html, 1)
    assert "ga_ls8c_ard_3 on 3rd May 2022" in _h1_text(html)

    # Empty day
    html = get_html(client, "/ga_ls8c_ard_3/2017/4/22")
    check_dataset_count(html, 0)


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_summary_product(client: FlaskClient) -> None:
    # These datasets have gigantic footprints that can trip up postgis.
    html = get_html(client, "/pq_count_summary")
    check_dataset_count(html, 20)


def test_uninitialised_overview(
    unpopulated_client: FlaskClient, summary_store: SummaryStore
) -> None:
    # Populate one product, so they don't get the usage error message ("run cubedash generate")
    # Then load an unpopulated product.
    summary_store.refresh("usgs_ls7e_level1_1")

    html = get_html(unpopulated_client, "/usgs_ls7e_level1_1/2017")

    # The page should load without error, but will display 'unknown' fields
    assert (
        html.css_first("h2").text(strip=True)
        == "usgs_ls7e_level1_1: United States Geological Survey Landsat 7 \
Enhanced Thematic Mapper Plus Level 1 Collection 1"
    )
    assert_text_contains(html, "Unknown number of datasets")
    assert_text_contains(html, "No data: not yet summarised")


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_uninitialised_product(
    empty_client: FlaskClient, summary_store: SummaryStore
) -> None:
    """
    An unsummarised product should still be viewable on the product page.

    (but should be described as not summarised)
    """
    # Populate one product, so they don't get the usage error message ("run cubedash generate")
    # Then load an unpopulated product.
    summary_store.refresh("ls7_nbar_albers")

    html = get_html(empty_client, "/products/ls7_nbar_scene")

    # The page should load without error, but will mention its lack of information
    assert "ls7_nbar_scene" in html.css_first("h2").text(strip=True)
    assert "not yet summarised" in html.css_first("#content", strict=True).text(
        strip=True
    )

    # ... and a product that we populated does not have the message:
    html = get_html(empty_client, "/products/ls7_nbar_albers")
    assert "not yet summarised" not in html.css_first("#content", strict=True).text(
        strip=True
    )


def test_empty_product_overview(client: FlaskClient) -> None:
    """
    A page is still displayable without error when it has no datasets.
    """
    html = get_html(client, "/usgs_ls5t_level1_1")
    assert_text_equals(html, "0 datasets", ".dataset-count")

    assert_text_equals(html, "landsat-5", ".query-param.key-platform .value")
    assert_text_equals(html, "TM", ".query-param.key-instrument .value")


def test_empty_product_page(client: FlaskClient) -> None:
    """
    A product page is displayable when summarised, but with 0 datasets.
    """
    html = get_html(client, "/products/usgs_ls5t_level1_1")
    assert_text_contains(html, "0 datasets", ".dataset-count")

    # ... yet a normal product doesn't show the message:
    html = get_html(client, "/products/usgs_ls7e_level1_1")
    html_text = get_normalized_text(html.css_first(".dataset-count", strict=True))
    assert "0 datasets" not in html_text
    assert "5 datasets" in html_text


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_uninitialised_search_page(
    empty_client: FlaskClient, summary_store: SummaryStore
) -> None:
    # Populate one product, so they don't get the usage error message ("run cubedash generate")
    summary_store.refresh("ls7_nbar_albers")

    # Then load a completely uninitialised product.
    html = get_html(empty_client, "/datasets/ls7_nbar_scene")
    search_results = html.css(".search-result a")
    assert len(search_results) == 4


def test_view_dataset(client: FlaskClient) -> None:
    # usgs_ls7e_level1 dataset
    html = get_html(client, "/dataset/7dff1cb5-b297-5701-8390-43c0f2d58fbb")

    # Label of dataset is header
    assert "usgs_ls7e_level1_1-0-20200628_097068_2020-06-01" in html.css_first(
        "h2"
    ).text(strip=True)
    assert not html.css_first(".key-creation_dt")

    # ga_ls_wo_fq_nov_mar_3 dataset (has no label or location)
    html = get_html(client, "/dataset/974e1e89-3757-4d94-be8d-7acaeb7adf24")
    assert "-26.129 to -25.15" in html.text()
    assert "111.533 to 112.639" in html.text()
    assert not html.css_first(".key-creation_dt")

    # No dataset found: should return 404, not a server error.
    rv = client.get(
        "/dataset/de071517-af92-4dd7-bf91-12b4e7c9a435", follow_redirects=True
    )

    assert rv.status_code == 404
    assert b"No dataset found" in rv.data, rv.data.decode("utf-8")


def _h1_text(html):
    return html.css_first("h1", strict=True).text()


def test_view_product(client: FlaskClient) -> None:
    html = get_html(client, "/product/ga_ls8c_ard_3")
    assert "Geoscience Australia Landsat 8" in html.text()


def test_view_metadata_type(client: FlaskClient, odc_test_db) -> None:
    # Does it load without error?
    html = get_html(client, "/metadata-type/eo3")
    assert html.css_first("h2").text(strip=True) == "eo3"

    how_many_are_eo3 = len(
        [
            p
            for p in odc_test_db.index.products.get_all()
            if p.metadata_type.name == "eo3"
        ]
    )
    assert (
        html.css_first(".header-follow").text(strip=True)
        == f"metadata type of {how_many_are_eo3} products"
    )

    # Does the page list products using the type?
    products_using_it = [t.text() for t in html.css(".type-usage-item")]
    assert "ga_ls_wo_fq_nov_mar_3" in products_using_it


def test_storage_page(client: FlaskClient, odc_test_db) -> None:
    html = get_html(client, "/audit/storage")

    product_names = [node.text() for node in html.css(".product-name")]
    assert "ga_ls9c_ard_3" in product_names

    product_count = len(list(odc_test_db.index.products.get_all()))
    assert f"{product_count} products" in html.text()
    assert len(html.css(".data-table tbody tr")) == product_count


def test_product_audit_redirects(client: FlaskClient) -> None:
    assert_redirects_to(
        client,
        "/product-audit/day-times.txt",
        "/audit/day-query-times.txt",
    )


@pytest.mark.skip(reason="TODO: fix out-of-date range return value")
def test_out_of_date_range(client: FlaskClient) -> None:
    """
    We have generated summaries for this product, but the date is out of the product's date range.
    """
    html = get_html(client, "/wofs_albers/2010")

    # The common error here is to say "No data: not yet summarised" rather than "0 datasets"
    check_dataset_count(html, 0)
    assert "Historic Flood Mapping Water Observations from Space" in html.text()


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_loading_high_low_tide_comp(client: FlaskClient) -> None:
    html = get_html(client, "/high_tide_comp_20p/2008")

    assert "High Tide 20 percentage composites for entire coastline" in html.text()

    check_dataset_count(html, 306)
    # Footprint is not exact due to shapely.simplify()
    check_area("2,984,...km2", html)

    assert (
        html.css_first(".last-processed time", strict=True).attributes["datetime"]
        == "2017-06-08T20:58:07.014314+00:00"
    )


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_api_returns_high_tide_comp_datasets(client: FlaskClient) -> None:
    """
    These are slightly fun to handle as they are a small number with a huge time range.
    """
    geojson = get_geojson(client, "/api/datasets/high_tide_comp_20p")
    assert len(geojson["features"]) == 306, (
        "Not all high tide datasets returned as geojson"
    )

    # Search and time summary is only based on center time.
    # These searches are within the dataset time range, but not the center_time.
    # Dataset range: '2000-01-01T00:00:00' to '2016-10-31T00:00:00'
    # year
    geojson = get_geojson(client, "/api/datasets/high_tide_comp_20p/2008")
    assert len(geojson["features"]) == 306, (
        "Expected high tide datasets within whole dataset range"
    )
    # month
    geojson = get_geojson(client, "/api/datasets/high_tide_comp_20p/2008/6")
    assert len(geojson["features"]) == 306, (
        "Expected high tide datasets within whole dataset range"
    )
    # day
    geojson = get_geojson(client, "/api/datasets/high_tide_comp_20p/2008/6/1")
    assert len(geojson["features"]) == 306, (
        "Expected high tide datasets within whole dataset range"
    )

    # Out of the test dataset time range. No results.

    # Completely outside of range
    geojson = get_geojson(client, "/api/datasets/high_tide_comp_20p/2018")
    assert len(geojson["features"]) == 0, (
        "Expected no high tide datasets in in this year"
    )
    # One day before/after (is time zone handling correct?)
    geojson = get_geojson(client, "/api/datasets/high_tide_comp_20p/2008/6/2")
    assert len(geojson["features"]) == 0, "Expected no result one-day-after center time"
    geojson = get_geojson(client, "/api/datasets/high_tide_comp_20p/2008/5/31")
    assert len(geojson["features"]) == 0, "Expected no result one-day-after center time"


def test_api_returns_scenes_as_geojson(client: FlaskClient) -> None:
    """
    L1 scenes have no footprint, falls back to bounds. Have weird CRSes too.
    """
    geojson = get_geojson(client, "/api/datasets/usgs_ls7e_level1_1")
    assert len(geojson["features"]) == 5, "Unexpected l1 polygon count"


def test_api_returns_tiles_as_geojson(client: FlaskClient) -> None:
    """
    Covers most of the 'normal' products: they have a footprint, bounds and a simple crs epsg code.
    """
    geojson = get_geojson(client, "/api/datasets/ga_ls8c_ard_3")
    assert len(geojson["features"]) == 21, "Unepected polygon count"


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_api_returns_high_tide_comp_regions(client: FlaskClient) -> None:
    """
    High tide doesn't have anything we can use as regions.

    It should be empty (no regions supported) rather than throw an exception.
    """

    rv = client.get("/api/regions/high_tide_comp_20p")
    assert rv.status_code == 404, (
        "High tide comp does not support regions: it should return not-exist code."
    )


def test_api_returns_scene_regions(client: FlaskClient) -> None:
    """
    L1 scenes have no footprint, falls back to bounds. Have weird CRSes too.
    """
    geojson = get_geojson(client, "/api/regions/usgs_ls7e_level1_1")
    assert len(geojson["features"]) == 5, "Unexpected l1 region count"


def test_region_page(client: FlaskClient) -> None:
    """
    Load a list of scenes for a given region.
    """
    html = get_html(client, "/region/ga_ls8c_ard_3/104074")
    search_results = html.css(".search-result a")
    assert len(search_results) == 1
    result = search_results[0]
    assert result.text() == "ga_ls8c_ard_3-2-1_104074_2022-07-19_interim"

    # If "I'm feeling lucky", and only one result, redirect straight to it.
    assert_redirects_to(
        client,
        "/product/ga_ls8c_ard_3/regions/104074?feelinglucky=",
        "/dataset/c867d666-bf01-48f2-8259-48f756f86858",
    )


def test_legacy_region_redirect(client: FlaskClient) -> None:
    # Legacy redirect works, and maintains "feeling lucky"
    assert_redirects_to(
        client,
        "/region/ga_ls8c_ard_3/104074?feelinglucky",
        "/product/ga_ls8c_ard_3/regions/104074?feelinglucky=",
    )


def assert_redirects_to(client: FlaskClient, url: str, redirects_to_url: str) -> None:
    __tracebackhide__ = True
    response = client.get(url, follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith(redirects_to_url), (
        "Expected redirect to end with:\n"
        f"    {redirects_to_url!r}\n"
        "but was redirected to:\n"
        f"    {response.location!r}"
    )


def test_search_page(client: FlaskClient) -> None:
    html = get_html(client, "/datasets/ga_ls8c_ard_3")
    search_results = html.css(".search-result a")
    assert len(search_results) == 21

    html = get_html(client, "/datasets/ga_ls8c_ard_3/2017/12")
    search_results = html.css(".search-result a")
    assert len(search_results) == 7

    html = get_html(client, "/datasets/ga_ls8c_ard_3/2018")
    search_results = html.css(".search-result a")
    assert len(search_results) == 0


def test_search_time_completion(client: FlaskClient) -> None:
    # They only specified a begin time, so the end time should be filled in with the product extent.
    html = get_html(client, "/datasets/ga_ls8c_ard_3?time-begin=1999-05-28")
    assert (
        html.css_first("#search-time-before", strict=True).attributes["value"]
        == "1999-05-28"
    )
    # One day after the product extent end (range is exclusive)
    assert (
        html.css_first("#search-time-after", strict=True).attributes["value"]
        == "2022-10-28"
    )
    search_results = html.css(".search-result a")
    assert len(search_results) == 21

    # if not provided as a span, it should become a span of one day
    html = get_html(client, "/datasets/ga_ls8c_ard_3?time=2022-07-18")
    assert (
        html.css_first("#search-time-before", strict=True).attributes["value"]
        == "2022-07-18"
    )
    assert (
        html.css_first("#search-time-after", strict=True).attributes["value"]
        == "2022-07-19"
    )
    search_results = html.css(".search-result a")
    assert len(search_results) == 2


def test_api_returns_tiles_regions(client: FlaskClient) -> None:
    """
    Covers most of the 'normal' products: they have a footprint, bounds and a simple crs epsg code.
    """
    geojson = get_geojson(client, "/api/regions/ga_ls9c_ard_3")
    assert len(geojson["features"]) == 11, "Unexpected product region count"


def test_api_returns_limited_tile_regions(client: FlaskClient) -> None:
    """
    Covers most of the 'normal' products: they have a footprint, bounds and a simple crs epsg code.
    """
    geojson = get_geojson(client, "/api/regions/ga_ls8c_ard_3/2022/02")
    assert len(geojson["features"]) == 3, "Unexpected region month count"
    geojson = get_geojson(client, "/api/regions/ga_ls8c_ard_3/2022/02/26")
    assert len(geojson["features"]) == 1, "Unexpected region day count"
    geojson = get_geojson(client, "/api/regions/ga_ls8c_ard_3/2022/04/6")
    assert len(geojson["features"]) == 0, "Unexpected region count"


def test_api_returns_timelines(client: FlaskClient) -> None:
    """
    Covers most of the 'normal' products: they have a footprint, bounds and a simple crs epsg code.
    """
    doc = get_json(client, "/api/dataset-timeline/ga_ls9c_ard_3")
    assert doc == {
        "2021-12-01T00:00:00": 0,
        "2021-12-02T00:00:00": 0,
        "2021-12-03T00:00:00": 0,
        "2021-12-04T00:00:00": 1,
        "2021-12-05T00:00:00": 0,
        "2021-12-06T00:00:00": 0,
        "2021-12-07T00:00:00": 0,
        "2021-12-08T00:00:00": 0,
        "2021-12-09T00:00:00": 0,
        "2021-12-10T00:00:00": 1,
        "2021-12-11T00:00:00": 0,
        "2021-12-12T00:00:00": 0,
        "2021-12-13T00:00:00": 0,
        "2021-12-14T00:00:00": 0,
        "2021-12-15T00:00:00": 0,
        "2021-12-16T00:00:00": 0,
        "2021-12-17T00:00:00": 0,
        "2021-12-18T00:00:00": 0,
        "2021-12-19T00:00:00": 0,
        "2021-12-20T00:00:00": 0,
        "2021-12-21T00:00:00": 0,
        "2021-12-22T00:00:00": 1,
        "2021-12-23T00:00:00": 0,
        "2021-12-24T00:00:00": 0,
        "2021-12-25T00:00:00": 0,
        "2021-12-26T00:00:00": 0,
        "2021-12-27T00:00:00": 0,
        "2021-12-28T00:00:00": 2,
        "2021-12-29T00:00:00": 0,
        "2021-12-30T00:00:00": 0,
        "2021-12-31T00:00:00": 0,
        "2022-01-01T00:00:00": 1,
        "2022-01-02T00:00:00": 0,
        "2022-01-03T00:00:00": 0,
        "2022-01-04T00:00:00": 0,
        "2022-01-05T00:00:00": 0,
        "2022-01-06T00:00:00": 0,
        "2022-01-07T00:00:00": 0,
        "2022-01-08T00:00:00": 0,
        "2022-01-09T00:00:00": 0,
        "2022-01-10T00:00:00": 0,
        "2022-01-11T00:00:00": 0,
        "2022-01-12T00:00:00": 0,
        "2022-01-13T00:00:00": 0,
        "2022-01-14T00:00:00": 0,
        "2022-01-15T00:00:00": 0,
        "2022-01-16T00:00:00": 0,
        "2022-01-17T00:00:00": 1,
        "2022-01-18T00:00:00": 0,
        "2022-01-19T00:00:00": 1,
        "2022-01-20T00:00:00": 2,
        "2022-01-21T00:00:00": 0,
        "2022-01-22T00:00:00": 0,
        "2022-01-23T00:00:00": 0,
        "2022-01-24T00:00:00": 0,
        "2022-01-25T00:00:00": 0,
        "2022-01-26T00:00:00": 0,
        "2022-01-27T00:00:00": 0,
        "2022-01-28T00:00:00": 0,
        "2022-01-29T00:00:00": 0,
        "2022-01-30T00:00:00": 1,
        "2022-01-31T00:00:00": 0,
    }

    doc = get_json(client, "/api/dataset-timeline/ga_ls9c_ard_3/2021")
    assert doc == {
        "2021-12-01T00:00:00": 0,
        "2021-12-02T00:00:00": 0,
        "2021-12-03T00:00:00": 0,
        "2021-12-04T00:00:00": 1,
        "2021-12-05T00:00:00": 0,
        "2021-12-06T00:00:00": 0,
        "2021-12-07T00:00:00": 0,
        "2021-12-08T00:00:00": 0,
        "2021-12-09T00:00:00": 0,
        "2021-12-10T00:00:00": 1,
        "2021-12-11T00:00:00": 0,
        "2021-12-12T00:00:00": 0,
        "2021-12-13T00:00:00": 0,
        "2021-12-14T00:00:00": 0,
        "2021-12-15T00:00:00": 0,
        "2021-12-16T00:00:00": 0,
        "2021-12-17T00:00:00": 0,
        "2021-12-18T00:00:00": 0,
        "2021-12-19T00:00:00": 0,
        "2021-12-20T00:00:00": 0,
        "2021-12-21T00:00:00": 0,
        "2021-12-22T00:00:00": 1,
        "2021-12-23T00:00:00": 0,
        "2021-12-24T00:00:00": 0,
        "2021-12-25T00:00:00": 0,
        "2021-12-26T00:00:00": 0,
        "2021-12-27T00:00:00": 0,
        "2021-12-28T00:00:00": 2,
        "2021-12-29T00:00:00": 0,
        "2021-12-30T00:00:00": 0,
        "2021-12-31T00:00:00": 0,
    }

    doc = get_json(client, "/api/dataset-timeline/ga_ls9c_ard_3/2022/01")
    assert doc == {
        "2022-01-01T00:00:00": 1,
        "2022-01-02T00:00:00": 0,
        "2022-01-03T00:00:00": 0,
        "2022-01-04T00:00:00": 0,
        "2022-01-05T00:00:00": 0,
        "2022-01-06T00:00:00": 0,
        "2022-01-07T00:00:00": 0,
        "2022-01-08T00:00:00": 0,
        "2022-01-09T00:00:00": 0,
        "2022-01-10T00:00:00": 0,
        "2022-01-11T00:00:00": 0,
        "2022-01-12T00:00:00": 0,
        "2022-01-13T00:00:00": 0,
        "2022-01-14T00:00:00": 0,
        "2022-01-15T00:00:00": 0,
        "2022-01-16T00:00:00": 0,
        "2022-01-17T00:00:00": 1,
        "2022-01-18T00:00:00": 0,
        "2022-01-19T00:00:00": 1,
        "2022-01-20T00:00:00": 2,
        "2022-01-21T00:00:00": 0,
        "2022-01-22T00:00:00": 0,
        "2022-01-23T00:00:00": 0,
        "2022-01-24T00:00:00": 0,
        "2022-01-25T00:00:00": 0,
        "2022-01-26T00:00:00": 0,
        "2022-01-27T00:00:00": 0,
        "2022-01-28T00:00:00": 0,
        "2022-01-29T00:00:00": 0,
        "2022-01-30T00:00:00": 1,
        "2022-01-31T00:00:00": 0,
    }

    doc = get_json(client, "/api/dataset-timeline/ga_ls9c_ard_3/2022/01/17")
    assert doc == {"2022-01-17T00:00:00": 1}


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_undisplayable_product(client: FlaskClient) -> None:
    """
    Telemetry products have no footprint available at all.
    """
    html = get_html(client, "/ls7_satellite_telemetry_data")
    check_dataset_count(html, 4)
    assert "36.6GiB" in html.css_first(".coverage-filesize", strict=True).text(
        strip=True
    )
    assert "(None displayable)" in html.text()
    assert "No CRSes defined" in html.text()


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_no_data_pages(client: FlaskClient) -> None:
    """
    Fetch products that exist but have no summaries generated.

    (these should load with "empty" messages: not throw exceptions)
    """
    html = get_html(client, "/ls8_nbar_albers/2017")
    html_text = get_normalized_text(html)
    assert "No data: not yet summarised" in html_text
    assert "Unknown number of datasets" in html_text

    html = get_html(client, "/ls8_nbar_albers/2017/5")
    html_text = get_normalized_text(html)
    assert "No data: not yet summarised" in html_text
    assert "Unknown number of datasets" in html_text

    # Days are generated on demand: it should query and see that there are no datasets.
    html = get_html(client, "/ls8_nbar_albers/2017/5/2")
    check_dataset_count(html, 0)


def test_general_dataset_redirect(client: FlaskClient) -> None:
    """
    When someone queries a dataset UUID, they should be redirected
    to the real URL for the collection.
    """
    rv = client.get(
        "/dataset/c867d666-bf01-48f2-8259-48f756f86858", follow_redirects=False
    )
    # It should be a redirect
    assert rv.status_code == 302
    assert (
        rv.location
        == "/products/ga_ls8c_ard_3/datasets/c867d666-bf01-48f2-8259-48f756f86858"
    )


def test_missing_dataset(client: FlaskClient) -> None:
    rv = client.get(
        "/products/ga_ls8c_ard_3/datasets/f22a33f4-42f2-4aa5-9b20-cee4ca4a875c",
        follow_redirects=False,
    )
    assert rv.status_code == 404

    # But a real dataset definitely works:
    rv = client.get(
        "/products/ga_ls8c_ard_3/datasets/c867d666-bf01-48f2-8259-48f756f86858",
        follow_redirects=False,
    )
    assert rv.status_code == 200


def test_invalid_product_returns_not_found(client: FlaskClient) -> None:
    """
    An invalid product should be "not found". No server errors.
    """
    rv = client.get("/products/fake_test_product/2017", follow_redirects=False)
    assert rv.status_code == 404


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_show_summary_cli(clirunner, client: FlaskClient) -> None:
    """
    You should be able to view a product with cubedash-view command-line program.

    This test expects the database timezone to be UTC
    """
    # ls7_nbar_scene, 2017, May
    res = clirunner(show.cli, ["ls7_nbar_scene", "2017", "5"])

    # Expect it to show the dates in local timezone.
    expected_from = datetime(2017, 4, 20, 0, 3, 26, tzinfo=timezone.utc)
    expected_to = datetime(2017, 5, 3, 1, 6, 41, 500000, tzinfo=timezone.utc)

    expected_header = "\n".join(
        (
            "ls7_nbar_scene",
            "",
            "3  datasets",
            f"from {expected_from.isoformat()} ",
            f"  to {expected_to.isoformat()} ",
        )
    )
    result_header = "\n".join(res.output.splitlines()[:5])
    assert expected_header == result_header
    expected_metadata = "\n".join(  # noqa: FLY002
        (
            "Metadata",
            "\tgsi: ASA",
            "\torbit: None",
            "\tformat: GeoTIFF",
            "\tplatform: LANDSAT_7",
            "\tinstrument: ETM",
            "\tproduct_type: nbar",
        )
    )
    assert expected_metadata in res.output
    expected_period = "\n".join(  # noqa: FLY002
        ("Period: 2017 5 all-days", "\tStorage size: 727.4MiB", "\t3 datasets", "")
    )
    assert expected_period in res.output


def test_show_summary_cli_out_of_bounds(clirunner, client: FlaskClient) -> None:
    """
    Can you view a date that doesn't exist?
    """
    # A period that's out of bounds.
    res = clirunner(show.cli, ["ga_ls8c_ard_3", "2030", "5"], expect_success=False)
    assert "No summary for chosen period." in res.output


def test_show_summary_cli_missing_product(clirunner, client: FlaskClient) -> None:
    """
    A missing product should return a nice error message from cubedash-view.

    (and error return code)
    """
    res = clirunner(show.cli, ["does_not_exist"], expect_success=False)
    output = res.output
    assert output.strip().startswith("Unknown product 'does_not_exist'")
    assert res.exit_code != 0


def test_show_summary_cli_unsummarised_product(
    clirunner, empty_client: FlaskClient
) -> None:
    """
    An unsummarised product should return a nice error message from cubedash-view.

    (and error return code)
    """
    res = clirunner(show.cli, ["ga_ls8c_ard_3"], expect_success=False)
    out = res.output.strip()
    assert out.startswith("No info: product 'ga_ls8c_ard_3' has not been summarised")
    assert res.exit_code != 0


def test_extent_debugging_method(odc_test_db, client: FlaskClient) -> None:
    index = odc_test_db.index
    product = index.products.get_by_name("ga_ls8c_ard_3")
    e_index = explorer_index(index)
    [cols] = _extents.get_sample_dataset([product], e_index)
    assert cols["id"] is not None
    assert cols["product_ref"] is not None
    assert cols["center_time"] is not None
    assert cols["footprint"] is not None

    # Can it be serialised without type errors? (for printing)
    output_json = _extents._as_json(cols)
    assert str(cols["id"]) in output_json

    [cols] = _extents.get_mapped_crses([product], e_index)
    assert cols["product"] == "ga_ls8c_ard_3"
    assert cols["crs"] in (32650, 32651, 32652, 32653, 32654, 32655, 32656)


def test_plain_product_list(client: FlaskClient) -> None:
    text, _ = get_text_response(client, "/products.txt")
    assert "ga_ls8c_ard_3\n" in text


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_raw_documents(client: FlaskClient) -> None:
    """
    Check that raw-documents load without error,
    and have embedded hints on where they came from (source-url)
    """

    def check_doc_start_has_hint(hint: str, url: str):
        __tracebackhide__ = True
        doc, _ = get_text_response(client, url)
        doc_opening = doc[:128]
        expect_pattern = f"# {hint}\n# url: http://localhost{url}\n"
        assert expect_pattern in doc_opening, (
            "No hint or source-url in yaml response.\n"
            f"Expected {expect_pattern!r}\n"
            f"Got      {doc_opening!r}"
        )

        try:
            YAML(typ="safe", pure=True).load(StringIO(doc))
        except YAMLError as e:
            raise AssertionError(f"Expected valid YAML document for url {url!r}") from e

    # Product
    check_doc_start_has_hint("Product", "/products/ls8_nbar_albers.odc-product.yaml")

    # Metadata type
    check_doc_start_has_hint("Metadata Type", "/metadata-types/eo3.odc-type.yaml")

    # A legacy EO1 dataset
    check_doc_start_has_hint(
        "EO1 Dataset", "/dataset/57848615-2421-4d25-bfef-73f57de0574d.odc-metadata.yaml"
    )


def test_get_robots(client: FlaskClient) -> None:
    """
    Check that robots.txt is correctly served from root
    """
    text, rv = get_text_response(client, "/robots.txt")
    assert "User-agent:" in text

    num_lines = len(text.split("\n"))
    assert num_lines > 1, "robots.txt should have multiple lines"

    assert rv.headers["Content-Type"] == "text/plain", (
        "robots.txt content-type should be text/plain"
    )


def test_all_give_404s(client: FlaskClient) -> None:
    """
    We should get 404 messages, not exceptions, for missing things.
    """

    def expect_404(url: str, message_contains: str | None = None):
        __tracebackhide__ = True
        response = get_text_response(client, url, expect_status_code=404)
        if message_contains and message_contains not in response:
            raise AssertionError(
                f"Expected {message_contains!r} in response {response!r}"
            )

    name = "does_not_exist"
    time = datetime.now(timezone.utc)
    region_code = "not_a_region"
    dataset_id = "37296b9a-e6ec-4bfd-ab80-cc32902429d1"

    expect_404(f"/metadata-types/{name}")
    expect_404(f"/metadata-types/{name}.odc-type.yaml")

    expect_404(f"/datasets/{name}")
    expect_404(f"/products/{name}")
    expect_404(f"/products/{name}.odc-product.yaml")

    expect_404(f"/products/{name}/extents/{time:%Y}")
    expect_404(f"/products/{name}/extents/{time:%Y/%m}")
    expect_404(f"/products/{name}/extents/{time:%Y/%m/%d}")

    expect_404(f"/products/{name}/datasets/{time:%Y}")
    expect_404(f"/products/{name}/datasets/{time:%Y/%m}")
    expect_404(f"/products/{name}/datasets/{time:%Y/%m/%d}")

    expect_404(f"/region/{name}/{region_code}")
    expect_404(f"/region/{name}/{region_code}/{time:%Y/%m/%d}")

    expect_404(f"/dataset/{dataset_id}")
    expect_404(f"/dataset/{dataset_id}.odc-metadata.yaml")

    expect_404("/api/dataset-timeline/non_existent/2025")


def test_invalid_query_gives_400(client: FlaskClient) -> None:
    """
    We should get 400 errors, not errors, for an invalid field values in a query
    """

    def expect_400(url: str) -> None:
        __tracebackhide__ = True
        get_text_response(client, url, expect_status_code=400)

    # errors that are caught when parsing query args
    expect_400("/products/ga_ls8c_ard_3/datasets?time=asdf")
    expect_400("/products/ga_ls8c_ard_3/datasets?lat=asdf")
    # errors that aren't caught until the db query
    expect_400("/products/ga_ls8c_ard_3/datasets?indexed_time=asdf")
    expect_400("/products/ga_ls8c_ard_3/datasets?id=asdf")
