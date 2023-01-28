from PySide2 import QtCore
from PySide2 import QtWidgets

import pymel.core as pm

from tools_core.lightboard.constants import constants as lb_const


def get_all_lights_in_scene():
    # TODO Refactor into another module
    # TODO USD Implementation

    lights = pm.ls(type=lb_const.LIGHT_TYPES)

    return lights


class LightListerWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(LightListerWidget, self).__init__(*args, **kwargs)

        self.setObjectName("SetsWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        pass

    def create_widgets(self):
        # REPLACE WITH MODEL ONCE LIGHTS MODEL IMPLEMENTED

        data = [str(l) for l in get_all_lights_in_scene()]

        model = QtCore.QStringListModel(data)

        self.cmbx = QtWidgets.QComboBox()
        # self.cmbx.addItems([str(s) for s in get_all_lights_in_scene()])
        self.cmbx.setModel(model)

        self.tv = QtWidgets.QTreeView()
        self.tv.setModel(model)

        self.lv = QtWidgets.QListView()
        self.lv.setModel(model)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.cmbx)
        main_layout.addWidget(self.tv)
        main_layout.addWidget(self.lv)

    def create_connections(self):
        pass
