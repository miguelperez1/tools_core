import sys
import ctypes

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from tools_core.pyqt_commons import common_widgets as cw


class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.setWindowTitle("Window")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("Window")

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        pass

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

    def create_connections(self):
        pass


def main():
    appid = ""
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    app = QtWidgets.QApplication(sys.argv)

    app_icon = QtGui.QIcon(r"F:\share\tools\shelf_icons\volumebox.png")

    app.setWindowIcon(app_icon)

    app.setStyle(QtWidgets.QStyleFactory.create("fusion"))

    app.setPalette(cw.DarkPalette())

    browser = Window()
    browser.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
