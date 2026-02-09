from __future__ import annotations

from typing import List

import numpy as np
import cv2


def motion_score(frames_bgr: List[np.ndarray], low_threshold: float = 2.0, high_threshold: float = 20.0) -> float:
    """Return motion-based spoof score in [0,1]. Higher = more suspicious.

    Heuristic: mean frame difference too low/high implies replay artifacts.
    """
    if len(frames_bgr) < 2:
        return 0.0

    diffs = []
    prev = cv2.cvtColor(frames_bgr[0], cv2.COLOR_BGR2GRAY)
    for frame in frames_bgr[1:]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = np.mean(cv2.absdiff(gray, prev))
        diffs.append(diff)
        prev = gray

    mean_diff = float(np.mean(diffs))
    if mean_diff < low_threshold:
        return 1.0
    if mean_diff > high_threshold:
        return 0.7
    return 0.2
