import tifffile
import numpy as np
from skimage.morphology import skeletonize, disk
from scipy.ndimage import (distance_transform_edt, white_tophat, 
                           gaussian_filter, binary_dilation)
from skimage.metrics import hausdorff_distance as sk_hd
import matplotlib.pyplot as plt
from sklearn.metrics import jaccard_score, log_loss


def shift_image(img, dx, axis=-1, fill=0):
    arr = np.asarray(img)
    if dx == 0:
        return arr.copy()
    if not isinstance(dx, (int, np.integer)):
        raise ValueError("dx must be an integer")

    axis = axis if axis >= 0 else arr.ndim + axis
    if axis < 0 or axis >= arr.ndim:
        raise ValueError("axis out of range")

    out = np.full_like(arr, fill)

    width = arr.shape[axis]
    if abs(dx) >= width:
        return out

    src = [slice(None)] * arr.ndim
    dst = [slice(None)] * arr.ndim

    if dx > 0:
        src[axis] = slice(0, width - dx)
        dst[axis] = slice(dx, width)
    else:
        d = -dx
        src[axis] = slice(d, width)
        dst[axis] = slice(0, width - d)

    out[tuple(dst)] = arr[tuple(src)]
    return out

def deteriorate(img, percentage=0.3333):
    pos = np.where(img > 0)
    rdm_idx = np.random.choice(len(pos[0]), size=int(len(pos[0]) * percentage), replace=False)
    img_deteriorated = img.copy()
    img_deteriorated[pos[0][rdm_idx], pos[1][rdm_idx]] = 0
    return img_deteriorated

def spread_from_skeleton(mask, skeleton):
    """
    Takes a mask and a skeleton.
    Produces a new image in which the number of positive pixels is the same as in the skeleton,
    but the positive pixels are randomly distributed within the mask.
    """
    n_items = np.sum(skeleton)
    canvas = np.zeros_like(mask, dtype=np.uint8)
    items = np.where(mask > 0)
    rdm_idx = np.random.choice(len(items[0]), size=n_items, replace=False)
    canvas[items[0][rdm_idx], items[1][rdm_idx]] = 1
    return canvas

def fracture(img, skeleton, n_fractures=20):
    """
    Uses the skeleton to induce fractures in the original mask.
    A copy is made, the original is not modified.
    """
    pos = np.where(skeleton > 0)
    if len(pos[0]) == 0:
        return img.copy()
    rdm_idx = np.random.choice(len(pos[0]), size=min(n_fractures, len(pos[0])), replace=False)
    img_fractured = img.copy()
    fractures_mask = np.zeros_like(img, dtype=np.uint8)
    fractures_mask[pos[0][rdm_idx], pos[1][rdm_idx]] = 1
    fractures_mask = binary_dilation(fractures_mask, structure=disk(10), iterations=1)
    img_fractured[fractures_mask > 0] = 0
    return img_fractured

def accuracy(y_true, y_pred):
    if y_true.shape != y_pred.shape:
        raise ValueError("Shapes of true labels and predicted labels must match.")
    y_true = (y_true > 0).astype(np.uint8)
    y_pred = (y_pred > 0).astype(np.uint8)
    
    correct_predictions = np.sum(y_true == y_pred)
    total_predictions   = y_true.size
    
    accuracy_score = correct_predictions / total_predictions
    return accuracy_score

def recall(y_true, y_pred):
    if y_true.shape != y_pred.shape:
        raise ValueError("Shapes of true labels and predicted labels must match.")
    y_true = (y_true > 0).astype(np.uint8)
    y_pred = (y_pred > 0).astype(np.uint8)

    true_positives = np.sum(y_true * y_pred)
    actual_positives = np.sum(y_true)

    if actual_positives == 0:
        return 0.0
    
    recall_score = true_positives / actual_positives
    return recall_score

def precision(y_true, y_pred):
    if y_true.shape != y_pred.shape:
        raise ValueError("Shapes of true labels and predicted labels must match.")
    y_true = (y_true > 0).astype(np.uint8)
    y_pred = (y_pred > 0).astype(np.uint8)

    true_positives      = np.sum(y_true * y_pred)
    predicted_positives = np.sum(y_pred)

    if predicted_positives == 0:
        return 0.0
    
    precision_score = true_positives / predicted_positives
    return precision_score

def specificity(y_true, y_pred):
    if y_true.shape != y_pred.shape:
        raise ValueError("Shapes of true labels and predicted labels must match.")
    y_true = (y_true > 0).astype(np.uint8)
    y_pred = (y_pred > 0).astype(np.uint8)

    true_negatives = np.sum((1 - y_true) * (1 - y_pred))
    actual_negatives = true_negatives + np.sum((1 - y_true) * y_pred)

    if actual_negatives == 0:
        return 0.0
    
    specificity_score = true_negatives / actual_negatives
    return specificity_score

def jaccard(y_true, y_pred): # IoU
    """
    Measures pixel overlap between prediction and ground truth
    """
    if y_true.shape != y_pred.shape:
        raise ValueError("Shapes of true labels and predicted labels must match.")
    y_true = (y_true > 0).astype(np.uint8)
    y_pred = (y_pred > 0).astype(np.uint8)

    return jaccard_score(y_true.flatten(), y_pred.flatten())

def dice(y_true, y_pred):
    """
    Measures pixel overlap between prediction and ground truth
    """
    if y_true.shape != y_pred.shape:
        raise ValueError("Shapes of true labels and predicted labels must match.")
    y_true = (y_true > 0).astype(np.uint8)
    y_pred = (y_pred > 0).astype(np.uint8)

    intersection = np.sum(y_true * y_pred)
    sum_sizes = np.sum(y_true) + np.sum(y_pred)

    if sum_sizes == 0:
        return 1.0
    
    dice_score = (2 * intersection) / sum_sizes
    return dice_score

def cl_dice(y_true, y_pred): # center-line dice
    """
    clDice metric was developed to evaluate a model's ability to maintain the connectivity of vascular structures.
    Analyzes the centerlines of tubular structures
    """
    if y_true.shape != y_pred.shape:
        raise ValueError("Shapes of true labels and predicted labels must match.")
    y_true = (y_true > 0).astype(np.uint8)
    y_pred = (y_pred > 0).astype(np.uint8)

    s_true = skeletonize(y_true, method='lee')
    s_pred = skeletonize(y_pred, method='lee')

    acc_true = np.sum(s_true)
    acc_pred = np.sum(s_pred)
    if acc_true == 0 or acc_pred == 0:
        return 0.0

    t_prec = np.sum(s_pred * y_true) / acc_pred
    t_sens = np.sum(s_true * y_pred) / acc_true
    total = t_prec + t_sens
    if total == 0:
        return 0.0
    return (2 * t_prec * t_sens) / total

def smooth_cl_dice(y_true, y_pred, sg=5):
    if y_true.shape != y_pred.shape:
        raise ValueError("Shapes of true labels and predicted labels must match.")
    y_true = (y_true > 0).astype(np.uint8)
    y_pred = (y_pred > 0).astype(np.uint8)

    s_true = skeletonize(y_true, method='lee')
    s_pred = skeletonize(y_pred, method='lee')

    d_true = distance_transform_edt(y_true)
    d_true = gaussian_filter(d_true, sigma=sg)
    d_pred = distance_transform_edt(y_pred)
    d_pred = gaussian_filter(d_pred, sigma=sg)

    acc_true = np.sum(s_true * d_true)
    acc_pred = np.sum(s_pred * d_pred)

    if acc_true == 0 or acc_pred == 0:
        return 0.0

    t_prec = np.sum(d_true * s_pred) / acc_pred
    t_sens = np.sum(d_pred * s_true) / acc_true
    total  = t_prec + t_sens
    if total == 0:
        return 0.0

    return (2 * t_prec * t_sens) / total

def hausdorff_distance(y_true, y_pred):
    """
    Measures the maximum distance of a set to the nearest point in the other set
    """
    if y_true.shape != y_pred.shape:
        raise ValueError("Shapes of true labels and predicted labels must match.")
    y_true = (y_true > 0).astype(np.uint8)
    y_pred = (y_pred > 0).astype(np.uint8)

    hd = sk_hd(y_true, y_pred)
    return 1.0 / (1.0 + hd)

def mean_hausdorff_distance(y_true, y_pred):
    """
    Measures the maximum distance of a set to the nearest point in the other set
    """
    if y_true.shape != y_pred.shape:
        raise ValueError("Shapes of true labels and predicted labels must match.")
    y_true = (y_true > 0).astype(np.uint8)
    y_pred = (y_pred > 0).astype(np.uint8)

    hd = sk_hd(y_true, y_pred, method='modified')
    return 1.0 / (1.0 + hd)

def get_all_metrics():
    return {
        "accuracy"       : accuracy,
        "precision"      : precision,
        "recall"         : recall,
        "specificity"    : specificity,
        "jaccard"        : jaccard,
        "dice"           : dice,
        "cl_dice"        : cl_dice,
        "smooth_cl_dice" : smooth_cl_dice,
        "hausdorff"      : hausdorff_distance,
        "mean_hausdorff" : mean_hausdorff_distance
    }

def plot_record(record):
        plt.figure(figsize=(8, 5))
        plt.plot(record["X shift"], record["dice"], label="Dice")
        plt.plot(record["X shift"], record["clDice"], label="clDice")
        plt.plot(record["X shift"], record["Smooth clDice"], label="Smooth clDice")
        plt.plot(record["X shift"], record["MBCE"], label="MBCE")
        plt.plot(record["X shift"], record["Hausdorff"], label="Hausdorff")
        plt.plot(record["X shift"], record["BCE"], label="BCE")
        plt.xlabel("X shift")
        plt.ylabel("Metric value")
        plt.title("Metric values VS. X shift")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

def use_smooth_cl_dice():
    y_true = tifffile.imread("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c-blank.tif")
    y_pred = tifffile.imread("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c1.tif")

    record = {
        "X shift"       : [],
        "dice"          : [],
        "clDice"        : [],
        "Smooth clDice" : [],
        "MBCE"          : [],
        "Hausdorff"     : [],
        "BCE"           : []
    }

    for s in range(-15, 16):
        shifted = shift_image(y_pred, s)
        print(f"Shift: {s}")
        d = float(round(dice(y_true, shifted), 4))
        cld = float(round(cl_dice(y_true, shifted), 4))
        scd = float(round(smooth_cl_dice(y_true, shifted), 4))
        mce = float(round(morpho_cross_entropy(y_true, shifted), 4))
        hd = float(round(hausdorff_distance(y_true, shifted), 4))
        bce = float(round(cross_entropy(y_true, shifted), 4))
        print(f"  | BCE           : {bce}")
        print(f"  | Dice          : {d}")
        print(f"  | clDice        : {cld}")
        print(f"  | Smooth clDice : {scd}")
        print(f"  | MBCE          : {mce}")
        print(f"  | Hausdorff     : {hd}")
        record["X shift"].append(s)
        record["dice"].append(d)
        record["clDice"].append(cld)
        record["Smooth clDice"].append(scd)
        record["MBCE"].append(mce)
        record["Hausdorff"].append(hd)
        record["BCE"].append(bce)

    plot_record(record)

def normalized_cross_entropy(y_true, y_pred):
    """
    Normalized Cross Entropy (NCE) is a metric used to evaluate the performance of segmentation models, particularly in medical imaging.
    It quantifies the difference between the predicted segmentation and the ground truth segmentation, normalized by the entropy of the ground truth.
    """
    if y_true.shape != y_pred.shape:
        raise ValueError("Shapes of true labels and predicted labels must match.")
    y_true = (y_true > 0).astype(np.uint8)
    y_pred = (y_pred > 0).astype(np.uint8)

    return log_loss(y_true.flatten(), y_pred.flatten(), normalize=True)

def get_degradation_functions():
    return {
        "Shift-3"         : lambda x: shift_image(x, 3, axis=1, fill=0),
        "Inverted"        : lambda x: 1 - x,
        "Random"          : lambda x: (np.random.rand(*x.shape) > 0.5).astype(np.uint8),
        "Zeroes"          : lambda x: np.zeros_like(x, dtype=np.uint8),
        "Ones"            : lambda x: np.ones_like(x, dtype=np.uint8),
        "Deteriorate-33%" : lambda x: deteriorate(x, percentage=0.3333),
        "Deteriorate-50%" : lambda x: deteriorate(x, percentage=0.5),
        "Fractured-80"    : lambda x: fracture(x, skeletonize(x, method='lee'), n_fractures=80),
        "Spread"          : lambda x: spread_from_skeleton(x, skeletonize(x, method='lee'))
    }

def demo_metric():
    y_true = tifffile.imread("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c1.tif")
    y_pre1 = tifffile.imread("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c2.tif")
    y_pre2 = tifffile.imread("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c3.tif")
    erased = tifffile.imread("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c1-erased.tif")
    metric_fx = smooth_cl_dice
    print(f"Using metric: {metric_fx.__name__}")

    # Same image
    ce = metric_fx(y_true, y_true)
    print(f"Same image: {round(ce, 4)}")

    # Negative image
    ce = metric_fx(y_true, 1 - y_true)
    print(f"Negative image: {round(ce, 4)}")

    # Random image
    ce = metric_fx(y_true, (np.random.rand(*y_true.shape) > 0.5))
    print(f"Random image: {round(ce, 4)}")

    # With black image
    ce = metric_fx(y_true, np.zeros_like(y_true))
    print(f"Black image: {round(ce, 4)}")

    # With ones image
    ce = metric_fx(y_true, np.ones_like(y_true))
    print(f"Ones image: {round(ce, 4)}")

    # Deteriorated image
    dtr = deteriorate(y_true, percentage=0.3333)
    ce = metric_fx(y_true, dtr)
    tifffile.imwrite("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c1-deter-0_33.tif", dtr)
    print(f"Deteriorated image (33%): {round(ce, 4)}")
    dtr = deteriorate(y_true, percentage=0.5)
    ce = metric_fx(y_true, dtr)
    tifffile.imwrite("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c1-deter-0_50.tif", dtr)
    print(f"Deteriorated image (50%): {round(ce, 4)}")

    # With alternative mask c1c2
    ce = metric_fx(y_true, y_pre1)
    print(f"Alternative mask c1c2: {round(ce, 4)}")

    # With alternative mask c1c3
    ce = metric_fx(y_true, y_pre2)
    print(f"Alternative mask c1c3: {round(ce, 4)}")

    # With alternative mask c2c3 shifted
    ce = metric_fx(y_pre1, y_pre2)
    print(f"Alternative mask c2c3: {round(ce, 4)}")

    # With the skeletonized version
    sk = skeletonize(y_true, method='lee')
    ce = metric_fx(y_true, sk)
    tifffile.imwrite("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c1-skeletonized.tif", sk)
    print(f"Skeletonized version: {round(ce, 4)}")

    # c1 vs erased
    ce = metric_fx(y_true, erased)
    print(f"c1 vs. erased: {round(ce, 4)}")

    # C1 vs. spread from skeleton
    spread = spread_from_skeleton(y_true, sk)
    ce = metric_fx(y_true, spread)
    tifffile.imwrite("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c1-spread-from-skeleton.tif", spread)
    print(f"c1 vs. spread: {round(ce, 4)}")

    # C1 vs. shifted C1
    shifted = shift_image(y_true, 3)
    ce = metric_fx(y_true, shifted)
    tifffile.imwrite("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c1-shifted.tif", shifted)
    print(f"c1 vs. shifted C1: {round(ce, 4)}")

    # C1 vs. fractured C1
    fractured = fracture(y_true, sk, n_fractures=80)
    ce = metric_fx(y_true, fractured)
    tifffile.imwrite("/home/clement/Documents/projects/mifobio-2025/processed/map-example/c1-fractured.tif", fractured)
    print(f"c1 vs. fractured C1: {round(ce, 4)}")

def test_shift():
    img_path = "/home/clement/Documents/projects/mifobio-2025/processed/map-example/c1.tif"
    img = tifffile.imread(img_path)
    im1 = shift_image(img, 5, axis=0)
    tifffile.imwrite("/tmp/im1.tif", im1)
    im2 = shift_image(img, 5, axis=1)
    tifffile.imwrite("/tmp/im2.tif", im2)

if __name__ == "__main__":
   # use_smooth_cl_dice()
   demo_metric()
   # test_shift()