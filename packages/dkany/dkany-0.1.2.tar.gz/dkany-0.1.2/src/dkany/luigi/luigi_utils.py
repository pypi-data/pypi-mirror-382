import logging
import json
from json import JSONEncoder

import luigi
from luigi.freezing import FrozenOrderedDict

from dkany.client.client import DKANClient

logger = logging.getLogger(__name__)


class DkanTarget(luigi.Target):
    def __init__(
        self,
        dataset_identifier=None,
        search_params=None,
        search_results_filter=None,
        datastore_idx=0,
        dkan_client_params=None,
        dkan_client=None,
    ):
        if (search_params is None) and (dataset_identifier is None):
            raise ValueError("Either dataset_identifier or search_params must be specified")

        if dkan_client is None:
            params = dkan_client_params or {}
            self.client = DKANClient(**params)
        else:
            self.client = dkan_client

        self.search_params = search_params
        self.search_results_filter = search_results_filter
        self.dataset_identifier = dataset_identifier
        self.datastore_idx = datastore_idx

    def verify_current_check(self, _dataset_metadata):
        # This check accomplishes nothing,
        # meant to be specialized in a subclass
        return True

    def exists(self):
        logger.debug("Checking datasets existance")
        dataset_identifier = None
        if self.dataset_identifier is not None:
            if self.client.check_dataset_exists(self.dataset_identifier):
                dataset_identifier = self.dataset_identifier
                dataset_found = True
            else:
                dataset_found = False

        elif self.search_params is not None:
            raw_results = self.client.search(**self.search_params)
            results = self.client.filter_search_results(raw_results, self.search_results_filter)
            n_results = len(results.keys())

            logger.debug("n_results %s", n_results)

            if n_results == 1:
                dataset_identifier = results[list(results.keys())[0]]["identifier"]
                dataset_found = True
            elif n_results == 0:
                dataset_found = False
            elif n_results > 1:
                error_text = (
                    f"{n_results} results was returned, when exactly 1 or 0 is required. " +
                    "The search criteria may need to be more specific, or " +
                    "a search_results_filter may need to be applied. " +
                    f"Search Params: \n{self.search_params}\n " +
                    f"search_results_filter: \n{self.search_results_filter}\n " +
                    f"Search Results: \n{results}\n"
                )
                raise ValueError(error_text)
            else:
                raise ValueError(f"n_results of {n_results} unexpected ")
        else:
            raise (
                ValueError(
                    "unexpectedly Both dataset Identifier and search results appear to be none"
                )
            )

        if dataset_found:
            dataset_metadata = self.client.get_dataset_metadata(dataset_identifier)
            current = self.verify_current_check(dataset_metadata)
        else:
            current = False

        if not dataset_found:
            logger.debug("Dataset not found, promting a creation")
        elif dataset_found and (not current):
            logger.debug("Dataset found but not current, promiting an update")
        elif dataset_found and (current):
            logger.debug("Dataset found and current, no action will be taken")
        else:
            raise ValueError("Unexpected State")

        return current


class FrozenOrderedDictEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, FrozenOrderedDict):
            return o.get_wrapped()
        return json.JSONEncoder.default(self, o)


class WriteToDkanDatasetIdBySearch(luigi.Task):
    dkan_client_params = luigi.DictParameter(
        description="The paramaters you'd like to use to make the dkan client"
    )
    dataset_search_params = luigi.DictParameter(
        description="The search paramaters you'd like to use to uniqely identify your dataset"
    )
    dataset_search_results_filter = luigi.DictParameter(
        description="The search paramaters you'd like to use to uniqely identify your dataset",
        default={},
    )
    dataset_request_body = luigi.DictParameter(
        description="The body of the request that you'd like to post"
    )
    datastore_idx = luigi.IntParameter(description="", default=0)

    def make_dkan_client(self):
        return DKANClient(**self.dkan_client_params)  # pylint: disable=E1134

    def output(self):
        target = DkanTarget(
            search_params=self.dataset_search_params,
            search_results_filter=self.dataset_search_results_filter,
            datastore_idx=self.datastore_idx,
            dkan_client=self.make_dkan_client(),
        )

        return target

    def run(self):
        logger.debug("Running CreateOrUpdateDkanDataset")
        dkan_client = self.make_dkan_client()

        raw_results = dkan_client.search(**self.dataset_search_params)  # pylint: disable=E1134
        results = dkan_client.filter_search_results(raw_results, self.dataset_search_results_filter)

        n_results = len(results.keys())

        # This is the easiest method to resursively transform everything to a dict
        request_body = json.loads(
            json.dumps(self.dataset_request_body, cls=FrozenOrderedDictEncoder)
        )

        if n_results == 1:
            dataset_identifier = results[list(results.keys())[0]]["identifier"]
            logger.debug("Updating existing dataset on DKAN. ID %s", dataset_identifier)
            request_body["identifier"] = dataset_identifier
            _ = dkan_client.update_dataset(dataset_identifier, request_body)
        elif n_results == 0:
            logger.debug("Creating New Dataset on DKAN")
            _ = dkan_client.create_dataset(request_body)
        else:
            raise ValueError(f"n_results of {n_results} unexpected ")
