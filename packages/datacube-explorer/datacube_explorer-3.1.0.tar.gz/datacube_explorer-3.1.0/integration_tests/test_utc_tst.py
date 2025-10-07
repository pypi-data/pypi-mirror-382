"""
Tests that load pages and check the contained text.
"""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from datacube.model import Range
from flask.testing import FlaskClient

from cubedash._utils import datetime_from_metadata, default_utc
from cubedash.summary import SummaryStore
from integration_tests.asserts import check_dataset_count, get_html

TEST_DATA_DIR = Path(__file__).parent / "data"

METADATA_TYPES = [
    "metadata/eo_metadata.yaml",
    "metadata/landsat_l1_scene.yaml",
    "metadata/eo3_landsat_l1.odc-type.yaml",
    "metadata/eo3_landsat_ard.odc-type.yaml",
]
PRODUCTS = [
    "products/ls5_fc_albers.odc-product.yaml",
    "products/ls5_scenes.odc-product.yaml",
    "products/ls7_scenes.odc-product.yaml",
    "products/ls8_scenes.odc-product.yaml",
    "products/usgs_ls7e_level1_1.odc-product.yaml",
    "products/ga_ls9c_ard_3.odc-product.yaml",
    "products/dsm1sv10.odc-product.yaml",
]
DATASETS = [
    "datasets/ls5_fc_albers-sample.yaml",
    "datasets/ga_ls9c_ard_3-sample.yaml",
    "datasets/usgs_ls7e_level1_1-sample.yaml",
]


# Use the 'auto_odc_db' fixture to populate the database with sample data.
pytestmark = pytest.mark.usefixtures("auto_odc_db")


@pytest.mark.parametrize("env_name", ("default",), indirect=True)
def test_summary_product(client: FlaskClient) -> None:
    # These datasets have gigantic footprints that can trip up postgis.
    html = get_html(client, "/ls5_fc_albers")

    check_dataset_count(html, 5)


def test_yearly_dataset_count(client: FlaskClient) -> None:
    html = get_html(client, "/ga_ls9c_ard_3/2021/12")
    check_dataset_count(html, 5)

    html = get_html(client, "/ga_ls9c_ard_3/2021/12/28")
    check_dataset_count(html, 2)

    html = get_html(client, "/ga_ls9c_ard_3/2022")
    check_dataset_count(html, 6)


def test_dataset_search_page_localised_time(client: FlaskClient) -> None:
    html = get_html(client, "/products/ga_ls9c_ard_3/datasets/2022")

    assert "2022-01-01 08:11:00" in [
        a.css_first("td").text(strip=True).strip() for a in html.css(".search-result")
    ], (
        "datestring does not match expected center_time recorded in dataset_spatial table"
    )

    assert "Time UTC: 2021-12-31 22:41:00" in [
        a.css_first("td").attributes["title"] for a in html.css(".search-result")
    ], (
        "datestring does not match expected center_time recorded in dataset_spatial table"
    )

    html = get_html(client, "/products/ga_ls9c_ard_3/datasets/2021")

    assert "2021-12-04 11:05:22" in [
        a.css_first("td").text(strip=True).strip() for a in html.css(".search-result")
    ], (
        "datestring does not match expected center_time recorded in dataset_spatial table"
    )


def test_clirunner_generate_grouping_timezone(
    odc_test_db, run_generate, empty_client
) -> None:
    res = run_generate("ga_ls9c_ard_3", grouping_time_zone="America/Chicago")
    assert "2021" in res.output

    store = SummaryStore.create(odc_test_db.index, grouping_time_zone="America/Chicago")

    # simulate search pages
    datasets = sorted(
        store.index.datasets.search(
            **{
                "product": "ga_ls9c_ard_3",
                "time": Range(
                    begin=datetime(
                        2021, 12, 27, 0, 0, tzinfo=ZoneInfo("America/Chicago")
                    ),
                    end=datetime(
                        2021, 12, 28, 0, 0, tzinfo=ZoneInfo("America/Chicago")
                    ),
                ),
            },
            limit=5,
        ),
        key=lambda d: d.center_time,
    )
    assert len(datasets) == 2

    # search pages
    datasets = sorted(
        store.index.datasets.search(
            **{
                "product": "ga_ls9c_ard_3",
                "time": Range(
                    begin=datetime(
                        2021, 12, 31, 0, 0, tzinfo=ZoneInfo("America/Chicago")
                    ),
                    end=datetime(2022, 1, 1, 0, 0, tzinfo=ZoneInfo("America/Chicago")),
                ),
            },
            limit=5,
        ),
        key=lambda d: d.center_time,
    )
    assert len(datasets) == 1

    # simulate product pages
    result = store.get("ga_ls9c_ard_3", year=2021, month=12)
    assert result is not None
    assert result.dataset_count == 6

    result = store.get("ga_ls9c_ard_3", year=2021, month=12, day=27)
    assert result is not None
    assert result.dataset_count == 2

    result = store.get("ga_ls9c_ard_3", year=2021, month=12, day=28)
    assert result is not None
    assert result.dataset_count == 0

    result = store.get("ga_ls9c_ard_3", year=2021, month=12, day=31)
    assert result is not None
    assert result.dataset_count == 1


# Unit tests
def test_dataset_day_link(summary_store) -> None:
    ds = summary_store.index.datasets.get("6293ac37-7f1d-430e-8d7e-ffdc1bfd556c")
    t = datetime_from_metadata(ds)
    t = default_utc(t).astimezone(ZoneInfo("Australia/Darwin"))
    assert t.year == 2022
    assert t.month == 1
    assert t.day == 1

    t = default_utc(t).astimezone(ZoneInfo("America/Chicago"))
    assert t.year == 2021
    assert t.month == 12
    assert t.day == 31


def test_dataset_search_page_ls7e_time(client: FlaskClient) -> None:
    html = get_html(client, "/products/usgs_ls7e_level1_1/datasets/2020/6/1")
    search_results = html.css(".search-result a")
    assert len(search_results) == 2

    html = get_html(client, "/products/usgs_ls7e_level1_1/datasets/2020/6/2")
    search_results = html.css(".search-result a")
    assert len(search_results) == 3
