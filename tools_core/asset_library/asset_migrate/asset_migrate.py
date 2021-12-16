import os
import json
from shutil import copytree

from tools_core.asset_library import library_manager as lm


def move_to_letter_paths():
    for library, lb_path in ("Material", r"F:\share\assets\libraries\Material"):
        if not os.path.isdir(lb_path):
            continue

        subdirs = os.listdir(lb_path)
        letters = []

        assets = {}

        for subdir in subdirs:
            if len(subdir) == 1 or os.path.isfile(os.path.join(lb_path, subdir)):
                continue

            asset = subdir
            asset_letter = asset[0].lower()

            asset_path = os.path.join(lb_path, asset)

            if asset_letter not in assets.keys():
                assets[asset_letter] = []

            assets[asset_letter].append(asset_path)

        for asset_letter, asset_paths in assets.items():
            letter_path = os.path.join(lb_path, asset_letter)

            if not os.path.isdir(letter_path):
                os.mkdir(letter_path)

            for asset_path in asset_paths:
                src = asset_path
                dst = os.path.join(letter_path, src.split("\\")[-1])

                copytree(src, dst)


def delete_data_json():
    for library, lb_path in lm.LIBRARIES.items():
        if library != "Material":
            continue

        if not os.path.isdir(lb_path):
            continue

        for letter in os.listdir(lb_path):
            letter_path = os.path.join(lb_path, letter)

            if os.path.isfile(letter_path):
                continue

            for asset in os.listdir(letter_path):
                asset_path = os.path.join(letter_path, asset)

                data_json = os.path.join(asset_path, "data.json")

                asset_data_tmp = {}

                if os.path.isfile(data_json):
                    # Get material data
                    asset_data_tmp = json.load(open(data_json))

                    if "material_data" in asset_data_tmp.keys():
                        material_data_tmp = asset_data_tmp["material_data"]

                        textures_data_reformat = {}

                        for tex_type, tex_data in material_data_tmp["textures"].items():
                            textures_data_reformat[tex_type] = tex_data["path"]

                        material_data_tmp["textures"] = textures_data_reformat

                        asset_data_tmp["material_data"] = material_data_tmp

                new_json_path = os.path.join(asset_path, "asset_data.json")

                if os.path.isfile(new_json_path):
                    os.remove(new_json_path)

                asset_data = {}

                asset_data_tmp["maya_file"] = ""

                for key in asset_data_tmp.keys():
                    if key == "import_file" and asset_data_tmp["import_file"].endswith(".ma"):
                        maya_file = os.path.join(asset_path, "maya", asset + ".ma")

                        if os.path.isfile(maya_file):
                            asset_data_tmp["maya_file"] = maya_file

                    if key in lm.ASSET_DATA_KEY_ORDER:
                        asset_data[key] = asset_data_tmp[key]

                with open(new_json_path, "w") as f:
                    try:
                        json.dump(lm.sort_asset_data(asset_data), f, indent=4)
                    except Exception:
                        continue

                print(asset_data["asset_name"])
                os.remove(data_json)


if __name__ == '__main__':
    lm.refresh_all_libraries()
