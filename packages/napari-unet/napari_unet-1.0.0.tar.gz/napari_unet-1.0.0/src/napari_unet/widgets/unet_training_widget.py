import os
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QTabWidget,
                            QGroupBox, QHBoxLayout, QLabel, 
                            QComboBox, QCheckBox, QLineEdit, 
                            QPushButton, QFileDialog, QDoubleSpinBox
)
from qtpy.QtCore import Qt, QThread

import napari
from napari.utils import progress

import numpy as np

from napari_unet.unet_training import (UNet2DTrainer, available_optimizers, 
                                       available_losses, available_schedulers)

from napari_unet.result_tables import DataSanityResultsTable
from napari_unet.qt_workers import QtUNetTraining
from napari_unet.data_control import load_tiff

_AUGMENTATION_PREFIX = "augmented-"
_EPOCH_PREFIX        = "epoch_"
_ORIGINAL_LAYER_NAME = "original"
_GT_LAYER_NAME       = "ground-truth"

class UNetTrainingWidget(QWidget):

    def __init__(self, viewer=None, parent=None):
        super().__init__(parent)
        viewer = viewer or napari.current_viewer()
        if viewer is None:
            raise ValueError("No Napari viewer instance found.")
        
        self.viewer = viewer
        self.model = UNet2DTrainer()
        self.rt = None
        self.training_thread = None
        self.training_worker = None
        self.training_pbr = None
        self.init_ui()

    def init_ui(self):
        # Main layout with a tab widget
        self.main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Build tabs and add them
        io_tab = self.init_io_ui()
        training_tab = self.init_training_ui()
        augmentation_tab = self.init_augmentation_ui()
        control_tab = self.init_control_ui()

        self.tabs.addTab(io_tab, "I/O")
        self.tabs.addTab(training_tab, "Training")
        self.tabs.addTab(augmentation_tab, "Augmentation")
        self.tabs.addTab(control_tab, "Control")

    def init_io_ui(self):
        # --- I/O TAB ---
        page = QWidget()
        io_layout = QVBoxLayout(page)

        # Data folder
        data_layout = QHBoxLayout()
        data_label = QLabel("Data Folder:")
        self.data_line_edit = QLineEdit("")
        self.data_browse_btn = QPushButton("Browse")
        self.data_browse_btn.clicked.connect(self.browse_data_folder)
        data_layout.addWidget(data_label)
        data_layout.addWidget(self.data_line_edit)
        data_layout.addWidget(self.data_browse_btn)
        io_layout.addLayout(data_layout)

        # Models folder
        models_layout = QHBoxLayout()
        models_label = QLabel("Models Folder:")
        self.models_line_edit = QLineEdit("")
        self.models_browse_btn = QPushButton("Browse")
        self.models_browse_btn.clicked.connect(self.browse_models_folder)
        models_layout.addWidget(models_label)
        models_layout.addWidget(self.models_line_edit)
        models_layout.addWidget(self.models_browse_btn)
        io_layout.addLayout(models_layout)

        # Working folder
        working_layout = QHBoxLayout()
        working_label = QLabel("Working Folder:")
        self.working_line_edit = QLineEdit("")
        self.working_browse_btn = QPushButton("Browse")
        self.working_browse_btn.clicked.connect(self.browse_working_folder)
        working_layout.addWidget(working_label)
        working_layout.addWidget(self.working_line_edit)
        working_layout.addWidget(self.working_browse_btn)
        io_layout.addLayout(working_layout)

        # Input name
        input_name_layout = QHBoxLayout()
        input_name_label = QLabel("Input Folder:")
        self.input_name_line_edit = QLineEdit("")
        self.input_name_line_edit.textChanged.connect(self.update_inputs_name)
        self.input_name_line_edit.setText(self.model.get_inputs_name() or "")
        input_name_layout.addWidget(input_name_label)
        input_name_layout.addWidget(self.input_name_line_edit)
        io_layout.addLayout(input_name_layout)

        # Ground truth name
        gt_name_layout = QHBoxLayout()
        gt_name_label = QLabel("Ground Truth Folder:")
        self.gt_name_line_edit = QLineEdit("")
        self.gt_name_line_edit.textChanged.connect(self.update_gt_name)
        self.gt_name_line_edit.setText(self.model.get_gt_name() or "")
        gt_name_layout.addWidget(gt_name_label)
        gt_name_layout.addWidget(self.gt_name_line_edit)
        io_layout.addLayout(gt_name_layout)

        # Models prefix
        model_prefix_layout = QHBoxLayout()
        model_prefix_label = QLabel("Model Prefix:")
        self.model_prefix_line_edit = QLineEdit("")
        self.model_prefix_line_edit.textChanged.connect(self.update_models_prefix)
        self.model_prefix_line_edit.setText(self.model.get_models_prefix())
        model_prefix_layout.addWidget(model_prefix_label)
        model_prefix_layout.addWidget(self.model_prefix_line_edit)
        io_layout.addLayout(model_prefix_layout)

        io_layout.addStretch(1)
        return page

    def init_training_ui(self):
        # --- TRAINING TAB ---
        page = QWidget()
        training_layout = QVBoxLayout(page)

        # Validation split
        val_split_layout = QHBoxLayout()
        val_split_label = QLabel("Validation Split:")
        self.val_split_spin = QDoubleSpinBox()
        self.val_split_spin.setRange(0.0, 100.0)
        self.val_split_spin.setSingleStep(1.0)
        self.val_split_spin.setValue(self.model.get_validation_split() * 100)
        self.val_split_spin.setSuffix("%")
        self.val_split_spin.valueChanged.connect(self.update_validation_split)
        val_split_layout.addWidget(val_split_label)
        val_split_layout.addWidget(self.val_split_spin)
        training_layout.addLayout(val_split_layout)

        # Batch size
        batch_layout = QHBoxLayout()
        batch_label = QLabel("Batch Size:")
        self.batch_spin = QDoubleSpinBox()
        self.batch_spin.setRange(1, 1024)
        self.batch_spin.setSingleStep(1)
        self.batch_spin.setDecimals(0)
        self.batch_spin.setValue(self.model.get_batch_size())
        self.batch_spin.valueChanged.connect(self.update_batch_size)
        batch_layout.addWidget(batch_label)
        batch_layout.addWidget(self.batch_spin)
        training_layout.addLayout(batch_layout)

        # Epochs
        epochs_layout = QHBoxLayout()
        epochs_label = QLabel("Epochs:")
        self.epochs_spin = QDoubleSpinBox()
        self.epochs_spin.setRange(1, 10000)
        self.epochs_spin.setSingleStep(1)
        self.epochs_spin.setDecimals(0)
        self.epochs_spin.setValue(self.model.get_epochs())
        self.epochs_spin.valueChanged.connect(self.update_epochs)
        epochs_layout.addWidget(epochs_label)
        epochs_layout.addWidget(self.epochs_spin)
        training_layout.addLayout(epochs_layout)

        # UNet depth
        depth_layout = QHBoxLayout()
        depth_label = QLabel("UNet Depth:")
        self.depth_spin = QDoubleSpinBox()
        self.depth_spin.setRange(1, 10)
        self.depth_spin.setSingleStep(1)
        self.depth_spin.setDecimals(0)
        self.depth_spin.setValue(self.model.get_unet_depth())
        self.depth_spin.valueChanged.connect(self.update_unet_depth)
        depth_layout.addWidget(depth_label)
        depth_layout.addWidget(self.depth_spin)
        training_layout.addLayout(depth_layout)

        # Initial filters
        filters_layout = QHBoxLayout()
        filters_label = QLabel("Initial Filters:")
        self.filters_spin = QDoubleSpinBox()
        self.filters_spin.setRange(1, 256)
        self.filters_spin.setSingleStep(1)
        self.filters_spin.setDecimals(0)
        self.filters_spin.setValue(self.model.get_initial_filters())
        self.filters_spin.valueChanged.connect(self.update_initial_filters)
        filters_layout.addWidget(filters_label)
        filters_layout.addWidget(self.filters_spin)
        training_layout.addLayout(filters_layout)

        # Dropout
        dropout_layout = QHBoxLayout()
        dropout_label = QLabel("Dropout:")
        self.dropout_spin = QDoubleSpinBox()
        self.dropout_spin.setRange(0.0, 100.0)
        self.dropout_spin.setSingleStep(1.0)
        self.dropout_spin.setValue(self.model.get_dropout() * 100)
        self.dropout_spin.valueChanged.connect(self.update_dropout)
        self.dropout_spin.setSuffix("%")
        dropout_layout.addWidget(dropout_label)
        dropout_layout.addWidget(self.dropout_spin)
        training_layout.addLayout(dropout_layout)

        # Optimizer
        optimizer_layout = QHBoxLayout()
        optimizer_label = QLabel("Optimizer:")
        self.optimizer_combo = QComboBox()
        self.optimizer_combo.addItems(list(available_optimizers().keys()))
        self.optimizer_combo.setCurrentText(self.model.get_optimizer_name())
        self.optimizer_combo.currentTextChanged.connect(self.update_optimizer)
        optimizer_layout.addWidget(optimizer_label)
        optimizer_layout.addWidget(self.optimizer_combo)
        training_layout.addLayout(optimizer_layout)

        # Loss function
        loss_layout = QHBoxLayout()
        loss_label = QLabel("Loss Function:")
        self.loss_combo = QComboBox()
        self.loss_combo.addItems(list(available_losses().keys()))
        self.loss_combo.setCurrentText(self.model.get_loss_name())
        self.loss_combo.currentTextChanged.connect(self.update_loss_function)
        loss_layout.addWidget(loss_label)
        loss_layout.addWidget(self.loss_combo)
        training_layout.addLayout(loss_layout)

        # Scheduler
        scheduler_layout = QHBoxLayout()
        scheduler_label = QLabel("Scheduler:")
        self.scheduler_combo = QComboBox()
        self.scheduler_combo.addItems(list(available_schedulers().keys()))
        self.scheduler_combo.setCurrentText(self.model.get_scheduler_name())
        self.scheduler_combo.currentTextChanged.connect(self.update_scheduler)
        scheduler_layout.addWidget(scheduler_label)
        scheduler_layout.addWidget(self.scheduler_combo)
        training_layout.addLayout(scheduler_layout)

        # Learning rate
        lr_layout = QHBoxLayout()
        lr_label = QLabel("Learning Rate:")
        self.lr_spin = QDoubleSpinBox()
        self.lr_spin.setRange(1e-3, 0.2)
        self.lr_spin.setSingleStep(1e-3)
        self.lr_spin.setDecimals(4)
        self.lr_spin.setValue(self.model.get_learning_rate())
        self.lr_spin.valueChanged.connect(self.update_learning_rate)
        lr_layout.addWidget(lr_label)
        lr_layout.addWidget(self.lr_spin)
        training_layout.addLayout(lr_layout)

        # Early stopping
        early_layout = QHBoxLayout()
        early_label = QLabel("Early Stopping (epochs):")
        self.early_spin = QDoubleSpinBox()
        self.early_spin.setRange(1, 1000)
        self.early_spin.setSingleStep(1)
        self.early_spin.setDecimals(0)
        self.early_spin.setValue(self.model.get_early_stopping())
        self.early_spin.valueChanged.connect(self.update_early_stopping)
        early_layout.addWidget(early_label)
        early_layout.addWidget(self.early_spin)
        training_layout.addLayout(early_layout)

        # Percentage of images per epoch
        imgs_per_epoch_layout = QHBoxLayout()
        self.imgs_per_epoch_spin = QDoubleSpinBox()
        self.imgs_per_epoch_spin.setRange(0.0, 100.0)
        self.imgs_per_epoch_spin.setSingleStep(1.0)
        self.imgs_per_epoch_spin.setDecimals(1)
        self.imgs_per_epoch_spin.setValue(self.model.get_images_per_epoch() * 100.0)
        self.imgs_per_epoch_spin.valueChanged.connect(self.update_images_per_epoch)
        self.imgs_per_epoch_spin.setSuffix("%")
        imgs_per_epoch_layout.addWidget(QLabel("Images / Epoch:"))
        imgs_per_epoch_layout.addWidget(self.imgs_per_epoch_spin)
        training_layout.addLayout(imgs_per_epoch_layout)

        # Use attention gates
        self.attention_checkbox = QCheckBox("Use Attention Gates")
        self.attention_checkbox.setChecked(self.model.get_attention_gates())
        self.attention_checkbox.stateChanged.connect(self.update_attention_gates)
        training_layout.addWidget(self.attention_checkbox)

        training_layout.addStretch(1)
        return page

    def init_augmentation_ui(self):
        # --- AUGMENTATION TAB ---
        page = QWidget()
        aug_layout = QVBoxLayout(page)

        # Mirroring
        self.mirroring_checkbox = QCheckBox("Use Mirroring")
        self.mirroring_checkbox.setChecked(self.model.get_use_mirroring())
        self.mirroring_checkbox.stateChanged.connect(self.update_mirroring)
        aug_layout.addWidget(self.mirroring_checkbox)

        # Gaussian noise
        noise_layout = QHBoxLayout()
        self.noise_checkbox = QCheckBox("Use Gaussian Noise")
        self.noise_checkbox.setChecked(self.model.get_use_gaussian_noise())
        self.noise_checkbox.stateChanged.connect(self.update_gaussian_noise)
        noise_scale_label = QLabel("Noise Scale:")
        self.noise_scale_spin = QDoubleSpinBox()
        self.noise_scale_spin.setRange(0.0, 0.01)
        self.noise_scale_spin.setSingleStep(0.0001)
        self.noise_scale_spin.setDecimals(5)
        self.noise_scale_spin.setValue(self.model.get_noise_scale())
        self.noise_scale_spin.valueChanged.connect(self.update_noise_scale)
        noise_layout.addWidget(self.noise_checkbox)
        noise_layout.addWidget(noise_scale_label)
        noise_layout.addWidget(self.noise_scale_spin)
        aug_layout.addLayout(noise_layout)

        # Random rotations
        rot_layout = QHBoxLayout()
        self.rot_checkbox = QCheckBox("Use Random Rotations")
        self.rot_checkbox.setChecked(self.model.get_use_random_rotations())
        self.rot_checkbox.stateChanged.connect(self.update_random_rotations)
        angle_label = QLabel("Angle Range:")
        self.angle_min_spin = QDoubleSpinBox()
        self.angle_min_spin.setRange(-180, 180)
        self.angle_min_spin.setDecimals(0)
        self.angle_min_spin.setValue(self.model.get_angle_range()[0])
        self.angle_min_spin.valueChanged.connect(self.update_angle_range_start)
        self.angle_max_spin = QDoubleSpinBox()
        self.angle_max_spin.setRange(-180, 180)
        self.angle_max_spin.setDecimals(0)
        self.angle_max_spin.setValue(self.model.get_angle_range()[1])
        self.angle_max_spin.valueChanged.connect(self.update_angle_range_end)
        rot_layout.addWidget(self.rot_checkbox)
        rot_layout.addWidget(angle_label)
        rot_layout.addWidget(self.angle_min_spin)
        rot_layout.addWidget(QLabel("to"))
        rot_layout.addWidget(self.angle_max_spin)
        aug_layout.addLayout(rot_layout)

        # Gamma correction
        gamma_layout = QHBoxLayout()
        self.gamma_checkbox = QCheckBox("Use Gamma Correction")
        self.gamma_checkbox.setChecked(self.model.get_use_gamma_correction())
        self.gamma_checkbox.stateChanged.connect(self.update_gamma_correction)
        gamma_label = QLabel("Gamma Range:")
        self.gamma_min_spin = QDoubleSpinBox()
        self.gamma_min_spin.setRange(0.01, 10.0)
        self.gamma_min_spin.setDecimals(2)
        self.gamma_min_spin.setValue(self.model.get_gamma_range()[0])
        self.gamma_min_spin.valueChanged.connect(self.update_gamma_range_start)
        self.gamma_max_spin = QDoubleSpinBox()
        self.gamma_max_spin.setRange(0.01, 10.0)
        self.gamma_max_spin.setDecimals(2)
        self.gamma_max_spin.setValue(self.model.get_gamma_range()[1])
        self.gamma_max_spin.valueChanged.connect(self.update_gamma_range_end)
        gamma_layout.addWidget(self.gamma_checkbox)
        gamma_layout.addWidget(gamma_label)
        gamma_layout.addWidget(self.gamma_min_spin)
        gamma_layout.addWidget(QLabel("to"))
        gamma_layout.addWidget(self.gamma_max_spin)
        aug_layout.addLayout(gamma_layout)

        # Holes
        holes_layout = QHBoxLayout()
        self.holes_checkbox = QCheckBox("Use Holes")
        self.holes_checkbox.setChecked(self.model.get_use_holes())
        self.holes_checkbox.stateChanged.connect(self.update_holes)
        holes_label = QLabel("Holes Percentage:")
        self.holes_percentage_spin = QDoubleSpinBox()
        self.holes_percentage_spin.setRange(0.0, 50.0)
        self.holes_percentage_spin.setSingleStep(0.01)
        self.holes_percentage_spin.setDecimals(3)
        self.holes_percentage_spin.setValue(self.model.get_holes_percentage() * 100)
        self.holes_percentage_spin.valueChanged.connect(self.update_holes_percentage)
        self.holes_percentage_spin.setSuffix("%")
        holes_layout.addWidget(self.holes_checkbox)
        holes_layout.addWidget(holes_label)
        holes_layout.addWidget(self.holes_percentage_spin)
        aug_layout.addLayout(holes_layout)

        aug_layout.addStretch(1)
        return page

    def init_control_ui(self):
        # --- CONTROL TAB ---
        page = QWidget()
        control_layout = QVBoxLayout(page)

        # Remove invalid data checkbox and Inspect data button
        inspect_layout = QHBoxLayout()
        self.remove_invalid_checkbox = QCheckBox("Remove invalid data")
        self.remove_invalid_checkbox.setChecked(False)
        self.inspect_btn = QPushButton("Inspect Data")
        self.inspect_btn.clicked.connect(self.inspect_data)
        inspect_layout.addWidget(self.remove_invalid_checkbox)
        inspect_layout.addWidget(self.inspect_btn)
        control_layout.addLayout(inspect_layout)

        # Augmentation preview controls
        aug_preview_layout = QHBoxLayout()
        self.nb_samples_spin = QDoubleSpinBox()
        self.nb_samples_spin.setRange(1, 1000)
        self.nb_samples_spin.setDecimals(0)
        self.nb_samples_spin.setValue(5)
        self.nb_samples_spin.setSingleStep(1)
        nb_samples_label = QLabel("Nb samples:")

        self.nb_versions_spin = QDoubleSpinBox()
        self.nb_versions_spin.setRange(1, 100)
        self.nb_versions_spin.setDecimals(0)
        self.nb_versions_spin.setValue(3)
        self.nb_versions_spin.setSingleStep(1)
        nb_versions_label = QLabel("Nb versions:")

        self.aug_preview_btn = QPushButton("Augmentation Preview")
        self.aug_preview_btn.clicked.connect(self.show_augmentation_sample)

        aug_preview_layout.addWidget(nb_samples_label)
        aug_preview_layout.addWidget(self.nb_samples_spin)
        aug_preview_layout.addWidget(nb_versions_label)
        aug_preview_layout.addWidget(self.nb_versions_spin)
        aug_preview_layout.addWidget(self.aug_preview_btn)
        control_layout.addLayout(aug_preview_layout)

        # Start training with "Re-use last" checkbox
        train_layout = QHBoxLayout()
        self.reuse_last_checkbox = QCheckBox("Re-use last")
        self.start_train_btn = QPushButton("Start Training")
        self.start_train_btn.clicked.connect(self.launch_training)
        train_layout.addWidget(self.reuse_last_checkbox)
        train_layout.addWidget(self.start_train_btn)
        control_layout.addLayout(train_layout)

        control_layout.addStretch(1)
        return page


    # --- Callbacks ---

    def set_active_ui(self, active):
        self.data_line_edit.setEnabled(active)
        self.data_browse_btn.setEnabled(active)
        self.models_line_edit.setEnabled(active)
        self.models_browse_btn.setEnabled(active)
        self.working_line_edit.setEnabled(active)
        self.working_browse_btn.setEnabled(active)
        self.input_name_line_edit.setEnabled(active)
        self.gt_name_line_edit.setEnabled(active)
        self.model_prefix_line_edit.setEnabled(active)
        self.val_split_spin.setEnabled(active)
        self.batch_spin.setEnabled(active)
        self.epochs_spin.setEnabled(active)
        self.depth_spin.setEnabled(active)
        self.filters_spin.setEnabled(active)
        self.dropout_spin.setEnabled(active)
        self.optimizer_combo.setEnabled(active)
        self.loss_combo.setEnabled(active)
        self.scheduler_combo.setEnabled(active)
        self.lr_spin.setEnabled(active)
        self.early_spin.setEnabled(active)
        self.imgs_per_epoch_spin.setEnabled(active)
        self.attention_checkbox.setEnabled(active)
        self.mirroring_checkbox.setEnabled(active)
        self.noise_checkbox.setEnabled(active)
        self.noise_scale_spin.setEnabled(active and self.model.get_use_gaussian_noise())
        self.rot_checkbox.setEnabled(active)
        self.angle_min_spin.setEnabled(active and self.model.get_use_random_rotations())
        self.angle_max_spin.setEnabled(active and self.model.get_use_random_rotations())
        self.gamma_checkbox.setEnabled(active)
        self.gamma_min_spin.setEnabled(active and self.model.get_use_gamma_correction())
        self.gamma_max_spin.setEnabled(active and self.model.get_use_gamma_correction())
        self.holes_checkbox.setEnabled(active)
        self.holes_percentage_spin.setEnabled(active and self.model.get_use_holes())
        self.remove_invalid_checkbox.setEnabled(active)
        self.inspect_btn.setEnabled(active)
        self.nb_samples_spin.setEnabled(active)
        self.nb_versions_spin.setEnabled(active)
        self.aug_preview_btn.setEnabled(active)
        self.reuse_last_checkbox.setEnabled(active)
        self.start_train_btn.setEnabled(active)

    def browse_data_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Data Folder")
        if folder:
            self.update_data_folder(folder)

    def browse_models_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Models Folder")
        if folder:
            self.update_models_folder(folder)

    def browse_working_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Working Folder")
        if folder:
            self.update_working_folder(folder)

    def update_scheduler(self, text):
        self.model.set_scheduler_name(text)

    def update_data_folder(self, text):
        self.data_line_edit.setText(text)
        self.model.set_data_folder(text)
        self.input_name_line_edit.setStyleSheet(f"color: {'green' if self.model.reach_inputs() else 'red'};")
        self.gt_name_line_edit.setStyleSheet(f"color: {'green' if self.model.reach_gt() else 'red'};")

    def update_models_folder(self, text):
        self.models_line_edit.setText(text)
        self.model.set_models_folder(text)

    def update_working_folder(self, text):
        self.working_line_edit.setText(text)
        self.model.set_working_folder(text)
    
    def update_inputs_name(self, text):
        self.input_name_line_edit.setText(text)
        try:
            self.model.set_inputs_name(text)
            self.input_name_line_edit.setStyleSheet("color: green;")
        except Exception as e:
            print(f"Error updating inputs name: {e}")
            self.input_name_line_edit.setStyleSheet("color: red;")

    def update_gt_name(self, text):
        self.gt_name_line_edit.setText(text)
        try:
            self.model.set_gt_name(text)
            self.gt_name_line_edit.setStyleSheet("color: green;")
        except Exception as e:
            print(f"Error updating ground truth name: {e}")
            self.gt_name_line_edit.setStyleSheet("color: red;")

    def update_models_prefix(self, text):
        self.model_prefix_line_edit.setText(text)
        try:
            self.model.set_models_prefix(text)
            self.model_prefix_line_edit.setStyleSheet("color: green;")
        except Exception as e:
            print(f"Error updating model prefix: {e}")
            self.model_prefix_line_edit.setStyleSheet("color: red;")

    def update_validation_split(self, value):
        self.model.set_validation_split(float(value) / 100.0)

    def update_batch_size(self, value):
        self.model.set_batch_size(int(value))

    def update_epochs(self, value):
        self.model.set_epochs(int(value))

    def update_unet_depth(self, value):
        self.model.set_unet_depth(int(value))

    def update_initial_filters(self, value):
        self.model.set_initial_filters(int(value))

    def update_dropout(self, value):
        self.model.set_dropout(float(value) / 100.0)

    def update_optimizer(self, value):
        self.model.set_optimizer_name(value)

    def update_learning_rate(self, value):
        self.model.set_learning_rate(float(value))

    def update_early_stopping(self, value):
        self.model.set_early_stopping(int(value))

    def update_images_per_epoch(self, value):
        self.model.set_images_per_epoch(float(value) / 100.0)

    def update_attention_gates(self, value):
        self.model.set_attention_gates(bool(value))

    def update_loss_function(self, value):
        self.model.set_loss_name(value)

    def update_mirroring(self, value):
        a = bool(value)
        self.model.set_use_mirroring(a)

    def update_gaussian_noise(self, value):
        a = bool(value)
        self.model.set_use_gaussian_noise(a)
        self.noise_scale_spin.setEnabled(a)

    def update_noise_scale(self, value):
        self.model.set_noise_scale(float(value))

    def update_random_rotations(self, value):
        a = bool(value)
        self.model.set_use_random_rotations(a)
        self.angle_min_spin.setEnabled(a)
        self.angle_max_spin.setEnabled(a)

    def update_angle_range_start(self, value):
        angle_start = float(value)
        angle_end = self.model.get_angle_range()[1]
        if angle_start >= angle_end:
            angle_start = angle_end - 1
            self.angle_min_spin.setValue(angle_start)
        self.model.set_angle_range((angle_start, angle_end))

    def update_angle_range_end(self, value):
        angle_start = self.model.get_angle_range()[0]
        angle_end = float(value)
        if angle_end <= angle_start:
            angle_end = angle_start + 1
            self.angle_max_spin.setValue(angle_end)
        self.model.set_angle_range((angle_start, angle_end))

    def update_gamma_correction(self, value):
        a = bool(value)
        self.model.set_use_gamma_correction(a)
        self.gamma_min_spin.setEnabled(a)
        self.gamma_max_spin.setEnabled(a)

    def update_gamma_range_start(self, value):
        start_gamma = float(value)
        end_gamma = self.model.get_gamma_range()[1]
        if start_gamma >= end_gamma:
            start_gamma = end_gamma - 0.01
            self.gamma_min_spin.setValue(start_gamma)
        self.model.set_gamma_range((start_gamma, end_gamma))

    def update_gamma_range_end(self, value):
        end_gamma = float(value)
        start_gamma = self.model.get_gamma_range()[0]
        if end_gamma <= start_gamma:
            end_gamma = start_gamma + 0.01
            self.gamma_max_spin.setValue(end_gamma)
        self.model.set_gamma_range((start_gamma, end_gamma))

    def update_holes(self, value):
        a = bool(value)
        self.model.set_use_holes(a)
        self.holes_percentage_spin.setEnabled(a)

    def update_holes_percentage(self, value):
        self.model.set_holes_percentage(float(value) / 100.0)

    def inspect_data(self):
        if self.remove_invalid_checkbox.isChecked():
            results = self.model.remove_invalid_data()
        else:
            results = self.model.get_invalid_data()
        self.rt = DataSanityResultsTable(results)
        self.rt.show()

    def show_augmentation_sample(self):
        n_samples = int(self.nb_samples_spin.value())
        n_versions = int(self.nb_versions_spin.value())
        versions = self.model.get_augmented_sample(n_samples, n_versions)
        last_x = 0
        
        layer_names = [l.name for l in self.viewer.layers if l.name.startswith(_AUGMENTATION_PREFIX)]
        for ln in layer_names:
            l = self.viewer.layers[ln]
            self.viewer.layers.remove(l)

        for image_name, (images, masks) in versions.items():
            vertical_imgs = np.concatenate(images, axis=0)
            vertical_msks = np.concatenate(masks, axis=0)
            everything = np.concatenate((vertical_imgs, vertical_msks), axis=1)
            l = self.viewer.add_image(everything, name=_AUGMENTATION_PREFIX+image_name)
            l.translate = (0, last_x)
            last_x += everything.shape[1] + 20
    
    def reload_training_preview(self, epoch_idx, step=5):
        if epoch_idx % step != 0:
            return
        wd = self.model.get_working_folder()
        if wd is None:
            return
        preview_folder = wd / "predictions"
        if not preview_folder.exists() or not preview_folder.is_dir():
            return
        self.remove_augmentation_preview()
        epoch_path = preview_folder / f"epoch_{epoch_idx:03d}"
        if not epoch_path.exists() or not epoch_path.is_dir():
            return
        self.show_inputs(epoch_path)
        self.show_mask(epoch_path)
        self.show_prediction(epoch_path, epoch_idx, step)

    def show_inputs(self, pred_path):
        if _ORIGINAL_LAYER_NAME in self.viewer.layers:
            return
        content = sorted(list(pred_path.glob("input_*.tif")))
        items = [load_tiff(p) for p in content]
        horizontally = np.concatenate(items, axis=1)
        self.viewer.add_image(horizontally, name=_ORIGINAL_LAYER_NAME)

    def show_mask(self, pred_path):
        if _GT_LAYER_NAME in self.viewer.layers:
            return
        content = sorted(list(pred_path.glob("mask_*.tif")))
        items = [(load_tiff(p) > 0).astype(np.uint8) for p in content]
        horizontally = np.concatenate(items, axis=1)
        self.viewer.add_labels(horizontally, name=_GT_LAYER_NAME)

    def show_prediction(self, pred_path, index, step):
        content = sorted(list(pred_path.glob("prediction_*.tif")))
        if not content:
            return
        items = [load_tiff(p) for p in content]
        horizontally = np.concatenate(items, axis=1)
        self.viewer.add_image(
            horizontally, 
            name=f"{_EPOCH_PREFIX}{str(index).zfill(3)}",
            colormap="turbo",
            blending="additive",
            contrast_limits=[0, 1]
        )
        previous = f"{_EPOCH_PREFIX}{str(int(index-step)).zfill(3)}"
        if previous in self.viewer.layers:
            self.viewer.layers[previous].visible = False

    def update_training(self, epoch_idx):
        if self.training_pbr is not None:
            self.training_pbr.update(1)
            self.training_pbr.set_description(f"Epoch {epoch_idx+1}/{self.model.get_epochs()}")
        print("=== Epoch:", epoch_idx)
        self.reload_training_preview(epoch_idx)

    def launch_training(self):
        if self.training_worker is not None:
            print("Training is already running.")
            return

        self.training_pbr = progress(total=self.model.get_epochs(), desc="Running Training")
        self.training_worker = QtUNetTraining(self.model)

        self.training_thread = QThread()
        self.training_worker.moveToThread(self.training_thread)

        self.training_thread.started.connect(self.training_worker.run)
        self.training_worker.update.connect(self.update_training)
        self.training_worker.finished.connect(self.finished_training)

        self.training_worker.finished.connect(self.training_thread.quit)

        self.set_active_ui(False)
        self.training_thread.finished.connect(lambda: self.set_active_ui(True))

        self.training_thread.start()
        print("Training started.")

    def finished_training(self):
        if self.training_pbr is not None:
            try:
                self.training_pbr.close()
            except Exception:
                pass
            self.training_pbr = None

        if self.training_worker is not None:
            try:
                self.training_worker.stop()
            except Exception:
                pass

        if self.training_thread is not None:
            if self.training_thread.isRunning():
                self.training_thread.quit()
                self.training_thread.wait(5000)
        self.training_worker = None
        self.training_thread = None
        print("Training finished")

    def remove_augmentation_preview(self):
        layer_names = [l.name for l in self.viewer.layers if l.name.startswith(_AUGMENTATION_PREFIX)]
        for ln in layer_names:
            l = self.viewer.layers[ln]
            self.viewer.layers.remove(l)

def launch_dev_procedure():
    viewer = napari.Viewer()
    widget = UNetTrainingWidget(viewer=viewer)
    viewer.window.add_dock_widget(widget)

    widget.update_data_folder("/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1")
    widget.update_models_folder("/home/clement/Documents/projects/mifobio-2025/processed/unet_models")
    widget.update_working_folder("/home/clement/Documents/projects/mifobio-2025/processed/unet_working")
    widget.update_inputs_name("input-patches")
    widget.update_gt_name("mask1-patches")

    napari.run()

if __name__ == "__main__":
    launch_dev_procedure()