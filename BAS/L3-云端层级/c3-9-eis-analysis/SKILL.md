---
name: C3.9-EIS谱图分析
description: >
  基于 Tikhonov 正则化，将非平稳的 EIS (电化学阻抗谱) Nyquist 频域数据反演为 DRT (弛豫时间分布)，解耦提取特定界面反应的物理衰退机制。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Solid-State]
tier: L3
compute_requirement: >512MB RAM, SciPy, CPU
pricing: Advanced
tags:
  - eis
  - drt
  - tikhonov-regularization
  - impedance
visibility: public
---

# C3.9 EIS谱图分析 (DRT)

## When to use this skill

Use this skill when:
- 新能源汽车/储能系统具备“在线交流阻抗” (Online EIS) 发生能力。
- 你想精确区分电池的阻抗增加是源于 SEI 膜加厚、极化内阻还是纯欧姆内阻上升。

## Quick Start
```bash
python templates/python/eis_analysis.py \
   --input data_samples/input/pack_eis_scan.csv \
   --output output/c3_9_drt.json
```

## How it works
这是一个计算高度密集的非适定方程求解：
$Z_{Im}(f) = -\int_{0}^{\infty} \frac{2\pi f \tau}{1 + (2\pi f \tau)^2} G(\tau) d(\ln \tau)$

算子使用 `scipy.optimize` 中的线性代数或最小二乘法进行 Tikhonov 正则化拟合，输出各个特征时间尺度下的峰面积。
