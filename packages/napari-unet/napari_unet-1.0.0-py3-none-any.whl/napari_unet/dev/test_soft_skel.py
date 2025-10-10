from pathlib import Path
import numpy as np
import tifffile
import tensorflow as tf
from napari_unet.soft_skeleton import soft_skel
import os
import shutil

def flatten_predictions(src_root, dst_dir, pattern="prediction_*.tif", move=False, prefix_depth=None):
    src_root = Path(src_root)
    dst_dir = Path(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)

    copied = 0
    for dirpath, _, _ in os.walk(src_root):
        dpath = Path(dirpath)
        for src in sorted(dpath.glob(pattern)):
            rel = src.parent.relative_to(src_root)
            if prefix_depth is not None and len(rel.parts) > prefix_depth:
                rel = Path(*rel.parts[-prefix_depth:])
            parts = [p for p in rel.parts if p not in (".", "")]
            prefix = "__".join(parts) if parts else "root"
            new_name = f"{prefix}__{src.name}" if prefix else src.name
            dest = dst_dir / new_name

            if dest.exists():
                stem, ext = dest.stem, dest.suffix
                i = 1
                while (dst_dir / f"{stem}__{i}{ext}").exists():
                    i += 1
                dest = dst_dir / f"{stem}__{i}{ext}"

            if move:
                shutil.move(str(src), str(dest))
            else:
                shutil.copy2(str(src), str(dest))
            copied += 1

    return copied


def soft_skeletonize_folder(input_dir, output_dir, iters=20, patterns=("*.tif", "*.tiff")):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for pat in patterns:
        files.extend(sorted(input_dir.glob(pat)))

    for src in files:
        arr = tifffile.imread(src)

        def _to_float01(x):
            if np.issubdtype(x.dtype, np.integer):
                return (x.astype(np.float32) / np.iinfo(x.dtype).max).astype(np.float32)
            return x.astype(np.float32)

        def _skel2d(img2d):
            x = _to_float01(img2d)
            x4 = tf.convert_to_tensor(x[None, ..., None], dtype=tf.float32)  # (1,H,W,1)
            y4 = soft_skel(x4, iters)
            y = y4.numpy()[0, ..., 0]
            return y

        if arr.ndim == 2:
            out = _skel2d(arr)
            tifffile.imwrite(output_dir / f"{src.stem}_softskel.tif", out.astype(np.float32))
        elif arr.ndim == 3:
            # Treat as Z-stack of 2D slices: (Z,H,W)
            if arr.shape[-1] == 1 and arr.shape[0] != 1:
                # Some files are (Z,H,W,1) squeezed; handle generically below
                arr = np.squeeze(arr, axis=-1)
            if arr.ndim == 3 and arr.shape[0] > 1 and arr.shape[1] > 1:
                out_slices = [_skel2d(arr[z]) for z in range(arr.shape[0])]
                out = np.stack(out_slices, axis=0).astype(np.float32)
                tifffile.imwrite(output_dir / f"{src.stem}_softskel.tif", out)
            else:
                # Likely (H,W,1): squeeze to 2D
                out = _skel2d(np.squeeze(arr))
                tifffile.imwrite(output_dir / f"{src.stem}_softskel.tif", out.astype(np.float32))
        else:
            raise ValueError(f"Unsupported image shape {arr.shape} for {src.name}")


if __name__ == "__main__":
    flatten_predictions(
        "/home/clement/Documents/projects/mifobio-2025/processed/unet_working/predictions",
        "/tmp/soft/in"
    )
    soft_skeletonize_folder(
        "/tmp/soft/in", 
        "/tmp/soft/out", 
        iters=20
    )
