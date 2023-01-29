from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from tools_core.lightboard.constants import constants as lb_const

import importlib

importlib.reload(lb_const)


class LightboardGraphModel(QtCore.QAbstractItemModel):

    def __init__(self, root, parent=None):
        super(LightboardGraphModel, self).__init__(parent)
        self.root_node = root

    def rowCount(self, parent):
        if not parent.isValid():
            parent_node = self.root_node
        else:
            parent_node = parent.internalPointer()

        return parent_node.child_count()

    def columnCount(self, parent):
        return 3

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.name()
            elif index.column() == 1:
                if node.node_type() in lb_const.LIGHT_TYPES:
                    return node.m_node.intensity.get()
            elif index.column() == 2:
                return node.node_type()


        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                type_info = node.node_type()

                icons = lb_const.ICONS

                if type_info in icons.keys():
                    icon_path = lb_const.ICONS[type_info]

                    return QtGui.QIcon(QtGui.QPixmap(icon_path))

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return ""
            elif section == 1:
                return "Intensity"

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def parent(self, index):
        node = index.internalPointer()

        parent_node = node.parent()

        if parent_node == self.root_node:
            return QtCore.QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def index(self, row, column, parent):
        if not parent.isValid():
            parent_node = self.root_node
        else:
            parent_node = parent.internalPointer()

        child_item = parent_node.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()
