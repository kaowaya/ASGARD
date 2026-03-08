---
name: C3.8-ICA深度分析
description: >
  基于大数据的增量容量分析(dQ/dV)。对慢充或恒流数据进行深度滤波并提取电化学相变峰位，诊断 SOH 衰减的老化微观机理(LLI, LAM)。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion]
tier: L3
compute_requirement: >512MB RAM, SciPy, CPU
pricing: Advanced
tags:
  - aging-mechanism
  - ica
  - dq-dv
  - signal-processing
visibility: public
---

# C3.8 ICA 深度分析 (dQ/dV)

## When to use this skill

Use this skill when:
- 想要评估电池的**内部老化机理**（如活性锂损失、电极材料损失），不满足于仅仅知道宏观的剩余容量。
- 获取到了较长且相对平稳的恒流充电（CC Charge）工况数据。

## Quick Start
```bash
python templates/python/ica_analysis.py \
   --input data_samples/input/cc_charge_segment.csv \
   --output output/c3_8_ica_peaks.json
```

## How it works
1. 读取 $V$, $I$, $t$。积分得到 $Q$（容量）。
2. 应用 Savitzky-Golay 平滑滤波器压制量化噪声。
3. 数值求导 $dQ / dV$。
4. 使用 `scipy.signal.find_peaks` 锁定相变峰，并给出峰高与峰宽反馈老化特征。
