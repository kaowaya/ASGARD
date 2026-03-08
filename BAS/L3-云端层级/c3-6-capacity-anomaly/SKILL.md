---
name: C3.6-容量异常检测
description: >
  基于群体大数据的孤立森林(Isolation Forest)无监督异常检测，旨在同批次车队中抓取衰减极度异常的落后车辆或电芯。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion]
tier: L3
compute_requirement: >1GB RAM, Python/Scikit-learn, CPU
pricing: Advanced
tags:
  - anomaly-detection
  - machine-learning
  - isolation-forest
  - fleet-management
visibility: public
---

# C3.6 容量异常检测

## When to use this skill

Use this skill when:
- 你拥有一个完整的车队 (Fleet) 或者储能集装箱簇级别的数据。
- 需要以月或季度为周期，筛选出异常衰减（相比于同样使用强度的同类车辆）的产品进行召回或检修。
- 没有大量带标签的故障数据，需要纯量化无监督算法。

## Quick Start
```bash
python templates/python/capacity_anomaly.py \
   --input data_samples/input/fleet_stats.csv \
   --output output/c3_6_anomaly.json
```

## How it works
基于 `scikit-learn` 实现的 Isolation Forest。随机森林切开多维特征空间，异常样本因为离群，将被以极短的路径深度隔离出来。
输出 -1 代表异常离群点，1 代表正常群体。
