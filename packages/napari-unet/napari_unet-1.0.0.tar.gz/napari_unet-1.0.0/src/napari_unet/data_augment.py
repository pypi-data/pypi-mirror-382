import numpy as np
import random
import tifffile
import cv2
from scipy.ndimage import rotate
from skimage.morphology import (binary_dilation,
                                disk, skeletonize)
from napari_unet.data_control import load_tiff

def deteriorate_image(image, mask, percentage=0.01):
    image = np.squeeze(image)
    mask = np.squeeze(mask)
    skel = skeletonize(mask > 0).astype(np.uint8)
    yx = np.argwhere(skel > 0)
    n = len(yx)
    if n == 0:
        return image, mask
    num_points = max(1, int(round(n * percentage)))
    if num_points > n:
        num_points = n
    selected_points = yx[np.random.choice(len(yx), num_points, replace=False)]
    to_erase = np.zeros_like(mask, dtype=np.uint8)
    to_erase[tuple(selected_points.T)] = 1
    k = disk(8)
    to_erase = binary_dilation(to_erase, footprint=k).astype(np.uint8)
    fixed = cv2.inpaint(image, to_erase, 8, cv2.INPAINT_NS)
    return fixed, mask

def get_deteriorate_image(settings):
    def func(image, mask):
        return deteriorate_image(
            image, 
            mask, 
            settings.get('percentage', 0.01)
        )
    return func

def random_flip(image, mask, h=True, v=True):
    """
    Applies a random horizontal or vertical flip to both the image and the mask.
    
    Args:
        image (np.ndarray): The input image.
        mask (np.ndarray): The input mask.
        
    Returns:
        (np.ndarray, np.ndarray): The flipped image and mask.
    """
    # Horizontal flip
    if h and np.random.rand() > 0.5:
        image = np.fliplr(image)
        mask = np.fliplr(mask)
    
    # Vertical flip
    if v and np.random.rand() > 0.5:
        image = np.flipud(image)
        mask = np.flipud(mask)
    
    return image, mask

def get_random_flip(settings):
    def func(image, mask):
        return random_flip(
            image, 
            mask, 
            settings.get('horizontal', True), 
            settings.get('vertical', True)
        )
    return func

def random_rotation(image, mask, ang_start=-180, ang_end=180):
    """
    Applies a random rotation (by any angle) to both the image and the mask.
    The image uses bilinear interpolation, while the mask uses nearest-neighbor interpolation to avoid grayscale artifacts.
    
    Args:
        image (np.ndarray): The input image.
        mask (np.ndarray): The input mask.
        angle_range (tuple): The range of angles (in degrees) from which to sample the random rotation angle.
        
    Returns:
        (np.ndarray, np.ndarray): The rotated image and mask.
    """
    angle = np.random.uniform(ang_start, ang_end)
    rotated_image = rotate(image, angle, reshape=False, order=1, mode='reflect')
    rotated_mask = rotate(mask, angle, reshape=False, order=0, mode='reflect')
    
    return rotated_image, rotated_mask

def get_random_rotation(settings):
    def func(image, mask):
        return random_rotation(
            image, 
            mask, 
            settings.get('angle_start', -180), 
            settings.get('angle_end', 180)
        )
    return func

def gamma_correction(image, mask, g_start=0.7, g_end=1.5):
    """
    Applies a random gamma correction to the image. The mask remains unchanged.
    
    Args:
        image (np.ndarray): The input image.
        mask (np.ndarray): The input mask.
        gamma_range (tuple): The range from which to sample the gamma value.
        
    Returns:
        (np.ndarray, np.ndarray): The gamma-corrected image and the unchanged mask.
    """
    gamma = np.random.uniform(g_start, g_end)
    image = np.power(image, gamma)
    
    return image, mask

def get_gamma_correction(settings):
    def func(image, mask):
        return gamma_correction(
            image, 
            mask, 
            settings.get('gamma_start', 0.7), 
            settings.get('gamma_end', 1.5)
        )
    return func

def add_gaussian_noise(image, mask, noise_scale=0.005):
    """
    Adds random Gaussian noise to the image. The mask remains unchanged.
    
    Args:
        image (np.ndarray): The input image.
        mask (np.ndarray): The input mask.
        
    Returns:
        (np.ndarray, np.ndarray): The noisy image and the unchanged mask.
    """
    noise = np.random.normal(1.0, noise_scale, image.shape)
    noise = noise.astype(image.dtype)
    noisy_image = image * noise
    noisy_image = np.clip(noisy_image, 0, 1)
    noisy_image = noisy_image.astype(image.dtype)
    return noisy_image, mask

def get_add_gaussian_noise(settings):
    def func(image, mask):
        return add_gaussian_noise(
            image, 
            mask, 
            settings.get('noise_scale', 0.005)
        )
    return func

def get_augmentation_steps():
    return [
        ("mirroring"       , get_random_flip),
        ("random_rotations", get_random_rotation),
        ("holes"           , get_deteriorate_image),
        ("gamma_correction", get_gamma_correction),
        ("gaussian_noise"  , get_add_gaussian_noise)
    ]

def get_data_augmentation_pipeline(settings):
    def apply_augmentations(image, mask):
        for name, generator in get_augmentation_steps():
            if settings['use'].get(name, False):
                func = generator(settings.get(name, {}))
                image, mask = func(image, mask)
        return image, mask
    return apply_augmentations

def get_n_versions(settings, path_in, path_gt, n=10):
    apply_augmentations = get_data_augmentation_pipeline(settings)
    images = []
    masks  = []
    for _ in range(n):
        im_in = load_tiff(path_in)
        mk_in = load_tiff(path_gt)
        im_in, mk_in = apply_augmentations(im_in, mk_in)
        images.append(im_in)
        masks.append(mk_in)
    return images, masks

if __name__ == "__main__":
    import os
    settings = {
        "use": {
            "mirroring"       : False,
            "random_rotations": False,
            "holes"           : True,
            "gamma_correction": False,
            "gaussian_noise"  : False
        },
        "mirroring": {
            "horizontal": True,
            "vertical"  : True
        },
        "random_rotations": {
            "angle_start": -180,
            "angle_end"  : 180
        },
        "holes": {
            "percentage": 0.01
        },
        "gamma_correction": {
            "gamma_start" : 0.7,
            "gamma_end"   : 1.5
        },
        "gaussian_noise": {
            "noise_scale": 0.005
        }
    }

    apply_augmentations = get_data_augmentation_pipeline(settings)
    
    folder   = "/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1"
    im_name  = "Image_01L_001.tif"

    in_path  = os.path.join(folder, "input-patches", im_name)
    mk_path  = os.path.join(folder, "mask-patches", im_name)
    versions = 10

    tifffile.imwrite("/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1/holes/im_in_000.tif", load_tiff(in_path))

    for v in range(1, versions+1):
        im_in = load_tiff(in_path)
        mk_in = load_tiff(mk_path)

        im_in, mk_in = apply_augmentations(im_in, mk_in)

        tifffile.imwrite(f"/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1/holes/im_in_{str(v).zfill(3)}.tif", im_in)