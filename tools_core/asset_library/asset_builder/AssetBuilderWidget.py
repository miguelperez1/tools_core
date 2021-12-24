import sys
import ctypes

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from tools_core.pyqt_commons import common_widgets as cw
from tools_core.asset_library import library_manager as lm
from tools_core.pipeline.Asset import Asset

ASSET_KEYS = {
    "asset_preview": True,
    "mesh": True,
    "tags": False
}


class AssetDataLineWidget(QtWidgets.QWidget):
    def __init__(self, label, key, fb=False, parent=None):
        super(AssetDataLineWidget, self).__init__(parent)
        self.label_text = label
        self.use_fb = fb
        self.key = key

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.lbl = QtWidgets.QLabel(self.label_text)
        self.le = QtWidgets.QLineEdit()

        if self.use_fb:
            self.fb_btn = cw.ImagePushButton(40, 40)
            file_browse_icon = QtGui.QIcon(':fileOpen.png')
            self.fb_btn.setIcon(file_browse_icon)

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        main_layout.addWidget(self.lbl)
        main_layout.addWidget(self.le)

        if self.use_fb:
            main_layout.addWidget(self.fb_btn)

    def create_connections(self):
        pass


class AssetBuilderWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AssetBuilderWidget, self).__init__(parent)

        self.setWindowTitle("Asset Builder")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("AssetBuilderWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.asset_name_widget = AssetDataLineWidget("Asset Name", key="asset_name")

        self.asset_library_cmbx = QtWidgets.QComboBox()
        self.asset_library_cmbx.addItems(lm.STD_LIBRARIES)

        self.asset_data_widgets = []

        for key, btn in ASSET_KEYS.items():
            widget = AssetDataLineWidget(" ".join(key.split("_")).title(), key, fb=btn)
            self.asset_data_widgets.append(widget)

        self.build_btn = QtWidgets.QPushButton("Build")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header_layout = QtWidgets.QHBoxLayout()

        header_layout.addWidget(self.asset_name_widget)
        header_layout.addWidget(self.asset_library_cmbx)

        main_layout.addLayout(header_layout)

        for widget in self.asset_data_widgets:
            main_layout.addWidget(widget)

        btn_layout = QtWidgets.QHBoxLayout()

        btn_layout.addStretch()
        btn_layout.addWidget(self.build_btn)

        main_layout.addLayout(btn_layout)

    def create_connections(self):
        # Asset name
        self.asset_name_widget.le.textChanged.connect(self.asset_name_check)

        # Build btn
        self.build_btn.clicked.connect(self.build_btn_callback)

        # Library cmbx
        self.asset_library_cmbx.currentIndexChanged.connect(self.library_callback)
        pass

    def build_btn_callback(self):
        asset_data = {}

        for key in lm.ASSET_DATA_KEY_ORDER:
            asset_data[key] = None

        for widget in self.asset_data_widgets:
            if widget.key == "tags":
                tags = []

                if "," in widget.le.text():
                    tags = widget.le.text().split(",")
                else:
                    tags = [widget.le.text()]

                asset_data["tags"] = tags

                continue

            asset_data[widget.key] = widget.le.text()

        asset_data["asset_name"] = self.asset_name_widget.le.text()

        asset_data["asset_type"] = self.asset_library_cmbx.currentText()

        asset = Asset.Asset(asset_data)

        asset.create_asset()

        self.asset_name_check()

    def asset_name_check(self):
        existing_assets = [a.lower() for a in
                           lm.get_library_data(self.asset_library_cmbx.currentText())["assets"].keys()]

        print(existing_assets)
        if self.asset_name_widget.le.text().lower() in [a.lower() for a in
                                                        lm.get_library_data(self.asset_library_cmbx.currentText())[
                                                            "assets"].keys()]:
            self.asset_name_widget.le.setStyleSheet("color: red")
            self.build_btn.setEnabled(False)

        else:
            self.asset_name_widget.le.setStyleSheet("")
            self.build_btn.setEnabled(True)

        pass

    def library_callback(self):
        self.asset_name_check()

        if self.asset_library_cmbx.currentText() not in ["Character", "Prop", "Transit", "Foliage"]:
            for widget in self.asset_data_widgets:
                if widget.key == "mesh":
                    widget.setHidden(True)
        else:
            for widget in self.asset_data_widgets:
                if widget.key == "mesh":
                    widget.setHidden(False)
