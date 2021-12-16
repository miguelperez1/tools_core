import os
import json
import logging
import string
import subprocess

logger = logging.getLogger(__name__)
logger.setLevel(10)

from tools_core.common_utilities import common_utilities as cu
from tools_core.asset_library import library_manager as lm


class Asset(object):
    def __init__(self, asset_data):
        self.asset_name = asset_data["asset_name"]
        self.asset_type = asset_data["asset_type"]

    def create_asset(self):
        # create letter directory if it doesn't exist
        letter_path = "/".join(self.asset_root_path.split("/")[:-1])

        if not os.path.isdir(letter_path):
            os.mkdir(letter_path)

        # create asset root path
        os.mkdir(self.asset_root_path)

        # Create asset directories
        asset_structure_json_path = r"F:\share\tools\tools_core\tools_core\pipeline\asset\asset_directory_structure.json"

        json_file = open(asset_structure_json_path, "r")
        asset_structure_data = json.load(json_file)
        json_file.close()

        cu.create_dirs_from_dict(asset_structure_data, self.asset_root_path)
