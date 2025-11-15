# modules/text_detector/cluster.py

from typing import List, Tuple
import numpy as np

from .utils import TextRegion

try:
    from sklearn.cluster import DBSCAN # type: ignore
    _HAS_SKLEARN = True
except ImportError:
    _HAS_SKLEARN = False


def cluster_regions_dbscan(
    regions: List[TextRegion],
    eps: float = 40.0,
    min_samples: int = 2,
) -> List[List[int]]:
    """
    Кластеризація регіонів за центрами через DBSCAN.
    Повертає список кластерів у вигляді списків індексів.
    """
    if not regions:
        return []

    centers = np.array([r.center for r in regions], dtype=np.float32)

    if _HAS_SKLEARN:
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(centers)
        labels = clustering.labels_
    else:
        # Спрощений fallback: кожна точка з сусідами в eps формується в кластер
        labels = _simple_radius_cluster(centers, eps, min_samples)

    clusters: List[List[int]] = []
    label_to_indices = {}
    for idx, lab in enumerate(labels):
        if lab == -1:
            continue  # шум
        label_to_indices.setdefault(int(lab), []).append(idx)

    for _, idxs in label_to_indices.items():
        clusters.append(idxs)

    return clusters


def _simple_radius_cluster(
    centers: np.ndarray,
    eps: float,
    min_samples: int,
):
    """
    Дуже простий кластеризатор для випадку, коли sklearn недоступний.
    Повертає масив label'ів як DBSCAN (шум = -1).
    """
    n = centers.shape[0]
    labels = -1 * np.ones(n, dtype=int)
    current_label = 0

    for i in range(n):
        if labels[i] != -1:
            continue
        diffs = centers - centers[i]
        dist2 = diffs[:, 0] ** 2 + diffs[:, 1] ** 2
        neighbors = np.where(dist2 <= eps * eps)[0]
        if len(neighbors) < min_samples:
            labels[i] = -1
            continue
        labels[neighbors] = current_label
        current_label += 1

    return labels
