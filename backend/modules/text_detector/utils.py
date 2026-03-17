# modules/text_detector/utils.py

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


BBox = Tuple[int, int, int, int]  # x, y, w, h


@dataclass
class TextRegion:
    """Окремий MSER-регіон (кандидат букви / фрагмента)."""
    box: BBox
    center: Tuple[float, float]
    area: int
    mask: np.ndarray  # невелика бінарна маска регіону


def bbox_area(box: BBox) -> int:
    x, y, w, h = box
    return int(w * h)


def bbox_center(box: BBox) -> Tuple[float, float]:
    x, y, w, h = box
    return (x + w / 2.0, y + h / 2.0)


def merge_bboxes(boxes: List[BBox]) -> BBox:
    """Об'єднати декілька bbox в один."""
    xs = [b[0] for b in boxes]
    ys = [b[1] for b in boxes]
    xe = [b[0] + b[2] for b in boxes]
    ye = [b[1] + b[3] for b in boxes]
    x_min, y_min = min(xs), min(ys)
    x_max, y_max = max(xe), max(ye)
    return int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)


def crop_mask_from_region(gray: np.ndarray, contour: np.ndarray, box: BBox) -> np.ndarray:
    """
    Побудувати маленьку бінарну маску регіону по контуру в межах box.
    """
    x, y, w, h = box
    mask = np.zeros((h, w), dtype=np.uint8)
    contour_shifted = contour.copy()
    if contour_shifted.ndim == 2:
        # reshape Nx2 to Nx1x2 so cv2.drawContours accepts it
        contour_shifted = contour_shifted[:, None, :]
    contour_shifted[:, 0, 0] -= x
    contour_shifted[:, 0, 1] -= y
    import cv2
    cv2.drawContours(mask, [contour_shifted], -1, 255, thickness=-1)
    return mask


def count_black_white_transitions(mask: np.ndarray) -> int:
    """
    Оцінка кількості переходів чорний/білий по центральній горизонталі маски.
    Використовується як грубий фільтр 'буква/шум'.
    """
    if mask.size == 0:
        return 0
    h, w = mask.shape
    if h < 2 or w < 2:
        return 0
    row = mask[h // 2, :]
    # Бінаризуємо
    row_bin = (row > 0).astype(np.uint8)
    # Рахуємо переходи 0->1 і 1->0
    diffs = np.diff(row_bin)
    transitions = int(np.count_nonzero(diffs))
    return transitions
