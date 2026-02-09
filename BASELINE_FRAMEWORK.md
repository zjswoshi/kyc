# KYC Baseline Framework (Python)

This baseline provides a minimal, runnable pipeline for:
- Face detection (Haar cascade fallback)
- Face embedding (placeholder histogram)
- Matching (cosine similarity)
- PAD heuristics (texture/frequency/motion/rPPG)

## Files
- src/detect.py: detection (RetinaFace/MTCNN/Haar)
- src/align.py: face crop/resize
- src/embed.py: ArcFace/InsightFace embeddings
- src/match.py: cosine similarity
- src/pad_*.py: PAD heuristic modules
- src/fuse.py: score fusion
- src/pipeline.py: CLI entry
- src/download_models.py: download InsightFace/RetinaFace weights
- configs/thresholds.yaml: default thresholds
- requirements.txt: dependencies

## Notes
- InsightFace is integrated for ArcFace embeddings.
- Provide image pairs CSV for FAR/FRR/EER using eval_metrics.py.
- Provide PAD samples CSV for APCER/BPCER using eval_pad.py.
- InsightFace weights download is automatic on first run, or run download_models.py.
- MTCNN weights are bundled within the mtcnn package (no manual download).
- PAD modules are heuristic baselines for print/screen replay tests.
- Tune thresholds in configs/thresholds.yaml using your own data.
