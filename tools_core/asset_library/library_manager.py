import os
import re
import json
from collections import OrderedDict
import logging

logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(10)

LIBRARIES_ROOT = r"F:\share\assets\libraries"

LIBRARIES = OrderedDict()

LIBRARIES['Character'] = r"{}\Character".format(LIBRARIES_ROOT)
LIBRARIES['Prop'] = r"{}\Prop".format(LIBRARIES_ROOT)
LIBRARIES['Set'] = r"{}\Set".format(LIBRARIES_ROOT)
LIBRARIES['Transit'] = r"{}\Transit".format(LIBRARIES_ROOT)
LIBRARIES['Foliage'] = r"{}\Foliage".format(LIBRARIES_ROOT)
LIBRARIES['Material'] = r"{}\Material".format(LIBRARIES_ROOT)
LIBRARIES['StudioLights'] = r"{}\StudioLights".format(LIBRARIES_ROOT)
LIBRARIES['Cucoloris'] = r"{}\Cucoloris".format(LIBRARIES_ROOT)
LIBRARIES['HDR'] = r"{}\HDR".format(LIBRARIES_ROOT)
LIBRARIES['Texture'] = r"{}\Texture".format(LIBRARIES_ROOT)

STD_LIBRARIES = [
    "Character",
    "Prop",
    "Set",
    "Transit",
    "Material",
    "Foliage"
]

IMG_LIBRARIES = [
    "HDR",
    "StudioLights",
    "Texture",
    "Cucoloris"
]

IMG_FILE_TYPES = [
    "jpg",
    "exr",
    "tex",
    "png",
    "tiff",
    "tif",
    "jpeg",
    "hdr"
]

ASSET_DATA_KEY_ORDER = [
    "asset_name",
    "asset_preview",
    "asset_type",
    "asset_path",
    "tags",
    "usd",
    "materials",
    "maya_file",
    "vrmesh",
    "vrproxy_maya",
    "vrscene",
    "vrscene_maya",
    "mesh",
    "megascan_id",
    "scale"
]


def create_library_data(library, override=True):
    # Check for valid library
    if library not in LIBRARIES.keys():
        return

    library_root = LIBRARIES[library]

    # Check for existing library data and override
    library_data = get_library_data(library)

    if library_data and not override:
        return
    elif not library_data:
        library_data = {
            "assets": {},
            "tags": []
        }

    # Look for assets

    # Scan assets in STD_LIBRARIES
    if library in STD_LIBRARIES:
        for letter in os.listdir(library_root):
            letter_path = os.path.join(library_root, letter)

            if os.path.isfile(letter_path):
                continue

            for asset in os.listdir(letter_path):
                asset_root = os.path.join(letter_path, asset)

                if os.path.isfile(asset_root):
                    continue

                # Get asset data
                asset_data = get_asset_data(library, asset)

                if not asset_data:
                    logger.warning("No asset data found for %s, it will be excluded from library data", asset)
                    continue

                # Add asset_data to library
                library_data["assets"][asset] = asset_data

    # Scan assets in IMG_LIBRARIES
    elif library in IMG_LIBRARIES:
        for asset in os.listdir(library_root):
            asset_root = os.path.join(library_root, asset)
            asset_name = asset.split(".")[0]

            if not os.path.isfile(asset_root):
                continue

            if asset.split(".")[-1] not in IMG_FILE_TYPES:
                continue

            # Find preview image
            asset_preview = ""

            asset_preview_path = os.path.join(library_root, "thumbnails", asset_name + "_preview.png")

            if os.path.isfile(asset_preview_path):
                asset_preview = asset_preview_path

            asset_data = {
                "asset_name": asset_name,
                "asset_type": library,
                "asset_path": asset_root,
                "asset_preview": asset_preview,
                "tags": []
            }

            # Check for existing asset data
            if get_library_data(library):
                asset_data_tmp = get_asset_data(library, asset_name)

                if asset_data_tmp:
                    # Store old tags
                    asset_data["tags"] = asset_data_tmp["tags"]

            # Add asset_data to library
            library_data["assets"][asset_name] = asset_data

    # Check if assets in library exists, if not remove
    remove_assets = []

    for asset_tmp, asset_data_tmp in library_data["assets"].items():
        if library in STD_LIBRARIES:
            if not os.path.isdir(asset_data_tmp["asset_path"]):
                logger.warning("%s no longer exists, removing from library_data", asset_tmp)
                remove_assets.append(asset_tmp)
        elif library in IMG_LIBRARIES:
            if not os.path.isfile(asset_data_tmp["asset_path"]):
                logger.warning("%s no longer exists, removing from library_data", asset_tmp)
                remove_assets.append(asset_tmp)

    for asset_tmp in remove_assets:
        if asset_tmp in library_data["assets"].keys():
            library_data["assets"].pop(asset_tmp)

    # Order library data by asset name
    ordered_library_data = OrderedDict()
    ordered_library_data["assets"] = OrderedDict()
    ordered_library_data["tags"] = []

    for asset in sorted(library_data["assets"].keys(), key=lambda a: a.lower()):
        ordered_library_data["assets"][asset] = sort_asset_data(library_data["assets"][asset])

    # Gather tags
    all_tags = []

    for asset, asset_data in ordered_library_data["assets"].items():
        all_tags.extend(asset_data["tags"])

    for tag in library_data["tags"]:
        if tag not in all_tags:
            library_data["tags"].remove(tag)

    if "" in all_tags:
        all_tags.remove("")
    if " " in all_tags:
        all_tags.remove(" ")

    ordered_library_data["tags"] = sorted(list(set(all_tags)))

    # Delete existing json if override
    if override:
        library_json = os.path.join(library_root, "library_data.json")
        if os.path.isfile(library_json):
            os.remove(library_json)

    # Write library data
    write_library_data(library, ordered_library_data)


def update_asset_in_library(library, asset, asset_data):
    library_data = get_library_data(library)

    library_data["assets"][asset] = sort_asset_data(asset_data)

    write_library_data(library, library_data)

    if get_library_data(library) == library_data:
        logger.info("Successfully updated %s in %s library", asset, library)
        return True
    else:
        logger.error("Error updating %s in %s library", asset, library)
        return False


def refresh_all_libraries():
    for library, library_path in LIBRARIES.items():
        if not os.path.isdir(library_path):
            continue

        create_library_data(library)


def get_library_data(library):
    library_json_path = os.path.join(LIBRARIES[library], "library_data.json")

    if not os.path.isfile(library_json_path):
        return None

    library_data = json.load(open(library_json_path))

    return library_data


def get_asset_data(library, asset):
    asset_data = None

    if library in STD_LIBRARIES:

        asset_json_path = os.path.join(LIBRARIES[library], asset[0].lower(), asset, "asset_data.json")

        if not os.path.isfile(asset_json_path):
            logger.error("Could not find asset json path for %s", asset)
            return None

        asset_data = json.load(open(asset_json_path))

    else:
        library_data = get_library_data(library)

        if not library_data:
            return None

        if asset not in library_data["assets"].keys():
            logger.error("Could not find asset data")
            return None

        asset_data = library_data["assets"][asset]

    return asset_data


def sort_asset_data(asset_data):
    ordered_asset_data = OrderedDict()

    for key in ASSET_DATA_KEY_ORDER:
        if key in asset_data.keys():
            ordered_asset_data[key] = asset_data[key]

    for key in asset_data.keys():
        if key not in ordered_asset_data.keys():
            ordered_asset_data[key] = asset_data[key]

    return ordered_asset_data


def write_library_data(library, library_data, override=True):
    library_json_path = os.path.join(LIBRARIES[library], "library_data.json")

    if get_library_data(library) and not override:
        return False

    # Write data
    with open(library_json_path, "w") as f:
        json.dump(library_data, f, indent=4)

    # Check if write was successful
    data = json.load(open(library_json_path))

    if library_data == data:
        logger.info("Successfully wrote %s library data", library)
        return True
    else:
        logger.error("Error writing %s library data", library)
        for asset, asset_data in library_data["assets"].items():
            if asset not in data["assets"].keys():
                logger.error("%s not written library data", asset)
                continue
            logger.debug(set(data["assets"][asset]) - set(asset_data))
        return False


def write_asset_data(library, asset, asset_data, override=True, update_library_data=False):
    new_data = {}

    if get_asset_data(library, asset) and not override:
        return False

    if library in STD_LIBRARIES:
        asset_json_path = os.path.join(LIBRARIES[library], asset[0].lower(), asset, "asset_data.json")

        with open(asset_json_path, "w") as f:
            json.dump(sort_asset_data(asset_data), f, indent=4)

        new_data = json.load(open(asset_json_path))

        if update_library_data:
            update_asset_in_library(library, asset, asset_data)

    elif library in IMG_LIBRARIES:
        library_data = get_library_data(library)

        library_data["assets"][asset] = asset_data

        write_library_data(library, library_data)

        new_data = get_library_data(library)["assets"][asset]

    if asset_data == new_data:
        logger.info("Successfully wrote %s asset data", asset)
        return True
    else:
        return False


def update_asset_tags(library, asset, tags, override=True):
    asset_data = get_asset_data(library, asset)

    if not asset_data:
        return

    if not override:
        current_tags = asset_data["tags"]
    else:
        current_tags = []

    new_tags = []

    if isinstance(tags, str):
        if "," in tags:
            new_tags = tags.split(",")
        else:
            new_tags.append(tags)
    elif isinstance(tags, list):
        new_tags.extend(tags)

    for tag in current_tags:
        if tag not in new_tags:
            new_tags.append(tag)

    if " " in new_tags:
        new_tags.remove(" ")

    if "" in new_tags:
        new_tags.remove("")

    asset_data["tags"] = sorted(list(set(new_tags)))

    if write_asset_data(library, asset, asset_data, update_library_data=True):
        logger.info("Updated %s tags", asset_data["asset_name"])
        return True
    else:
        return False


def get_assets(library):
    assets = []

    for letter in os.listdir(LIBRARIES[library]):
        letter_path = os.path.join(LIBRARIES[library], letter)

        if os.path.isfile(letter_path):
            continue

        for asset in os.listdir(letter_path):
            if asset not in assets:
                assets.append(asset)

    return assets


# HELPER TRANSITION FUNCTIONS

def _reformat_asset_datas():
    for library in STD_LIBRARIES:
        if library != "Material":
            continue

        library_path = LIBRARIES[library]

        if not os.path.isdir(library_path):
            continue

        for letter in os.listdir(library_path):
            letter_path = os.path.join(library_path, letter)

            if not os.path.isdir(letter_path):
                continue

            for asset in os.listdir(letter_path):
                asset_path = os.path.join(library_path, asset[0].lower(), asset)

                if not os.path.isdir(asset_path):
                    continue

                if "asset_data.json" not in os.listdir(asset_path):
                    continue

                old_asset_data = json.load(open(os.path.join(asset_path, "asset_data.json")))

                logger.info("Converting %s asset data json", asset)

                asset_data = {
                    "asset_name": "",
                    "asset_preview": "",
                    "asset_type": library,
                    "asset_path": asset_path,
                    "usd": "",
                    "vrmesh": "",
                    "vrproxy_maya": "",
                    "vrscene": "",
                    "vrscene_maya": "",
                    "maya_file": "",
                    "mesh": "",
                    "scale": 0,
                    "material_data": "",
                    "megascan_id": "",
                    "tags": []
                }

                # Copy existing data
                for key in asset_data.keys():
                    if key in old_asset_data.keys() and key != "tags":
                        asset_data[key] = old_asset_data[key]

                    if "tags" in old_asset_data.keys() and isinstance(old_asset_data["tags"], str):
                        tags = []
                        old_tags = old_asset_data["tags"]

                        if "," in old_tags:
                            tags = [t.replace(" ", "") for t in old_asset_data['tags'].split(",")]
                        elif old_tags and "," not in old_tags:
                            tags = [old_tags]

                        asset_data["tags"] = sorted(list(set(tags)))

                asset_data["asset_type"] = library
                if asset_data["asset_preview"]:
                    asset_data["asset_preview"] = os.path.join(asset_path, "{}_preview.png".format(asset))

                # Set new data
                with open(os.path.join(asset_path, "asset_data.json"), "w") as f:
                    json.dump(sort_asset_data(asset_data), f, indent=4)


def _copy_img_tags():
    for library in IMG_LIBRARIES:
        all_tags = []

        new_library_data = get_library_data(library)

        library_root = LIBRARIES[library]

        old_library_json = os.path.join(library_root, "assets.json")

        if not os.path.isfile(old_library_json):
            continue

        old_library_data = json.load(open(old_library_json))

        for asset, asset_data in old_library_data["assets"].items():
            if asset not in new_library_data["assets"].keys():
                continue

            if "tags" in asset_data.keys():
                tags = [t.replace(" ", "") for t in asset_data["tags"].split(",")]

                if "" in tags:
                    tags.remove("")

                new_library_data["assets"][asset]["tags"] = sorted(list(set(tags)))

                for tag in tags:
                    if tag not in all_tags:
                        all_tags.append(tag)

        new_library_data["tags"] = sorted(list(set(all_tags)))

        with open(os.path.join(library_root, "library_data.json"), "w") as f:
            json.dump(new_library_data, f, indent=4)


def _fix_scale():
    for library in STD_LIBRARIES:
        library_data = get_library_data(library)

        for asset, asset_data in library_data["assets"].items():
            if "scale" in asset_data.keys() and asset_data["scale"] == 1.0:
                asset_data["scale"] = None

            write_asset_data(library, asset, asset_data)

        create_library_data(library)


def _reorder_existing_asset_datas():
    for library in STD_LIBRARIES:
        library_data = get_library_data(library)

        for asset, asset_data in library_data["assets"].items():
            new_asset_data = OrderedDict()
            for key in ASSET_DATA_KEY_ORDER:
                if key in asset_data.keys():
                    new_asset_data[key] = asset_data[key]

            write_asset_data(library, asset, new_asset_data)

        create_library_data(library)


def _delete_library_jsons():
    for library, library_path in LIBRARIES.items():
        library_json = os.path.join(library_path, "library_data.json")

        if os.path.isfile(library_json):
            os.remove(library_json)


def _delete_all_asset_datas():
    for library in STD_LIBRARIES:
        library_data = get_library_data(library)

        for asset in library_data["assets"].keys():
            asset_path = os.path.join(LIBRARIES[library], asset[0].lower(), asset)

            asset_json_path = os.path.join(asset_path, "asset_data.json")

            if os.path.isfile(asset_json_path):
                os.remove(asset_json_path)


if __name__ == '__main__':
    refresh_all_libraries()
