from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setContentsMargins(0, 0, 0, 0)


class QVLine(QtWidgets.QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class LabeledLineEdit(QtWidgets.QWidget):
    def __init__(self, label=None):
        super(LabeledLineEdit, self).__init__()

        self.lbl_widget = QtWidgets.QLabel()
        self.le_widget = QtWidgets.QLineEdit()

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.lbl_widget)
        self.main_layout.addSpacing(5)
        self.main_layout.addWidget(self.le_widget)

        if label:
            self.setText(label)

    def text(self):
        return self.le_widget.text()

    def setText(self, text):
        self.le_widget.setText(text)


class ImagePushButton(QtWidgets.QPushButton):
    def __init__(self, size_x, size_y):
        super(ImagePushButton, self).__init__()
        self.set_default()
        self.size_x = size_x
        self.size_y = size_y
        self.setFixedSize(self.size_x, self.size_y)

    def set_image(self, path, scale=1):
        icon = QtGui.QIcon(path)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(self.size_x * scale, self.size_y * scale))

    def set_default(self):
        default_path = r'F:\share\tools\core\maya_core\asset_browser\icons\default.png'
        self.setIcon(QtGui.QPixmap(default_path).scaledToWidth(100, QtCore.Qt.SmoothTransformation))
