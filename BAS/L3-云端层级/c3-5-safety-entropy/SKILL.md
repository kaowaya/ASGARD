---
name: C3.5-安全熵
description: >
  基于多维信息熵理论，将单体电压、温度、容量流失等分布从时域转换为概率分布，量化电池包的退化与热失控风险（安全熵增）。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM]
tier: L3
compute_requirement: >512MB RAM, CPU
pricing: Premium
tags:
  - anomaly-detection
  - shannon-entropy
  - statistics
visibility: public
---

# C3.5 多维安全熵评分

## When to use this skill

Use this skill when:
- 需要给整个电池 Pack 给出一个无量纲的、平滑的“安全评分（0~100）”展示给终端用户。
- 传统阈值报警（压差、温差过大）很容易造成虚警，需要借用信息熵的系统不确定性来做柔性判断。

## Quick Start
```bash
python templates/python/safety_entropy.py \
   --input data_samples/input/pack_features.csv \
   --output output/c3_5_report.json
```

## How it works
此算子提取一段时间里各电芯 dV/dt (电压梯度) 和 dT/dt (温度梯度) 的概率密度函数 $P(x)$。
计算香农信息熵：
$S = -\sum P(x) \log(P(x))$

- 如果系统纯净且一致性极高（大家都一样），熵值极低。
- 随着电池衰减、一致性变差或是出现热异常，分布变得“混乱和宽泛”，系统的多维信息熵急剧上升，当熵超过危险阈值，输出安全报警。
