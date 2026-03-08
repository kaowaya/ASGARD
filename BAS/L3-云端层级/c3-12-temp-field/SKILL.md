---
name: C3.12-温度场重构
description: >
  利用外部表面温度NTC数据与充放电产热模型，运用反演观测器估算电池真正的内部核心温度 (T_core)。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM]
tier: L3
compute_requirement: >256MB RAM, CPU
pricing: Standard
tags:
  - thermal-model
  - state-estimation
  - safety
visibility: public
---

# C3.12 温度场重构 (T_core)

## When to use this skill

Use this skill when:
- 想挖掘电池在高负荷（例如 4C 超充或下赛道）时的真实内部热边界。
- 为基于内部温度激发的后续高级特征（如C3.13析锂）提供更为精准的热力学输入参考。

## Quick Start
```bash
python templates/python/temp_core_reconstruct.py \
   --input data_samples/input/thermal_profile.csv \
   --output output/c3_12_tcore.json
```

## How it works
这是一个基于二阶集总参数热模型的数值观测器。它将读取历史电流（计算焦耳热 $I^2 R$）以及表面温度传感器，推导出热阻带来的内外温差梯度，从而反向还原核心温度 $T_{core} $。
