from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PadScores:
    texture: float
    freq: float
    motion: float
    rppg: float


@dataclass
class PadDecision:
    score: float
    is_spoof: bool


def fuse_scores(scores: PadScores, weights: dict, decision_threshold: float) -> PadDecision:
    total = (
        scores.texture * weights.get("texture", 0.0)
        + scores.freq * weights.get("freq", 0.0)
        + scores.motion * weights.get("motion", 0.0)
        + scores.rppg * weights.get("rppg", 0.0)
    )
    is_spoof = total >= decision_threshold
    return PadDecision(score=total, is_spoof=is_spoof)
