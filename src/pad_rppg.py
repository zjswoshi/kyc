from __future__ import annotations

from typing import List

import numpy as np
import cv2


def rppg_snr(frames_bgr: List[np.ndarray]) -> float:
    """Estimate rPPG SNR from green channel mean signal.

    Returns SNR in [0,1] (heuristic).
    """
    if len(frames_bgr) < 30:
        return 0.0

    g = []
    for frame in frames_bgr:
        green = frame[:, :, 1]
        g.append(np.mean(green))

    signal = np.array(g, dtype=np.float32)
    signal = signal - np.mean(signal)

    fft = np.fft.rfft(signal)
    power = np.abs(fft) ** 2

    # Rough band selection: 0.7-3.0 Hz mapped to bins by ratio
    n = len(signal)
    freqs = np.fft.rfftfreq(n, d=1 / 30)  # assume 30 fps
    band = (freqs >= 0.7) & (freqs <= 3.0)
    band_power = float(np.sum(power[band]))
    noise_power = float(np.sum(power[~band])) + 1e-9

    snr = band_power / noise_power
    snr_norm = float(np.clip(snr / 5.0, 0.0, 1.0))
    return snr_norm
