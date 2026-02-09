from __future__ import annotations

import argparse
from pathlib import Path

from insightface.app import FaceAnalysis


def download_retinaface(model_name: str = "buffalo_l", ctx_id: int = -1, det_size: tuple[int, int] = (640, 640)) -> Path:
    app = FaceAnalysis(name=model_name)
    app.prepare(ctx_id=ctx_id, det_size=det_size)
    return Path(app.model_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download InsightFace/RetinaFace models")
    parser.add_argument("--model", default="buffalo_l", help="InsightFace model pack name")
    parser.add_argument("--cpu", action="store_true", help="Force CPU download/prepare")
    parser.add_argument("--det-size", default="640,640", help="Detector input size, e.g. 640,640")
    args = parser.parse_args()

    det_w, det_h = [int(x) for x in args.det_size.split(",")]
    ctx_id = -1 if args.cpu else 0

    model_dir = download_retinaface(args.model, ctx_id=ctx_id, det_size=(det_w, det_h))
    print(f"Downloaded to: {model_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
