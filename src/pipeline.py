from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import cv2
import numpy as np
import yaml

from .detect import FaceDetector, select_largest_face
from .align import crop_and_resize
from .embed import FaceEmbedder
from .match import cosine_similarity
from .pad_texture import texture_score
from .pad_freq import freq_score
from .pad_motion import motion_score
from .pad_rppg import rppg_snr
from .fuse import PadScores, fuse_scores


def read_video_frames(video_path: Path, max_frames: int = 120) -> List[np.ndarray]:
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


def main() -> int:
    parser = argparse.ArgumentParser(description="KYC baseline pipeline (det/rec/PAD)")
    parser.add_argument("--image", type=str, help="Input selfie image path")
    parser.add_argument("--video", type=str, help="Input selfie video path")
    parser.add_argument("--reference", type=str, help="Reference ID face image path")
    parser.add_argument("--config", type=str, default="configs/thresholds.yaml")
    args = parser.parse_args()

    if not args.image and not args.video:
        print("Provide --image or --video")
        return 1

    config = load_config(Path(args.config))

    detector_backend = config.get("detector", {}).get("backend", "retinaface")
    detector = FaceDetector(backend=detector_backend)
    embedder = FaceEmbedder()

    if args.image:
        image = cv2.imread(args.image)
        if image is None:
            print("Failed to read image")
            return 1
        boxes = detector.detect_faces(image)
        face = select_largest_face(boxes)
        if face is None:
            print("No face detected")
            return 1
        face_img = crop_and_resize(image, face)

        tex = texture_score(face_img, config["pad"]["texture"]["lbp_points"], config["pad"]["texture"]["lbp_radius"])
        fq = freq_score(face_img, config["pad"]["freq"]["high_freq_ratio_threshold"])
        scores = PadScores(texture=tex, freq=fq, motion=0.0, rppg=0.0)
        decision = fuse_scores(scores, config["fusion"]["weights"], config["fusion"]["decision_threshold"])

        print(f"PAD score: {decision.score:.3f}, spoof={decision.is_spoof}")

        if args.reference:
            ref = cv2.imread(args.reference)
            if ref is None:
                print("Failed to read reference image")
                return 1
            ref_boxes = detector.detect_faces(ref)
            ref_face = select_largest_face(ref_boxes)
            if ref_face is None:
                print("No face in reference")
                return 1
            ref_img = crop_and_resize(ref, ref_face)

            emb1 = embedder.embed(face_img)
            emb2 = embedder.embed(ref_img)
            sim = cosine_similarity(emb1, emb2)
            thr = config["recognition"]["cosine_threshold"]
            print(f"Cosine similarity: {sim:.3f}, match={sim >= thr}")
        return 0

    if args.video:
        frames = read_video_frames(Path(args.video))
        if not frames:
            print("Failed to read video")
            return 1
        # detect face on first frame for PAD features
        boxes = detector.detect_faces(frames[0])
        face = select_largest_face(boxes)
        if face is None:
            print("No face detected")
            return 1
        face_frames = [crop_and_resize(f, face) for f in frames]

        tex = texture_score(face_frames[0], config["pad"]["texture"]["lbp_points"], config["pad"]["texture"]["lbp_radius"])
        fq = freq_score(face_frames[0], config["pad"]["freq"]["high_freq_ratio_threshold"])
        mot = motion_score(face_frames, config["pad"]["motion"]["mean_diff_low_threshold"], config["pad"]["motion"]["mean_diff_high_threshold"])
        rppg = rppg_snr(face_frames)

        scores = PadScores(texture=tex, freq=fq, motion=mot, rppg=rppg)
        decision = fuse_scores(scores, config["fusion"]["weights"], config["fusion"]["decision_threshold"])

        print(f"PAD score: {decision.score:.3f}, spoof={decision.is_spoof}")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
