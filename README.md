# KYC (Know Your Customer)

This repository contains comprehensive research and documentation about KYC processes, with a focus on facial verification technology.

## Contents

- **[KYC Facial Verification Deep Research (CN)](./KYC_FACIAL_VERIFICATION_DEEP_RESEARCH_CN.md)** - 中文深度研究手册，包含关键词、阅读路线、攻击面清单与研究模板。
- **[KYC Facial Verification Research Guide](./KYC_FACIAL_VERIFICATION_RESEARCH_GUIDE.md)** - A comprehensive guide covering key points and keywords for in-depth research on KYC facial verification, including:
  - Core concepts and technical components
  - Implementation workflows
  - Regulatory and compliance requirements
  - Security and privacy considerations
  - Technologies, algorithms, and industry standards
  - Performance metrics and best practices
  - Future trends and research resources

## About KYC

Know Your Customer (KYC) is a standard in the financial services industry that ensures businesses verify the identity of their clients. Facial verification is an increasingly important component of digital KYC processes, enabling secure and convenient remote identity verification.

## Getting Started

If you're researching KYC facial verification, start with the [comprehensive research guide](./KYC_FACIAL_VERIFICATION_RESEARCH_GUIDE.md) which provides detailed information on all aspects of facial verification technology for identity verification purposes.

## Baseline Framework Usage Flow

### 1) Install Dependencies
- Install Python dependencies from [requirements.txt](./requirements.txt).

### 2) Download Models (RetinaFace/InsightFace)
- Run the downloader in [src/download_models.py](./src/download_models.py) to prefetch weights.
- MTCNN weights are bundled with the `mtcnn` package (no manual download).

### 3) Run Baseline Pipeline
- Use [src/pipeline.py](./src/pipeline.py) with `--image` or `--video`.
- Configure detector backend in [configs/thresholds.yaml](./configs/thresholds.yaml).

### 4) Evaluate Face Matching (FAR/FRR/EER)
- Prepare a CSV of image pairs: `img1,img2,label` (label: 1 same, 0 different).
- Run [src/eval_metrics.py](./src/eval_metrics.py).

### 5) Evaluate PAD (APCER/BPCER)
- Prepare a CSV of samples: `path,label` (label: 1 spoof, 0 bonafide).
- Run [src/eval_pad.py](./src/eval_pad.py).

### 6) Tune Thresholds
- Adjust defaults in [configs/thresholds.yaml](./configs/thresholds.yaml) based on your data.
