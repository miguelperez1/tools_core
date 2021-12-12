import os
import re
from functools import partial
import subprocess
import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from tools_core.asset_library import library_manager as lm
from tools_core.pyqt_commons import common_widgets as cw

# TODO Filter by search
# TODO Edit tags functionality

logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(10)


class AssetTreeWidget(QtWidgets.QTreeWidget):
    tags_updated = QtCore.Signal()

    def __init__(self):
        super(AssetTreeWidget, self).__init__()
        self.header_item = QtWidgets.QTreeWidgetItem(["Preview", "Name", "Tags"])
        self.setHeaderItem(self.header_item)

        self.asset_items = []

        self.create_all_asset_items()

    def create_all_asset_items(self):
        self.blockSignals(True)

        for library in lm.LIBRARIES.keys():
            library_data = lm.get_library_data(library)

            if not library_data:
                continue

            for asset in sorted(library_data["assets"].keys(), key=lambda a: a.lower()):
                asset_data = library_data["assets"][asset]
                asset_item = QtWidgets.QTreeWidgetItem()
                asset_item.asset_data = asset_data
                asset_item.library = library
                asset_preview = asset_data["asset_preview"]

                asset_item.setText(1, asset)

                if "tags" in asset_data.keys():
                    asset_item.setText(2, ",".join(asset_data["tags"]))

                preview_widget = cw.PreviewLabel()
                preview_widget.setFixedSize(160, 160)

                if os.path.isfile(asset_preview):
                    preview_widget.set_image(asset_preview, 150)
                else:
                    preview_widget.set_default()

                self.addTopLevelItem(asset_item)

                self.setItemWidget(asset_item, 0, preview_widget)

                asset_item.setHidden(True)

                self.asset_items.append(asset_item)

        self.blockSignals(False)

    def refresh_assets(self, libraries, tags=None):
        self.blockSignals(True)

        for asset_item in self.asset_items:
            if asset_item.library not in libraries:
                asset_item.setHidden(True)

            elif asset_item.library in libraries and not tags:
                asset_item.setHidden(False)

            elif asset_item.library in libraries and tags:
                # TODO This is broken
                filter_tags_set = set(tags)
                asset_tags_set = set(asset_item.asset_data["tags"])

                if len(filter_tags_set.intersection(asset_tags_set)) > 0:
                    asset_item.setHidden(False)
                else:
                    asset_item.setHidden(True)

        self.blockSignals(False)


class AssetBrowserWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, margin=30, dims=(1280, 720)):
        super(AssetBrowserWidget, self).__init__(parent)
        self.margin = margin
        dims_margin = 0.95
        self.dims = (dims[0] * dims_margin, dims[1] * dims_margin)

        self.setMinimumSize(self.dims[0], self.dims[1])

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        self.open_explorer_action = QtWidgets.QAction("Open in Explorer")
        self.copy_root_path_action = QtWidgets.QAction("Copy root path")

        self.library_menu_actions = {}

        for library in lm.LIBRARIES.keys():
            self.library_menu_actions[library] = []

        self.library_menu_actions["all"] = [
            self.open_explorer_action,
            self.copy_root_path_action
        ]

    def create_widgets(self):
        # Widgets
        self.search_lbl = QtWidgets.QLabel("Search")
        self.search_le = QtWidgets.QLineEdit()

        self.libraries_tw = QtWidgets.QTreeWidget()
        libraries_header_item = QtWidgets.QTreeWidgetItem(["Libraries"])
        self.libraries_tw.setHeaderItem(libraries_header_item)

        self.libraries_tw.setMaximumWidth(self.dims[0] * .25)

        self.assets_tw = AssetTreeWidget()
        self.assets_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.populate_libraries_tw()

        # Context Menus
        self.library_menus = {}

        for library in lm.LIBRARIES.keys():
            if not lm.get_library_data(library):
                continue

            menu = QtWidgets.QMenu()
            menu.library = library

            # Add Common Actions
            for action in self.library_menu_actions["all"]:
                menu.addAction(action)

            menu.addSeparator()

            for action in self.library_menu_actions[library]:
                if action == "separator":
                    menu.addSeparator()
                else:
                    menu.addAction(action)

            self.library_menus[library] = menu

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(self.margin, self.margin, self.margin, self.margin)

        search_layout = QtWidgets.QHBoxLayout()
        search_layout.addWidget(self.search_lbl)
        search_layout.addWidget(self.search_le)

        main_layout.addLayout(search_layout)

        tws_layout = QtWidgets.QHBoxLayout()

        tws_layout.addWidget(self.libraries_tw)
        tws_layout.addWidget(self.assets_tw)

        main_layout.addLayout(tws_layout)

    def create_connections(self):
        self.libraries_tw.itemSelectionChanged.connect(self.refresh_assets)
        self.open_explorer_action.triggered.connect(self.open_explorer_action_callback)

        self.assets_tw.customContextMenuRequested.connect(self.show_assets_tw_context_menu)

    def create_custom_connections(self, connections):
        for connection in connections:
            widget = getattr(self, connection["widget"])
            signal = getattr(widget, connection["signal"])
            signal.connect(connection["function"])

    def populate_libraries_tw(self):
        self.libraries_tw.blockSignals(True)
        self.libraries_tw.clear()

        for library in lm.LIBRARIES.keys():
            library_data = lm.get_library_data(library)

            if not library_data:
                continue

            library_item = QtWidgets.QTreeWidgetItem()
            library_item.setText(0, library)
            library_item.library = library
            library_item.is_tag = False

            self.libraries_tw.addTopLevelItem(library_item)

            for tag in library_data["tags"]:
                tag_item = QtWidgets.QTreeWidgetItem()
                tag_item.library = library
                tag_item.is_tag = True

                tag_item.setText(0, tag)

                library_item.addChild(tag_item)

        self.libraries_tw.blockSignals(False)

    def refresh_assets(self):
        current_selection = self.libraries_tw.selectedItems()

        if not current_selection:
            return

        tags = []
        libraries = []

        for item in current_selection:
            if item.is_tag and item.text(0) not in tags:
                tags.append(item.text(0))

            if item.library not in libraries:
                libraries.append(item.library)

        logger.debug((libraries, tags))

        self.assets_tw.refresh_assets(libraries, tags)

    def show_assets_tw_context_menu(self, eventPosition):
        asset_item = self.assets_tw.itemAt(eventPosition)

        context_menu = self.library_menus[asset_item.library]

        action = context_menu.exec_(self.assets_tw.mapToGlobal(eventPosition))

    def open_explorer_action_callback(self):
        if not self.assets_tw.selectedItems():
            return

        current_library = self.libraries_tw.selectedItems()[0].library

        for item in self.assets_tw.selectedItems():
            asset = item.text(1)

            if current_library in ['material', 'model', 'rigs', 'plants']:
                subprocess.Popen('explorer "{}"'.format(os.path.join(lm.LIBRARIES[current_library], asset)))
            else:
                subprocess.Popen('explorer "{}"'.format(lm.LIBRARIES[current_library]))

    def add_actions_to_menus(self, actions_data):
        for library, actions in actions_data.items():
            menu = self.library_menus[library]

            for action_data in actions:
                action_object = action_data["action_object"]
                action_callback = action_data["action_callback"]

                if action_object == "separator":
                    menu.addSeparator()
                    continue

                action_object.triggered.connect(action_callback)

                menu.addAction(action_object)
