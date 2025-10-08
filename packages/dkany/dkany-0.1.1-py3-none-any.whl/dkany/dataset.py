import logging
from datetime import datetime as dt
from copy import deepcopy as copy

logger = logging.getLogger(__name__)


class DKANDatasetFactory(object):
    """
    docstring
    """

    def __init__(
        self,
        default_dataset_metadata=None,
        auto_set_modified_time=True,
        modified_time_stamp=None,
    ):
        self.auto_set_modified_time = auto_set_modified_time

        self.default_dataset_metadata = default_dataset_metadata
        self.dkan_time_format = "%Y-%m-%dT%H:%M:%S"

        if self.auto_set_modified_time:
            self.modified_time_stamp = dt.now().strftime(self.dkan_time_format)
        else:
            self.modified_time_stamp = modified_time_stamp

    def _get_distribution_format_from_url(self, download_url):
        assert download_url.endswith(".csv"), "unsupported file format"
        return {"mediaType": "text/csv", "format": "csv"}

    def create_dataset_body_with_one_distribution(
        self,
        dataset_title,
        distribution_title,
        distribution_description,
        download_url,
        identifier=None,
    ):
        dataset_params = copy(self.default_dataset_metadata)
        dataset_param_updates = {
            "title": dataset_title,
        }
        if identifier is not None:
            dataset_param_updates["identifier"] = identifier

        if self.auto_set_modified_time:
            dataset_param_updates["modified"] = self.modified_time_stamp

        dataset_params.update(dataset_param_updates)

        distribution_params = {
            "title": distribution_title,
            "description": distribution_description,
            "downloadURL": download_url,
        }

        format = self._get_distribution_format_from_url(download_url)
        distribution_params.update(format)

        if "distribution" not in dataset_params:
            dataset_params["distribution"] = []

        dataset_params["distribution"].append(distribution_params)

        return dataset_params
