import logging

logging.basicConfig()

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui


class PreviewLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super(PreviewLabel, self).__init__(*args, **kwargs)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(1, 1)
        self.setContentsMargins(0, 0, 0, 0)
        self.set_default()

    def set_image(self, path, scale=160):
        self.pixmap = QtGui.QPixmap(path).scaledToWidth(scale, QtCore.Qt.SmoothTransformation)
        self.setPixmap(self.pixmap)

    def set_default(self):
        self.setPixmap(QtGui.QPixmap(r"F:\share\tools\tools_core\tools_core\asset_library\asset_browser\icons\default.png").scaledToWidth(100,
                                                                                                           QtCore.Qt.SmoothTransformation))
