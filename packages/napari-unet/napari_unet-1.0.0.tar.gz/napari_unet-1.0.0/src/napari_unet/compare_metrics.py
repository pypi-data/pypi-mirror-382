from pathlib import Path
import numpy as np
import tifffile

from napari_unet.data_control import load_tiff
from napari_unet.metrics import (get_all_metrics, 
                                 get_degradation_functions)

class CompareMetrics(object):
    def __init__(self):
        self.data_root    = None
        self.input_folder = None
        self.gt_folder    = None
        self.metrics      = {k: True for k in get_all_metrics().keys()}

    def set_metric_enabled(self, metric_name, enabled=True):
        if metric_name not in self.metrics:
            raise ValueError(f"Metric {metric_name} is not recognized.")
        self.metrics[metric_name] = bool(enabled)

    def is_metric_enabled(self, metric_name):
        return self.metrics.get(metric_name, False)

    def set_input_folder(self, folder_name):
        if self.data_root is None or folder_name is None or len(folder_name) == 0:
            raise ValueError("Data root and input folder must be set.")
        candidate = self.data_root / folder_name
        if not candidate.exists() or not candidate.is_dir():
            raise ValueError(f"Input folder {candidate} does not exist or is not a folder.")
        self.input_folder = folder_name

    def get_input_folder(self):
        return self.input_folder
    
    def set_gt_folder(self, folder_name):
        if self.data_root is None or folder_name is None or len(folder_name) == 0:
            raise ValueError("Data root and ground-truth folder must be set.")
        candidate = self.data_root / folder_name
        if not candidate.exists() or not candidate.is_dir():
            raise ValueError(f"Ground-truth folder {candidate} does not exist or is not a folder.")
        self.gt_folder = folder_name
    
    def get_gt_folder(self):
        return self.gt_folder
    
    def set_data_root(self, path):
        if path is None:
            raise ValueError("Data root must be set.")
        candidate = Path(path)
        if not candidate.exists() or not candidate.is_dir():
            raise ValueError(f"Data root {candidate} does not exist or is not a folder.")
        self.data_root = candidate

    def get_data_root(self):
        return self.data_root
    
    def get_data_pool(self):
        if self.data_root is None or self.input_folder is None or self.gt_folder is None:
            raise ValueError("Data root, input folder and ground-truth folder must be set.")
        input_path = self.data_root / self.input_folder
        gt_path    = self.data_root / self.gt_folder
        input_files = sorted([f for f in input_path.iterdir() if f.is_file() and f.suffix in (".tif", ".tiff")])
        gt_files    = sorted([f for f in gt_path.iterdir() if f.is_file() and f.suffix in (".tif", ".tiff")])
        input_names = set([f.name for f in input_files])
        gt_names    = set([f.name for f in gt_files])
        common_names = input_names.intersection(gt_names)
        return common_names
    
    def get_modalities(self):
        if self.data_root is None:
            raise ValueError("Data root must be set.")
        if self.input_folder is None or self.gt_folder is None:
            raise ValueError("At least one of input folder or ground-truth folder must be set.")
        return [l.name for l in self.data_root.iterdir() if l.is_dir() and l.name not in (self.input_folder, self.gt_folder)]
    
    def compute_one_shot_metrics(self, image_name):
        modalities = self.get_modalities()
        results = {}
        if self.data_root is None or self.input_folder is None or self.gt_folder is None:
            raise ValueError("Data root, input folder and ground-truth folder must be set.")
        gt_path = self.data_root / self.gt_folder / image_name
        if not gt_path.exists() or not gt_path.is_file():
            raise ValueError(f"Ground-truth file {gt_path} does not exist or is not a file.")
        gt = load_tiff(gt_path)
        metrics_fx = get_all_metrics()
        for mod in modalities:
            mod_path = self.data_root / mod / image_name
            if not mod_path.exists() or not mod_path.is_file():
                continue
            pred = load_tiff(mod_path)
            computed = {}
            for k, fx in metrics_fx.items():
                if self.metrics.get(k, False):
                    try:
                        v = fx(gt, pred)
                        computed[k] = float(v)
                    except Exception as e:
                        computed[k] = None
            results[mod] = computed
        return results
    
    def compute_batch_metrics(self, metric):
        modalities = self.get_modalities()
        if metric not in self.metrics or not self.metrics[metric]:
            raise ValueError(f"Metric {metric} is not recognized or not enabled.")
        pool = self.get_data_pool()
        results = {}
        if self.data_root is None or self.input_folder is None or self.gt_folder is None:
            raise ValueError("Data root, input folder and ground-truth folder must be set.")
        fx = get_all_metrics().get(metric, None)
        if fx is None:
            raise ValueError(f"Metric function for {metric} not found.")
        for im_name in pool:
            gt_path = self.data_root / self.gt_folder / im_name
            if not gt_path.exists() or not gt_path.is_file():
                continue
            gt = load_tiff(gt_path)
            computed = {}
            for mod in modalities:
                mod_path = self.data_root / mod / im_name
                if not mod_path.exists() or not mod_path.is_file():
                    continue
                pred = load_tiff(mod_path)
                try:
                    v = fx(gt, pred)
                    computed[mod] = float(v)
                except Exception as e:
                    computed[mod] = None
            results[im_name] = computed
        return results
    
    def generate_degraded_versions(self):
        if self.data_root is None or self.input_folder is None or self.gt_folder is None:
            raise ValueError("Data root, input folder and ground-truth folder must be set.")
        pool = self.get_data_pool()
        gt_path = self.data_root / self.gt_folder
        for image in pool:
            mask = load_tiff(gt_path / image)
            print(f"Generating degraded versions for {image}...")
            for name, fx in get_degradation_functions().items():
                print(f"   - {name}")
                degraded = fx(mask)
                out_path = self.data_root / name
                if not out_path.exists():
                    out_path.mkdir(parents=True)
                save_path = out_path / image
                np.clip(degraded, 0, 1, out=degraded)
                tifffile.imwrite(save_path, degraded)

if __name__ == "__main__":
    from pprint import pprint
    import json

    cm = CompareMetrics()
    cm.set_data_root("/home/clement/Documents/projects/mifobio-2025/datasets/CHASEDB1-results")
    cm.set_input_folder("inputs")
    cm.set_gt_folder("masks1")

    res = cm.compute_one_shot_metrics("Image_01L.tif")
    with open("/tmp/oneshot.json", "w") as f:
        json.dump(res, f, indent=4)
    
    res = cm.compute_batch_metrics("dice")
    with open("/tmp/batch.json", "w") as f:
        json.dump(res, f, indent=4)
