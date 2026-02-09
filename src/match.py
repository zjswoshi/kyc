from __future__ import annotations

import numpy as np

from .embed import FaceEmbedding


def cosine_similarity(a: FaceEmbedding, b: FaceEmbedding) -> float:
    va = a.vector
    vb = b.vector
    denom = (np.linalg.norm(va) * np.linalg.norm(vb)) + 1e-9
    return float(np.dot(va, vb) / denom)
