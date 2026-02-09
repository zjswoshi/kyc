from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np

from .detect import FaceDetector, select_largest_face
from .align import crop_and_resize
from .embed import FaceEmbedder
from .match import cosine_similarity


def load_pairs(csv_path: Path) -> List[Tuple[str, str, int]]:
    pairs = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            left, right, label = [x.strip() for x in line.split(",")]
            pairs.append((left, right, int(label)))
    return pairs


def compute_scores(pairs: List[Tuple[str, str, int]]) -> Tuple[List[float], List[int]]:
    detector = FaceDetector(backend="retinaface")
    embedder = FaceEmbedder()

    scores = []
    labels = []

    for left, right, label in pairs:
        img1 = cv2.imread(left)
        img2 = cv2.imread(right)
        if img1 is None or img2 is None:
            continue

        b1 = select_largest_face(detector.detect_faces(img1))
        b2 = select_largest_face(detector.detect_faces(img2))
        if b1 is None or b2 is None:
            continue

        f1 = crop_and_resize(img1, b1)
        f2 = crop_and_resize(img2, b2)

        e1 = embedder.embed(f1)
        e2 = embedder.embed(f2)
        sim = cosine_similarity(e1, e2)

        scores.append(sim)
        labels.append(label)

    return scores, labels


def far_frr_at_threshold(scores: List[float], labels: List[int], threshold: float) -> Tuple[float, float]:
    fa = 0
    fr = 0
    pos = 0
    neg = 0

    for s, y in zip(scores, labels):
        if y == 1:
            pos += 1
            if s < threshold:
                fr += 1
        else:
            neg += 1
            if s >= threshold:
                fa += 1

    far = fa / max(neg, 1)
    frr = fr / max(pos, 1)
    return far, frr


def find_eer(scores: List[float], labels: List[int]) -> Tuple[float, float]:
    thresholds = np.linspace(0.0, 1.0, 201)
    best_thr = 0.0
    best_gap = 1.0
    best_eer = 1.0

    for thr in thresholds:
        far, frr = far_frr_at_threshold(scores, labels, thr)
        gap = abs(far - frr)
        if gap < best_gap:
            best_gap = gap
            best_thr = thr
            best_eer = (far + frr) / 2.0

    return best_eer, best_thr


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute FAR/FRR/EER from image pairs")
    parser.add_argument("--pairs", required=True, help="CSV: img1,img2,label(1=same,0=diff)")
    parser.add_argument("--threshold", type=float, default=0.40, help="Cosine threshold")
    args = parser.parse_args()

    pairs = load_pairs(Path(args.pairs))
    scores, labels = compute_scores(pairs)
    if not scores:
        print("No valid pairs processed")
        return 1

    far, frr = far_frr_at_threshold(scores, labels, args.threshold)
    eer, eer_thr = find_eer(scores, labels)

    print(f"Pairs: {len(scores)}")
    print(f"FAR@{args.threshold:.2f}: {far:.4f}")
    print(f"FRR@{args.threshold:.2f}: {frr:.4f}")
    print(f"EER: {eer:.4f} at threshold {eer_thr:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
