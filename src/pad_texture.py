from __future__ import annotations

import numpy as np
import cv2
from skimage.feature import local_binary_pattern


def texture_score(face_bgr: np.ndarray, lbp_points: int = 8, lbp_radius: int = 1) -> float:
    """Return a texture-based spoof score in [0,1]. Higher = more suspicious.

    Heuristic: normalized LBP entropy.
    """
    gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
    lbp = local_binary_pattern(gray, lbp_points, lbp_radius, method="uniform")
    hist, _ = np.histogram(lbp.ravel(), bins=lbp_points + 2, range=(0, lbp_points + 2))
    hist = hist.astype(np.float32)
    hist = hist / (hist.sum() + 1e-9)
    entropy = -np.sum(hist * np.log(hist + 1e-9))
    score = float(np.clip(entropy / 2.5, 0.0, 1.0))
    return score
