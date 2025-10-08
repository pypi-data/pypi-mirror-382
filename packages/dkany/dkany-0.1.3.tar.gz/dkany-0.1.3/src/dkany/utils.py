import logging
import os

import yaml

logger = logging.getLogger(__name__)


def get_project_root(directories_to_go_up=3):
    project_dir = os.path.abspath(__file__)

    for _ in range(directories_to_go_up):
        project_dir = os.path.dirname(project_dir)

    return project_dir


def read_yaml_file(full_file_path):
    with open(full_file_path, "r", encoding="utf-8") as stream:
        out_dict = yaml.safe_load(stream)
    return out_dict
