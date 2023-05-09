import importlib
import pymel.core as pm

from PySide2 import QtCore
from PySide2 import QtWidgets

from tools_core.lightboard.constants import constants as lb_const
from tools_core.lightboard.models.LightModel import LightModel
from tools_core.lightboard.models import Nodes

importlib.reload(lb_const)
importlib.reload(LightModel)
importlib.reload(Nodes)


def get_maya_widget(widget_name=None):
    widgets = {w.objectName(): w for w in QtWidgets.QApplication.allWidgets()}
    if widget_name:
        return widgets[widget_name]
    else:
        return widgets


def modifiers_graph_model():
    modifiers_n = pm.PyNode("lgt_rig|modifiers")

    if not modifiers_n:
        modifiers_n = pm.createNode("transform", name="modifiers", parent="lgt_rig")

    root_node = Nodes.TransformNode(modifiers_n)

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

        self.set_widgets()

    def set_widgets(self):
        pass
        # for i in range(self.tv.model().rowCount(QtCore.QModelIndex())):
        #     item = self.light_graph_model.index(i, 1, QtCore.QModelIndex())
        #
        #     self.tv.setIndexWidget(item, QtWidgets.QCheckBox(""))
        #
        #     for sub_row in range(self.light_graph_model.rowCount(item)):
        #         sub_item = self.light_graph_model.index(sub_row, 1, item)
        #
        #         self.tv.setIndexWidget(sub_item, QtWidgets.QCheckBox(""))

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        main_layout.addWidget(self.tv)

    def create_connections(self):
        self.tv.selectionModel().selectionChanged.connect(self.selection_changed)

    def selection_changed(self):
        pm.select(clear=1)

        for index in self.tv.selectedIndexes():
            node = index.internalPointer()

            pm.select(node._m_node)
