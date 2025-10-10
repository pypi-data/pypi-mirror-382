from pathlib import Path
import numpy as np
import tifffile

from napari_unet.data_control import _TIFF_REGEX, load_tiff
from napari_unet.losses import (get_bce_loss, get_focal_loss, get_tversky_loss, 
                                get_dice_loss, get_bce_dice_loss, get_cl_dice_loss, 
                                get_bce_cl_dice_loss, get_tversky_cl_dice_loss)
from napari_unet.tiles.tiler import normalize, ImageTiler2D

from keras.models import load_model

class UNet2DInference(object):
    def __init__(self):
        self.input_folder  = None
        self.output_folder = None
        self.model_folder  = None
        self.patch_size    = 256
        self.overlap       = 64
        self.batch_size    = 8
        self.threshold     = 0.5
        self.data_pool     = set([])
        self.unet_model    = None

    def set_input_folder(self, path):
        p = Path(path)
        if not p.exists() or not p.is_dir():
            raise ValueError(f"Input folder {path} does not exist or is not a folder.")
        self.input_folder = p
        self.probe_input_folder()
        print(f"Input folder set to: {self.input_folder}")

    def get_input_folder(self):
        return self.input_folder
    
    def set_output_folder(self, path):
        p = Path(path)
        if not p.exists():
            p.mkdir(parents=True)
        elif not p.is_dir():
            raise ValueError(f"Output folder {path} is not a folder.")
        self.output_folder = p
        print(f"Output folder set to: {self.output_folder}")

    def get_output_folder(self):
        return self.output_folder
    
    def set_model_folder(self, path):
        p = Path(path)
        if not p.exists() or not p.is_dir():
            raise ValueError(f"Model folder {path} does not exist or is not a folder.")
        self.model_folder = p
        self.get_model_path()
        print(f"Model folder set to: {self.model_folder}")
    
    def get_model_folder(self):
        return self.model_folder
    
    def set_patch_size(self, size):
        if not isinstance(size, int) or size <= 0:
            raise ValueError("Patch size must be a positive integer.")
        self.patch_size = size
        print(f"Patch size set to: {self.patch_size}")

    def get_patch_size(self):
        return self.patch_size
    
    def set_overlap(self, overlap):
        if not isinstance(overlap, int) or overlap < 0:
            raise ValueError("Overlap must be a non-negative integer.")
        if overlap >= self.patch_size:
            raise ValueError("Overlap must be smaller than patch size.")
        self.overlap = overlap
        print(f"Overlap set to: {self.overlap}")
    
    def get_overlap(self):
        return self.overlap
    
    def set_batch_size(self, batch_size):
        if not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError("Batch size must be a positive integer.")
        self.batch_size = batch_size
        print(f"Batch size set to: {self.batch_size}")

    def get_batch_size(self):
        return self.batch_size
    
    def set_threshold(self, threshold):
        if not isinstance(threshold, (int, float)) or not (0.0 <= threshold <= 1.0):
            raise ValueError("Threshold must be a float between 0 and 1.")
        self.threshold = threshold
        print(f"Threshold set to: {self.threshold}")

    def get_threshold(self):
        return self.threshold
    
    def probe_input_folder(self):
        if self.input_folder is None:
            raise ValueError("Input folder is not set.")
        pool = set([i for i in self.input_folder.iterdir() if i.is_file()])
        pool = set([i.name for i in pool if _TIFF_REGEX.match(i.name)])
        self.data_pool = pool

    def get_data_pool(self):
        if len(self.data_pool) == 0:
            self.probe_input_folder()
        return self.data_pool
    
    def get_model_path(self):
        if self.model_folder is None:
            raise ValueError("Model folder is not set.")
        model_path = self.model_folder / "best.keras"
        if not model_path.exists() or not model_path.is_file():
            raise ValueError(f"Model file {model_path} does not exist or is not a file.")
        return model_path
    
    def load_model(self):
        model_path = self.get_model_path()
        print(f"Loading model from: {model_path}")
        self.unet_model = load_model(
            model_path,
            custom_objects={
                "bce_loss"            : get_bce_loss({}),
                "focal_loss"          : get_focal_loss({}),
                "tversky_loss"        : get_tversky_loss({}),
                "dice_loss"           : get_dice_loss({}),
                "bce_dice_loss"       : get_bce_dice_loss({}),
                "cl_dice_loss"        : get_cl_dice_loss({}),
                "bce_cl_dice_loss"    : get_bce_cl_dice_loss({}),
                "tversky_cl_dice_loss": get_tversky_cl_dice_loss({})
            }
        )
        print("Model loaded successfully.")

    def refresh_masks(self, callback=None):
        if self.output_folder is None:
            raise ValueError("Output folder is not set.")
        if len(self.data_pool) == 0:
            self.probe_input_folder()
        if len(self.data_pool) == 0:
            raise ValueError(f"No TIFF files found in input folder {self.input_folder}.")
        
        print(f"Reprocessing masks in {self.output_folder} with threshold {self.threshold}")
        for rank, file_name in enumerate(sorted(list(self.data_pool)), start=1):
            print(f"[{str(rank).zfill(2)}/{str(len(self.data_pool)).zfill(2)}] Reprocessing file: {file_name}")
            output_path = self.output_folder / file_name
            proba_path = output_path.parent / ("proba-" + file_name)
            if not proba_path.exists() or not proba_path.is_file():
                print(f"  Probability map {proba_path} does not exist. Skipping.")
                continue
            if callback is not None:
                callback(file_name)
            pm = load_tiff(proba_path)
            mask = (pm >= self.threshold).astype(np.uint8)
            tifffile.imwrite(output_path, mask)
        print("Mask reprocessing complete.")
    
    def run_inference(self, callback=None):
        if self.input_folder is None:
            raise ValueError("Input folder is not set.")
        if self.output_folder is None:
            raise ValueError("Output folder is not set.")
        if self.model_folder is None:
            raise ValueError("Model folder is not set.")
        if len(self.data_pool) == 0:
            self.probe_input_folder()
        if len(self.data_pool) == 0:
            raise ValueError(f"No TIFF files found in input folder {self.input_folder}.")
        
        self.load_model()
        if self.unet_model is None:
            raise ValueError("Model is not loaded. Call load_model() first.")

        print(f"Processing {len(self.data_pool)} files from {self.input_folder} to {self.output_folder}")
        for rank, file_name in enumerate(sorted(list(self.data_pool)), start=1):
            print(f"[{str(rank).zfill(2)}/{str(len(self.data_pool)).zfill(2)}] Processing file: {file_name}")
            if callback is not None:
                callback(file_name)
            input_path = self.input_folder / file_name
            output_path = self.output_folder / file_name
            image = load_tiff(input_path)
            shape = image.shape
            tiles_manager = ImageTiler2D(self.patch_size, self.overlap, shape)
            input_unet = normalize(image, 0.0, 1.0, np.float32)
            tiles = np.array(tiles_manager.image_to_tiles(input_unet, False))
            predictions = np.squeeze(self.unet_model.predict(tiles, batch_size=self.batch_size))
            pm = tiles_manager.tiles_to_image(predictions)
            tifffile.imwrite(output_path.parent / ("proba-" + file_name), pm)
            mask = (pm >= self.threshold).astype(np.uint8)
            tifffile.imwrite(output_path, mask)
        print("Inference complete.")

if __name__ == "__main__":
    inference = UNet2DInference()
    inference.set_input_folder("/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1/inputs")
    inference.set_output_folder("/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1/bce-cosine-inference")
    inference.set_model_folder("/home/clement/Documents/projects/mifobio-2025/processed/unet_models/bce-cosine")
    inference.set_patch_size(256)
    inference.set_overlap(64)
    inference.set_batch_size(8)
    inference.set_threshold(0.1)
    inference.run_inference()