from __future__ import annotations

import numpy as np
import cv2


def freq_score(face_bgr: np.ndarray, high_freq_ratio_threshold: float = 0.35) -> float:
    """Return frequency-based spoof score in [0,1]. Higher = more suspicious."""
    gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude = np.abs(fshift)

    h, w = magnitude.shape
    cy, cx = h // 2, w // 2
    radius = min(h, w) // 8
    low = magnitude[cy - radius : cy + radius, cx - radius : cx + radius]
    low_energy = np.sum(low)
    total_energy = np.sum(magnitude) + 1e-9
    high_ratio = float(1.0 - (low_energy / total_energy))

    score = float(np.clip(high_ratio / max(high_freq_ratio_threshold, 1e-6), 0.0, 1.0))
    return score
