from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel, QGridLayout,
    QPushButton, QComboBox, QLineEdit, QFileDialog, QCheckBox
)
from qtpy.QtCore import Qt
import napari

from napari_unet.skeleton_measures import SkeletonMeasures
from napari_unet.result_tables import SkeletonMeasuresResultsTable
from napari_unet.data_control import load_tiff

import math
from pathlib import Path
import numpy as np

_MASK_LAYER_NAME = "Mask"
_SKEL_LAYER_NAME = "Skeleton"

class SkeletonAnalysisWidget(QWidget):

    def __init__(self, viewer=None, parent=None):
        super().__init__(parent)
        viewer = viewer or napari.current_viewer()
        if viewer is None:
            raise ValueError("No Napari viewer instance found.")
        
        self.model = SkeletonMeasures()
        self.viewer = viewer
        self.measure_checkboxes = {}
        self.masks_path = Path("")
        self.rt = None
        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self._build_data_group()
        self._build_measures_group()

        self.main_layout.addStretch(1)

    def _build_data_group(self):
        group = QGroupBox("Data")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Masks folder chooser
        row = QHBoxLayout()
        row.addWidget(QLabel("Masks Folder:"))
        self.masks_line = QLineEdit("")
        self.masks_btn = QPushButton("Browse")
        self.masks_btn.clicked.connect(self.browse_masks_folder)
        self.masks_line.editingFinished.connect(self.update_masks_folder)
        row.addWidget(self.masks_line)
        row.addWidget(self.masks_btn)
        layout.addLayout(row)

        # Image selector (combobox under the folder field)
        img_row = QHBoxLayout()
        img_row.addWidget(QLabel("Image:"))
        self.image_combo = QComboBox()
        self.image_combo.addItem("-----")
        self.image_combo.currentTextChanged.connect(self.update_selected_image)
        img_row.addWidget(self.image_combo)
        layout.addLayout(img_row)

        self.main_layout.addWidget(group)

    def _build_measures_group(self):
        group = QGroupBox("Measures")
        vbox = QVBoxLayout(group)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(4)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        vbox.addLayout(grid)

        measures = list(self.model.get_measures_list())

        n = len(measures)
        rows = max(1, math.ceil(n / 2))

        for i, name in enumerate(measures):
            cb = QCheckBox(name)
            cb.setChecked(True)
            self.measure_checkboxes[name] = cb

            row = i % rows
            col = i // rows  # 0 or 1
            grid.addWidget(cb, row, col, alignment=Qt.AlignLeft)

        # Compute button spans both columns
        self.compute_btn = QPushButton("Compute Measures")
        self.compute_btn.clicked.connect(self.compute_measures)
        grid.addWidget(self.compute_btn, rows, 0, 1, 2)

        self.main_layout.addWidget(group)

    # ---------------- Callbacks (placeholders) ----------------

    def browse_masks_folder(self):
        """Browse for masks folder and populate the Image combobox with TIFF files."""
        folder = QFileDialog.getExistingDirectory(self, "Masks Folder")
        if not folder:
            return
        self.update_masks_folder(folder)

    def update_image_list(self):
        p = Path(self.masks_path)
        tif_files = sorted([f.name for f in p.iterdir() if f.is_file() and f.suffix.lower() in (".tif", ".tiff")])
        self.image_combo.clear()
        self.image_combo.addItems(tif_files)
        self.update_image()

    def update_image(self):
        img_name = self.image_combo.currentText()
        full_path = self.masks_path / img_name
        if not full_path.exists() or not full_path.is_file():
            return
        image = (load_tiff(full_path) > 0).astype(np.uint8)
        if _MASK_LAYER_NAME in self.viewer.layers:
            l = self.viewer.layers[_MASK_LAYER_NAME]
            l.data = image
        else:
            l = self.viewer.add_labels(image, name=_MASK_LAYER_NAME)
        self.update_skeleton(l)

    def update_skeleton(self, mask_layer):
        image = mask_layer.data
        skeleton = self.model.make_skeleton(image)
        if _SKEL_LAYER_NAME in self.viewer.layers:
            l = self.viewer.layers[_SKEL_LAYER_NAME]
            l.data = skeleton * 2
        else:
            l = self.viewer.add_labels(skeleton * 2, name=_SKEL_LAYER_NAME)

    def update_masks_folder(self, folder):
        self.masks_path = Path(folder)
        self.masks_line.setText(folder)
        self.update_image_list()

    def update_selected_image(self, name: str):
        self.update_image()

    def compute_measures(self):
        active_measures = [name for name, cb in self.measure_checkboxes.items() if cb.isChecked()]
        if not active_measures:
            return
        if _SKEL_LAYER_NAME not in self.viewer.layers:
            return
        skel_layer = self.viewer.layers[_SKEL_LAYER_NAME]
        calib = skel_layer.scale
        skel_data = (skel_layer.data > 0).astype(np.uint8)
        calib = calib[-len(skel_data.shape):]
        self.model.set_calibration(calib)
        results = self.model.compute_measures(skel_data, measures=active_measures)
        self.rt = SkeletonMeasuresResultsTable(results, self.image_combo.currentText())
        self.rt.show()

def launch_dev_procedure():
    viewer = napari.Viewer()
    widget = SkeletonAnalysisWidget(viewer=viewer)
    viewer.window.add_dock_widget(widget)

    napari.run()

if __name__ == "__main__":
    launch_dev_procedure()