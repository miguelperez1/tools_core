import os
import json
import subprocess
from shutil import copyfile

from tools_core.asset_library import library_manager as lm


class AssetBuilder(object):
    def __init__(self, asset_data, build_maya=False):
        super(AssetBuilder, self).__init__()
        self.asset_data = asset_data

        self.build_maya_file = build_maya

        if self.asset_data["asset_library"] in lm.STD_LIBRARIES:
            self.asset_root = os.path.join(lm.LIBRARIES[self.asset_data["asset_library"]],
                                           self.asset_data["asset_name"])

        self.json_path = os.path.join(self.asset_root, "asset_data.json")

    def create_asset(self, save_type=None):
        self._create_directories()
        self._copy_preview()
        self._publish_material()
        self._copy_mesh()
        self._create_asset_json()

        if self.build_maya_file:
            self._build_maya()

    def _create_directories(self):
        os.mkdir(self.asset_root)

        self.maya_dir = os.path.join(self.asset_root, "maya")
        os.mkdir(self.maya_dir)

        if 'material_data' in self.asset_data.keys() and self.asset_data['material_data']:
            mat_dir = os.path.join(self.asset_root, "material", self.asset_data['material_data']['name'])
            os.mkdir(mat_dir)

            textures_dir = os.path.join(mat_dir, "textures")
            os.mkdir(textures_dir)

        if 'has_proxy' in self.asset_data.keys() and self.asset_data['has_proxy']:
            self.publish_data['has_proxy'] = self.asset_data['has_proxy']
            os.mkdir(os.path.join(self.asset_root, 'vrayproxy'))

        if 'mesh' in self.asset_data.keys() and self.asset_data['mesh']:
            os.mkdir(os.path.join(self.asset_root, 'mesh'))

    def _create_asset_json(self):
        with open(self.json_path, "w") as f:
            json.dump(self.publish_data, f, indent=4)

    def _publish_material(self):
        # TODO
        pass

    def _copy_preview(self):
        if 'asset_preview' in self.asset_data.keys() and self.asset_data['asset_preview']:
            src_preview = self.asset_data['asset_preview']
            preview_name = "{0}_preview.png".format(self.name)
            dst_preview = os.path.join(self.asset_root, preview_name)

            self.publish_data['asset_preview'] = dst_preview

            copyfile(src_preview, dst_preview)

    def _copy_mesh(self):
        if 'mesh' in self.asset_data.keys() and self.asset_data['mesh']:
            src_mesh = self.asset_data['mesh']
            dst_mesh = os.path.join(self.asset_root, "mesh", src_mesh.split("\\")[-1])
            copyfile(src_mesh, dst_mesh)

            self.publish_data['mesh'] = dst_mesh

    def _build_maya(self):
        function = r'F:\share\tools\tools_core\python\maya_core\asset_manager\asset_builder\maya_builder.py'

        arg = '{}'.format(self.json_path)

        log_path = os.path.join(self.asset_root, "build_log", "build_log.txt")
        f = open(log_path, "w")

        print("running mayapy process for {}".format(self.name))

        subprocess.call(['mayapy', function, arg], stdout=f, stderr=subprocess.STDOUT)

    def _publish_textures(self, texture_data=None):
        if not texture_data.keys():
            return


def build_asset(asset_data, build_maya=False):
    if not asset_data:
        print("no asset data provided")
        return

    asset_builder = AssetBuilder(asset_data, build_maya=build_maya)
    asset_builder.create_asset()
