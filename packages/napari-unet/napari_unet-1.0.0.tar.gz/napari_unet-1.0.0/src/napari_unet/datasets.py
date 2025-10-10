import numpy as np
import tensorflow as tf
from napari_unet.data_control import load_tiff

def open_pair(input_path, mask_path, img_only, apply_data_augmentation=None):
    raw_img  = load_tiff(input_path)
    raw_mask = load_tiff(mask_path)
    raw_mask = raw_mask.astype(np.float32)
    if apply_data_augmentation is not None:
        raw_img, raw_mask = apply_data_augmentation(raw_img, raw_mask)
    raw_img  = np.expand_dims(raw_img, axis=-1)
    raw_mask = np.expand_dims(raw_mask, axis=-1)
    image = tf.constant(raw_img, dtype=tf.float32)
    mask  = tf.constant(raw_mask, dtype=tf.float32)
    if img_only:
        return image
    else:
        return (image, mask)
