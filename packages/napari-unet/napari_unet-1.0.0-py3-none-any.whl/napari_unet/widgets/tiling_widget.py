from qtpy.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QButtonGroup,
                            QSpinBox, QHBoxLayout, QPushButton, 
                            QFileDialog, QComboBox, QLabel, QRadioButton,
                            QCheckBox, QSpinBox, QSlider, QLineEdit)

from PyQt5.QtCore import Qt

from PyQt5.QtGui import QFont, QDoubleValidator

import napari
from napari.utils.notifications import show_info
from napari.utils import progress

import math
import os
import re
import random
import tifffile

from napari_unet.data_control import load_tiff
from napari_unet import TIFF_REGEX
from napari_unet.tiles.tiler import ImageTiler2D

_DEFAULT_PATCH_SIZE = 512
_DEFAULT_OVERLAP    = 128

_PREVIEW_IMAGE_LAYER = "Whole-image"
_PREVIEW_SHAPE_LAYER = "Tile-box"
_FOLDER_MOSAIC_LAYER = "Folder-mosaic"

class TilesCreatorWidget(QWidget):
    
    def __init__(self, viewer=None, parent=None):
        super().__init__(parent)
        # Get the current viewer instance
        viewer = viewer or napari.current_viewer()
        if viewer is None:
            raise ValueError("No Napari viewer instance found.")
        self.viewer = viewer
        # Size (in pixels) of the tiles to be exported
        self.patch_size = _DEFAULT_PATCH_SIZE
        # Overlap (in pixels) between the tiles
        self.overlap = _DEFAULT_OVERLAP
        # Path of the folder containing the TIFF to convert in tiles.
        self.in_path = None
        # Path of the folder where the tiles will be exported.
        self.out_path = None
        # Font used to draw emojis as icons
        self.ui_font = QFont("Arial Unicode MS, Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji")
        self.main_layout = QVBoxLayout()
        self.init_ui()

    # -------- UI: ----------------------------------

    def init_ui(self):
        self.setLayout(self.main_layout)
        self.media_control_panel()
        self.normalization_panel()
        self.configure_tiles_panel()
        self.export_tiles_group()
    
    def media_control_panel(self):
        media_control_group = QGroupBox("Media Control")
        layout = QVBoxLayout()

        # Reset button
        self.clear_state_button = QPushButton("❌ Clear state")
        self.clear_state_button.setFont(self.ui_font)
        self.clear_state_button.clicked.connect(self.clear_state)
        layout.addWidget(self.clear_state_button)

        # Some vertical spacing
        layout.addSpacing(20)

        # Load button
        self.load_button = QPushButton("📂 Load")
        self.load_button.setFont(self.ui_font)
        self.load_button.clicked.connect(self.load_folder)
        layout.addWidget(self.load_button)

        # Number of images label
        self.n_sources_label = QLabel("Sources: ---")
        self.n_sources_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.n_sources_label)

        # Detected shape label
        self.shape_label = QLabel("Shape: (XXX, XXX)")
        self.shape_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.shape_label)

        media_control_group.setLayout(layout)
        self.main_layout.addWidget(media_control_group)

    def normalization_panel(self):
        self.normalization_group = QGroupBox("Normalization")
        layout = QVBoxLayout()

        self.use_normalization = QCheckBox("Use normalization")
        self.use_normalization.setChecked(True)
        self.use_normalization.stateChanged.connect(self.update_normalization)
        layout.addWidget(self.use_normalization)

        # Lower and upper bounds inputs float
        h_layout = QHBoxLayout()
        self.bounds_label = QLabel("Bounds:")

        float_validator = QDoubleValidator()
        float_validator.setNotation(QDoubleValidator.StandardNotation)

        self.lower_bound_input = QLineEdit()
        self.lower_bound_input.setValidator(float_validator)
        self.lower_bound_input.setText("0.0")

        self.upper_bound_input = QLineEdit()
        self.upper_bound_input.setValidator(float_validator)
        self.upper_bound_input.setText("1.0")

        h_layout.addWidget(self.bounds_label)
        h_layout.addWidget(self.lower_bound_input)
        h_layout.addWidget(self.upper_bound_input)
        layout.addLayout(h_layout)

        # Output type
        h_layout = QHBoxLayout()
        self.out_type_label = QLabel("Output type:")
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["float32", "uint8", "uint16"])
        h_layout.addWidget(self.out_type_label)
        h_layout.addWidget(self.type_dropdown)
        layout.addLayout(h_layout)

        # Output file format
        h_layout = QHBoxLayout()
        self.format_label = QLabel("Output format:")
        self.format_dropdown = QComboBox()
        self.format_dropdown.addItems([".tif", ".png", ".jpg"])
        h_layout.addWidget(self.format_label)
        h_layout.addWidget(self.format_dropdown)
        layout.addLayout(h_layout)

        self.normalization_group.setLayout(layout)
        self.main_layout.addWidget(self.normalization_group)
    
    def configure_tiles_panel(self):
        self.tiles_group = QGroupBox("Tiles configuration")
        layout = QVBoxLayout()

        # Patch size
        h_layout = QHBoxLayout()
        patch_size_label = QLabel("Patch size:")
        self.patch_size_input = QSpinBox()
        self.patch_size_input.setRange(1, 10000)
        self.patch_size_input.setValue(_DEFAULT_PATCH_SIZE)
        self.patch_size_input.valueChanged.connect(self.update_patch_size)
        h_layout.addWidget(patch_size_label)
        h_layout.addWidget(self.patch_size_input)
        layout.addLayout(h_layout)

        # Overlap size
        h_layout = QHBoxLayout()
        overlap_label = QLabel("Overlap:")
        self.overlap_input = QSpinBox()
        self.overlap_input.setRange(1, 10000)
        self.overlap_input.setValue(_DEFAULT_OVERLAP)
        self.overlap_input.valueChanged.connect(self.update_overlap)
        h_layout.addWidget(overlap_label)
        h_layout.addWidget(self.overlap_input)
        layout.addLayout(h_layout)

        # Preview tiles button
        self.tilesButton = QPushButton("💡 Preview tiles")
        self.tilesButton.setFont(self.ui_font)
        self.tilesButton.clicked.connect(self.preview_tiles)
        layout.addWidget(self.tilesButton)

        # Slider to change the preview layout/box
        h_layout = QHBoxLayout()
        self.preview_slider = QSlider(Qt.Horizontal)
        self.preview_slider.setMinimum(0)
        self.preview_slider.setMaximum(0)
        self.preview_slider.setValue(0)
        self.preview_slider.setTickInterval(1)
        self.preview_slider.setTickPosition(QSlider.TicksBelow)
        self.preview_slider.valueChanged.connect(self.update_patch_preview)
        h_layout.addWidget(self.preview_slider)
        self.slider_value_label = QLabel("0")
        h_layout.addWidget(self.slider_value_label)
        layout.addLayout(h_layout)

        # Show all checkbox
        self.show_all_tiles = QCheckBox("Show all tiles")
        self.show_all_tiles.stateChanged.connect(self.update_show_all_tiles)
        layout.addWidget(self.show_all_tiles)

        self.tiles_group.setLayout(layout)
        self.main_layout.addWidget(self.tiles_group)
    
    def export_tiles_group(self):
        self.export_group = QGroupBox("Export configuration")
        layout = QVBoxLayout()

        # Select export folder button
        self.exportFolderButton = QPushButton("📂 Select export folder")
        self.exportFolderButton.setFont(self.ui_font)
        self.exportFolderButton.clicked.connect(self.choose_folder)
        layout.addWidget(self.exportFolderButton)

        # Empty export folder button
        self.emptyFolderButton = QPushButton("🗑️ Empty export folder")
        self.emptyFolderButton.setFont(self.ui_font)
        self.emptyFolderButton.clicked.connect(self.empty_folder)
        layout.addWidget(self.emptyFolderButton)

        # Export tiles button
        self.exportButton = QPushButton("📦 Export tiles")
        self.exportButton.setFont(self.ui_font)
        self.exportButton.clicked.connect(self.export_tiles)
        layout.addWidget(self.exportButton)

        self.export_group.setLayout(layout)
        self.main_layout.addWidget(self.export_group)
    
    # -------- CALLBACKS: ------------------------------

    def clear_state(self):
        self.patch_size = _DEFAULT_PATCH_SIZE
        self.overlap    = _DEFAULT_OVERLAP
        self.in_path    = None
        self.out_path   = None
        self.lower_bound_input.setText("0.0")
        self.upper_bound_input.setText("1.0")
        self.use_normalization.setChecked(True)
        self.update_normalization()
        self.update_patch_size()
        self.update_overlap()
        if _FOLDER_MOSAIC_LAYER in self.viewer.layers:
            l = self.viewer.layers[_FOLDER_MOSAIC_LAYER]
            self.viewer.layers.remove(l)
        if _PREVIEW_IMAGE_LAYER in self.viewer.layers:
            l = self.viewer.layers[_PREVIEW_IMAGE_LAYER]
            self.viewer.layers.remove(l)
        if _PREVIEW_SHAPE_LAYER in self.viewer.layers:
            l = self.viewer.layers[_PREVIEW_SHAPE_LAYER]
            self.viewer.layers.remove(l)
        self.shape_label.setText("Shape: (XXX, XXX)")
        self.n_sources_label.setText("Sources: ---")

    def load_folder(self):
        """
        Prompts the use to select a folder containing TIFF images.
        """
        folder_path = QFileDialog.getExistingDirectory(self, "Select sources folder")
        if (folder_path is None) or (folder_path == ""):
            return
        self.set_sources_folder(folder_path)
    
    def update_normalization(self):
        active = self.use_normalization.isChecked()
        self.lower_bound_input.setEnabled(active)
        self.upper_bound_input.setEnabled(active)
        self.bounds_label.setEnabled(active)

    def update_patch_size(self):
        self.patch_size = int(self.patch_size_input.value())

    def update_overlap(self):
        self.overlap = int(self.overlap_input.value())
    
    def reset_preview_boxes(self):
        """
        Each bounding box is stored in its own layer for the preview.
        One of the images to which they correspond are is displayed below them.
        This function removes all the bounding boxes and the image.
        """
        names = [layer.name for layer in self.viewer.layers]
        # The bounding-box layers
        for name in names:
            if name.startswith(_PREVIEW_SHAPE_LAYER):
                l = self.viewer.layers[name]
                self.viewer.layers.remove(l)
        # The whole image layer
        if _PREVIEW_IMAGE_LAYER in self.viewer.layers:
            l = self.viewer.layers[_PREVIEW_IMAGE_LAYER]
            self.viewer.layers.remove(l)
        # The data sample layer
        if _FOLDER_MOSAIC_LAYER in self.viewer.layers:
            l = self.viewer.layers[_FOLDER_MOSAIC_LAYER]
            self.viewer.layers.remove(l)

    def pick_random_image(self):
        """
        Returns the name (not the path) of a random TIFF file from the input folder.
        """
        tiff_list = [f for f in os.listdir(self.in_path) if re.match(TIFF_REGEX, f)]
        random.shuffle(tiff_list)
        return tiff_list[0]
    
    def is_setup_ready(self):
        # Is the input folder path correctly configured
        if (self.in_path is None) or (self.in_path == ""):
            show_info("Please select a folder with tiff images.")
            return False
        # Did we configure the tiles (size and overlap)?
        if (self.patch_size is None) or (self.overlap is None):
            show_info("Please configure the tiles first.")
            return False
        return True

    def preview_tiles(self):
        if not self.is_setup_ready():
            show_info("Please configure the tiles first.")
            return

        self.reset_preview_boxes()
        # Open random image to show tiles over it.
        im_data = load_tiff(os.path.join(self.in_path, self.pick_random_image()))
        self.viewer.add_image(im_data, name=_PREVIEW_IMAGE_LAYER, colormap='gray')
        tiler = ImageTiler2D(self.patch_size, self.overlap, im_data.shape)

        if tiler.get_layout() is None:
            show_info("Could not compute the layout. Please check the tile configuration.")
            return

        rectangles = []
        for tile in tiler.get_layout():
            rectangles.append(tile.as_napari_rectangle())
        colors = ['red'] + ['transparent' for _ in range(len(rectangles)-1)]
        
        l = self.viewer.add_shapes(
            rectangles, 
            name=_PREVIEW_SHAPE_LAYER, 
            face_color='transparent', 
            edge_color=colors, 
            edge_width=4
        )
        l.editable = False

        # The slider allows to hide the boxes and show them one by one.
        show_info(f"Cut {len(tiler.get_layout())} tiles from the image.")
        self.preview_slider.setMinimum(0)
        self.preview_slider.setMaximum(len(tiler.get_layout())-1)
        self.update_patch_preview()
    
    def update_patch_preview(self):
        """
        Function allowing to show only one bounding box at a time.
        Bounding boxes are stored in layers with names starting with _PREVIEW_SHAPE_LAYER.
        There is the possibility to show them all at once with a checkbox.
        In this case, the active one shows up red and the others blue.
        """
        index = int(self.preview_slider.value())
        self.slider_value_label.setText(str(index))
        if _PREVIEW_SHAPE_LAYER not in self.viewer.layers:
            return
        layer    = self.viewer.layers[_PREVIEW_SHAPE_LAYER]
        main_clr = 'red' if not self.show_all_tiles.isChecked() else 'blue'
        other    = 'blue' if self.show_all_tiles.isChecked() else 'transparent'
        colors   = [main_clr if i == index else other for i in range(len(layer.data))]
        layer.edge_color = colors
    
    def update_show_all_tiles(self):
        """
        Function allowing to show all the bounding boxes at once.
        """
        status = self.show_all_tiles.isChecked()
        self.preview_slider.setEnabled(not status)
        self.update_patch_preview()

    def choose_folder(self):
        """
        Function to choose the folder where the tiles will be exported.
        Prompts the user to select a folder.
        """
        folder_path = QFileDialog.getExistingDirectory(self, "Select export folder")
        if (folder_path is None) or (folder_path == ""):
            return
        if self.in_path == folder_path:
            show_info("Please select a folder different from the input folder.")
            return
        self.out_path = folder_path

    def empty_folder(self):
        """
        Removes every file located in the previously selected export folder.
        """
        if self.out_path is None or self.out_path == "":
            return
        content = os.listdir(self.out_path)
        for item in content:
            if os.path.isfile(os.path.join(self.out_path, item)):
                os.remove(os.path.join(self.out_path, item))

    def export_tiles(self):
        """
        Converts all the content of the input folder to tiles.
        The tiles are exported to the previously selected output folder.
        """
        tifffiles = [f for f in os.listdir(self.in_path) if re.match(TIFF_REGEX, f)]
        if len(tifffiles) == 0:
            show_info("No tiff files found in the selected folder.")
            return
        if not self.is_setup_ready():
            show_info("Please configure the tiles first.")
            return
        if (self.out_path is None) or (self.out_path == ""):
            show_info("Please select an export folder.")
            return
        lower_bound = None # For global normalization
        upper_bound = None
        use_norm = False
        if self.use_normalization.isChecked():
            use_norm = True
            lower_bound = float(self.lower_bound_input.text())
            upper_bound = float(self.upper_bound_input.text())
        for img in progress(tifffiles, "Exporting tiles..."):
            im_data = load_tiff(os.path.join(self.in_path, img))
            tiler = ImageTiler2D(self.patch_size, self.overlap, im_data.shape)
            tiles = tiler.image_to_tiles(im_data, use_norm, lower_bound, upper_bound)
            for i, tile in enumerate(tiles):
                tile_name = TIFF_REGEX.match(img).group(1) + f"_{str(i).zfill(3)}.tif"
                tifffile.imwrite(os.path.join(self.out_path, tile_name), tile)
        

    # -------- METHODS: ----------------------------------

    def probe_folder_shape(self, tifffiles):
        """
        The goal here is to determine if a folder contains images of the same shape.
        If it doesn't, a warning is raised.
        No error is signaled as a new ImageTiler2D object will be created for each image.
        """
        shape = None
        same = True
        for tiff in tifffiles:
            data = load_tiff(os.path.join(self.in_path, tiff))
            if shape is None:
                shape = data.shape
            elif shape != data.shape:
                same = False
                break
        if same:
            self.shape_label.setText(f"Shape: {shape}")
        else:
            self.shape_label.setText("Shape: ⚠️ Different shapes")

    def set_sources_folder(self, folder_path):
        """
        Expects the path to a folder containing tiff images.
        """
        tiff_list = sorted([f for f in os.listdir(folder_path) if re.match(TIFF_REGEX, f)])
        if len(tiff_list) == 0:
            show_info("No tiff files found in the selected folder.")
            return
        self.in_path = folder_path
        self.n_sources_label.setText(f"Sources: {len(tiff_list)}")
        self.probe_folder_shape(tiff_list)
    
    def mosaic_shape(self, items):
        """
        Given a list of items, we want to determine the shape of the mosaic.
        We want a mosaic as close as possible to a square.
        The content of the 'items' list doesn't matter, it is not taken into account.
        """
        sqrt_N = math.sqrt(len(items))
        rows = math.floor(sqrt_N)
        cols = math.ceil(sqrt_N)
        if rows * cols < len(items):
            rows += 1
        return rows, cols

    def lower_resolution(self, img_height, img_width, max_size=512):
        """
        When we build a mosaic of images to show what's in the input folder, we want to keep the size of the images reasonable.
        So we downscale everything we find to have a size (per image) of 512 pixels on the largest side.
        """
        while (img_height > max_size) or (img_width > max_size):
            img_height //= 2
            img_width //= 2
        return img_height, img_width


def launch_dev_procedure():
    viewer = napari.Viewer()

    widget = TilesCreatorWidget(viewer=viewer)
    # widget.set_sources_folder("/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1/inputs")
    # widget.patch_size_input.setValue(256)
    # widget.overlap_input.setValue(64)

    viewer.window.add_dock_widget(widget)
    napari.run()

if __name__ == "__main__":
    launch_dev_procedure()