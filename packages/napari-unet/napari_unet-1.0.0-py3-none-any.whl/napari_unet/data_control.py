import numpy as np
import tifffile
import re

_TIFF_REGEX = re.compile(r".+\.tiff?", re.IGNORECASE)

def load_tiff(path, ndims=2):
    img = np.squeeze(tifffile.imread(path))
    new_img = None
    if len(img.shape) == 1:
        raise ValueError(f"Image at {path} seems corrupted (1D shape).")
    elif len(img.shape) == 2:
        new_img = img
    elif len(img.shape) == 3:
        new_img = 0.299 * img[:,:,0] + 0.587 * img[:,:,1] + 0.114 * img[:,:,2]
        new_img = new_img.reshape(img.shape[0], img.shape[1])
    else:
        raise ValueError(f"Image at {path} has an unsupported shape ({img.shape}).")
    if ndims == 2:
        return new_img
    elif ndims == 3:
        return new_img.reshape(new_img.shape[0], new_img.shape[1], 1)
    else:
        raise ValueError(f"ndims must be 2 or 3, got {ndims}.")

def get_data_pools(root_folder, folders, tif_only=False):
    """
    Aims to return the files available for training in every folder (not path).
    Probes the content of the data folders provided by the user.
    Both the images and the masks are probed.
    It is possible to filter the files to keep only the tiff files, whatever the case is (Hi Windows users o/).
    In the returned tuple, the first element is a list (not a dict) following the same order as the 'folders' list.

    Args:
        root_folder (str): The root folder containing the images and masks folders.
        folders (list): The list of folders to probe.
        tif_only (bool): If True, only the tiff files will be kept.
    
    Returns:
        tuple: (pool of files per individual folder, the set of all the files found everywhere merged together.)
    """
    pools = [] # Pools of files found in the folders.
    all_data = set() # All the names of files found gathered together.
    for f in folders: # Fetching content from folders
        path = root_folder / f
        pool = set([i for i in path.iterdir() if i.is_file()])
        if tif_only:
            pool = set([i for i in pool if _TIFF_REGEX.match(i.name)])
        pools.append(pool)
        all_data = all_data.union(pool)
    return pools, all_data

def get_shape(data_folder, inputs_name="inputs"):
    """
    Searches for the first image in the images folder to determine the input shape of the model.

    Returns:
        tuple: The shape of the input image.
    """
    _, l_files = get_data_pools(data_folder, [inputs_name], True)
    if len(l_files) == 0:
        raise ValueError(f"No TIFF files found in {data_folder / inputs_name}. Cannot determine input shape.")
    raw = load_tiff(list(l_files)[0])
    s = raw.shape
    if len(s) == 2:
        s = (s[0], s[1], 1)
    return s

def is_extension_correct(root_folder, folders):
    """
    Checks that the files are all TIFF images.

    Args:
        root_folder (str): The root folder containing the images and masks folders
        folders (list): The list of folders to probe (these folders must be in `root_folder`).

    Returns:
        dict: Keys are files, values are booleans. True if the file is a TIFF image, False otherwise.
    """
    _, all_data = get_data_pools(root_folder, folders)
    _, all_tiff = get_data_pools(root_folder, folders, True)
    extensions = {k: (k in all_tiff) for k in all_data}
    return extensions

def is_data_shape_identical(root_folder, folders):
    """
    All the data must be the same shape in X, Y and Z.

    Args:
        root_folder (str): The root folder containing the images and masks folders.
        folders (str): The list of folders to probe (these folders must be in `root_folder`).

    Returns:
        dict: Keys are files, values are booleans. True if the shape is identical, False otherwise.
    """
    _, all_data = get_data_pools(root_folder, folders, True)
    ref_size = None
    shapes = {k: False for k in all_data}
    for file in all_data:
        img_data = load_tiff(file)
        if ref_size is None:
            ref_size = img_data.shape
        shapes[file] = img_data.shape == ref_size
    return shapes

def is_data_useful(root_folder, folders):
    """
    There must not be empty masks or empty images.

    Args:
        root_folder (str): The root folder containing the images and masks folders

    Returns:
        bool: True if the data is consistent, False otherwise.
    """
    inputs_name, masks_name = folders
    images_path = root_folder / inputs_name
    masks_path = root_folder / masks_name
    _, all_data = get_data_pools(root_folder, folders, True)
    useful_data = {k: False for k in all_data}

    for file_path in all_data:
        item_data = load_tiff(file_path)
        s = True
        s = s and bool(np.nan not in set(np.unique(item_data)))
        if file_path.parent == images_path:
            s = s and bool((np.max(item_data) - np.min(item_data)) > 1e-6)
        else:
            s = s and bool(len(np.unique(item_data)) == 2)
        useful_data[file_path] = s
    return useful_data

def is_matching_data(root_folder, folders):
    """
    Every file present in the inputs folder must also be in the masks folder.
    Lists every possible file and verifies that it's present everywhere.

    Args:
        root_folder (str): The root folder containing the images and masks folders
        folders (list): The list of folders to probe (these folders must be in `root_folder`).

    Returns:
        dict: Keys are files, values are booleans. True if the file is present everywhere, False otherwise.
    """
    _, all_data = get_data_pools(root_folder, folders)
    all_names = set([f.name for f in all_data])
    inputs_name, masks_name = folders
    inputs_path = root_folder / inputs_name
    masks_path = root_folder / masks_name
    matching_data = {}

    for name in all_names:
        input_path = inputs_path / name
        mask_path = masks_path / name
        matching_data[input_path] = input_path.is_file() and mask_path.is_file()
        matching_data[mask_path] = input_path.is_file() and mask_path.is_file()

    return matching_data

def get_sanity_checks():
    return {
        "Extension correct": is_extension_correct,
        "Data shape identical": is_data_shape_identical,
        "Data useful": is_data_useful,
        "Matching data": is_matching_data
    }

if __name__ == "__main__":
    from pathlib import Path
    from pprint import pprint

    path = Path("/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1")
    pools, all_data = get_data_pools(path, ["inputs", "masks1"], False)
    shp = get_shape(path, "inputs")
    print(f"Input shape: {shp}")
    pprint(is_extension_correct(path, ["inputs", "masks1"]))