import os
import logging

logging.basicConfig()

from tools_core.asset_library import library_manager as lm
from tools_core.pipeline.Asset import Asset


class MaterialAsset(Asset.Asset):
    def __init__(self, asset_data):
        super(MaterialAsset, self).__init__(asset_data)

    def create_asset(self):
        super(MaterialAsset, self).create_asset()
