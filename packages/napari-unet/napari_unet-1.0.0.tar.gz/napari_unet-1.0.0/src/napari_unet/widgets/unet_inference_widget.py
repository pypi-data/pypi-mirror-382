from pathlib import Path
import numpy as np
import tifffile

import napari
from napari.utils import progress

from qtpy.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QLineEdit, QFileDialog, QSpinBox, QDoubleSpinBox
)
from qtpy.QtCore import Qt, QThread
from napari_unet.qt_workers import QtUNetInference, QtUNetRefreshMasks

from napari_unet.unet_inference import UNet2DInference
from napari_unet.data_control import load_tiff

_IMAGE_LAYER = "Original"
_PROBA_LAYER = "Prediction"
_MASK_LAYER  = "Mask"

class UNet2DInferenceWidget(QWidget):
    def __init__(self, viewer=None, parent=None):
        super().__init__(parent)
        viewer = viewer or napari.current_viewer()
        if viewer is None:
            raise ValueError("No Napari viewer instance found.")
        self.viewer = viewer
        self.model = UNet2DInference()
        self.inference_worker = None
        self.inference_thread = None
        self.inference_pbr    = None
        self.refresh_worker = None
        self.refresh_thread = None
        self.refresh_pbr    = None
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.init_data_ui()
        self.init_inference_ui()
        self.init_postproc_ui()

    def init_data_ui(self):
        group = QGroupBox("Data")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Input folder
        in_layout = QHBoxLayout()
        in_label = QLabel("Input Folder:")
        self.input_line = QLineEdit("")
        self.in_btn = QPushButton("Browse")
        self.in_btn.clicked.connect(self.browse_input_folder)
        in_layout.addWidget(in_label)
        in_layout.addWidget(self.input_line)
        in_layout.addWidget(self.in_btn)
        layout.addLayout(in_layout)

        # Output folder
        out_layout = QHBoxLayout()
        out_label = QLabel("Output Folder:")
        self.output_line = QLineEdit("")
        self.out_btn = QPushButton("Browse")
        self.out_btn.clicked.connect(self.browse_output_folder)
        out_layout.addWidget(out_label)
        out_layout.addWidget(self.output_line)
        out_layout.addWidget(self.out_btn)
        layout.addLayout(out_layout)

        # Image combobox
        img_layout = QHBoxLayout()
        img_label = QLabel("Image:")
        self.image_combo = QComboBox()
        self.image_combo.addItems(["-----"])
        self.image_combo.currentTextChanged.connect(self.update_image_selection)
        img_layout.addWidget(img_label)
        img_layout.addWidget(self.image_combo)
        layout.addLayout(img_layout)

        self.main_layout.addWidget(group)

    def init_inference_ui(self):
        group = QGroupBox("Inference")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Model folder
        model_layout = QHBoxLayout()
        model_label = QLabel("Model Folder:")
        self.model_line = QLineEdit("")
        self.model_btn = QPushButton("Browse")
        self.model_btn.clicked.connect(self.browse_model_folder)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_line)
        model_layout.addWidget(self.model_btn)
        layout.addLayout(model_layout)

        # Patch size
        patch_layout = QHBoxLayout()
        patch_label = QLabel("Patch Size:")
        self.patch_spin = QSpinBox()
        self.patch_spin.setRange(1, 4096)
        self.patch_spin.valueChanged.connect(self.update_patch_size)
        self.patch_spin.setValue(self.model.get_patch_size())
        patch_layout.addWidget(patch_label)
        patch_layout.addWidget(self.patch_spin)
        layout.addLayout(patch_layout)

        # Overlap size
        overlap_layout = QHBoxLayout()
        overlap_label = QLabel("Overlap:")
        self.overlap_spin = QSpinBox()
        self.overlap_spin.setRange(0, 4096)
        self.overlap_spin.valueChanged.connect(self.update_overlap_size)
        self.overlap_spin.setValue(self.model.get_overlap())
        overlap_layout.addWidget(overlap_label)
        overlap_layout.addWidget(self.overlap_spin)
        layout.addLayout(overlap_layout)

        # Batch size
        batch_layout = QHBoxLayout()
        batch_label = QLabel("Batch Size:")
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(1, 1024)
        self.batch_spin.valueChanged.connect(self.update_batch_size)
        self.batch_spin.setValue(self.model.get_batch_size())
        batch_layout.addWidget(batch_label)
        batch_layout.addWidget(self.batch_spin)
        layout.addLayout(batch_layout)

        # Launch inference button
        launch_layout = QHBoxLayout()
        self.launch_btn = QPushButton("Run Inference")
        self.launch_btn.clicked.connect(self.launch_inference)
        launch_layout.addWidget(self.launch_btn)
        layout.addLayout(launch_layout)

        self.main_layout.addWidget(group)

    def init_postproc_ui(self):
        group = QGroupBox("Post-processing")
        layout = QVBoxLayout()
        group.setLayout(layout)

        thresh_layout = QHBoxLayout()
        thresh_label = QLabel("Threshold:")
        self.thresh_spin = QDoubleSpinBox()
        self.thresh_spin.setRange(0.0, 1.0)
        self.thresh_spin.setSingleStep(0.01)
        self.thresh_spin.setDecimals(3)
        self.thresh_spin.valueChanged.connect(self.update_threshold)
        self.thresh_spin.setValue(self.model.get_threshold())
        thresh_layout.addWidget(thresh_label)
        thresh_layout.addWidget(self.thresh_spin)
        layout.addLayout(thresh_layout)

        reproc_layout = QHBoxLayout()
        self.reproc_btn = QPushButton("Reprocess masks")
        self.reproc_btn.clicked.connect(self.reprocess_masks)
        reproc_layout.addWidget(self.reproc_btn)
        layout.addLayout(reproc_layout)

        self.main_layout.addWidget(group)

    # === CALLBACKS ===

    def browse_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Input Folder")
        if folder:
            self.update_input_folder(folder)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Output Folder")
        if folder:
            self.update_output_folder(folder)

    def browse_model_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Model Folder")
        if folder:
            self.update_model_folder(folder)

    def update_image_selection(self):
        self.show_image(self.image_combo.currentText())
        self.show_proba(self.image_combo.currentText())
        self.show_mask(self.image_combo.currentText())

    def update_patch_size(self, value):
        self.model.set_patch_size(int(value))

    def update_overlap_size(self, value):
        self.model.set_overlap(int(value))

    def update_batch_size(self, value):
        self.model.set_batch_size(int(value))

    def set_active_ui(self, active):
        self.input_line.setEnabled(active)
        self.output_line.setEnabled(active)
        self.model_line.setEnabled(active)
        self.image_combo.setEnabled(active)
        self.patch_spin.setEnabled(active)
        self.overlap_spin.setEnabled(active)
        self.batch_spin.setEnabled(active)
        self.thresh_spin.setEnabled(active)
        self.launch_btn.setEnabled(active)
        self.reproc_btn.setEnabled(active)
        self.in_btn.setEnabled(active)
        self.out_btn.setEnabled(active)
        self.model_btn.setEnabled(active)

    def launch_inference(self):
        if self.inference_worker is not None:
            print("Inference already running.")
            return

        self.inference_pbr = progress(total=len(self.model.get_data_pool()), desc="Running Inference")
        self.inference_worker = QtUNetInference(self.model)

        self.inference_thread = QThread()
        self.inference_worker.moveToThread(self.inference_thread)

        self.inference_thread.started.connect(self.inference_worker.run)
        self.inference_worker.update.connect(self.update_inference)
        self.inference_worker.finished.connect(self.finished_inference)

        self.inference_worker.finished.connect(self.inference_thread.quit)

        self.set_active_ui(False)
        self.inference_thread.finished.connect(lambda: self.set_active_ui(True))

        self.inference_thread.start()
        print("Inference started.")

    def update_inference(self, message):
        if self.inference_pbr is not None:
            self.inference_pbr.update(1)
            self.inference_pbr.set_description(message)

    def finished_inference(self):
        if self.inference_pbr is not None:
            try:
                self.inference_pbr.close()
            except Exception:
                pass
            self.inference_pbr = None

        if self.inference_worker is not None:
            try:
                self.inference_worker.stop()
            except Exception:
                pass

        if self.inference_thread is not None:
            if self.inference_thread.isRunning():
                self.inference_thread.quit()
                self.inference_thread.wait(5000)
        self.inference_worker = None
        self.inference_thread = None
        print("Inference finished")
        self.update_image_selection()

    def update_threshold(self, value):
        if not 0.0 <= float(value) <= 1.0:
            return
        self.model.set_threshold(float(value))

    def update_masks(self, message):
        if self.refresh_pbr is not None:
            self.refresh_pbr.update(1)
            self.refresh_pbr.set_description(message)

    def reprocess_masks(self):
        if getattr(self, "refresh_worker", None) is not None:
            print("Mask reprocessing already running.")
            return

        self.refresh_pbr = progress(total=len(self.model.get_data_pool()), desc="Reprocessing Masks")
        self.refresh_worker = QtUNetRefreshMasks(self.model)

        self.refresh_thread = QThread()
        self.refresh_worker.moveToThread(self.refresh_thread)

        self.refresh_thread.started.connect(self.refresh_worker.run)
        self.refresh_worker.update.connect(self.update_masks)
        self.refresh_worker.finished.connect(self.finished_masks)

        self.refresh_worker.finished.connect(self.refresh_thread.quit)

        self.set_active_ui(False)
        self.refresh_thread.finished.connect(lambda: self.set_active_ui(True))

        self.refresh_thread.start()
        print("Mask reprocessing started.")

    def finished_masks(self):
        if self.refresh_pbr is not None:
            try:
                self.refresh_pbr.close()
            except Exception:
                pass
            self.refresh_pbr = None

        if self.refresh_worker is not None:
            try:
                self.refresh_worker.stop()
            except Exception:
                pass

        if self.refresh_thread is not None:
            if self.refresh_thread.isRunning():
                self.refresh_thread.quit()
                self.refresh_thread.wait(5000)
        self.refresh_worker = None
        self.refresh_thread = None
        print("Mask reprocessing finished")
        self.update_image_selection()

    def update_input_folder(self, folder):
        folder = Path(folder)
        self.input_line.setText(str(folder))
        try:
            self.model.set_input_folder(folder)
            self.input_line.setStyleSheet(f"color: green;")
            self.update_inputs_list()
        except Exception as e:
            self.input_line.setStyleSheet(f"color: red;")
            print(f"Error updating input folder: {e}")

    def update_output_folder(self, folder):
        folder = Path(folder)
        self.output_line.setText(str(folder))
        try:
            self.model.set_output_folder(folder)
            self.output_line.setStyleSheet(f"color: green;")
            self.update_image_selection()
        except Exception as e:
            self.output_line.setStyleSheet(f"color: red;")
            print(f"Error updating output folder: {e}")

    def update_model_folder(self, folder):
        folder = Path(folder)
        self.model_line.setText(str(folder))
        try:
            self.model.set_model_folder(folder)
            self.model_line.setStyleSheet(f"color: green;")
        except Exception as e:
            self.model_line.setStyleSheet(f"color: red;")
            print(f"Error updating model folder: {e}")

    def update_inputs_list(self):
        inputs = self.model.get_data_pool()
        self.image_combo.clear()
        if len(inputs) == 0:
            self.image_combo.addItems(["-----"])
        else:
            self.image_combo.addItems(sorted(list(inputs)))
        self.image_combo.setCurrentIndex(0)
    
    def show_image(self, name):
        input_path = Path(self.input_line.text())
        img_path = input_path / name
        print("ORIGINAL", img_path)
        if not img_path.exists() or not img_path.is_file():
            return
        data = load_tiff(img_path)
        if _IMAGE_LAYER in self.viewer.layers:
            self.viewer.layers[_IMAGE_LAYER].data = data
        else:
            self.viewer.add_image(data, name=_IMAGE_LAYER, colormap='gray', contrast_limits=[0, np.percentile(data, 99.9)])

    def show_proba(self, name):
        output_path = Path(self.output_line.text())
        proba_path = output_path / ("proba-" + name)
        print("PROBA", proba_path)
        if not proba_path.exists() or not proba_path.is_file():
            if _PROBA_LAYER in self.viewer.layers and _IMAGE_LAYER in self.viewer.layers:
                data = np.zeros_like(self.viewer.layers[_IMAGE_LAYER].data)
            else:
                return
        else:
            data = load_tiff(proba_path)
        if _PROBA_LAYER in self.viewer.layers:
            self.viewer.layers[_PROBA_LAYER].data = data
        else:
            self.viewer.add_image(data, name=_PROBA_LAYER, colormap='magenta', contrast_limits=[0, 1.0], blending='additive', visible=False)

    def show_mask(self, name):
        output_path = Path(self.output_line.text())
        mask_path = output_path / name
        print("MASK", mask_path)
        if not mask_path.exists() or not mask_path.is_file():
            if _MASK_LAYER in self.viewer.layers and _IMAGE_LAYER in self.viewer.layers:
                data = np.zeros_like(self.viewer.layers[_IMAGE_LAYER].data, dtype=np.uint8)
            else:
                return
        else:
            data = load_tiff(mask_path)
        if _MASK_LAYER in self.viewer.layers:
            self.viewer.layers[_MASK_LAYER].data = data
        else:
            self.viewer.add_labels(data, name=_MASK_LAYER)

def launch_dev_procedure():
    viewer = napari.Viewer()
    widget = UNet2DInferenceWidget(viewer=viewer)
    viewer.window.add_dock_widget(widget)

    # widget.update_input_folder("/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1/inputs")
    # widget.update_output_folder("/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1/bce-cosine-inference")
    # widget.update_model_folder("/home/clement/Documents/projects/mifobio-2025/processed/unet_models/bce-cosine")

    napari.run()


if __name__ == "__main__":
    launch_dev_procedure()
