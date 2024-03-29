import importlib
import pymel.core as pm

from PySide2 import QtCore
from PySide2 import QtWidgets

from tools_core.lightboard.constants import constants as lb_const
from tools_core.lightboard.models.LightModel import LightModel
from tools_core.lightboard.models import Nodes
from tools_core.lightboard.widgets.common_widgets import common_widgets as cw

importlib.reload(lb_const)
importlib.reload(LightModel)
importlib.reload(Nodes)

ICON_SIZE = 33


def get_maya_widget(widget_name=None):
    widgets = {w.objectName(): w for w in QtWidgets.QApplication.allWidgets()}
    if widget_name:
        return widgets[widget_name]
    else:
        return widgets


def lgt_rig_graph_model():
    lgt_rig = pm.PyNode("lgt_rig|lights")

    if not lgt_rig:
        lgt_rig = pm.createNode("transform", name="lgt_rig")

    root_node = Nodes.TransformNode(lgt_rig)

    all_nodes = [root_node]

    def recursive_search(graph_node):
        if graph_node is None:
            return

        for child in pm.listRelatives(graph_node.m_node, c=1):
            if child is None:
                continue
            else:
                new_graph_node = None

                if pm.nodeType(child) == "transform" and len(pm.listRelatives(child, typ=lb_const.LIGHT_TYPES)) == 0:
                    new_graph_node = Nodes.TransformNode(pm.PyNode(child), graph_node)

                elif pm.nodeType(child) == "transform" and len(pm.listRelatives(child, typ=lb_const.LIGHT_TYPES)) > 0:
                    new_graph_node = Nodes.LightNode(pm.PyNode(child), graph_node)

                if new_graph_node is not None:
                    all_nodes.append(new_graph_node)

                recursive_search(new_graph_node)

    recursive_search(root_node)

    model = LightModel.LightboardGraphModel(root_node)

    return model, all_nodes


class LightListerWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(LightListerWidget, self).__init__(*args, **kwargs)

        self.setObjectName("LightListerWidget")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.setContentsMargins(0, 0, 0, 0)

    def create_actions(self):
        pass

    def create_widgets(self):
        self.light_graph_model, self.graph_nodes = lgt_rig_graph_model()

        self.tv = QtWidgets.QTreeView()
        self.tv.setModel(self.light_graph_model)
        self.tv.setAlternatingRowColors(True)
        self.tv.setIndentation(15)
        self.tv.setColumnWidth(0, 200)
        # self.tv.expandAll()
        self.tv.setColumnHidden(self.light_graph_model.columnCount(QtCore.QModelIndex()) - 1, True)

        self.create_light_btns()

    def create_light_btns(self):
        self.light_btns = []

        for light_type in lb_const.LIGHT_TYPES:

            if light_type in lb_const.ICONS.keys():
                btn = cw.ImagePushButton(ICON_SIZE, ICON_SIZE)

                btn.set_image(lb_const.ICONS[light_type])

                btn.setToolTip(light_type)

                self.light_btns.append(btn)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        create_lights_layout = QtWidgets.QHBoxLayout()

        for btn in self.light_btns:
            create_lights_layout.addWidget(btn)

        create_lights_layout.addStretch()

        move_to_camera_btn = cw.ImagePushButton(ICON_SIZE, ICON_SIZE)
        move_to_camera_btn.set_image("F:/share/tools/shelf_icons/move_toi.png")
        move_to_camera_btn.setToolTip("Match to Camera")

        create_lights_layout.addWidget(move_to_camera_btn)

        main_layout.addLayout(create_lights_layout)

        main_layout.addWidget(self.tv)

    def create_connections(self):
        self.tv.selectionModel().selectionChanged.connect(self.selection_changed)

    def selection_changed(self):
        pm.select(clear=1)

        for index in self.tv.selectedIndexes():
            node = index.internalPointer()

            pm.select(node._m_node)
