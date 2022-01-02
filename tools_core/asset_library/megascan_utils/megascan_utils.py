import os
import re
import json
import shutil
import string
import logging
import subprocess
from collections import OrderedDict

from tools_core.asset_library import library_manager as lm
from tools_core.pipeline.Asset import MaterialAsset
from tools_core.pipeline.Asset import Asset

logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(10)

materials_library = r"F:\share\assets\quixel\Downloaded\surface"


def build_megascan_materials():
    lm.create_library_data("Material")

    assets = {}

    subdirs = os.listdir(materials_library)

    assets_to_build = 0
    for root in subdirs:
        for subdir in os.listdir(os.path.join(materials_library, root)):
            if subdir.endswith(".json"):
                assets_to_build += 1

    logger.info("Assets to build: %s", assets_to_build)

    for subdir in subdirs:
        root_path = os.path.join(materials_library, subdir)

        # Initialize varibales
        megascan_json = None
        asset_preview = ""
        megascan_id = ""

        if not os.path.isdir(root_path):
            continue

        # Find megascan json data
        for p in os.listdir(root_path):
            if p.endswith(".json"):
                megascan_json = os.path.join(root_path, p)
            if p.endswith("view.png"):
                asset_preview = os.path.join(root_path, p)

        if not megascan_json:
            logger.debug("Could not find megascan json for %s, skipping", subdir)
            continue

        json_file = open(megascan_json, "r")
        megascan_asset_data = json.load(json_file)
        json_file.close()

        # Get asset name from megascan data
        var_num = 0
        asset_name_tmp = megascan_asset_data["semanticTags"]["name"].replace("(", "").replace(")", "").replace("-",
                                                                                                               "_").replace(
            " ",
            "_").replace(
            ".", "_").lower() + "_var{}".format(var_num)

        # Check if asset for megascan id in existing library
        if 'id' in megascan_asset_data.keys():
            megascan_id = megascan_asset_data['id']

            if megascan_asset_exists(megascan_id, "Material"):
                logger.warning("%s exists, skipping", asset_name_tmp)
                continue

        # Determine variant number
        while asset_name_tmp in assets.keys():
            var_num = var_num + 1
            asset_name_tmp = "{0}_var{1}".format(asset_name_tmp.split("_var")[0], var_num)

        asset_name_short = "".join(asset_name_tmp.split("_var")[0].replace("_", " ").title().split(" "))

        asset_name = asset_name_short + string.ascii_uppercase[var_num]

        # Get material data
        material_data = get_megascan_material(root_path, asset_name, megascan_id)

        if not material_data["textures"].keys():
            logger.warning("No textures found for %s, skipping", asset_name)
            continue

        logger.info("Building %s", asset_name)

        # Rebuild Asset Data
        asset_data = {
            "asset_name": asset_name,
            "asset_preview": asset_preview,
            "asset_type": "Material",
            "asset_path": "",
            "usd": "",
            "vrmesh": "",
            "vrproxy_maya": "",
            "vrscene": "",
            "vrscene_maya": "",
            "maya_file": "",
            "mesh": "",
            "scale": "",
            "materials": [material_data],
            "megascan_id": megascan_id,
            "tags": ["megascans"]
        }

        # Store new asset
        assets[asset_name_tmp] = asset_data

        # Run asset builder

        new_asset = MaterialAsset.MaterialAsset(asset_data)

        try:
            new_asset.create_asset()
        except Exception:
            logger.error("Error building %s", asset_name)
            continue

        try:
            build_maya(new_asset)
        except Exception:
            logger.error("Error building %s", asset_name)
            continue

        # Check if asset build was successful
        if os.path.isfile(new_asset.asset_data_json):
            logger.info("%s build was successfull", new_asset.asset_name)

            assets_to_build -= 1

            logger.info("%s assets left to build", assets_to_build)


def megascan_asset_exists(asset_id, library):
    assets_data = lm.get_library_data(library)['assets']

    for asset, asset_data in assets_data.items():
        if 'megascan_id' in asset_data.keys():
            if asset_id == asset_data['megascan_id']:
                return True

    return False


def build_megascan_models():
    megascans_library = r"F:\share\assets\quixel\Downloaded\3d"

    current_assets = lm.get_library_data('Prop')
    assets = []
    assets.extend(current_assets['assets'].keys())

    assets_to_build = 0
    for dir in os.listdir(megascans_library):
        for subdir in os.listdir(os.path.join(megascans_library, dir)):
            if subdir.endswith(".json"):
                assets_to_build += 1

    print("Assets to build: {}".format(assets_to_build))

    for dir in os.listdir(megascans_library):
        asset_data = {
            "asset_name": None,
            "asset_preview": None,
            "asset_type": "Prop",
            "asset_path": None,
            "usd": None,
            "vrmesh": None,
            "vrproxy_maya": None,
            "vrscene": None,
            "vrscene_maya": None,
            "maya_file": None,
            "mesh": None,
            "scale": None,
            "materials": None,
            "megascan_id": None,
            "tags": ["megascans"]
        }

        megascan_data = None

        for subdir in os.listdir(os.path.join(megascans_library, dir)):

            if subdir.endswith(".json"):
                # Load Json Data
                try:
                    json_file = open(os.path.join(megascans_library, dir, subdir), "r")
                    megascan_data = json.load(json_file)
                    json_file.close()
                except Exception:
                    logger.error("Error reading json file")
                    continue

        if megascan_data is None:
            logger.warning("Could not find megascan data for %s, skipping".format(dir))
            continue

        # Get asset id
        if 'id' in megascan_data.keys():
            asset_id = megascan_data['id']
            # print("Asset id: " + asset_id)
            asset_data['megascan_id'] = asset_id

        # Get asset name
        var_num = 0
        asset_name = megascan_data['semanticTags']['name'].lower().replace(" ", "_") + "_var" + str(var_num)
        asset_name = asset_name.replace("__", "_")

        if megascan_asset_exists(asset_id, "Prop"):
            logger.warning("%s already exists, skipping", asset_name)
            # print("{} exists, skipping".format(asset_name))
            continue

        # print("Building asset from {}".format(dir))

        # Skip if existing
        while asset_name in assets:
            var_num += 1
            asset_name = "{0}_var{1}".format(asset_name.split("_var")[0], var_num)

        asset_name_short = "".join(asset_name.split("_var")[0].replace("_", " ").title().split(" "))

        an = asset_name_short + string.ascii_uppercase[var_num]

        assets.append(asset_name)
        asset_data['asset_name'] = str(an)
        # print("Asset Name: " + asset_name)

        # Get material data
        material_data = get_megascan_material(os.path.join(megascans_library, dir), an, asset_id)

        if not material_data:
            logger.warning("Could not find material data, skipping")
            continue

        asset_data['materials'] = [material_data]

        # Get mesh
        mesh_file = os.path.join(megascans_library, dir, "{}_LOD0.obj".format(asset_id))
        if os.path.isfile(mesh_file):
            asset_data["mesh"] = mesh_file
            # print("Found mesh file: " + mesh_file)
        elif os.path.isfile(mesh_file.replace(".obj", ".fbx")):
            asset_data["mesh"] = mesh_file.replace(".obj", ".fbx")
        else:
            logger.error("Could not find mesh file skipping")
            continue

        # Get scale
        for d in megascan_data["meta"]:
            if d["key"] == "height":
                scale = 3.28 * float(d["value"].split("m")[0])
                asset_data['scale'] = scale

        # Get preview
        preview_file = os.path.join(megascans_library, dir, "{}_preview.png".format(asset_id))
        if os.path.isfile(preview_file):
            asset_data['asset_preview'] = preview_file
        elif os.path.isfile(preview_file.replace(".png", ".jpg")):
            asset_data['asset_preview'] = preview_file.replace(".png", ".jpg")

        new_asset = Asset.Asset(asset_data)

        try:
            new_asset.create_asset()
        except Exception as e:
            logger.error("Error building %s", asset_name)
            raise e
            continue

        try:
            build_maya(new_asset)
        except Exception as e:
            logger.error("Error building maya %s", asset_name)
            raise e
            continue

        # Check if asset build was successful
        if os.path.isfile(new_asset.asset_data_json):
            logger.info("%s build was successfull", new_asset.asset_name)

            assets_to_build -= 1

            logger.info("%s assets left to build", assets_to_build)

        assets_to_build += 1

    print(assets_to_build)


def get_megascan_material(root_path, asset_name, asset_id):
    material_data = {
        "material_name": asset_name,
        "material_shader": "VRayMtl",
        "textures": {}
    }

    textures = {}

    diffuse_path = os.path.join(root_path, "{}_4K_Albedo.exr".format(asset_id))
    if os.path.isfile(diffuse_path):
        textures['diffuse'] = diffuse_path

    specular_path = os.path.join(root_path, "{}_4K_Specular.exr".format(asset_id))
    if os.path.isfile(specular_path):
        textures['specular'] = specular_path

    gloss_path = os.path.join(root_path, "{}_4K_Gloss.exr".format(asset_id))
    if os.path.isfile(gloss_path):
        textures['gloss'] = gloss_path

    normal_path = os.path.join(root_path, "{}_4K_Normal_LOD0.exr".format(asset_id))
    if os.path.isfile(normal_path):
        textures['normal'] = normal_path

    elif os.path.isfile(normal_path.replace("_LOD0", "")):
        textures['normal'] = normal_path.replace("_LOD0", "")

    displacement_path = os.path.join(root_path, "{}_4K_Displacement.exr".format(asset_id))
    if os.path.isfile(displacement_path):
        textures['displacement'] = displacement_path

    material_data["textures"] = textures

    return material_data


def delete_existing_megascans():
    for asset in lm.get_assets("Prop"):
        asset_data = lm.get_asset_data("Prop", asset)

        if "megascans" in asset_data["tags"]:
            logger.debug("Removing %s", asset)
            shutil.rmtree(asset_data["asset_path"])


def build_maya(asset):
    # Python script path
    function = r"F:\share\tools\maya_core\maya_core\asset_library\megascan_builder\megascan_builder.py"

    # Pass asset data as argument
    arg = '{}'.format(asset.asset_data_json)

    # Log build path
    log_path = os.path.join(asset.asset_root_path, "00_data", "logs", "build_log.txt")
    f = open(log_path, "w")

    logger.debug("running mayapy process for %s", asset.asset_name)

    subprocess.call(['mayapy', function, arg], stdout=f, stderr=subprocess.STDOUT)


if __name__ == '__main__':
    delete_existing_megascans()
    lm.refresh_all_libraries()
    build_megascan_models()
