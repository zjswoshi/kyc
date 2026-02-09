from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np

from .detect import FaceBox


def crop_and_resize(image_bgr: np.ndarray, box: FaceBox, size: Tuple[int, int] = (112, 112)) -> np.ndarray:
    h, w = image_bgr.shape[:2]
    x1 = max(0, box.x)
    y1 = max(0, box.y)
    x2 = min(w, box.x + box.w)
    y2 = min(h, box.y + box.h)
    face = image_bgr[y1:y2, x1:x2]
    if face.size == 0:
        return np.zeros((size[1], size[0], 3), dtype=np.uint8)
    return cv2.resize(face, size, interpolation=cv2.INTER_LINEAR)
