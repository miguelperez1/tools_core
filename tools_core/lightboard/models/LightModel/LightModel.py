from PySide2 import QtCore
from PySide2 import QtGui

from tools_core.lightboard.constants import constants as lb_const

from tools_core.lightboard.models import Nodes

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
        return 10

    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.name()
            elif index.column() == 2:
                if node.node_type() in lb_const.LIGHT_CLASS["arnold"]:
                    return float(node.m_node.exposure.get())
                elif node.node_type() == "directionalLight":
                    return float(node.m_node.aiExposure.get())
                elif node.node_type() in lb_const.LIGHT_CLASS["maya"]:
                    return float(node.m_node.intensity.get())
            elif index.column() == 3:
                if node.node_type() in lb_const.LIGHT_CLASS["vray"]:
                    return str(["%.2f" % v for v in node.m_node.lightColor.get()])
                if node.node_type() in lb_const.LIGHT_CLASS["maya"] or node.node_type() in lb_const.LIGHT_CLASS[
                    "arnold"]:
                    return str(["%.2f" % v for v in node.m_node.color.get()])
            elif index.column() == self.columnCount(QtCore.QModelIndex()) - 1:
                return node.node_type()

        if role == QtCore.Qt.TextAlignmentRole and index.column == 1:
            return QtCore.Qt.AlignHCenter

        if role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(40, 30)

        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                type_info = node.node_type()

                icons = lb_const.ICONS

                if type_info in icons.keys():
                    icon_path = lb_const.ICONS[type_info]

                    return QtGui.QIcon(QtGui.QPixmap(icon_path))

        if role == QtCore.Qt.CheckStateRole and index.column() == 1:
            return QtCore.Qt.Checked if node.m_node.visibility.get() else QtCore.Qt.Unchecked
        if role == QtCore.Qt.CheckStateRole and index.column() == 4:
            if hasattr(node.m_node, "camera"):
                return QtCore.Qt.Checked if not bool(node.m_node.camera.get()) else QtCore.Qt.Unchecked
            if hasattr(node.m_node, "aiCamera"):
                return QtCore.Qt.Checked if not bool(node.m_node.aiCamera.get()) else QtCore.Qt.Unchecked

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            node = index.internalPointer()

            if role == QtCore.Qt.EditRole:

                if index.column() == 0:
                    node.set_name(value)

                if index.column() == 2 and node.node_type() in lb_const.LIGHT_TYPES:
                    node.set_intensity(value)

                if index.column() == 3 and node.node_type() in lb_const.LIGHT_TYPES:
                    node.set_color(value)

                self.dataChanged.emit(index, index)

            if role == QtCore.Qt.CheckStateRole:
                if index.column() == 1:
                    node.m_node.visibility.set(bool(value))

                    self.dataChanged.emit(index, index)

                if index.column() == 4:
                    if hasattr(node.m_node, "camera"):
                        node.m_node.camera.set(not bool(value))

                        self.dataChanged.emit(index, index)

                    elif hasattr(node.m_node, "aiCamera"):
                        node.m_node.aiCamera.set(not bool(value))

                        self.dataChanged.emit(index, index)

                return True

        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return ""
            elif section == 1:
                return "Enabled"
            elif section == 2:
                return "Exposure"
            elif section == 3:
                return "Color:"
            elif section == 4:
                return "Invisible"
            elif section == self.columnCount(QtCore.QModelIndex()) - 1:
                return "Light Type"

    def flags(self, index):
        node = index.internalPointer()

        flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

        if index.column() == 1 or index.column() == 4:
            flags |= QtCore.Qt.ItemIsUserCheckable
        else:
            flags |= QtCore.Qt.ItemIsEditable

        return flags

    def parent(self, index):
        node = self.get_node(index)
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

    def get_node(self, index):
        if index.isValid():
            node = index.internalPointer()

            if node:
                return node

        return self.root_node

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):

        parent_node = self.get_node(parent)

        self.beginInsertRows(parent, position, position + rows - 1)

        for row in range(rows):
            child_count = parent_node.child_count()

            child_node = Nodes.Node("untitled" + str(child_count))
            success = parent_node.insert_child(position, child_node)

        self.endInsertRows()

        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        parent_node = self.get_node(parent)

        self.beginRemoveRows(parent, position, position + rows - 1)

        for row in range(rows):
            success = parent_node.remove_child(position)

        self.endRemoveRows()

        return success
