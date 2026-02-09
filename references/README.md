# KYC Facial Verification References

本目录用于保存可公开下载的 KYC 人脸核验相关文献与报告（优先 PDF）。

## 计划下载文献

### 人脸表征学习（可作为 1:1 比对基线）
- ArcFace (CVPR 2019)
- CosFace (CVPR 2018)
- FaceNet (CVPR 2015)
- SphereFace (CVPR 2017)

### 活体检测 / 反攻击（PAD）
- Silent-Face-Anti-Spoofing (MiniFASNet)

### 评测与规范性报告（公开）
- NIST FRVT Ongoing report
- NIST Digital Identity Guidelines (SP 800-63-3)

## 无法直接下载的标准（受版权限制）
以下标准通常需要通过 ISO/IEC 渠道购买或机构订阅：
- ISO/IEC 30107（PAD）
- ISO/IEC 19795（生物识别性能测试）
- ISO/IEC 29794（样本质量）

## 下载方法
在仓库根目录执行：

```bash
bash scripts/download_references.sh
```


## 说明
- 如运行环境受限（例如外网被阻断），脚本会继续执行并在 `references/download_failed.txt` 记录失败项。
