---
name: C3.4-内短路诊断-等效电路
description: >
  利用动态工况（高频充放电），基于二阶 Thevenin 等效电路进行参数辨识提取视在内阻异常特征，辅助内短路预警。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM]
tier: L3
compute_requirement: >512MB RAM, CPU
pricing: Standard
tags:
  - isc-detection
  - ecm
  - rls
visibility: public
---

# C3.4 内短路诊断-等效电路

## When to use this skill

Use this skill when:
- 缺乏充分静置时长（不适用 C3.2），但具备高动态变载工况数据。
- 需要实时或准实时的云内阻剥离估计与交叉验证。

## Quick Start
```bash
python templates/python/ecm_isc_diagnosis.py \
   --input data_samples/input/dynamic_segment.csv \
   --output output/c3_4_report.json
```

## How it works
算法利用递推最小二乘法 (RLS) 基于 Thevenin 模型结构动态拟合输入-输出序列 (I-V)。
拟合参数 $R_0$ 若相较健康包均值发现严重飘移，即通过电阻网络特性推导出并联微短路特征。
