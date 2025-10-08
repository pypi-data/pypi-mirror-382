import logging
from copy import deepcopy as copy
from datetime import datetime as dt
from typing import List, Optional

import requests
from requests.cookies import RequestsCookieJar
from requests_toolbelt import sessions # type: ignore

from dkany.client.errors import BadResponse

logger = logging.getLogger(__name__)


def url_join(url_part_list):
    return "/".join(url_part_list)


class DKANClient:
    """
    docstring
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        cookie_dict: Optional[dict] = None,
        user_name: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.base_url = base_url

        logger.info("Creating DKAN client for %s", self.base_url)

        session = sessions.BaseUrlSession(self.base_url)
        if user_name is not None:
            session.auth = (user_name, password)
            self.user_name = user_name
        else:
            self.user_name = "anonymous"

        if cookie_dict is not None:
            cookies = RequestsCookieJar()
            cookies = requests.utils.add_dict_to_cookiejar(cookies, cookie_dict)
            session.cookies = cookies

        self.session = session

        self.search_url = "api/1/search?_format=json"
        self.post_new_dataset_url = "api/1/metastore/schemas/dataset/items?_format=json"
        self.existing_dataset_url = (
            "api/1/metastore/schemas/dataset/items/{dataset_identifier}?_format=json"
        )
        self.revise_dataset_url = "api/1/metastore/schemas/dataset/items/{dataset_identifier}/revisions?_format=json"
        self.query_datastore_url = (
            "api/1/datastore/query/{dataset_identifier}/{datastore_idx}?_format=json"
        )

        self.hide_dataset_dict = {"state": "hidden", "message": "hiding dataset"}
        self.publish_dataset_dict = {
            "state": "published",
            "message": "publishing dataset",
        }

        self.dkan_time_format = "%Y-%m-%dT%H:%M:%S"

    def __repr__(self) -> str:
        return f"DKAN client for {self.base_url} with user {self.user_name}"

    def __str__(self) -> str:
        return f"DKAN client for {self.base_url} with user {self.user_name}"

    def _process_response(
        self, response, acceptable_responses: Optional[List[int]] = None
    ):
        acceptable_responses = acceptable_responses or [200, 201]
        if response.status_code not in acceptable_responses:
            raise BadResponse(response, acceptable_responses)
        out = response.json()
        return out

    def _paged_search(self, params, page):
        params["page"] = page

        response = self.session.get(self.search_url, params=params)

        return self._process_response(response)

    def _search_all_pages(self, params):
        page = 1
        out = self._paged_search(params, page)
        total = int(out["total"])
        all_results = copy(out["results"])

        if total > 0:
            while len(all_results.keys()) < total:
                page += 1
                out = self._paged_search(params, page)
                all_results.update(out["results"])

        if all_results != []:
            assert len(all_results.keys()) == total

        return all_results

    def search(
        self, title: Optional[str] = None, tags=None, categories=None, page="ALL"
    ):
        params = {}
        if title is not None:
            params["title"] = title
        if tags is not None:
            params["keyword"] = tags
        if categories is not None:
            params["theme"] = categories

        # Paging Logic
        if page != "ALL":
            out = self._paged_search(params, page)["results"]
        else:
            out = self._search_all_pages(params)

        # search returns a dict if it finds something
        # and and empty list if it does not find anything
        # this is for type consistentcy
        if out == []:
            out = {}

        return out

    def filter_search_results(self, search_results, filter_params):
        if filter_params is None:
            return search_results
        if len(filter_params.keys()) == 0:
            return search_results

        inital_search_results = list(search_results.items())

        for search_key, search_result_value in inital_search_results:
            for filter_key, filter_value in filter_params.items():
                if search_result_value[filter_key] != filter_value:
                    search_results.pop(search_key)
                    break

        return search_results

    def create_dataset(self, body):
        response = self.session.post(self.post_new_dataset_url, json=body)
        return self._process_response(response)

    def delete_dataset(self, dataset_identifier):
        response = self.session.delete(
            self.existing_dataset_url.format(dataset_identifier=dataset_identifier)
        )
        return self._process_response(response)

    def update_dataset(self, dataset_identifier, body):
        response = self.session.put(
            self.existing_dataset_url.format(dataset_identifier=dataset_identifier),
            json=body,
        )
        return self._process_response(response)

    def mark_dataset_hidden(self, dataset_identifier, message=""):
        """
        Sets dataset accesslevel to "hidden"
        Hides dataset from searches made on data.medicare.gov user interface
        """
        if message:
            self.hide_dataset_dict["message"] = message
        response = self.session.post(
            self.revise_dataset_url.format(dataset_identifier=dataset_identifier),
            json=self.hide_dataset_dict,
        )
        return self._process_response(response)

    def mark_dataset_public(self, dataset_identifier, message=""):
        """
        Sets dataset accesslevel to "published"
        Makes a dataset searchable through data.medicare.gov user interface
        """
        if message:
            self.publish_dataset_dict["message"] = message
        response = self.session.post(
            self.revise_dataset_url.format(dataset_identifier=dataset_identifier),
            json=self.publish_dataset_dict,
        )
        return self._process_response(response)

    def get_dataset_metadata(self, dataset_identifier):
        response = self.session.get(
            self.existing_dataset_url.format(dataset_identifier=dataset_identifier),
            params={"_format": "json"},
        )
        return self._process_response(response)

    def check_dataset_exists(self, dataset_identifier):
        try:
            _ = self.get_dataset_metadata(dataset_identifier)
            return True
        except BadResponse:
            return False

    def trigger_dataset_reimport(self, dataset_identifier):
        body = self.get_dataset_metadata(dataset_identifier)
        body["modified"] = dt.now().strftime(self.dkan_time_format)
        return self.update_dataset(dataset_identifier, body)

    def get_full_query_url(self, dataset_identifier, datastore_idx=0):
        return url_join(
            [
                self.base_url,
                self.query_datastore_url.format(
                    dataset_identifier=dataset_identifier, datastore_idx=datastore_idx
                ),
            ]
        )

    def get_data_by_dataset_identifier(self, dataset_identifier, datastore_idx=0):
        response = self.session.get(
            self.query_datastore_url.format(
                dataset_identifier=dataset_identifier, datastore_idx=datastore_idx
            )
        )
        return self._process_response(response)
