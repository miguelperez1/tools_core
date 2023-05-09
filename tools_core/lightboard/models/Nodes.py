from tools_core.lightboard.constants import constants as lb_const


class Node(object):

    def __init__(self, m_node, parent=None):
        self._m_node = m_node
        self._name = self._m_node.name()
        self._children = []
        self._parent = parent

        if parent is not None:
            parent.add_child(self)

    def node_type(self):
        try:
            shape = self._m_node.getShape()
        except AttributeError:
            shape = None

        if not shape:
            node_type = self._m_node.nodeType()
        else:
            node_type = shape.nodeType()

        return node_type

    def add_child(self, child):
        if child not in self._children:
            self._children.append(child)
            child._parent = self

    def insert_child(self, position, child):
        if position < 0 or position < len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self

        return True

    def remove_child(self, position):
        if position < 0 or position < len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None

        return True

    def name(self):
        return self._name

    def set_name(self, name):
        self._name = name
        self._m_node.rename(name)

    def child(self, row):
        return self._children[row]

    def child_count(self):
        return len(self._children)

    def parent(self):
        return self._parent

    @property
    def m_node(self):
        return self._m_node

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def log(self):
        pass


class LightNode(Node):
    def __init__(self, m_node, parent=None):
        super(LightNode, self).__init__(m_node, parent)

    def set_intensity(self, value):
        if self.node_type() in lb_const.LIGHT_CLASS["arnold"]:
            self.m_node.exposure.set(float(value))
        elif self.node_type() == "directionalLight":
            self.m_node.aiExposure.set(float(value))
        else:
            self._m_node.intensity.set(float(value))

    def set_color(self, value):
        self._m_node.color.set(value)


class TransformNode(Node):
    def __init__(self, m_node, parent=None):
        super(TransformNode, self).__init__(m_node, parent)


class CameraNode(Node):
    def __init__(self, m_node, parent=None):
        super(CameraNode, self).__init__(m_node, parent)
