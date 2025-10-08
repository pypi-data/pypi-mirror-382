# ignore redefining from outer scope, false positive from fixtures
# pylint: disable=W0621
import pytest
from dkany.client import DKANClient


# ----------------------------------
# Fixtures
# ----------------------------------
@pytest.fixture(scope="function")
def dkan_client():
    client = DKANClient(base_url="https://edit.data.medicaid.gov")
    return client


@pytest.fixture(scope="function")
def read_dataset_id():
    return "9e407144-9ed9-5cee-937a-17d65b07a9a7"


# ----------------------------------
# Tests
# ----------------------------------
def test_search(dkan_client):
    title_success = "Product Data for Newly Reported Drugs in the Medicaid Drug Rebate Program 2023-02-06-to-2023-02-12"
    search_success = dkan_client.search(title=title_success)
    assert len(search_success) == 1
    print("Search success:", len(search_success))

    title_fail = "Product Data for asdfasdf"
    search_fail = dkan_client.search(title=title_fail)
    assert len(search_fail) == 0
    print("Search fail:", len(search_fail))


def test_check_dataset_exists(dkan_client, read_dataset_id):
    exists = dkan_client.check_dataset_exists(read_dataset_id)
    print(f"dataset {exists} exists")
    assert exists


def test_get_dataset_metadata(dkan_client, read_dataset_id):
    metadata = dkan_client.get_dataset_metadata(read_dataset_id)
    assert metadata["identifier"] == read_dataset_id


def test_get_data_by_dataset_identifier(dkan_client, read_dataset_id):
    results = dkan_client.get_data_by_dataset_identifier(read_dataset_id)
    assert len(results) > 0
