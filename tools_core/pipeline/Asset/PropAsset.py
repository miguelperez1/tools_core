import os
import logging

logging.basicConfig()

from tools_core.asset_library import library_manager as lm
from tools_core.pipeline.Asset import Asset


class PropAsset(Asset.Asset):
    def __init__(self, asset_data):
        super(PropAsset, self).__init__(asset_data)

    def create_asset(self):
        self._create_asset()
