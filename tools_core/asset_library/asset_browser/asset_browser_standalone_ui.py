import os
import sys
import ctypes
import logging
from functools import partial

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from tools_core.asset_library.asset_browser import AssetBrowserWidget
from tools_core.asset_library import library_manager as lm
from tools_core.pyqt_commons import common_widgets as cw

logging.basicConfig()

logger = logging.getLogger(__name__)


class AssetBrowser(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AssetBrowser, self).__init__(parent)

        self.setWindowTitle("Asset Browser")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.dims = (1920, 1080)

        self.setMinimumSize(self.dims[0], self.dims[1])

        self.setObjectName("AssetBrowser")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.custom_browser_setup()

    def create_actions(self):
        pass

    def create_custom_actions(self):
        self.custom_actions = {}

        for library in lm.LIBRARIES.keys():
            if not lm.get_library_data(library):
                continue

            self.custom_actions[library] = []

        # Actions
        open_with_maya_action = QtWidgets.QAction("Open with Maya")

        send_to_nuke_action = QtWidgets.QAction("Send to Nuke")

        # Datas

        for std_library in lm.STD_LIBRARIES:
            if std_library not in self.custom_actions.keys():
                continue

            action_datas = [
                {
                    "action_object": open_with_maya_action,
                    "action_callback": partial(self.open_with_maya_action_callback),
                    "action_asset_data_conditions": ["maya_file"]
                }
            ]

            self.custom_actions[std_library].extend(action_datas)

        for img_library in lm.IMG_LIBRARIES:
            if img_library not in self.custom_actions.keys():
                continue

            action_datas = [
                {
                    "action_object": send_to_nuke_action,
                    "action_callback": partial(self.send_to_nuke_action_callback)
                }
            ]

            self.custom_actions[img_library].extend(action_datas)

        self.asset_browser.add_actions_to_menus(self.custom_actions)

    def create_widgets(self):
        self.asset_browser = AssetBrowserWidget.AssetBrowserWidget()

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.asset_browser)

    def create_connections(self):
        pass

    def create_custom_connections(self):
        connection_data = []

        self.asset_browser.create_custom_connections(connection_data)

    def custom_browser_setup(self):
        self.create_custom_connections()
        self.create_custom_actions()

    def open_with_maya_action_callback(self):
        items = self.asset_browser.assets_tw.selectedItems()

        if not items:
            return

        for item in items:
            os.startfile(item.asset_data["maya_file"])

    def send_to_nuke_action_callback(self):
        print("send_to_nuke_action_callback")

def main():
    appid = "tools_core.asset_library.asset_browser.asset_browser_standalone_ui"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    app = QtWidgets.QApplication(sys.argv)

    app_icon = QtGui.QIcon(r"F:\share\tools\tools_core\tools_core\asset_library\asset_browser\icons\browser.png")

    app.setWindowIcon(app_icon)

    app.setStyle(QtWidgets.QStyleFactory.create("fusion"))

    app.setPalette(cw.DarkPalette())

    browser = AssetBrowser()
    browser.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
