import sys
import ctypes

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

from tools_core.pyqt_commons import common_widgets as cw


def inline_layout(widgets, stretch=False):
    layout = QtWidgets.QHBoxLayout()

    for widget in widgets:
        if isinstance(widget, str) and widget == "stretch":
            layout.addStretch()
            continue

        layout.addWidget(widget)

    return layout


class PropagateSceneDataUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PropagateSceneDataUI, self).__init__(parent)

        self.setWindowTitle("Window")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("Window")

        self.setFixedSize(1920 * 0.5, 960 * 0.5)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.src_header_lbl = QtWidgets.QLabel("Propagate From: ")

        self.src_seq_lbl = QtWidgets.QLabel("Seq: ")
        self.src_shot_lbl = QtWidgets.QLabel("Shot: ")

        self.src_seq_le = QtWidgets.QLineEdit()
        self.src_shot_le = QtWidgets.QLineEdit()

        self.dst_header_lbl = QtWidgets.QLabel("Propagate To: ")

        self.dst_seq_lbl = QtWidgets.QLabel("Seq: ")
        self.dst_shot_lbl = QtWidgets.QLabel("Shot: ")

        self.dst_seq_le = QtWidgets.QLineEdit()
        self.dst_shot_le = QtWidgets.QLineEdit()

        self.prop_lighting_cb = QtWidgets.QCheckBox("Propagate Lighting")

        self.dst_lighting_name_lbl = QtWidgets.QLabel("Scene name: ")
        self.dst_lighting_name_le = QtWidgets.QLineEdit()
        self.dst_lighting_name_auto_cb = QtWidgets.QCheckBox("Auto")

        self.prop_nuke_cb = QtWidgets.QCheckBox("Propagate Nuke")

        self.dst_nuke_name_lbl = QtWidgets.QLabel("Nuke name: ")
        self.dst_nuke_name_le = QtWidgets.QLineEdit()
        self.dst_nuke_name_auto_cb = QtWidgets.QCheckBox("Auto")

        self.src_lighting_tw = QtWidgets.QTreeWidget()

        src_lighting_tw_header_item = QtWidgets.QTreeWidgetItem(["Source Lighting Scene"])
        self.src_lighting_tw.setHeaderItem(src_lighting_tw_header_item)

        self.src_nuke_tw = QtWidgets.QTreeWidget()

        src_nuke_tw_header_item = QtWidgets.QTreeWidgetItem(["Source Nuke File"])
        self.src_nuke_tw.setHeaderItem(src_nuke_tw_header_item)

        self.propagate_btn = QtWidgets.QPushButton("Propagate Scene")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        in_col_layout = QtWidgets.QHBoxLayout()

        in_l_col_layout = QtWidgets.QVBoxLayout()

        in_l_col_layout.addWidget(self.src_header_lbl)

        src_in_layout = inline_layout(
            [
                self.src_seq_lbl,
                self.src_seq_le,
                self.src_shot_lbl,
                self.src_shot_le
            ]
        )

        in_l_col_layout.addLayout(src_in_layout)

        in_l_col_layout.addStretch()

        in_col_layout.addLayout(in_l_col_layout)
        in_col_layout.addWidget(cw.QVLine())

        in_r_col_layout = QtWidgets.QVBoxLayout()

        in_r_col_layout.addWidget(self.dst_header_lbl)

        dst_in_layout = inline_layout(
            [
                self.dst_seq_lbl,
                self.dst_seq_le,
                self.dst_shot_lbl,
                self.dst_shot_le
            ]
        )

        in_r_col_layout.addLayout(dst_in_layout)

        in_r_col_layout.addStretch()

        in_col_layout.addLayout(in_r_col_layout)

        main_layout.addLayout(in_col_layout)

        main_layout.addWidget(cw.QHLine())

        srcs_layout = QtWidgets.QHBoxLayout()

        src_lighting_layout = QtWidgets.QVBoxLayout()

        src_lighting_layout.addWidget(self.prop_lighting_cb)

        lighting_dst_layout = inline_layout(
            [
                self.dst_lighting_name_lbl,
                self.dst_lighting_name_le,
                self.dst_lighting_name_auto_cb
            ]
        )

        src_lighting_layout.addLayout(lighting_dst_layout)

        src_lighting_layout.addWidget(self.src_lighting_tw)

        srcs_layout.addLayout(src_lighting_layout)

        srcs_layout.addWidget(cw.QVLine())

        src_nuke_layout = QtWidgets.QVBoxLayout()

        src_nuke_layout.addWidget(self.prop_nuke_cb)

        nuke_dst_layout = inline_layout(
            [
                self.dst_nuke_name_lbl,
                self.dst_nuke_name_le,
                self.dst_nuke_name_auto_cb
            ]
        )

        src_nuke_layout.addLayout(nuke_dst_layout)

        src_nuke_layout.addWidget(self.src_nuke_tw)

        srcs_layout.addLayout(src_nuke_layout)

        main_layout.addLayout(srcs_layout)

        main_layout.addStretch()

        btn_layout = QtWidgets.QHBoxLayout()

        btn_layout.addStretch()
        btn_layout.addWidget(self.propagate_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

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

    browser = PropagateSceneDataUI()
    browser.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
