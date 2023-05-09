import importlib
import pymel.core as pm

from PySide2 import QtCore
from PySide2 import QtWidgets

from tools_core.lightboard.constants import constants as lb_const


class SceneListerWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(SceneListerWidget, self).__init__(*args, **kwargs)

        self.setObjectName("LightListerWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        pass

    def create_widgets(self):
        self.tv = QtWidgets.QTreeWidget()
        self.tv.setAlternatingRowColors(True)
        self.tv.setIndentation(15)
        self.tv.setColumnWidth(0, 200)
        self.tv.setHeaderHidden(True)

        for n in pm.ls(assemblies=1):
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, str(n))

            self.tv.addTopLevelItem(item)

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        main_layout.addWidget(self.tv)

    def create_connections(self):
        pass
