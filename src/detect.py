from __future__ import annotations

from dataclasses import dataclass
from typing import List

import cv2
import numpy as np
from insightface.app import FaceAnalysis


@dataclass
class FaceBox:
    x: int
    y: int
    w: int
    h: int
    score: float = 1.0


class FaceDetector:
    """Detector wrapper supporting RetinaFace, MTCNN, and Haar."""

    def __init__(
        self,
        backend: str = "retinaface",
        min_size: int = 40,
        scale_factor: float = 1.1,
        min_neighbors: int = 5,
        ctx_id: int = 0,
        det_size: tuple[int, int] = (640, 640),
    ):
        self.backend = backend
        self.min_size = min_size
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors

        self._haar = None
        self._mtcnn = None
        self._retina = None

        if backend == "haar":
            self._haar = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
        elif backend == "mtcnn":
            try:
                from mtcnn import MTCNN  # type: ignore

                self._mtcnn = MTCNN()
            except Exception as exc:  # pragma: no cover
                raise RuntimeError("MTCNN backend requires the 'mtcnn' package") from exc
        elif backend == "retinaface":
            self._retina = FaceAnalysis(name="buffalo_l")
            self._retina.prepare(ctx_id=ctx_id, det_size=det_size)
        else:
            raise ValueError("backend must be one of: retinaface, mtcnn, haar")

    def detect_faces(self, image_bgr: np.ndarray) -> List[FaceBox]:
        if self.backend == "haar":
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            boxes = self._haar.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=(self.min_size, self.min_size),
            )
            return [FaceBox(int(x), int(y), int(w), int(h), 1.0) for (x, y, w, h) in boxes]

        if self.backend == "mtcnn":
            rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            results = self._mtcnn.detect_faces(rgb)
            boxes = []
            for r in results:
                x, y, w, h = r.get("box", [0, 0, 0, 0])
                score = float(r.get("confidence", 1.0))
                boxes.append(FaceBox(int(x), int(y), int(w), int(h), score))
            return boxes

        faces = self._retina.get(image_bgr)
        boxes = []
        for f in faces:
            x1, y1, x2, y2 = f.bbox.astype(int)
            boxes.append(FaceBox(int(x1), int(y1), int(x2 - x1), int(y2 - y1), float(f.det_score)))
        return boxes


def select_largest_face(boxes: List[FaceBox]) -> FaceBox | None:
    if not boxes:
        return None
    return max(boxes, key=lambda b: b.w * b.h)
