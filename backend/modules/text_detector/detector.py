# modules/text_detector/detector.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import cv2
import numpy as np

from .utils import TextRegion, bbox_center, bbox_area, merge_bboxes, crop_mask_from_region
from .filters import filter_regions, estimate_neighbor_density, classify_text_block
from .cluster import cluster_regions_dbscan


BBox = Tuple[int, int, int, int]


@dataclass
class TextBlock:
    id: int
    bbox: BBox
    center: Tuple[float, float]
    mser_count: int
    type: str
    confidence: float


def _build_regions_from_mser(
    gray: np.ndarray,
    regions: List[np.ndarray],
    boxes: List[BBox],
) -> List[TextRegion]:
    """Перетворює вихід MSER у список TextRegion."""
    result: List[TextRegion] = []
    for contour, box in zip(regions, boxes):
        x, y, w, h = box
        if w <= 0 or h <= 0:
            continue
        mask = crop_mask_from_region(gray, contour, box)
        center = bbox_center(box)
        area = bbox_area(box)
        result.append(TextRegion(box=box, center=center, area=area, mask=mask))
    return result


def detect_text(image_bgr: np.ndarray) -> List[TextBlock]:
    """
    Головна функція детекції тексту.
    Повертає список TextBlock, кожен з яких є кластером тексту (слово/рядок/SFX-блок).
    """
    # 1. Нормалізація
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    h_img, w_img = gray.shape[:2]

    # 2. MSER-детектор
    # параметри можна буде підкрутити під типові розміри твоїх сторінок
    mser = cv2.MSER_create(delta=5, min_area=20, max_area=1500)

    # Pass 1: оригінал
    regions1, boxes1 = mser.detectRegions(gray)
    boxes1 = [tuple(map(int, b)) for b in boxes1]

    # Pass 2: інверсія
    inv = 255 - gray
    regions2, boxes2 = mser.detectRegions(inv)
    boxes2 = [tuple(map(int, b)) for b in boxes2]

    all_regions = regions1 + regions2
    all_boxes = boxes1 + boxes2

    # 3. Побудова TextRegion
    regions = _build_regions_from_mser(gray, all_regions, all_boxes)

    if not regions:
        return []

    # 4. Первинні фільтри (area, aspect, transitions)
    regions = filter_regions(regions)

    if not regions:
        return []

    # 5. Фільтр по щільності сусідів
    keep_mask = estimate_neighbor_density(regions, radius=25.0)
    regions = [r for r, k in zip(regions, keep_mask) if k]

    if not regions:
        return []

    # 6. Кластеризація (DBSCAN / fallback)
    clusters = cluster_regions_dbscan(regions, eps=40.0, min_samples=2)

    blocks: List[TextBlock] = []
    block_id = 1

    for cluster_indices in clusters:
        cluster_regions = [regions[i] for i in cluster_indices]
        cluster_boxes = [r.box for r in cluster_regions]

        # Об'єднаний bbox
        merged_box = merge_bboxes(cluster_boxes)
        cx, cy = bbox_center(merged_box)
        mser_count = len(cluster_regions)

        # Класифікація типу тексту
        text_type, conf = classify_text_block(merged_box, mser_count, len(cluster_regions))

        blocks.append(
            TextBlock(
                id=block_id,
                bbox=(
                    max(0, merged_box[0]),
                    max(0, merged_box[1]),
                    min(merged_box[2], w_img - merged_box[0]),
                    min(merged_box[3], h_img - merged_box[1]),
                ),
                center=(float(cx), float(cy)),
                mser_count=mser_count,
                type=text_type,
                confidence=float(conf),
            )
        )
        block_id += 1

    return blocks
