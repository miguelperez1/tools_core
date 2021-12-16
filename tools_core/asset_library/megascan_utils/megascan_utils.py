import os
import re
import json
import shutil
import logging
from collections import OrderedDict

from tools_core.asset_library import library_manager as lm
# from tools_core.asset_library.asset_builder import asset_builder

logging.basicConfig()

logger = logging.getLogger("__name__")
logger.setLevel(10)

materials_library = r"F:\share\assets\quixel\Downloaded\surface"


def build_megascan_materials():
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
        var_num = 1
        asset_name = megascan_asset_data["semanticTags"]["name"].replace("(", "").replace(")", "").replace("-",
                                                                                                           "_").replace(
            " ",
            "_").replace(
            ".", "_").lower() + "_var{}".format(var_num)

        # Check if asset for megascan id in existing library
        if 'id' in megascan_asset_data.keys():
            megascan_id = megascan_asset_data['id']

            if megascan_asset_exists(megascan_id, "material"):
                logger.warning("%s exists, skipping", asset_name)
                continue

        # Determine variant number
        while asset_name in assets.keys():
            var_num = int(asset_name.split("var")[-1]) + 1
            asset_name = "{0}_var{1}".format(asset_name.split("_var")[0], var_num)

        # Get material data
        material_data = get_megascan_material(root_path, asset_name, megascan_id)

        # Rebuild Asset Data
        asset_data = {
            "asset_name": asset_name,
            "asset_preview": asset_preview,
            "asset_library": "material",
            "asset_path": os.path.join(lm.LIBRARIES["material"], asset_name),
            "usd": "",
            "vrmesh": "",
            "vrproxy_maya": "",
            "vrscene": "",
            "vrscene_maya": "",
            "maya_file": "",
            "mesh": "",
            "scale": "",
            "material_data": material_data,
            "megascan_id": megascan_id,
            "tags": [
                "megascans"
            ]
        }

        # Store new asset
        assets[asset_name] = asset_data

        # Run asset builder
        logger.debug(asset_data)

        # Check if asset build was successful


def megascan_asset_exists(asset_id, library):
    assets_data = lm.get_library_data(library)['assets']

    for asset, asset_data in assets_data.items():
        if 'megascan_id' in asset_data.keys():
            if asset_id == asset_data['megascan_id']:
                return True

    return False


# def build_megascan_models(new=1):
#     megascans_library = r"F:\share\assets\quixel\Downloaded\3d"
#
#     current_assets = get_library_data('model')
#     assets = []
#     assets.extend(current_assets['assets'].keys())
#
#     assets_to_build = 0
#     for dir in os.listdir(megascans_library):
#         for subdir in os.listdir(os.path.join(megascans_library, dir)):
#             if subdir.endswith(".json"):
#                 assets_to_build += 1
#
#     print("Assets to build: {}".format(assets_to_build))
#
#     for dir in os.listdir(megascans_library):
#         asset_data = {
#             'name': '',
#             'asset_type': 'model',
#             'preview': None,
#             'tags': 'megascans',
#             'mesh': None,
#             'material_data': None,
#             'scale': 1,
#             'has_proxy': 1,
#             'megascan_id': None
#         }
#
#         megascan_data = None
#
#         for subdir in os.listdir(os.path.join(megascans_library, dir)):
#
#             if subdir.endswith(".json"):
#                 # Load Json Data
#                 json_file = open(os.path.join(megascans_library, dir, subdir), "r")
#                 megascan_data = json.load(json_file)
#                 json_file.close()
#
#         if megascan_data is None:
#             print("Could not find megascan data for {}, skipping".format(dir))
#             continue
#
#         # Get asset id
#         if 'id' in megascan_data.keys():
#             asset_id = megascan_data['id']
#             print("Asset id: " + asset_id)
#             asset_data['megascan_id'] = asset_id
#
#         # Get asset name
#         var_num = 1
#         asset_name = megascan_data['semanticTags']['name'].lower().replace(" ", "_") + "_var" + str(var_num)
#         asset_name = asset_name.replace("__", "_")
#
#         if megascan_asset_exists(asset_id, "model"):
#             print("{} exists, skipping".format(asset_name))
#             continue
#
#         print("Building asset from {}".format(dir))
#
#         # Skip if existing
#         while asset_name in assets:
#             var_num += 1
#             asset_name = "{0}_var{1}".format(asset_name.split("_var")[0], var_num)
#
#         assets.append(asset_name)
#         asset_data['name'] = asset_name
#         print("Asset Name: " + asset_name)
#
#         # Get material data
#         material_data = get_megascan_material(os.path.join(megascans_library, dir), asset_name, asset_id)
#         asset_data['material_data'] = material_data
#
#         # Get mesh
#         mesh_file = os.path.join(megascans_library, dir, "{}_LOD0.obj".format(asset_id))
#         if os.path.isfile(mesh_file):
#             asset_data["mesh"] = mesh_file
#             print("Found mesh file: " + mesh_file)
#         else:
#             print("Could not find mesh file for {}, skipping".format(dir))
#
#         # Get scale
#         for d in megascan_data["meta"]:
#             if d["key"] == "height":
#                 scale = 3.28 * float(d["value"].split("m")[0])
#                 asset_data['scale'] = scale
#
#         # Get preview
#         preview_file = os.path.join(megascans_library, dir, "{}_preview.png".format(asset_id))
#         if os.path.isfile(preview_file):
#             asset_data['asset_preview'] = preview_file
#         elif os.path.isfile(preview_file.replace(".png", ".jpg")):
#             asset_data['asset_preview'] = preview_file.replace(".png", ".jpg")
#
#         asset_builder.build_asset(asset_data, build_maya=True)
#
#         if os.path.isfile(os.path.join(libraries['model'], asset_name, 'maya', '{}.ma'.format(asset_name))):
#             print("Built {} successfully".format(asset_name))
#             assets_to_build -= 1
#             print("Remaining assets to build: {}".format(assets_to_build))
#
#             build_library_jsons()


def get_megascan_material(path, asset_name, asset_id):
    material_data = {
        "name": asset_name,
        "material_type": "VRayMtl",
        "textures": {}
    }

    textures = {}

    diffuse_path = os.path.join(path, "{}_4K_Albedo.exr".format(asset_id))
    if os.path.isfile(diffuse_path):
        textures['diffuse'] = diffuse_path

    specular_path = os.path.join(path, "{}_4K_Specular.exr".format(asset_id))
    if os.path.isfile(specular_path):
        textures['specular'] = specular_path

    gloss_path = os.path.join(path, "{}_4K_Gloss.exr".format(asset_id))
    if os.path.isfile(gloss_path):
        textures['gloss'] = gloss_path

    normal_path = os.path.join(path, "{}_4K_Normal_LOD0.exr".format(asset_id))
    if os.path.isfile(normal_path):
        textures['normal'] = normal_path

    elif os.path.isfile(normal_path.replace("_LOD0", "")):
        textures['normal'] = normal_path.replace("_LOD0", "")

    displacement_path = os.path.join(path, "{}_4K_Displacement.exr".format(asset_id))
    if os.path.isfile(displacement_path):
        textures['displacement'] = displacement_path

    material_data["textures"] = textures

    return material_data


def delete_existing_megascans():
    paths = [
        r"F:\share\assets\libraries\model",
        r"F:\share\assets\libraries\material"
    ]

    for m_path in paths:
        for dir in os.listdir(m_path):
            data_file = os.path.join(m_path, dir, "data.json")
            if os.path.isfile(data_file):
                json_file = open(data_file, "r")
                asset_data = json.load(json_file)
                json_file.close()

                if "megascans" in asset_data["tags"]:
                    print("Deleting {}".format(os.path.join(m_path, dir)))
                    shutil.rmtree(os.path.join(m_path, dir))


if __name__ == '__main__':
    build_megascan_materials()
