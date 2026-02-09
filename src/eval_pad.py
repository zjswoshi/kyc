from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple

import cv2
import yaml

from .detect import FaceDetector, select_largest_face
from .align import crop_and_resize
from .pad_texture import texture_score
from .pad_freq import freq_score
from .pad_motion import motion_score
from .pad_rppg import rppg_snr
from .fuse import PadScores, fuse_scores


def read_video_frames(video_path: Path, max_frames: int = 120) -> List:
    cap = cv2.VideoCapture(str(video_path))
    frames = []
    while len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames


def load_config(config_path: Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_pad_samples(csv_path: Path) -> List[Tuple[str, int]]:
    samples = []
    with open(csv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            path, label = [x.strip() for x in line.split(",")]
            samples.append((path, int(label)))
    return samples


def score_sample(detector: FaceDetector, config: dict, path: str) -> float | None:
    if path.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
        frames = read_video_frames(Path(path))
        if not frames:
            return None
        face = select_largest_face(detector.detect_faces(frames[0]))
        if face is None:
            return None
        face_frames = [crop_and_resize(f, face) for f in frames]
        tex = texture_score(face_frames[0], config["pad"]["texture"]["lbp_points"], config["pad"]["texture"]["lbp_radius"])
        fq = freq_score(face_frames[0], config["pad"]["freq"]["high_freq_ratio_threshold"])
        mot = motion_score(face_frames, config["pad"]["motion"]["mean_diff_low_threshold"], config["pad"]["motion"]["mean_diff_high_threshold"])
        rppg = rppg_snr(face_frames)
    else:
        image = cv2.imread(path)
        if image is None:
            return None
        face = select_largest_face(detector.detect_faces(image))
        if face is None:
            return None
        face_img = crop_and_resize(image, face)
        tex = texture_score(face_img, config["pad"]["texture"]["lbp_points"], config["pad"]["texture"]["lbp_radius"])
        fq = freq_score(face_img, config["pad"]["freq"]["high_freq_ratio_threshold"])
        mot = 0.0
        rppg = 0.0

    scores = PadScores(texture=tex, freq=fq, motion=mot, rppg=rppg)
    decision = fuse_scores(scores, config["fusion"]["weights"], config["fusion"]["decision_threshold"])
    return decision.score


def compute_apcer_bpcer(scores: List[float], labels: List[int], threshold: float) -> Tuple[float, float]:
    # label: 1=spoof (attack), 0=bonafide
    apc = 0
    bpc = 0
    attack = 0
    bona = 0

    for s, y in zip(scores, labels):
        if y == 1:
            attack += 1
            if s < threshold:
                apc += 1
        else:
            bona += 1
            if s >= threshold:
                bpc += 1

    apcer = apc / max(attack, 1)
    bpcer = bpc / max(bona, 1)
    return apcer, bpcer


def find_eer_like(scores: List[float], labels: List[int]) -> Tuple[float, float]:
    thresholds = [i / 100 for i in range(0, 101)]
    best_gap = 1.0
    best_thr = 0.5
    best_val = 1.0

    for thr in thresholds:
        apcer, bpcer = compute_apcer_bpcer(scores, labels, thr)
        gap = abs(apcer - bpcer)
        if gap < best_gap:
            best_gap = gap
            best_thr = thr
            best_val = (apcer + bpcer) / 2.0

    return best_val, best_thr


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute APCER/BPCER for PAD")
    parser.add_argument("--samples", required=True, help="CSV: path,label(1=spoof,0=bonafide)")
    parser.add_argument("--config", default="configs/thresholds.yaml")
    parser.add_argument("--threshold", type=float, default=None, help="Decision threshold")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    detector = FaceDetector(backend=config.get("detector", {}).get("backend", "retinaface"))

    samples = load_pad_samples(Path(args.samples))
    scores = []
    labels = []

    for path, label in samples:
        score = score_sample(detector, config, path)
        if score is None:
            continue
        scores.append(score)
        labels.append(label)

    if not scores:
        print("No valid samples processed")
        return 1

    threshold = args.threshold
    if threshold is None:
        threshold = config["fusion"]["decision_threshold"]

    apcer, bpcer = compute_apcer_bpcer(scores, labels, threshold)
    eer_like, eer_thr = find_eer_like(scores, labels)

    print(f"Samples: {len(scores)}")
    print(f"APCER@{threshold:.2f}: {apcer:.4f}")
    print(f"BPCER@{threshold:.2f}: {bpcer:.4f}")
    print(f"EER-like: {eer_like:.4f} at threshold {eer_thr:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
