from pathlib import Path
import numpy as np
import tifffile

import napari

from napari_unet.data_control import load_tiff
from napari_unet.metrics import get_all_metrics
from napari_unet.compare_metrics import CompareMetrics
from napari_unet.result_tables import OneShotMetricsResultsTable, BatchMetricsResultsTable

from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QFileDialog, QCheckBox, QGridLayout
)
from qtpy.QtCore import Qt

_INPUT_LAYER     = "Input"
_GT_LAYER        = "Ground-truth"
_MODALITY_PREFIX = "Modality: "

class CompareResultsWidget(QWidget):
    def __init__(self, viewer=None, parent=None):
        super().__init__(parent)
        viewer = viewer or napari.current_viewer()
        if viewer is None:
            raise ValueError("No Napari viewer instance found.")
        self.viewer = viewer
        self.model = CompareMetrics()
        self.results_table = []
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.init_data_ui()
        self.init_one_shot_metrics()
        self.init_batch_metrics()

    # ==== UI: Data ====
    def init_data_ui(self):
        group = QGroupBox("Data")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Root folder
        root_layout = QHBoxLayout()
        root_label = QLabel("Root:")
        self.root_line = QLineEdit("")
        self.root_btn = QPushButton("Browse")
        self.root_btn.clicked.connect(self.browse_root_folder)
        root_layout.addWidget(root_label)
        root_layout.addWidget(self.root_line)
        root_layout.addWidget(self.root_btn)
        layout.addLayout(root_layout)

        # Inputs subfolder name (string)
        in_layout = QHBoxLayout()
        in_label = QLabel("Inputs:")
        self.inputs_line = QLineEdit("")
        self.inputs_line.textChanged.connect(self.update_inputs_name)
        self.inputs_line.setText(self.model.get_input_folder() or "")
        in_layout.addWidget(in_label)
        in_layout.addWidget(self.inputs_line)
        layout.addLayout(in_layout)

        # Ground-truth subfolder name (string)
        gt_layout = QHBoxLayout()
        gt_label = QLabel("Ground-truth:")
        self.gt_line = QLineEdit("")
        self.gt_line.textChanged.connect(self.update_gt_name)
        self.gt_line.setText(self.model.get_gt_folder() or "")
        gt_layout.addWidget(gt_label)
        gt_layout.addWidget(self.gt_line)
        layout.addLayout(gt_layout)

        # Image combo
        img_layout = QHBoxLayout()
        img_label = QLabel("Image:")
        self.image_combo = QComboBox()
        self.image_combo.addItems(["-----"])
        self.image_combo.currentTextChanged.connect(self.on_image_changed)
        img_layout.addWidget(img_label)
        img_layout.addWidget(self.image_combo)
        layout.addLayout(img_layout)

        # Button to generate degraded versions
        self.degraded_btn = QPushButton("Generate degraded versions")
        self.degraded_btn.clicked.connect(self.generate_degraded_versions)
        layout.addWidget(self.degraded_btn)

        self.main_layout.addWidget(group)

    # ==== UI: Metrics ====
    def init_one_shot_metrics(self):
        group = QGroupBox("One-shot")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Two-column checkbox grid
        metrics = list(get_all_metrics().keys())
        self.metric_checks = {}
        grid = QGridLayout()
        col_count = 2
        rows = (len(metrics) + col_count - 1) // col_count
        for idx, name in enumerate(metrics):
            r = idx % rows
            c = idx // rows
            cb = QCheckBox(name)
            cb.stateChanged.connect(lambda state, n=name: self.model.set_metric_enabled(n, state == Qt.Checked))
            cb.setChecked(self.model.is_metric_enabled(name))
            self.metric_checks[name] = cb
            grid.addWidget(cb, r, c, alignment=Qt.AlignLeft)
        layout.addLayout(grid)

        self.one_shot_btn = QPushButton("Compute Metrics")
        self.one_shot_btn.clicked.connect(self.compute_one_shot_metrics)
        layout.addWidget(self.one_shot_btn)

        self.main_layout.addWidget(group)

    def init_batch_metrics(self):
        group = QGroupBox("Batch")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Dropdown for metrics
        h_layout = QHBoxLayout()
        self.batch_metric_combo = QComboBox()
        metrics = list(get_all_metrics().keys())
        self.batch_metric_combo.addItems(metrics)
        h_layout.addWidget(QLabel("Metric:"))
        h_layout.addWidget(self.batch_metric_combo)
        layout.addLayout(h_layout)

        # Compute button
        self.batch_compute_btn = QPushButton("Compute Metrics")
        self.batch_compute_btn.clicked.connect(self.compute_batch_metrics)
        layout.addWidget(self.batch_compute_btn)

        self.main_layout.addWidget(group)

    # ==== Data browsing / updates ====
    def browse_root_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Root Folder")
        if folder:
            self.update_root_folder(folder)

    def update_root_folder(self, folder):
        folder = Path(folder)
        self.root_line.setText(str(folder))
        try:
            self.model.set_data_root(folder)
            self.root_line.setStyleSheet("color: green;")
        except ValueError as e:
            self.root_line.setStyleSheet("color: red;")
            print(f"Error setting data root: {e}")
        self.update_images_list()

    def update_images_list(self):
        items = ["------"]
        try:
            items = sorted(self.model.get_data_pool())
        except Exception as e:
            pass
        self.image_combo.clear()
        self.image_combo.addItems(items)
        self.image_combo.setCurrentIndex(0)

    def on_image_changed(self, name: str):
        self.show_original(name)
        self.show_ground_truth(name)
        self.show_modalities(name)
    
    def show_original(self, name):
        r = self.model.get_data_root()
        if r is None:
            return
        i = self.model.get_input_folder()
        if i is None:
            return
        p = r / i / name
        if not p.exists() or not p.is_file():
            return
        img = load_tiff(p)
        if _INPUT_LAYER in self.viewer.layers:
            self.viewer.layers[_INPUT_LAYER].data = img
        else:
            self.viewer.add_image(img, name=_INPUT_LAYER, colormap='gray',
                                  contrast_limits=[0, float(np.percentile(img, 99.9))])

    def show_ground_truth(self, name):
        r = self.model.get_data_root()
        if r is None:
            return
        g = self.model.get_gt_folder()
        if g is None:
            return
        p = r / g / name
        if not p.exists() or not p.is_file():
            return
        gt = load_tiff(p)
        if _GT_LAYER in self.viewer.layers:
            self.viewer.layers[_GT_LAYER].data = gt
        else:
            self.viewer.add_labels(gt, name=_GT_LAYER)

    def show_modalities(self, name):
        r = self.model.get_data_root()
        if r is None:
            return
        if self.model.get_input_folder() is None or self.model.get_gt_folder() is None:
            return
        mods = self.model.get_modalities()
        for i, m in enumerate(mods, start=2):
            p = r / m / name
            if not p.exists() or not p.is_file():
                continue
            img = load_tiff(p) * i
            layer_name = f"{_MODALITY_PREFIX} {m}"
            if layer_name in self.viewer.layers:
                self.viewer.layers[layer_name].data = img
            else:
                self.viewer.add_labels(img, name=layer_name)

    def update_inputs_name(self, text):
        try:
            self.model.set_input_folder(text.strip())
            self.inputs_line.setStyleSheet("color: green;")
        except ValueError as e:
            self.inputs_line.setStyleSheet("color: red;")
            print(f"Error setting input folder: {e}")
        self.update_images_list()

    def update_gt_name(self, text):
        try:
            self.model.set_gt_folder(text.strip())
            self.gt_line.setStyleSheet("color: green;")
        except ValueError as e:
            self.gt_line.setStyleSheet("color: red;")
            print(f"Error setting input folder: {e}")
        self.update_images_list()

    def compute_one_shot_metrics(self):
        if not self.image_combo.currentText() in self.model.get_data_pool():
            return
        name = self.image_combo.currentText()
        results = self.model.compute_one_shot_metrics(name)
        self.results_table.append(OneShotMetricsResultsTable(results, name, parent=self))
        self.results_table[-1].show()

    def compute_batch_metrics(self):
        if not self.batch_metric_combo.currentText() in set(get_all_metrics().keys()):
            return
        name = self.batch_metric_combo.currentText()
        results = self.model.compute_batch_metrics(name)
        self.results_table.append(BatchMetricsResultsTable(results, name, parent=self))
        self.results_table[-1].show()

    def generate_degraded_versions(self):
        self.model.generate_degraded_versions()
        self.update_images_list()

    # ==== Helpers ====
    def get_selected_metrics(self):
        return [name for name, cb in self.metric_checks.items() if cb.isChecked()]

# ===== Dev launcher (optional) =====

def launch_dev_procedure():
    viewer = napari.Viewer()
    widget = CompareResultsWidget(viewer=viewer)
    viewer.window.add_dock_widget(widget)

    widget.update_root_folder("/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1-results")
    widget.inputs_line.setText("inputs")
    widget.gt_line.setText("masks1")

    napari.run()

if __name__ == "__main__":
    launch_dev_procedure()
