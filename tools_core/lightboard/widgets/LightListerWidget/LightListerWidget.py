import importlib
import pymel.core as pm

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from tools_core.lightboard.constants import constants as lb_const
from tools_core.lightboard.models.LightModel import LightModel
from tools_core.lightboard.models.LightModel import Nodes

importlib.reload(lb_const)
importlib.reload(LightModel)
importlib.reload(Nodes)


def lgt_rig_graph_model():
    lgt_rig = pm.PyNode("lgt_rig")

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
        # REPLACE WITH MODEL ONCE LIGHTS MODEL IMPLEMENTED

        self.light_graph_model, self.graph_nodes = lgt_rig_graph_model()

        # print(model.root_node.child_count())

        self.cmbx = QtWidgets.QComboBox()
        # self.cmbx.addItems([str(s) for s in get_all_lights_in_scene()])
        self.cmbx.setModel(self.light_graph_model)

        self.tv = QtWidgets.QTreeView()
        self.tv.setModel(self.light_graph_model)
        self.tv.setAlternatingRowColors(True)
        self.tv.setIndentation(15)

        self.lv = QtWidgets.QListView()
        self.lv.setModel(self.light_graph_model)

        self.set_widgets()

    def set_widgets(self):
        pass

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.cmbx)
        main_layout.addWidget(self.tv)
        main_layout.addWidget(self.lv)

    def create_connections(self):
        pass
