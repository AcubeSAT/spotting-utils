import sys

import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui

import PySide6.QtWidgets as QtWidgets

from GCodeUtils import dec_coor, inc_coor, replace_coor
from IOUtils import lines_to_text, read_gcode, write_gcode
from paths import get_path


class GCodeUtils(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._init_ui()

    def _init_ui(self) -> None:
        self._create_io_group_box()
        self._create_coor_group_box()

        self.selected_gcode_path = QtWidgets.QLabel(self.tr("Selected G-Code: "))

        self.gcode_viewer = QtWidgets.QPlainTextEdit()
        self.gcode_viewer.setReadOnly(True)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self._io_group_box)
        main_layout.addWidget(self.selected_gcode_path)
        main_layout.addWidget(self.gcode_viewer)
        main_layout.addWidget(self._coor_group_box)
        self.setLayout(main_layout)

        self.setWindowTitle(self.tr("Lab-On-a-Chip Spotting Utilties"))

        # To have widgets appear.
        dummy_widget = QtWidgets.QWidget()
        dummy_widget.setLayout(main_layout)
        self.setCentralWidget(dummy_widget)

        toolbar = QtWidgets.QToolBar("Edit")
        ICON_WIDTH, ICON_HEIGHT = (25, 25)
        toolbar.setIconSize(QtCore.QSize(ICON_WIDTH, ICON_HEIGHT))
        self.addToolBar(toolbar)

        plus_button = QtWidgets.QPushButton(QtGui.QIcon(str(get_path("assets-plus"))), "", self)
        plus_button.setStatusTip(self.tr("Increase X/Y/Z G-Code coordinates by value"))
        plus_button.clicked.connect(self._handle_plus_button)

        toolbar.addWidget(plus_button)
        toolbar.addSeparator()

        minus_button = QtWidgets.QPushButton(QtGui.QIcon(str(get_path("assets-minus"))), "", self)
        minus_button.setStatusTip(self.tr("Decrease X/Y/Z G-Code coordinates by value"))
        minus_button.clicked.connect(self._handle_minus_button)

        toolbar.addWidget(minus_button)
        toolbar.addSeparator()

        replace_button = QtWidgets.QPushButton(QtGui.QIcon(str(get_path("assets-replace"))), "", self)
        replace_button.setStatusTip(self.tr("Replace X/Y/Z G-Code coordinates with value"))
        replace_button.clicked.connect(self._handle_replace_button)

        toolbar.addWidget(replace_button)

        self.setStatusBar(QtWidgets.QStatusBar(self))

        self.gcode = None

    @QtCore.Slot()
    def _handle_plus_button(self):
        if self._specific_val_checkbox.isChecked():
            self.gcode = [inc_coor(line, self._coor_dropdown.currentText(), self._new_coor_val.value(), only_for_val = self._specific_val_selector.value()) for line in self.gcode]
        else:
            self.gcode = [inc_coor(line, self._coor_dropdown.currentText(), self._new_coor_val.value()) for line in self.gcode]

        self._update_gcode_viewer()

    @QtCore.Slot()
    def _handle_minus_button(self):
        if self._specific_val_checkbox.isChecked():
            self.gcode = [dec_coor(line, self._coor_dropdown.currentText(), self._new_coor_val.value(), only_for_val = self._specific_val_selector.value()) for line in self.gcode]
        else:
            self.gcode = [dec_coor(line, self._coor_dropdown.currentText(), self._new_coor_val.value()) for line in self.gcode]

        self._update_gcode_viewer()

    @QtCore.Slot()
    def _handle_replace_button(self):
        if self._specific_val_checkbox.isChecked():
            self.gcode = [replace_coor(line, self._coor_dropdown.currentText(), self._new_coor_val.value(), only_for_val = self._specific_val_selector.value()) for line in self.gcode]
        else:
            self.gcode = [replace_coor(line, self._coor_dropdown.currentText(), self._new_coor_val.value()) for line in self.gcode]

        self._update_gcode_viewer()

    def _create_io_group_box(self) -> None:
        self._io_group_box = QtWidgets.QGroupBox(self.tr("IO"))
        layout = QtWidgets.QHBoxLayout()

        browse_button = QtWidgets.QPushButton(self.tr("Browse"))
        browse_button.clicked.connect(self._browse_gcode)

        save_button = QtWidgets.QPushButton(self.tr("Save"))
        save_button.clicked.connect(self._save_gcode)

        layout.addWidget(browse_button)
        layout.addWidget(save_button)

        self._io_group_box.setLayout(layout)

    def _create_coor_group_box(self) -> None:
        SELECTOR_MIN, SELECTOR_MAX = (0, 300)

        self._coor_group_box = QtWidgets.QGroupBox(self.tr("Coordinates"))
        layout = QtWidgets.QHBoxLayout()

        self._coor_dropdown = QtWidgets.QComboBox()
        self._coor_dropdown.addItems(['X', 'Y', 'Z'])

        self._new_coor_val = QtWidgets.QSpinBox()
        self._new_coor_val.setRange(SELECTOR_MIN, SELECTOR_MAX)

        self._specific_val_checkbox = QtWidgets.QCheckBox(self.tr("Specific value only"))

        self._specific_val_selector = QtWidgets.QSpinBox()
        self._specific_val_selector.setRange(SELECTOR_MIN, SELECTOR_MAX)

        layout.addWidget(self._coor_dropdown)
        layout.addWidget(self._new_coor_val)
        layout.addWidget(self._specific_val_checkbox)
        layout.addWidget(self._specific_val_selector)

        self._coor_group_box.setLayout(layout)

    def _browse_gcode(self) -> None:
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        dialog.setViewMode(QtWidgets.QFileDialog.List)
        dialog.setNameFilter(self.tr("G-Code (*.gcode)"))

        if dialog.exec():
            gcode_filename = dialog.selectedFiles()[0]

            self.selected_gcode_path.setText(self.tr(f"Selected G-Code: {gcode_filename}"))
            self.gcode = read_gcode(gcode_filename)

            self._update_gcode_viewer()

    def _save_gcode(self) -> None:
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setViewMode(QtWidgets.QFileDialog.List)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setDefaultSuffix(self.tr("gcode"))
        dialog.setNameFilter(self.tr("G-Code (*.gcode)"))

        if dialog.exec():
            gcode_filename = dialog.selectedFiles()[0]
            write_gcode(gcode_filename, self.gcode)
    
    def _update_gcode_viewer(self) -> None:
        self.gcode_viewer.setPlainText(lines_to_text(self.gcode))


if __name__ == "__main__":
    WIDTH, HEIGHT = (600, 700)
    app = QtWidgets.QApplication([])

    window = GCodeUtils()
    window.resize(WIDTH, HEIGHT)
    window.show()

    sys.exit(app.exec())
