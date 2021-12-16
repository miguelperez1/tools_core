import os
from shutil import copytree
from datetime import datetime


def create_dirs_from_dict(d, asset_root, parent=None):
    if "subfolders" in d.keys():
        if d['folder_name'] == "top_level":
            _ = [create_dirs_from_dict(a, asset_root, parent=asset_root) for a in d['subfolders']]
        else:
            path = os.path.join(parent, d['folder_name'])

            if not os.path.isdir(path):
                os.mkdir(path)

            _ = [create_dirs_from_dict(a, asset_root, parent=path) for a in d['subfolders']]
    else:
        path = os.path.join(parent, d['folder_name'])

        if not os.path.isdir(path):
            os.mkdir(path)


def create_tools_backup(package):
    tools_root = r"F:\share\tools"

    if package not in ["tools_core", "maya_core", "houdini_core"]:
        return

    package_src = os.path.join(tools_root, package)

    if not os.path.isdir(package_src):
        return

    backup_root = r"F:\share\tools\backup"

    package_backup_root = os.path.join(backup_root, package)

    if not os.path.isdir(package_backup_root):
        os.mkdir(package_backup_root)

    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")

    backup_dst = os.path.join(package_backup_root, dt_string)

    copytree(package_src, backup_dst)


def backup_tools():
    for package in ["tools_core", "maya_core", "houdini_core"]:
        create_tools_backup(package)


if __name__ == '__main__':
    backup_tools()
