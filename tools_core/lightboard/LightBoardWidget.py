import logging
import importlib

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from tools_core.lightboard.widgets.LightListerWidget import LightListerWidget
from tools_core.lightboard.widgets.RenderLayersWidget import RenderLayersWidget
from tools_core.lightboard.widgets.PropertiesWidget import PropertiesWidget
from tools_core.lightboard.widgets.SceneListerWidget import SceneListerWidget

importlib.reload(LightListerWidget)
importlib.reload(RenderLayersWidget)
importlib.reload(PropertiesWidget)
importlib.reload(SceneListerWidget)

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

        self.setMinimumSize(2000, 750)

    def create_actions(self):
        pass

    def create_widgets(self):
        # self.create_menu_bar()

        self.scene_lister_widget = SceneListerWidget.SceneListerWidget()

        self.render_layers_widget = RenderLayersWidget.RenderLayersWidget()

        self.ll_widget = LightListerWidget.LightListerWidget()

        self.properties_widget = PropertiesWidget.PropertiesWidget()
        self.properties_widget.setModel(self.ll_widget.light_graph_model)

        QtCore.QObject.connect(
            self.ll_widget.tv.selectionModel(),
            QtCore.SIGNAL("currentChanged(QModelIndex, QModelIndex)"),
            self.properties_widget.set_selection
        )

        self.console_tbw = QtWidgets.QTabWidget()
        self.console_tbw.setMovable(True)

        self.console_tbw.addTab(self.scene_lister_widget, "Scene")
        self.console_tbw.addTab(self.ll_widget, "Lights")
        self.console_tbw.addTab(QtWidgets.QWidget(), "Modifiers")
        self.console_tbw.addTab(QtWidgets.QWidget(), "Render Settings")
        self.console_tbw.addTab(QtWidgets.QWidget(), "AOVs")

        self.console_tbw.setCurrentIndex(1)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        # main_layout.addWidget(self.menu_bar)
        # main_layout.addWidget(self.render_layers_widget)

        tab_properties_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        tab_properties_splitter.addWidget(self.render_layers_widget)
        tab_properties_splitter.addWidget(self.console_tbw)
        tab_properties_splitter.addWidget(self.properties_widget)

        main_layout.addWidget(tab_properties_splitter)

    def create_connections(self):
        pass

    def create_menu_bar(self):
        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_bar.setContentsMargins(0, 0, 0, 0)

        file_action = self.menu_bar.addMenu("File")
