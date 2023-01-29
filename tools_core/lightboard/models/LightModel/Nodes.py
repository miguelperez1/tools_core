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

    def name(self):
        return self._name

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


class TransformNode(Node):
    def __init__(self, m_node, parent=None):
        super(TransformNode, self).__init__(m_node, parent)


class CameraNode(Node):
    def __init__(self, m_node, parent=None):
        super(CameraNode, self).__init__(m_node, parent)
