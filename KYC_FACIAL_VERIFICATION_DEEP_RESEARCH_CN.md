# KYC 人脸核验深度研究手册（中文）

## 1. 核心概念（先打基础）
- **1:1 验证**：核验“自拍是否与证件照同一人”，是 KYC 主流场景。
- **1:N 识别**：在大库里搜索“这是谁”，更常见于安防，不是开户主流程。
- **人脸核验流水线**：检测（Detection）→ 对齐（Alignment）→ 表征（Embedding）→ 相似度比对（Matching）。
- **活体检测（PAD）**：防照片翻拍、屏幕回放、面具、深伪等攻击。

## 2. 你必须关注的指标
- **FAR / FMR**：误接收率（把攻击者当真人放过）。
- **FRR / FNMR**：误拒率（把真人拒绝）。
- **TAR@FAR=x**：在某安全阈值下的通过能力。
- **EER**：FAR 与 FRR 相等时的误差点。
- **APCER / BPCER（PAD）**：攻击被放过率 / 真人被误拒率。

> 研究时一定问：数据集是什么？阈值设多少？是在什么 FAR 点报出的 TAR？

## 3. 攻击面清单（Threat Model）
- 打印照片攻击（print attack）
- 屏幕回放攻击（replay attack）
- 3D 面具攻击（3D mask）
- 深伪/换脸视频攻击（deepfake/face swap）
- 摄像头流注入攻击（injection attack）
- 合成身份（synthetic identity）与人工作弊代过活体

## 4. 高价值研究关键词（可直接检索）

### 4.1 人脸核验与表征学习
- `face verification embedding ArcFace CosFace SphereFace`
- `metric learning for face recognition`
- `face image quality assessment`

### 4.2 活体与反攻击（PAD）
- `presentation attack detection ISO 30107`
- `face anti-spoofing replay print 3D mask`
- `active liveness passive liveness`
- `rPPG liveness detection`

### 4.3 KYC 业务流程与风控
- `document selfie matching`
- `identity proofing onboarding fraud`
- `risk-based authentication KYC`
- `step-up verification manual review`

### 4.4 合规与治理
- `ISO/IEC 19795 biometric performance testing`
- `NIST FRVT face recognition`
- `GDPR biometric data`
- `BIPA biometric privacy`

## 5. 建议阅读顺序（4 周）
1. **第 1 周：基础**
   - 学会 pipeline 与核心指标（FAR/FRR/TAR/EER）。
2. **第 2 周：PAD 专题**
   - 按攻击类型研究论文，重点看 APCER/BPCER 与泛化能力。
3. **第 3 周：KYC 全流程**
   - 证件真伪 + OCR 一致性 + 自拍比对 + 风险评分联动。
4. **第 4 周：合规与运营**
   - 数据留存、删除策略、人工复核、审计日志、偏差监控。

## 6. 论文/厂商评估模板（可复制）

```md
# 标题
- 类型：论文 / 标准 / 厂商白皮书 / 评测报告
- 时间：
- 场景：开户KYC / 高风险交易复核 / 账户接管防护

## 1) 问题定义
- 解决什么问题？
- 适用业务边界是什么？

## 2) 方法
- 输入输出是什么？
- 是否依赖端侧能力或特定硬件？

## 3) 数据与评测
- 数据来源：公开/私有
- 人群分布：年龄/肤色/设备/地区
- 攻击覆盖：print/replay/mask/deepfake/injection
- 指标：FAR/FRR/TAR@FAR/APCER/BPCER/时延

## 4) 结果
- 在低 FAR 点表现如何？
- 是否给了置信区间和显著性分析？

## 5) 风险与局限
- 偏差问题有哪些？
- 从实验室到线上是否可迁移？

## 6) 合规
- 数据最小化、保留期、删除机制
- 用户告知与同意机制

## 7) 结论
- 是否值得落地？
- 还缺哪些证据？
```

## 7. 最终研究产出建议
- 一页 **指标字典**（统一定义 FAR/FRR/TAR/APCER/BPCER）。
- 一页 **攻击覆盖矩阵**（每种攻击是否覆盖、覆盖深度）。
- 一页 **阈值策略建议**（安全 vs 转化率）。
- 一页 **合规清单**（收集、处理、留存、删除、审计）。

---

如果你后续要继续，我可以再补一份《30 天学习计划（每天 1 小时）》文档版本。

## 8. 目前可作为基准的开源 KYC 相关模型/方案

严格来说没有一个“官方通用 KYC 大一统模型”，但可以用以下开源组件拼出强基线：

### 8.1 人脸比对（1:1）基线
- **InsightFace (ArcFace)**：工业界常用开源基线，识别与验证能力强。
- **facenet-pytorch / FaceNet 复现**：教学与快速原型常用。
- **DeepFace（聚合库）**：便于快速横向比较 ArcFace/Facenet/VGGFace 等。

### 8.2 活体检测（PAD）基线
- **Silent-Face-Anti-Spoofing（MiniFASNet）**：轻量、社区常见。
- **Face Anti-Spoofing Challenge 相关开源复现**：可用于 print/replay 场景基线。

### 8.3 证件 OCR 与字段一致性
- **PaddleOCR / Tesseract**：做证件字段抽取和与用户输入比对。
- **MRZ 解析开源库**：用于护照等机读区一致性核验。

### 8.4 建议的“可复现实验基线”
- Face verification：使用 ArcFace embedding + cosine similarity。
- PAD：使用 MiniFASNet（二分类 bonafide/attack）。
- 规则引擎：
  - 若 PAD 分数 < 阈值 → 拒绝；
  - 否则用 face score 与证件一致性分数组合决策。

> 结论：有开源“组件级”基线，但没有直接可商用的完整开源 KYC 套件；真正上线还需要补齐合规、审计、重试流程与人工复核闭环。
