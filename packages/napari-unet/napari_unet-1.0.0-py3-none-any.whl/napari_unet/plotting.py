import re
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt

def find_metric_pairs(keys):
    keys_set = set(keys)
    val_keys = {k for k in keys_set if k.startswith("val_")}
    train_keys = keys_set - val_keys
    pairs = []
    for t in sorted(train_keys):
        v = f"val_{t}"
        if v in val_keys:
            pairs.append((t, v))
            val_keys.remove(v)
        else:
            pairs.append((t, None))
    for v in sorted(val_keys):
        pairs.append((None, v))
    return pairs

def _sanitize(name):
    return re.sub(r"[^\w\-]+", "_", name).strip("_")

def plot_metrics(metrics, pairs, out_dir, dpi=150, figsize=(6.0, 4.0), fmt="png"):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plt.ioff()
    saved = []
    for train_key, val_key in pairs:
        base = train_key or val_key
        if base is None:
            continue
        short = base[len("val_"):] if base.startswith("val_") else base
        train_vals = np.asarray(metrics[train_key], dtype=np.float64) if (train_key and train_key in metrics) else None
        val_vals = np.asarray(metrics[val_key], dtype=np.float64) if (val_key and val_key in metrics) else None
        if train_vals is None and val_vals is None:
            continue
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        plotted = False
        if train_vals is not None:
            x = np.arange(train_vals.shape[0])
            ax.plot(x, train_vals, label=train_key, marker="o", linewidth=1)
            plotted = True
        if val_vals is not None:
            x = np.arange(val_vals.shape[0])
            ax.plot(x, val_vals, label=val_key, marker="s", linewidth=1)
            if train_vals is not None and val_vals.shape[0] != train_vals.shape[0]:
                ax.text(0.99, 0.01, f"train_len={len(train_vals)}, val_len={len(val_vals)}",
                        transform=ax.transAxes, ha="right", va="bottom", fontsize=8, alpha=0.8)
            plotted = True
        if not plotted:
            plt.close(fig)
            continue
        ax.set_xlabel("epoch")
        ax.set_ylabel(short)
        ax.set_title(f"{short} (train vs val)")
        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
        ax.legend(loc="best", fontsize="small")
        base_fname = _sanitize(short)
        path = out_dir / f"{base_fname}.{fmt}"
        idx = 1
        while path.exists():
            path = out_dir / f"{base_fname}_{idx}.{fmt}"
            idx += 1
        fig.tight_layout()
        fig.savefig(str(path), bbox_inches="tight")
        plt.close(fig)
        saved.append(path)
    return saved



if __name__ == "__main__":
    sample_metrics = {
        "accuracy": [0.6, 0.7, 0.75],
        "val_accuracy": [0.58, 0.69, 0.73],
        "loss": [1.2, 0.8, 0.6],
        "val_loss": [1.1, 0.85, 0.65],
        "learning_rate": [1e-3, 5e-4, 2.5e-4],
    }
    pairs = find_metric_pairs(list(sample_metrics.keys()))
    out = plot_metrics(sample_metrics, pairs, out_dir="/tmp/metrics_plots")
