---
name: C3.0-云端异常清洗与特征提取器
description: >
  基于Pandas和NumPy矢量化架构的车联网电池时序数据预处理管道。
  解决车联网数据断点、乱序、毛刺突变问题，并自动衍生高级电化学特征。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Semi-Solid, Solid-State]
tier: L3
compute_requirement: >1GB RAM, x86/ARM64 Server
pricing: Free
tags:
  - data-pipeline
  - preprocessing
  - feature-engineering
  - cloud-native
visibility: public
---

# C3.0 云端异常清洗与特征提取器

## When to use this skill

Use this skill when:
- 准备运行任何 L3 层级的云端高级算法 (例如内短路诊断、析锂分析)。
- 获取到的原始 T-Box 车联网数据是不规则的、含有大量 NAN 和传感器噪声突变的。
- 需要在将数据喂入深度学习模型前，将其对齐到标准的时间网格并提取特征 (dV/dt, dT/dt 等)。

**替代方案**:
- 若数据来源本身就是台架 (Lab tester) 的高精度已清洗数据，可以跳过该模块直接喂入算法。

## Quick Start
1. **准备输入数据**: 含有任意时间戳格式的原始脏数据 CSV。
2. **运行清洗管道**:
   ```bash
   python templates/python/pipeline.py \
       --input data_samples/input/raw_noisy_data.csv \
       --output output/clean_features.csv \
       --freq 1S \
       --col-vol voltage \
       --v-min 0.0 \
       --v-max 1000.0
   ```

## Decisions Points
- **长时断点处理**: 若存在大于 15 分钟的断连，默认切断为多个独立的 "Segment"（连续时间段），不进行跨片段强行线性插值。
- **重采样频率**: 强烈建议统一归一化为 `1S` (1秒一条)。因为诸如**析锂分析 (Lithium Plating)** 等高阶电化学特征，需要极高精度的松弛电压曲线，如果降采样到 `10S` 会导致关键的高频电化学反应特征丢失。保留原分辨率的同时统一网格是云端清洗的核心法则。

## How it works
1. **时间窗对齐**: 利用 `pandas.DataFrame.resample` 结合时间索引，把不规则数据映射成确定频率的时序网格。
2. **孤立点剔除 (Z-Score & Bounds)**: 设定电压物理极值约束且剔除 dV/dt 超过极限的“毛刺”。
3. **特征衍生**:
   - `dV_dt`: 每秒电压变化率。
   - `dI_dt`: 用于判断工况剧烈程度。
   - `dT_dt`: 第一温升导数。

## Quality Checklist
- [ ] Pipeline 严禁使用多层 Python `for` 循环操作 Row，必须 100% 矢量化，保证批处理速度。
- [ ] 处理输出后必须绝对保证时间戳是严格单调递增且等间隔的。

## Extended References
- [templates/python/pipeline.py](templates/python/pipeline.py)
