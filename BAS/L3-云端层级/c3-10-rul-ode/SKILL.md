---
name: C3.10-RUL预测-半物理ODE
description: >
  基于电化学衰减机理（SEI生长随时间平方根定律与Arrhenius方程）的半物理常微分方程（ODE），对未来任意长周期的寿命进行带约束的前向预测。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM]
tier: L3
compute_requirement: >512MB RAM, SciPy, CPU
pricing: Advanced
tags:
  - rul-prediction
  - ode
  - physical-model
  - life-estimation
visibility: public
---

# C3.10 RUL预测 (半物理ODE)

## When to use this skill

Use this skill when:
- 想要评估储能电站未来的重置成本，需要预估到哪一年哪一月电池 SOH 会掉到 80% 以下。
- 需要基于物理公式而非“深度学习瞎猜”，以确保外推预测曲线的单调性与合理性。

## Quick Start
```bash
python templates/python/ode_rul_predict.py \
   --current_soh 92.5 \
   --profile "standard_1c" \
   --output output/c3_10_rul.json
```

## How it works
1. 初始化 ODE 系统，并将当前真实系统的 $SOH_{initial}$ 注入积分起点。
2. 配置未来的每日预期负荷画像 `Profile` (如每日工作小时数、平均温度、充放电倍率)。
3. 使用 `solve_ivp` 或者 `odeint` 前向数值步进求解非线性系统，直到 $SOH < 80\%$ 挂起，截断输出生命周期。
