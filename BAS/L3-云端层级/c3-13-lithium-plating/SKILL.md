---
name: C3.13-析锂检测-弛豫法
description: >
  通过捕获大倍率/低温充电结束后静置期的电压平台拐点 (dV/dt极值)，确凿诊断负极表面是否发生了不可逆或可逆的析锂现象。
version: "1.0.0"
author: ASGARD
battery_types: [NCM, LFP (Limited applicability due to flat OCV)]
tier: L3
compute_requirement: >512MB RAM, CPU
pricing: Premium
tags:
  - lithium-plating
  - relaxation
  - anomaly-detection
visibility: public
---

# C3.13 析锂检测-弛豫法

## When to use this skill

Use this skill when:
- 车辆完成了一次快充 (Fast Charge) 或在极寒环境下完成充电。
- 充电后伴随着至少 30 分钟 - 1 小时的带电静置 (Rest/Relaxation)。

## Quick Start
```bash
python templates/python/lithium_plating_relax.py \
   --input data_samples/input/post_charge_rest.csv \
   --output output/c3_13_lithium.json
```

## How it works
算法利用 `scipy.signal` 的 Savitzky-Golay 或者高斯滤波压平充电机断开的电磁毛刺，计算电压随时间的演化率 $dV/dt$。
如果没有析锂，该导数是单调平滑的；若探测到了“先平缓后急降”的局部拐点，则认定触发了金属锂剥离现象，标记严重异常并累计析锂标签。
