---
name: C3.7-SOH深度学习网络
description: >
  使用时序 LSTM 结合 XGBoost 的混合深度学习策略，纯利用云端不连贯的碎片化工况片段推算电芯健康衰减状态 (SOH)。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM]
tier: L3
compute_requirement: >2GB RAM, GPU/TRT Recommended
pricing: Advanced
tags:
  - soh-estimation
  - deep-learning
  - lstm
  - xgboost
visibility: public
---

# C3.7 SOH 深度学习 (LSTM + XGBoost)

## When to use this skill

Use this skill when:
- 车辆因为使用习惯问题（如出租车、网约车）几周甚至几个月都没有发生满充满放，导致 L2 板端 BMS OCV 修正功能失灵，SOH 锁死假死。
- 你需要在云端利用任何只要持续大于十分钟的行车充放电“碎片片段”，推算出当前 SOH。

## Quick Start
```bash
python templates/python/soh_dl_inference.py \
   --input data_samples/input/fragment_features.csv \
   --output output/c3_7_soh.json
```

## How it works
这是一个推理前向脚本 (Inference Script)。
模型训练阶段（离线）：收集百万车辆完整工况，利用已知的 SOH 标签，训练一个能够提取片段工况隐藏特征的 LSTM 编码器，然后用 XGBoost 回归 SOH。
模型推理阶段（本算子）：将车辆传入的最新数据矩阵投喂给 PyTorch 的 LSTM 模型获取 Embedding，送入预训练的 XGBoost 分类器直接吐出 SOH 预测值。
