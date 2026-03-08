---
name: C3.11-热失控预警-MEMS
description: >
  融合气压变率、VOC气体浓度以及局部温度上翘特征，判定防爆阀是否排气(Venting)，发出火灾逃生前的终极预警信号。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Solid-State, Na-ion]
tier: L3
compute_requirement: >256MB RAM, CPU
pricing: Critical-Safety
tags:
  - thermal-runaway
  - sensor-fusion
  - safety-critical
visibility: public
---

# C3.11 热失控MEMS感知与预警

## When to use this skill

Use this skill when:
- 硬件平台已配备了箱内绝对压力传感器 (Absolute Pressure) 与可燃气体传感器 (VOC/CO/H2)。
- 车辆或储能系统对接了消防联动接口。

## Quick Start
```bash
python templates/python/thermal_mems_warning.py \
   --input data_samples/input/mems_stream.csv \
   --output output/c3_11_alarm.json
```

## How it works
高频扫描 MEMS 时序流：
计算 $dP / dt$ (压力导数) 过滤掉缓慢的海拔变化。如果导数超过某阈值，激活联动状态机。
结合可燃气体浓度的非线性飙升以及温度配合，过滤水汽带来的误报，确信度达标后触发报警。
