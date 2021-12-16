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

logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(10)


# TODO CBB Autocompleter


class LogLE(QtWidgets.QLineEdit):
    def __init__(self):
        super(LogLE, self).__init__()

        self.setReadOnly(True)

    def log(self, msg, level):
        options = {
            "info": "lime-green",
            "debug": "yellow",
            "error": "red"
        }

        if level not in options.keys():
            return

        getattr(logger, level)("%s", msg)

        self.setText(msg)
        self.setStyleSheet("color: {}".format(options[level]))


class AssetTreeWidget(QtWidgets.QTreeWidget):
    tags_updated = QtCore.Signal()

    def onTreeWidgetItemDoubleClicked(self, item, column):
        # Only allow the tags column to be edited
        if column == 2:
            self.editItem(item, column)
        else:
            return

    def __init__(self):
        super(AssetTreeWidget, self).__init__()
        self.header_item = QtWidgets.QTreeWidgetItem(["Preview", "Name", "Tags"])
        self.setHeaderItem(self.header_item)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.itemDoubleClicked.connect(self.onTreeWidgetItemDoubleClicked)
        self.setAlternatingRowColors(True)

        self.asset_items = []

        self.create_all_asset_items()

        self.itemChanged.connect(self.update_tags)

    def create_all_asset_items(self):
        self.blockSignals(True)

        self.clear()
        self.asset_items = []

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
                asset_item.setFlags(asset_item.flags() | QtCore.Qt.ItemIsEditable)

                item_font = QtGui.QFont()
                item_font.setPointSize(10)
                asset_item.setFont(1, item_font)
                asset_item.setFont(2, item_font)

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

    def refresh_assets(self, libraries, tags=None, regex=None):
        self.blockSignals(True)

        for asset_item in self.asset_items:
            if asset_item.library not in libraries:
                asset_item.setHidden(True)

            elif asset_item.library in libraries:
                if tags:
                    filter_tags_set = set(tags)
                    asset_tags_set = set(asset_item.asset_data["tags"])

                    if len(filter_tags_set.intersection(asset_tags_set)) > 0:
                        if regex:
                            if not regex.search(asset_item.asset_data["asset_name"].lower()):
                                asset_item.setHidden(True)
                            else:
                                asset_item.setHidden(False)
                        else:
                            asset_item.setHidden(False)
                    else:
                        asset_item.setHidden(True)
                elif not tags:
                    if regex:
                        if not regex.search(asset_item.asset_data["asset_name"].lower()):
                            asset_item.setHidden(True)
                        else:
                            asset_item.setHidden(False)
                    else:
                        asset_item.setHidden(False)

        self.blockSignals(False)

    def update_tags(self, item, column):
        asset_data = item.asset_data

        if not lm.get_library_data(asset_data["asset_type"]):
            return

        lm.update_asset_tags(asset_data["asset_type"], asset_data["asset_name"], str(item.text(2)), override=True)

        new_asset_data = lm.get_asset_data(asset_data["asset_type"], asset_data["asset_name"])

        item.asset_data = new_asset_data

        item.setText(2, ",".join(new_asset_data["tags"]))

        lm.create_library_data(item.library)

        self.tags_updated.emit()


class AssetBrowserWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, margin=15, dims=(1280, 720)):
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
        self.open_asset_explorer_action = QtWidgets.QAction("Open in Explorer")
        self.copy_root_path_action = QtWidgets.QAction("Copy root path")

        self.library_menu_actions = {}

        for library in lm.LIBRARIES.keys():
            self.library_menu_actions[library] = []

        self.library_menu_actions["all"] = [
            self.open_asset_explorer_action,
            self.copy_root_path_action
        ]

        self.open_library_explorer_action = QtWidgets.QAction("Open in Explorer")

    def create_widgets(self):
        # Widgets
        self.search_lbl = QtWidgets.QLabel("Search")
        self.search_le = QtWidgets.QLineEdit()

        self.libraries_tw = QtWidgets.QTreeWidget()
        libraries_header_item = QtWidgets.QTreeWidgetItem(["Libraries"])
        self.libraries_tw.setHeaderItem(libraries_header_item)

        self.libraries_tw.setMaximumWidth(self.dims[0] * .25)
        self.libraries_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.refresh_btn = cw.ImagePushButton(30, 30)
        self.refresh_btn.set_image(r"F:\share\tools\tools_core\tools_core\pyqt_commons\icons\reload.png")

        self.assets_tw = AssetTreeWidget()
        self.assets_tw.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.assets_tw.setColumnWidth(0, self.dims[0] * .225)

        self.populate_libraries_tw()

        self.asset_counter_le = QtWidgets.QLineEdit()
        self.asset_counter_le.setReadOnly(True)
        self.asset_counter_le.setMaximumWidth(self.dims[0] * .0325)
        self.asset_counter_le.setAlignment(QtCore.Qt.AlignRight)

        self.status_le = LogLE()

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
        main_layout.setContentsMargins(self.margin, self.margin * .75, self.margin, self.margin)
        main_layout.setSpacing(self.margin)

        search_layout = QtWidgets.QHBoxLayout()

        search_layout.addWidget(self.search_lbl)
        search_layout.addWidget(self.search_le)
        search_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(search_layout)

        main_layout.addWidget(cw.QHLine())

        tws_layout = QtWidgets.QHBoxLayout()

        tws_layout.addWidget(self.libraries_tw)
        tws_layout.addWidget(self.assets_tw)

        main_layout.addLayout(tws_layout)

        status_layout = QtWidgets.QHBoxLayout()

        status_layout.addWidget(self.status_le)
        status_layout.addWidget(self.asset_counter_le)

        main_layout.addLayout(status_layout)

    def create_connections(self):
        # Actions
        self.open_asset_explorer_action.triggered.connect(self.open_explorer_action_callback)
        self.open_library_explorer_action.triggered.connect(self.open_library_explorer_action_callback)

        # Menus
        self.assets_tw.customContextMenuRequested.connect(self.show_assets_tw_context_menu)
        self.libraries_tw.customContextMenuRequested.connect(self.show_libraries_tw_context_menu)

        # Misc
        self.search_le.textChanged.connect(self.refresh_assets)
        self.refresh_btn.clicked.connect(self.refresh_all)
        self.libraries_tw.itemSelectionChanged.connect(self.refresh_assets)

        # Custom
        self.assets_tw.tags_updated.connect(self.populate_libraries_tw)

    def create_custom_connections(self, connections):
        for connection in connections:
            widget = getattr(self, connection["widget"])

            if not widget:
                logger.error("%s not found", connection["widget"])
                continue

            signal = getattr(widget, connection["signal"])

            if not signal:
                logger.error("Signal %s for %s not found", connection["signal"], connection["widget"])
                continue

            signal.connect(connection["function"])

    def populate_libraries_tw(self):
        current_selection = []

        if self.libraries_tw.selectedItems():
            current_selection = [i.text(0) for i in self.libraries_tw.selectedItems()]

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

            if library in current_selection:
                library_item.setSelected(True)

            for tag in library_data["tags"]:
                tag_item = QtWidgets.QTreeWidgetItem()
                tag_item.library = library
                tag_item.is_tag = True

                tag_item.setText(0, tag)

                library_item.addChild(tag_item)

                if tag in current_selection:
                    tag_item.setSelected(True)

        self.libraries_tw.blockSignals(False)

        self.refresh_assets()

    def refresh_assets(self):
        current_selection = self.libraries_tw.selectedItems()

        if not current_selection:
            return

        tags = []
        libraries = []
        regex = None

        for item in current_selection:
            if item.is_tag and item.text(0) not in tags:
                tags.append(item.text(0))

            if item.library not in libraries:
                libraries.append(item.library)

        if self.search_le.text():
            regex = re.compile(self.search_le.text().lower())

        self.assets_tw.refresh_assets(libraries, tags, regex)

        asset_count = len(lm.get_library_data(self.libraries_tw.selectedItems()[0].library)["assets"].keys())

        self.asset_counter_le.setText(str(asset_count))

    def show_assets_tw_context_menu(self, eventPosition):
        asset_item = self.assets_tw.itemAt(eventPosition)

        context_menu = self.library_menus[asset_item.library]

        for action in self.library_menu_actions[asset_item.library]:
            if hasattr(action, "action_asset_data_conditions"):
                condition_keys = action.action_asset_data_conditions

                is_valid = True

                for condition_key in condition_keys:
                    if not asset_item.asset_data[condition_key]:
                        is_valid = False
                        break
                    elif asset_item.asset_data[condition_key] and action not in context_menu.actions():
                        is_valid = True

                if not is_valid:
                    context_menu.removeAction(action)
                else:
                    context_menu.addAction(action)

        _ = context_menu.exec_(self.assets_tw.mapToGlobal(eventPosition))

    def show_libraries_tw_context_menu(self, eventPosition):
        context_menu = QtWidgets.QMenu()

        context_menu.addAction(self.open_library_explorer_action)

        _ = context_menu.exec_(self.libraries_tw.mapToGlobal(eventPosition))

    def open_explorer_action_callback(self):
        if not self.assets_tw.selectedItems():
            return

        current_library = self.assets_tw.selectedItems()[0].asset_data["asset_type"]

        for item in self.assets_tw.selectedItems():
            if item.asset_data["asset_type"] in lm.STD_LIBRARIES:
                subprocess.Popen('explorer "{}"'.format(item.asset_data["asset_path"]))
            else:
                subprocess.Popen('explorer "{}"'.format(lm.LIBRARIES[current_library]))

    def open_library_explorer_action_callback(self):
        if not self.libraries_tw.selectedItems():
            return

        for item in self.libraries_tw.selectedItems():
            subprocess.Popen('explorer "{}"'.format(lm.LIBRARIES[item.library]))

    def add_actions_to_menus(self, actions_data):
        registered_actions = []
        for library, actions in actions_data.items():
            menu = self.library_menus[library]

            for action_data in actions:
                action_object = action_data["action_object"]

                if action_object == "separator":
                    menu.addSeparator()
                    continue

                action_callback = action_data["action_callback"]

                if "action_asset_data_conditions" in action_data.keys():
                    action_object.action_asset_data_conditions = action_data["action_asset_data_conditions"]

                if action_object not in registered_actions:
                    logger.debug("Connecting action %s to %s", action_object.text(), action_callback)

                    action_object.triggered.connect(action_callback)
                    registered_actions.append(action_object)

                self.library_menu_actions[library].append(action_object)

                menu.addAction(action_object)

    def log(self, msg, level):
        self.status_le.log(msg, level)

    def refresh_all(self):
        lm.refresh_all_libraries()
        self.assets_tw.create_all_asset_items()
        self.populate_libraries_tw()
