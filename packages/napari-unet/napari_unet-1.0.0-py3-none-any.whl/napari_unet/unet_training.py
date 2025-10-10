from pathlib import Path
import numpy as np
import random
import json
import shutil
from pprint import pprint

from napari_unet.datasets import open_pair
from napari_unet.data_control import (get_sanity_checks, get_data_pools,
                                      get_shape, load_tiff)
from napari_unet.data_augment import (get_data_augmentation_pipeline, 
                                      get_n_versions)
from napari_unet.architecture import (SavePredictionsCallback, create_unet2d_model,
                                      get_cosine_annealing_scheduler,
                                      get_reduce_lr_on_plateau, EpochTickCallback)
from napari_unet.losses import (get_bce_loss, get_focal_loss, get_tversky_loss, 
                                get_dice_loss, get_bce_dice_loss, get_cl_dice_loss, 
                                get_bce_cl_dice_loss, get_tversky_cl_dice_loss)
from napari_unet.plotting import find_metric_pairs, plot_metrics

import tensorflow as tf
from keras.optimizers import Adam, RMSprop, SGD
from keras.callbacks import (ModelCheckpoint, EarlyStopping)
from keras.metrics import Precision, Recall, Accuracy
from keras.models import load_model

def available_optimizers():
    return {
        "Adam"   : Adam,
        "RMSprop": RMSprop,
        "SGD"    : SGD
    }

def available_losses():
    return {
        "BCE"             : get_bce_loss,
        "Focal"           : get_focal_loss,
        "Tversky"         : get_tversky_loss,
        "Dice"            : get_dice_loss,
        "BCE + Dice"      : get_bce_dice_loss,
        "clDice"          : get_cl_dice_loss,
        "BCE + clDice"    : get_bce_cl_dice_loss,
        "Tversky + clDice": get_tversky_cl_dice_loss
    }

def available_schedulers():
    return {
        "CosineDecay"    : get_cosine_annealing_scheduler,
        "ReduceOnPlateau": get_reduce_lr_on_plateau
    }

class UNet2DTrainer(object):

    def __init__(self):
        self.data_folder    = None
        self.qc_folder      = None
        self.models_folder  = None
        self.working_folder = None
        self.inputs_name    = "inputs"
        self.gt_name        = "masks"
        self.model_prefix   = "unet"

        self.validation_split = 0.15
        self.batch_size       = 8
        self.epochs           = 500
        self.unet_depth       = 4
        self.initial_filters  = 32
        self.dropout          = 0.5
        self.optimizer_name   = "Adam"
        self.learning_rate    = 0.001
        self.loss_name        = "BCE + clDice"
        self.early_stopping   = 50
        self.start_from_prev  = False
        self.attention_gates  = False
        self.scheduler_name   = "CosineDecay"
        self.imgs_per_epoch   = 0.33

        self.use_mirroring         = True
        self.use_gaussian_noise    = True
        self.noise_scale           = 0.0005
        self.use_random_rotations  = True
        self.angle_range           = (-90, 90)
        self.use_gamma_correction  = True
        self.gamma_range           = (0.2, 5.0)
        self.use_holes             = True
        self.holes_percentage      = 0.01

        self.current_working_folder = None
        self.unet_model             = None
        self.data_partition         = {
            'training'  : set([]), 
            'validation': set([])
        }

    def set_images_per_epoch(self, value):
        if not (0.0 < value <= 1.0):
            raise ValueError("Images per epoch must be a number between 0 and 1.")
        self.imgs_per_epoch = float(value)
        print(f"Images per epoch set to: {self.imgs_per_epoch}")

    def get_images_per_epoch(self):
        return self.imgs_per_epoch
    
    def make_data_partition(self):
        data_pools, _ = get_data_pools(self.data_folder, [self.inputs_name, self.gt_name], True)
        all_items = set([p.name for p in data_pools[0]])
        n_items = len(all_items)
        n_validation = int(self.validation_split * n_items)
        val_items = set(list(np.random.choice(list(all_items), n_validation)))
        trn_items = all_items - val_items
        self.data_partition['training'] = trn_items
        self.data_partition['validation'] = val_items
        print(f"Using {len(trn_items)} items for training, and {len(val_items)} for validation.")

    def get_invalid_data(self):
        results = {}
        checks = get_sanity_checks()
        for name, func in checks.items():
            results[name] = func(self.data_folder, [self.inputs_name, self.gt_name])
        final_results = {}
        for test, pool in results.items():
            for file, value in pool.items():
                entry = file.name
                row = final_results.get(entry, {})
                row[test] = row.get(test, True) and value
                final_results[entry] = row
        for values in final_results.values():
            for key in checks.keys():
                values.setdefault(key, False)
        return final_results
    
    def remove_invalid_data(self):
        if self.data_folder is None:
            raise ValueError("Data folder must be set before removing invalid data.")
        results = self.get_invalid_data()
        inputs_folder = self.data_folder / self.inputs_name
        gt_folder     = self.data_folder / self.gt_name
        to_remove = [k for k, v in results.items() if not all(v.values())]
        for file in to_remove:
            input_path = inputs_folder / file
            gt_path    = gt_folder / file
            if input_path.is_file():
                print(f"Removing {input_path}")
                input_path.unlink()
            if gt_path.is_file():
                print(f"Removing {gt_path}")
                gt_path.unlink()
        return results

    def reach_inputs(self):
        if not self.data_folder or not self.inputs_name:
            return False
        i_path = self.data_folder / self.inputs_name
        if not i_path.is_dir():
            return False
        return True
    
    def reach_gt(self):
        if not self.data_folder or not self.gt_name:
            return False
        gt_path = self.data_folder / self.gt_name
        if not gt_path.is_dir():
            return False
        return True
    
    def set_scheduler_name(self, name):
        if not isinstance(name, str) or not name:
            raise ValueError("Scheduler name must be a non-empty string.")
        if name not in available_schedulers():
            raise ValueError(f"Scheduler '{name}' is not recognized. Available schedulers: {list(available_schedulers().keys())}")
        self.scheduler_name = name
        print(f"Scheduler set to: {self.scheduler_name}")

    def get_scheduler_name(self):
        return self.scheduler_name
    
    def set_models_prefix(self, prefix):
        if not prefix or len(prefix.strip()) == 0:
            raise ValueError("Model prefix cannot be empty.")
        self.model_prefix = prefix.strip()
        print(f"Model prefix set to: {self.model_prefix}")

    def get_models_prefix(self):
        return self.model_prefix

    def set_attention_gates(self, use_attention):
        self.attention_gates = use_attention
        print(f"Attention gates set to: {self.attention_gates}")

    def get_attention_gates(self):
        return self.attention_gates

    def set_inputs_name(self, name):
        if not self.data_folder:
            raise ValueError("Data folder must be set before setting input name pattern.")
        if not name:
            raise ValueError("Input name pattern cannot be empty.")
        
        i_path = self.data_folder / name
        if not i_path.is_dir():
            raise ValueError(f"Input folder {i_path} does not exist or is not a directory.")
        self.inputs_name = name
        print(f"Input folder set to: {self.inputs_name}")

        if self.qc_folder:
            qc_i_path = self.qc_folder / name
            if qc_i_path.is_dir() and i_path == qc_i_path:
                raise ValueError("Input folder and QC folder cannot be the same.")

    def get_inputs_name(self):
        return self.inputs_name
    
    def set_gt_name(self, name):
        if not self.data_folder:
            raise ValueError("Data folder must be set before setting ground truth name pattern.")
        if not name:
            raise ValueError("Ground truth name pattern cannot be empty.")
        
        gt_path = self.data_folder / name
        if not gt_path.is_dir():
            raise ValueError(f"Ground truth folder {gt_path} does not exist or is not a directory.")
        self.gt_name = name
        print(f"Ground truth folder set to: {self.gt_name}")

        if self.qc_folder:
            qc_gt_path = self.qc_folder / name
            if qc_gt_path.is_dir() and gt_path == qc_gt_path:
                raise ValueError("Ground truth folder and QC folder cannot be the same.")
    
    def get_gt_name(self):
        return self.gt_name

    def set_data_folder(self, path):
        if path is None:
            raise ValueError("Data folder path cannot be None.")
        df = Path(path)
        if not df.is_dir():
            raise ValueError(f"Data folder {path} does not exist or is not a directory.")
        if (self.qc_folder is not None) and (df == self.qc_folder):
            raise ValueError("Data folder and QC folder cannot be the same.")
        self.data_folder = df
        print(f"Data folder set to: {self.data_folder}")
    
    def get_data_folder(self):
        return self.data_folder
    
    def set_qc_folder(self, path):
        if path is None:
            raise ValueError("QC folder path cannot be None.")
        qc = Path(path)
        if not qc.is_dir():
            raise ValueError(f"QC folder {path} does not exist or is not a directory.")
        if self.data_folder is not None and self.data_folder == qc:
            raise ValueError("Data folder and QC folder cannot be the same.")
        self.qc_folder = qc
        print(f"QC folder set to: {self.qc_folder}")

    def get_qc_folder(self):
        return self.qc_folder
        
    def set_models_folder(self, path):
        if path is None:
            raise ValueError("Models folder path cannot be None.")
        mf = Path(path)
        if not mf.is_dir():
            raise ValueError(f"Models folder {path} does not exist or is not a directory.")
        self.models_folder = mf
        print(f"Models folder set to: {self.models_folder}")

    def get_models_folder(self):
        return self.models_folder
    
    def set_working_folder(self, path):
        if path is None:
            raise ValueError("Working folder path cannot be None.")
        wf = Path(path)
        if not wf.is_dir():
            raise ValueError(f"Working folder {path} does not exist or is not a directory.")
        self.working_folder = wf
        print(f"Working folder set to: {self.working_folder}")

    def get_working_folder(self):
        return self.working_folder
    
    def set_validation_split(self, value):
        if not (0 < value < 1):
            raise ValueError("Validation split must be between 0 and 1.")
        self.validation_split = value
        print(f"Validation split set to: {self.validation_split}")

    def get_validation_split(self):
        return self.validation_split

    def set_batch_size(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Batch size must be a positive integer.")
        self.batch_size = value
        print(f"Batch size set to: {self.batch_size}")

    def get_batch_size(self):
        return self.batch_size

    def set_epochs(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Epochs must be a positive integer.")
        self.epochs = value
        print(f"Epochs set to: {self.epochs}")

    def get_epochs(self):
        return self.epochs

    def set_unet_depth(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("UNet depth must be a positive integer.")
        self.unet_depth = value
        print(f"UNet depth set to: {self.unet_depth}")

    def get_unet_depth(self):
        return self.unet_depth

    def set_initial_filters(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Initial filters must be a positive integer.")
        self.initial_filters = value
        print(f"Initial filters set to: {self.initial_filters}")

    def get_initial_filters(self):
        return self.initial_filters

    def set_dropout(self, value):
        if not (0 <= value <= 1):
            raise ValueError("Dropout must be between 0 and 1.")
        self.dropout = value
        print(f"Dropout set to: {self.dropout}")

    def get_dropout(self):
        return self.dropout

    def set_optimizer_name(self, value):
        if not isinstance(value, str) or not value:
            raise ValueError("Optimizer name must be a non-empty string.")
        if value not in available_optimizers():
            raise ValueError(f"Optimizer '{value}' is not recognized. Available optimizers: {list(available_optimizers().keys())}")
        self.optimizer_name = value
        print(f"Optimizer set to: {self.optimizer_name}")

    def get_optimizer_name(self):
        return self.optimizer_name

    def set_learning_rate(self, value):
        if not (isinstance(value, float) or isinstance(value, int)) or value <= 0:
            raise ValueError("Learning rate must be a positive number.")
        self.learning_rate = float(value)
        print(f"Learning rate set to: {self.learning_rate}")

    def get_learning_rate(self):
        return self.learning_rate

    def set_loss_name(self, value):
        if not isinstance(value, str):
            raise ValueError("Loss function must be a string.")
        if value not in available_losses():
            raise ValueError(f"Loss function '{value}' is not recognized. Available losses: {list(available_losses().keys())}")
        self.loss_name = value
        print(f"Loss function set to: {self.loss_name}")

    def get_loss_name(self):
        return self.loss_name

    def set_early_stopping(self, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError("Early stopping must be a non-negative integer.")
        self.early_stopping = value
        print(f"Early stopping set to: {self.early_stopping}")

    def get_early_stopping(self):
        return self.early_stopping

    def set_start_from_prev(self, value):
        if not isinstance(value, bool):
            raise ValueError("Start from previous must be a boolean.")
        self.start_from_prev = value
        print(f"Start from previous model set to: {self.start_from_prev}")

    def get_start_from_prev(self):
        return self.start_from_prev
    
    def set_use_mirroring(self, value):
        if not isinstance(value, bool):
            raise ValueError("use_mirroring must be a boolean.")
        self.use_mirroring = value
        print(f"Use mirroring set to: {self.use_mirroring}")

    def get_use_mirroring(self):
        return self.use_mirroring

    def set_use_gaussian_noise(self, value):
        if not isinstance(value, bool):
            raise ValueError("use_gaussian_noise must be a boolean.")
        self.use_gaussian_noise = value
        print(f"Use Gaussian noise set to: {self.use_gaussian_noise}")

    def get_use_gaussian_noise(self):
        return self.use_gaussian_noise

    def set_noise_scale(self, value):
        if not (isinstance(value, float) or isinstance(value, int)) or value < 0:
            raise ValueError("noise_scale must be a non-negative number.")
        self.noise_scale = float(value)
        print(f"Noise scale set to: {self.noise_scale}")

    def get_noise_scale(self):
        return self.noise_scale

    def set_use_random_rotations(self, value):
        if not isinstance(value, bool):
            raise ValueError("use_random_rotations must be a boolean.")
        self.use_random_rotations = value
        print(f"Use random rotations set to: {self.use_random_rotations}")

    def get_use_random_rotations(self):
        return self.use_random_rotations

    def set_angle_range(self, value):
        if (not isinstance(value, tuple) or len(value) != 2 or
            not all(isinstance(v, (int, float)) for v in value)):
            raise ValueError("angle_range must be a tuple of two numbers.")
        self.angle_range = value
        print(f"Angle range set to: {self.angle_range}")

    def get_angle_range(self):
        return self.angle_range

    def set_use_gamma_correction(self, value):
        if not isinstance(value, bool):
            raise ValueError("use_gamma_correction must be a boolean.")
        self.use_gamma_correction = value
        print(f"Use gamma correction set to: {self.use_gamma_correction}")

    def get_use_gamma_correction(self):
        return self.use_gamma_correction

    def set_gamma_range(self, value):
        if (not isinstance(value, tuple) or len(value) != 2 or
            not all(isinstance(v, (int, float)) for v in value) or
            value[0] <= 0 or value[1] <= 0 or value[0] > value[1]):
            raise ValueError("gamma_range must be a tuple of two positive numbers (min <= max).")
        self.gamma_range = value
        print(f"Gamma range set to: {self.gamma_range}")

    def get_gamma_range(self):
        return self.gamma_range

    def set_use_holes(self, value):
        if not isinstance(value, bool):
            raise ValueError("use_holes must be a boolean.")
        self.use_holes = value
        print(f"Use holes set to: {self.use_holes}")

    def get_use_holes(self):
        return self.use_holes

    def set_holes_percentage(self, value):
        if not (isinstance(value, float) or isinstance(value, int)) or not (0 <= value <= 1):
            raise ValueError("holes_percentage must be a number between 0 and 1.")
        self.holes_percentage = float(value)
        print(f"Holes percentage set to: {self.holes_percentage}")

    def get_holes_percentage(self):
        return self.holes_percentage
    
    def get_augmented_sample(self, n_samples=1, n_versions=1):
        if self.data_folder is None or self.inputs_name is None or self.gt_name is None:
            raise ValueError("Data folder, inputs name, and ground truth name must be set before getting augmented samples.")
        settings = self.get_augmentation_settings()
        data_pools, _ = get_data_pools(self.data_folder, [self.inputs_name, self.gt_name], True)
        if len(data_pools) == 0:
            raise ValueError("No data found to augment.")
        versions = {}
        items = np.random.choice(list(data_pools[0]), n_samples)
        items = [i.name for i in items]
        for im_name in items:
            input_path = self.data_folder / self.inputs_name / im_name
            mask_path  = self.data_folder / self.gt_name / im_name
            images, masks = get_n_versions(settings, input_path, mask_path, n=n_versions)
            versions[im_name] = (images, masks)
        return versions

    def get_augmentation_settings(self):
        return {
            "use": {
                "mirroring"       : self.use_mirroring,
                "random_rotations": self.use_random_rotations,
                "holes"           : self.use_holes,
                "gamma_correction": self.use_gamma_correction,
                "gaussian_noise"  : self.use_gaussian_noise
            },
            "mirroring": {
                "horizontal": True,
                "vertical"  : True
            },
            "random_rotations": {
                "angle_start": self.angle_range[0] if self.angle_range else -180,
                "angle_end"  : self.angle_range[1] if self.angle_range else 180
            },
            "holes": {
                "percentage": self.holes_percentage
            },
            "gamma_correction": {
                "gamma_start": self.gamma_range[0] if self.gamma_range else 0.7,
                "gamma_end"  : self.gamma_range[1] if self.gamma_range else 1.5
            },
            "gaussian_noise": {
                "noise_scale": self.noise_scale
            }
        }
    
    def pairs_generator(self, src_set, training=False, img_only=False):
        src_set = src_set.decode("utf-8")
        if self.data_folder is None:
            raise ValueError(f"No data folder defined yet.")
        dataset = list(self.data_partition[src_set])
        apply_augmentation_fx = get_data_augmentation_pipeline(self.get_augmentation_settings()) if training else None
        # while True:
        i = 0
        random.shuffle(dataset)
        while i < len(dataset):
            input_path = self.data_folder / self.inputs_name / dataset[i]
            mask_path  = self.data_folder / self.gt_name     / dataset[i]
            yield open_pair(input_path, mask_path, img_only, apply_augmentation_fx)
            i += 1
    
    def qc_pairs_generator(self):
        if self.data_folder is None:
            raise ValueError("No data folder defined yet.")

        files = sorted(self.data_partition["validation"])
        for fname in files:
            input_path = self.data_folder / self.inputs_name / fname
            mask_path  = self.data_folder / self.gt_name     / fname
            yield open_pair(input_path, mask_path, img_only=False, apply_data_augmentation=None)

    def probe_proportions(self):
        if not self.data_folder:
            raise ValueError("The data folder is required to probe for proportions")
        if not self.gt_name:
            raise ValueError("The name of the folder containing the GT is required.")
        fg, total = 0, 0
        for image_name in self.data_partition["training"]:
            mask_path = self.data_folder / self.gt_name / image_name
            if not mask_path.is_file():
                continue
            img = load_tiff(mask_path)
            fg += np.sum(img)
            total += img.size
        return fg / total if total > 0 else 0.0

    def make_dataset(self, source, training=False, img_only=False):
        shape = get_shape(self.data_folder, self.inputs_name)
        output_signature=tf.TensorSpec(shape=shape, dtype=tf.float32, name=None)
        
        if not img_only:
            output_signature = (output_signature, tf.TensorSpec(shape=shape, dtype=tf.float32, name=None))
        
        ds = tf.data.Dataset.from_generator(
            self.pairs_generator,
            args=(source, training, img_only),
            output_signature=output_signature
        )
        
        return ds
    
    def qc_make_dataset(self):
        shape = get_shape(self.data_folder, self.inputs_name)
        output_signature = (
            tf.TensorSpec(shape=shape, dtype=tf.float32),
            tf.TensorSpec(shape=shape, dtype=tf.float32),
        )

        ds = tf.data.Dataset.from_generator(
            self.qc_pairs_generator,
            output_signature=output_signature
        )
        return ds
    
    def get_version(self):
        """
        Used to auto-increment the version number of the model.
        Since each model is saved in a separate folder, we need to find the latest version number.
        Starts at 1 when the destination folder is empty.

        Returns:
            int: The next version number, that doesn't exist yet in the models folder.
        """
        if not self.models_folder:
            raise RuntimeError("A folder for the models must be set")
        models_path = self.models_folder
        model_name_prefix = self.model_prefix
        content = sorted([f.name for f in models_path.iterdir() if f.name.startswith(model_name_prefix) and f.is_dir()])
        if len(content) == 0:
            return 1
        else:
            return int(content[-1].split('-')[-1].replace('V', '')) + 1

    def get_model_path(self):
        if self.models_folder is None:
            raise RuntimeError("A folder for the models must be set")
        v = self.get_version()
        version_name = f"{self.model_prefix}-V{str(v).zfill(3)}"
        output_path = self.models_folder / version_name
        output_path.mkdir(parents=True, exist_ok=True)
        with open(output_path / "version.txt", "w") as f:
            f.write(version_name)
        return output_path

    def init_from_prev(self):
        if self.unet_model is None:
            raise RuntimeError("Model has not been instantiated. Cannot initialize from previous.")
        if self.models_folder is None:
            raise RuntimeError("A folder for the models must be set")
        v = self.get_version() - 1
        if v < 1:
            raise RuntimeError("No previous model version found to initialize from.")
        version_name = f"{self.model_prefix}-V{str(v).zfill(3)}"
        model_path = self.models_folder / version_name / 'best.keras'
        if not model_path.is_file():
            raise RuntimeError(f"Previous model file {model_path} does not exist.")
        print(f"Initializing model weights from: {model_path}")

        pretrained = load_model(str(model_path), compile=False)
        self.unet_model.set_weights(pretrained.get_weights())

    def instanciate_model(self):
        input_shape = get_shape(self.data_folder, self.inputs_name)
        if input_shape is None:
            raise ValueError("Input shape could not be determined. Please provide it manually.")
        model = create_unet2d_model(
            input_shape, 
            self.get_unet_depth(), 
            self.get_initial_filters(), 
            self.get_dropout(), 
            self.get_attention_gates()
        )
        if self.start_from_prev:
            try:
                self.init_from_prev()
            except Exception:
                print("Could not initialize from previous model. Proceeding with random initialization.")
        optz = available_optimizers().get(self.get_optimizer_name(), Adam)
        loss_settings = {
            "fg-proportion": self.probe_proportions()
        }
        pprint(loss_settings)
        loss_gettr = available_losses().get(self.get_loss_name(), get_bce_loss)
        loss_fx = loss_gettr(loss_settings)
        model.compile(
            optimizer=optz(self.learning_rate),
            loss=loss_fx, 
            metrics=[
                Precision(),
                Recall(),
                Accuracy()
            ]
        )
        self.unet_model = model

    def save_settings_as_json(self, model_path):
        settings = {
            "data_folder"       : str(self.data_folder) if self.data_folder else None,
            "qc_folder"         : str(self.qc_folder) if self.qc_folder else None,
            "models_folder"     : str(self.models_folder) if self.models_folder else None,
            "working_folder"    : str(self.working_folder) if self.working_folder else None,
            "inputs_name"       : self.inputs_name,
            "gt_name"           : self.gt_name,
            "model_prefix"      : self.model_prefix,
            "validation_split"  : self.validation_split,
            "batch_size"        : self.batch_size,
            "epochs"            : self.epochs,
            "unet_depth"        : self.unet_depth,
            "initial_filters"   : self.initial_filters,
            "dropout"           : self.dropout,
            "optimizer_name"    : self.optimizer_name,
            "learning_rate"     : self.learning_rate,
            "loss_name"         : self.loss_name,
            "early_stopping"    : self.early_stopping,
            "scheduler_name"    : self.scheduler_name,
            "start_from_prev"   : self.start_from_prev,
            "attention_gates"   : self.attention_gates,
            "use_mirroring"         : self.use_mirroring,
            "use_gaussian_noise"    : self.use_gaussian_noise,
            "noise_scale"           : self.noise_scale,
            "use_random_rotations"  : self.use_random_rotations,
            "angle_range"           : self.angle_range,
            "use_gamma_correction"  : self.use_gamma_correction,
            "gamma_range"           : self.gamma_range,
            "use_holes"             : self.use_holes,
            "holes_percentage"      : self.holes_percentage
        }
        with open(model_path / "settings.json", "w") as f:
            json.dump(settings, f, indent=4)

    def save_partition_as_json(self, model_path):
        as_json = {k: list(v) for k, v in self.data_partition.items()}
        with open(model_path / "data_partition.json", "w") as f:
            json.dump(as_json, f, indent=4)

    def reset_predictions(self):
        if not self.working_folder:
            return
        preds_path = self.working_folder / "predictions"
        if preds_path.is_dir():
            shutil.rmtree(preds_path)
            preds_path.mkdir(parents=True, exist_ok=True)

    def train(self, callback_fx=None):
        model_path = self.get_model_path()
        print(f"💾 Exporting model to: {model_path}")
        self.make_data_partition()
        self.instanciate_model()
        checkpoint = ModelCheckpoint(model_path / 'best.keras', save_best_only=True, monitor='val_loss', mode='min')
        lastpoint = ModelCheckpoint(model_path / 'last.keras', save_best_only=False, monitor='val_loss', mode='min')
        early_stopping = EarlyStopping(monitor='val_loss', patience=self.get_early_stopping(), mode='min')
        schedule_gettr = available_schedulers().get(self.scheduler_name, get_cosine_annealing_scheduler)
        lr_callback = schedule_gettr(self.learning_rate, self.get_epochs())
        self.reset_predictions()
        
        B = self.get_batch_size()
        N = int(self.imgs_per_epoch * len(self.data_partition["training"]))
        K = int(self.imgs_per_epoch * len(self.data_partition["validation"]))
        training_dataset   = self.make_dataset("training", True).repeat().batch(B).take(N//B)
        validation_dataset = self.make_dataset("validation", False).repeat().batch(B).take(K//B)
        print(f"   • Training dataset: {len(list(training_dataset))} ({training_dataset}).")
        print(f"   • Validation dataset: {len(list(validation_dataset))} ({validation_dataset}).")

        self.save_settings_as_json(model_path)
        self.save_partition_as_json(model_path)

        save_preds = SavePredictionsCallback(
            model_path, 
            self.working_folder if self.working_folder else model_path, 
            lambda: self.qc_make_dataset()
        )

        if self.unet_model is None:
            raise RuntimeError("Model has not been instantiated. Cannot proceed with training.")
        
        callbacks = [checkpoint, lastpoint, early_stopping, lr_callback, save_preds]
        if callback_fx is not None:
            callbacks.append(EpochTickCallback(callback_fx))

        history = self.unet_model.fit(
            training_dataset,
            validation_data=validation_dataset,
            epochs=self.get_epochs(),
            callbacks=callbacks,
            verbose=2
        )

        history = history.history
        print("Training complete.")
        pairs = find_metric_pairs(list(history.keys()))
        metrics_folder = model_path / "metrics_plots"
        out = plot_metrics(history, pairs, out_dir=metrics_folder)
        print("Saved:", out)


if __name__ == "__main__":
    trainer = UNet2DTrainer()
    trainer.set_data_folder("/path/to/data")
    trainer.set_models_folder("/path/to/models")
    trainer.set_working_folder("/path/to/working")
    trainer.set_inputs_name("inputs")
    trainer.set_gt_name("masks")
    trainer.set_models_prefix("unet")
    trainer.set_epochs(100)
    trainer.set_batch_size(4)
    trainer.set_unet_depth(4)
    trainer.set_initial_filters(32)
    trainer.set_dropout(0.5)
    trainer.set_optimizer_name("Adam")
    trainer.set_learning_rate(0.001)
    trainer.set_loss_name("Tversky + clDice")
    trainer.set_early_stopping(10)
    trainer.set_scheduler_name("CosineDecay")
    trainer.set_start_from_prev(False)
    trainer.set_attention_gates(False)
    
    # Data augmentation settings
    trainer.set_use_mirroring(True)
    trainer.set_use_gaussian_noise(True)
    trainer.set_noise_scale(0.0005)
    trainer.set_use_random_rotations(True)
    trainer.set_angle_range((-90, 90))
    trainer.set_use_gamma_correction(True)
    trainer.set_gamma_range((0.2, 5.0))
    trainer.set_use_holes(True)
    trainer.set_holes_percentage(0.01)

    # Remove invalid data before training
    invalid_data_report = trainer.remove_invalid_data()
    pprint(invalid_data_report)

    # Start training
    trainer.train()