# modules/text_detector/filters.py

from typing import List, Tuple
import numpy as np

from .utils import TextRegion, bbox_area, count_black_white_transitions


def filter_regions(
    regions: List[TextRegion],
    min_area: int = 20,
    max_area: int = 3000,
    max_aspect_ratio: float = 5.0,
    min_transitions: int = 2,
    max_transitions: int = 12,
) -> List[TextRegion]:
    """Фільтр MSER-регіонів за площею, пропорціями, переходами."""

    filtered: List[TextRegion] = []

    for r in regions:
        x, y, w, h = r.box
        area = bbox_area(r.box)
        if area < min_area or area > max_area:
            continue

        if w == 0 or h == 0:
            continue

        ar1 = h / float(w)
        ar2 = w / float(h)
        if ar1 > max_aspect_ratio or ar2 > max_aspect_ratio:
            continue

        # Переходи чорне/біле по масці
        transitions = count_black_white_transitions(r.mask)
        if transitions < min_transitions or transitions > max_transitions:
            continue

        filtered.append(r)

    return filtered


def estimate_neighbor_density(regions: List[TextRegion], radius: float = 25.0) -> List[bool]:
    """
    Для кожного регіону оцінюємо, чи є поруч сусіди.
    Повертаємо масив масок: True = залишити, False = видалити (ізольований шум).
    """
    if not regions:
        return []

    centers = np.array([r.center for r in regions], dtype=np.float32)
    n = len(regions)
    keep = [False] * n

    for i in range(n):
        diffs = centers - centers[i]
        dist2 = diffs[:, 0] ** 2 + diffs[:, 1] ** 2
        # рахуємо, скільки точок у радіусі (виключаючи саму себе)
        neighbors = int(np.count_nonzero(dist2 <= radius * radius)) - 1
        if neighbors >= 1:
            keep[i] = True

    return keep


def classify_text_block(
    bbox: Tuple[int, int, int, int],
    mser_count: int,
    region_count: int,
) -> Tuple[str, float]:
    """
    Груба класифікація типу тексту за bbox та кількістю регіонів.

    Повертає:
        (type, confidence)
    type ∈ {"dialog", "sfx", "background", "unknown"}
    """

    x, y, w, h = bbox
    area = w * h
    aspect = w / float(h + 1e-6)

    # Діалог: не надто великий блок, ширший ніж високий, помірна кількість регіонів
    if mser_count >= 3 and mser_count <= 60 and area <= 200000 and 0.6 <= aspect <= 5.0:
        return "dialog", 0.9

    # SFX: дуже великий блок або дуже багато MSER-регіонів
    if mser_count > 60 or area > 200000:
        return "sfx", 0.9

    # background: маленький блок, небагато регіонів
    if area < 15000 and mser_count <= 10:
        return "background", 0.6

    return "unknown", 0.5
