import sys
from functools import partial

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from tools_core.asset_library.asset_browser import AssetBrowserWidget
from tools_core.asset_library import library_manager as lm


class AssetBrowser(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AssetBrowser, self).__init__(parent)

        self.setWindowTitle("Window")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.dims = (1920, 1080)

        self.setMinimumSize(self.dims[0], self.dims[1])

        self.setObjectName("ExampleDialog")

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

            self.custom_actions[library] = {}

        # Model library custom actions
        model_action = QtWidgets.QAction("This is model")
        material_action = QtWidgets.QAction("This is mtl")
        after_action = QtWidgets.QAction("after")

        self.custom_actions["model"] = [
            {
                "action_object": model_action,
                "action_callback": partial(self.model_action_callback)
            },
            {
                "action_object": "separator",
                "action_callback": ""
            },
            {
                "action_object": after_action,
                "action_callback": partial(print, "hello")
            }
        ]

        self.custom_actions["material"] = [
            {
                "action_object": material_action,
                "action_callback": partial(self.material_action_callback)
            }
        ]

        self.asset_browser.add_actions_to_menus(self.custom_actions)

    def model_action_callback(self):
        print("this is model")

    def material_action_callback(self):
        print("mate")

    def create_widgets(self):
        self.asset_browser = AssetBrowserWidget.AssetBrowserWidget()

        self.test_btn = QtWidgets.QPushButton("Test")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.asset_browser)
        main_layout.addWidget(self.test_btn)

    def create_connections(self):
        pass

    def create_custom_connections(self):
        self.connection_data = [
            {
                "widget": "assets_tw",
                "signal": "itemClicked",
                "function": lambda: self.test_connection()
            }
        ]

        self.asset_browser.create_custom_connections(self.connection_data)

    def custom_browser_setup(self):
        # Custom Connections
        self.create_custom_connections()
        self.create_custom_actions()

    def test_connection(self):
        print("hello")


def main():
    app = QtWidgets.QApplication(sys.argv)

    app.setStyle(QtWidgets.QStyleFactory.create("fusion"))

    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(45, 45, 45))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(45, 45, 48))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(208, 208, 208))
    dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(45, 45, 48))
    app.setPalette(dark_palette)

    browser = AssetBrowser()
    browser.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
