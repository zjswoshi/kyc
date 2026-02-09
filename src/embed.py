from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from insightface.app import FaceAnalysis


@dataclass
class FaceEmbedding:
    vector: np.ndarray


class FaceEmbedder:
    """ArcFace/InsightFace embedding wrapper."""

    def __init__(self, model_name: str = "buffalo_l", ctx_id: int = 0, det_size: tuple[int, int] = (640, 640)):
        self.app = FaceAnalysis(name=model_name)
        self.app.prepare(ctx_id=ctx_id, det_size=det_size)

    def embed(self, face_bgr: np.ndarray) -> FaceEmbedding:
        faces = self.app.get(face_bgr)
        if not faces:
            return FaceEmbedding(vector=np.zeros((512,), dtype=np.float32))
        face = max(faces, key=lambda f: f.bbox[2] * f.bbox[3])
        emb = face.embedding.astype(np.float32)
        norm = np.linalg.norm(emb) + 1e-9
        emb = emb / norm
        return FaceEmbedding(vector=emb)
