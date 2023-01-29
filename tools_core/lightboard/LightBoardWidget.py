import logging
import importlib

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from tools_core.lightboard.widgets.LightListerWidget import LightListerWidget
importlib.reload(LightListerWidget)

logger = logging.getLogger(__name__)
logger.setLevel(10)


class LightBoardWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LightBoardWidget, self).__init__(parent)

        self.setObjectName("LightBoardWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.setMinimumSize(1500, 500)

    def create_actions(self):
        pass

    def create_widgets(self):
        pass
        self.ll_widget = LightListerWidget.LightListerWidget()

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.ll_widget)

    def create_connections(self):
        pass
