import os
import json
import logging
import string
import subprocess
from shutil import copyfile

logger = logging.getLogger(__name__)
logger.setLevel(10)

from tools_core.common_utilities import common_utilities as cu
from tools_core.asset_library import library_manager as lm


class Asset(object):
    def __init__(self, asset_data, build_maya=False):
        self.asset_data = asset_data
        self.asset_name = self.asset_data["asset_name"]
        self.asset_type = self.asset_data["asset_type"]
        self.asset_root_path = os.path.join(lm.LIBRARIES[self.asset_type], self.asset_name[0].lower(), self.asset_name)
        self.asset_data["asset_path"] = self.asset_root_path
        self.asset_data_json = os.path.join(self.asset_root_path, "asset_data.json")
        self.preview_path = os.path.join(self.asset_root_path, "{}_preview.png".format(self.asset_name))
        self.build_maya = build_maya
        self.world_node_path = os.path.join(self.asset_root_path, "01_build", "world_node", self.asset_name + ".ma")

    def create_asset(self):
        # create letter directory if it doesn't exist
        letter_path = os.path.join(lm.LIBRARIES[self.asset_type], self.asset_name[0].lower())

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

        if self.asset_data["materials"]:
            self._copy_images()

        if self.asset_data["asset_preview"]:
            if not self.asset_data["asset_preview"].startswith(self.asset_root_path) and os.path.isfile(
                    self.asset_data["asset_preview"]):
                if self.publish_preview(self.asset_data["asset_preview"]):
                    self.asset_data["asset_preview"] = self.preview_path

        if self.asset_data["mesh"] and not self.asset_data["mesh"].startswith(self.asset_root_path) and os.path.isfile(
                self.asset_data["mesh"]):
            self.publish_mesh(self.asset_data["mesh"])

        self._create_asset_json()

        if self.build_maya:
            self._build_maya_world_node()

        # lm.create_library_data(self.asset_type)

    def _copy_images(self):
        materials = self.asset_data["materials"]
        new_mtls = []

        for material_data in materials:
            new_mtl_data = {
                "textures": {
                    "unknown": []
                },
                "material_name": material_data["material_name"],
                "material_shader": material_data["material_shader"]
            }

            mtl_root_path = os.path.join(self.asset_root_path, "03_lookdev", "publish", "materials",
                                         material_data["material_name"])

            if not os.path.isdir(mtl_root_path):
                os.mkdir(mtl_root_path)

            for tex_type, tex_path in material_data["textures"].items():
                if tex_type == "unknown":
                    for tex in tex_path:
                        src = tex
                        dst = os.path.join(mtl_root_path, tex.replace("/", "\\").split("\\")[-1])

                        logger.debug(material_data)

                        copyfile(src, dst)

                        new_mtl_data["textures"]["unknown"].append(dst)

                    continue

                if tex_path.startswith(mtl_root_path) and os.path.isfile(tex_path):
                    continue

                src = tex_path
                dst = os.path.join(mtl_root_path, tex_path.replace("/", "\\").split("\\")[-1])

                copyfile(src, dst)

                new_mtl_data["textures"][tex_type] = dst

            new_mtls.append(new_mtl_data)

        for material in new_mtls:
            valid_material = True

            for tt, tex_path in material["textures"].items():
                if tt == "unknown":
                    continue

                if os.path.isfile(tex_path) and valid_material:
                    valid_material = True
                else:
                    valid_material = False

            if valid_material:
                logger.debug("%s build: %s published successfully", self.asset_name, material["material_name"])
            else:
                logger.warning("%s build: %s published unsuccessfully", self.asset_name, material["material_name"])

        self.asset_data["materials"] = new_mtls

    def _create_asset_json(self):
        with open(self.asset_data_json, "w") as f:
            json.dump(lm.sort_asset_data(self.asset_data), f, indent=4)

        if os.path.isfile(self.asset_data_json):
            logger.debug("Created %s asset data json", self.asset_name)

    def _build_maya_world_node(self):
        # Python script path
        function = r"F:\share\tools\maya_core\maya_core\pipeline\MayaAsset\create_world_node.py"

        # Pass asset data as argument
        arg = '{}'.format(self.asset_data_json)

        # Log build path
        log_path = os.path.join(self.asset_root_path, "00_data", "logs", "build_log.txt")
        f = open(log_path, "w")

        logger.debug("running mayapy process for %s", self.asset_name)

        subprocess.call(['mayapy', function, arg], stdout=f, stderr=subprocess.STDOUT)

    def publish_mesh(self, mesh):
        src = mesh.replace("/", "\\")

        file_ext = src.split(".")[-1]

        dst = os.path.join(self.asset_root_path, "02_model", "publish", "{}.{}".format(self.asset_name, file_ext))

        copyfile(src, dst)

        self.asset_data["mesh"] = dst

    def get_asset_data(self):
        return lm.sort_asset_data(json.load(open(self.asset_data_json)))

    def publish_preview(self, preview_src):
        if not os.path.isfile(preview_src):
            logger.error("Preview source is not a file")
            return False

        if os.path.isfile(self.preview_path):
            os.remove(self.preview_path)

        copyfile(preview_src, self.preview_path)

        if os.path.isfile(self.preview_path):
            logger.info("Preview published successfully")

            return True
