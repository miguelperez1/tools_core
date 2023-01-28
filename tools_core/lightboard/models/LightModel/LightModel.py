from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui


class Node(object):

    def __init__(self, name, parent=None):
        self._name = name
        self._children = []
        self._parent = parent

        if parent is not None:
            parent.add_child(self)

    def add_child(self, child):
        self._children.append(child)

    def name(self):
        return self._name

    def child(self, row):
        return self._children[row]

    def child_count(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def log(self, tab_level=-1):
        output = ""
        tab_level += 1

        for i in range(tab_level):
            output += "\t"

        output += self._name + "\n"

        for child in self._children:
            output += child.log(tab_level)

        tab_level -= 1

        return output

    def __repr__(self):
        return self.log()


class LightGraphModel(QtCore.QAbstractItemModel):

    def __init__(self, root, parent=None):
        super(LightGraphModel, self).__init__(parent)
        self.root_node = root

    def rowCount(self, parent):
        pass

    def columnCount(self, parent):
        pass

    def data(self, index, role):
        pass

    def headerData(self, section, orientation, role):
        pass

    def flags(self, index):
        pass

    def parent(self, index):
        node = index.internalPointer()

        parent_node = node.parent()

        if parent_node == self.root_node:
            return QtCore.QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def index(self, row, column, parent):
        pass
