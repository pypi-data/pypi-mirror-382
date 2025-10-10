import numpy as np
from skan import Skeleton, summarize
from skimage.morphology import skeletonize
from scipy.sparse.csgraph import connected_components

class SkeletonMeasures(object):
    def __init__(self, calibration=(1.0, 1.0, 1.0)):
        self.calibration = calibration

    def set_calibration(self, calibration):
        self.calibration = calibration

    def make_skeleton(self, image):
        image = (image > 0).astype(np.uint8)
        return skeletonize(image, method='lee')
    
    def get_measures_list(self):
        return [
            'total_length',
            'avg_branch',
            'n_branches',
            'n_components',
            'n_leaves',
            'v_vertices',
            'n_holes'
        ]

    def compute_measures(self, skeleton, measures=None):
        sk = Skeleton(skeleton, spacing=self.calibration)
        df = summarize(sk, separator='_')

        A = getattr(sk, "csgraph", getattr(sk, "graph", None)).tocsr()

        V = A.shape[0]
        E = A.nnz // 2 
        deg = np.diff(A.indptr)

        n_components, _ = connected_components(A, directed=False)

        total_length = float(df['branch_distance'].sum()) if len(df) else 0.0
        avg_branch   = float(df['branch_distance'].mean()) if len(df) else 0.0
        n_branches   = int(len(df))
        v_vertices   = int(V)
        n_leaves     = int((deg == 1).sum())
        n_holes      = int(E - V + n_components)

        computed = {
            'total_length' : total_length,
            'avg_branch'   : avg_branch,
            'n_branches'   : n_branches,
            'n_components' : int(n_components),
            'n_leaves'     : n_leaves,
            'v_vertices'   : v_vertices,
            'n_holes'      : n_holes,
        }
        if measures is None:
            return computed
        else:
            return {m: computed[m] for m in measures if m in computed}
