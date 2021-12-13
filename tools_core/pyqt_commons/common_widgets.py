from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

import sys

from functools import partial


def get_signals(source):
    cls = source if isinstance(source, type) else type(source)
    signal = type(QtCore.Signal())
    signals = []
    for name in dir(source):
        try:
            if isinstance(getattr(cls, name), signal):
                signals.append(name)
        except AttributeError:
            pass
    return signals


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


class ScrollAreaWidget(QtWidgets.QWidget):
    def __init__(self, height):
        super(ScrollAreaWidget, self).__init__()

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(height)
        self.scroll.setStyleSheet("border: none; background-color: rgb(50,50,50);")
        self.scroll.setContentsMargins(0, 0, 0, 0)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.scroll)

    def set_widget(self, widget):
        self.scroll.setWidget(widget)

    def remove_widget(self):
        self.scroll.takeWidget()


class LabeledLineEdit(QtWidgets.QWidget):
    def __init__(self, label):
        super(LabeledLineEdit, self).__init__()

        self.label = label
        self.lbl_widget = QtWidgets.QLabel(self.label)
        self.le_widget = QtWidgets.QLineEdit()

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.lbl_widget)
        self.main_layout.addSpacing(5)

        self.main_layout.addWidget(self.le_widget)

    def text(self):
        return self.le_widget.text()

    def setText(self, text):
        self.le_widget.setText(text)


class LabeledLineEditButton(QtWidgets.QWidget):
    def __init__(self, label, btn_label):
        super(LabeledLineEdit, self).__init__()

        self.label = label
        self.lbl_widget = QtWidgets.QLabel(self.label)
        self.le_widget = QtWidgets.QLineEdit()
        self.btn_widget = QtWidgets.QPushButton(btn_label)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.lbl_widget)
        self.main_layout.addSpacing(5)

        self.main_layout.addWidget(self.le_widget)

    def text(self):
        return self.le_widget.text()

    def setText(self, text):
        self.le_widget.setText(text)


class FileBrowseWidget(QtWidgets.QWidget):
    def __init__(self, label, size=(30, 30), justify='left', starting_dir=None):
        super(FileBrowseWidget, self).__init__()

        self.label = label
        self.size = size

        self.lble_widget = LabeledLineEdit(self.label)

        if justify == 'right':
            self.lble_widget.lbl_widget.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.fb_btn = QtWidgets.QPushButton()
        file_browse_icon = QtGui.QIcon(':fileOpen.png')
        self.fb_btn.setIcon(file_browse_icon)

        self.fb_btn.clicked.connect(self.browse_file)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.addWidget(self.lble_widget)
        self.main_layout.addWidget(self.fb_btn)

    def setText(self, text):
        self.lble_widget.le_widget.setText(text)

    def text(self):
        return self.lble_widget.le_widget.text()

    def browse_file(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, '')[0]

        if file_name:
            self.setText(file_name)


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


class HeaderLabel(QtWidgets.QLabel):
    def __init__(self, text, scale=1):
        super(HeaderLabel, self).__init__()
        self.setText(text)
        self.setStyleSheet("font: {0}px".format(str(int(20 * scale))))


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
        self.setPixmap(QtGui.QPixmap(r'F:\share\tools\core\asset_browser\icons\default.png').scaledToWidth(100,
                                                                                                           QtCore.Qt.SmoothTransformation))


class DoubleSlider(QtWidgets.QSlider):
    log_event = QtCore.Signal(str, str)
    clicked_event = QtCore.Signal(QtWidgets.QTreeWidgetItem)
    doubleValueChanged = QtCore.Signal(float)

    def __init__(self, decimals=3, *args, **kwargs):
        super(DoubleSlider, self).__init__(*args, **kwargs)

        self.decimals = decimals
        self.multiplier = 10 ** self.decimals

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(DoubleSlider, self).value()) / self.multiplier
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self.multiplier

    def setMinimum(self, value):
        return super(DoubleSlider, self).setMinimum(value * self.multiplier)

    def setMaximum(self, value):
        return super(DoubleSlider, self).setMaximum(value * self.multiplier)

    def setSingleStep(self, value):
        return super(DoubleSlider, self).setSingleStep(value * self.multiplier)

    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self.multiplier

    def setValue(self, value):
        super(DoubleSlider, self).setValue(int(value * self.multiplier))


class MTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, *args, **kwargs):
        super(MTreeWidget, self).__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        self.clearSelection()
        QtWidgets.QTreeWidget.mousePressEvent(self, event)


class VSpacerWidget(QtWidgets.QWidget):
    def __init__(self, height):
        super(VSpacerWidget, self).__init__()

        self.setFixedHeight(height)


class LabeledIntSlider(QtWidgets.QWidget):
    value_changed = QtCore.Signal(int)

    def __init__(self, label, min_range, max_range, value):
        super(LabeledIntSlider, self).__init__()

        self.label = label
        self.min_range = min_range
        self.max_range = max_range
        self.starting_value = value

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.lbl = QtWidgets.QLabel(self.label)
        self.le = QtWidgets.QLineEdit()
        self.le.setMaximumWidth(80)
        self.le.setAlignment(QtCore.Qt.AlignRight)
        self.le.setText(str(self.starting_value))

        self.slider = QtWidgets.QSlider()
        self.slider.setRange(self.min_range, self.max_range)
        self.slider.setValue(self.starting_value)

        self.slider.setOrientation(QtCore.Qt.Horizontal)

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        main_layout.addWidget(self.lbl)
        main_layout.addWidget(self.le)
        main_layout.addWidget(self.slider)

    def create_connections(self):
        self.le.editingFinished.connect(self.le_callback)
        self.slider.valueChanged.connect(self.slider_callback)

    def le_callback(self):
        self.slider.blockSignals(True)

        prev_value = self.slider.value()

        try:
            value = int(self.le.text())
            self.slider.setValue(value)
            self.value_changed.emit(value)
        except Exception:
            self.le.setText(str(prev_value))

        self.slider.blockSignals(False)

    def slider_callback(self):
        self.le.blockSignals(True)

        self.le.setText(str(self.slider.value()))
        self.value_changed.emit(self.slider.value())

        self.le.blockSignals(False)

    def value(self):
        return self.slider.value()


class DarkPalette(QtGui.QPalette):
    def __init__(self):
        super(DarkPalette, self).__init__()

        self.setColor(QtGui.QPalette.Window, QtGui.QColor(45, 45, 45))
        self.setColor(QtGui.QPalette.WindowText, QtGui.QColor(208, 208, 208))
        self.setColor(QtGui.QPalette.Base, QtGui.QColor(37, 37, 37))
        self.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(208, 208, 208))
        self.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(208, 208, 208))
        self.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(208, 208, 208))
        self.setColor(QtGui.QPalette.Text, QtGui.QColor(208, 208, 208))
        self.setColor(QtGui.QPalette.Button, QtGui.QColor(45, 45, 48))
        self.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(208, 208, 208))
        self.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        self.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        self.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
