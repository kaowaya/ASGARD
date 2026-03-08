---
name: C3.14-析锂检测-SV/RV
description: >
  通过比对同温/同倍率下，充电与放电过程的电压差分解（对称电压滞回差分），识别 LFP (磷酸铁锂) 或 NCM 在高 SOC 下的不可逆析锂极化特征。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM]
tier: L3
compute_requirement: >512MB RAM, CPU
pricing: Premium
tags:
  - lithium-plating
  - lfp-specialty
  - charge-discharge-symmetry
visibility: public
---

# C3.14 析锂检测 (SV-RV 法)

## When to use this skill

Use this skill when:
- 检测 LFP (磷酸铁锂) 的微弱析锂，或者在没有充分条件享受“长时不间断静置”时。
- 依赖于用户具备一定的充放电深度对冲（例如晚间慢充，白天特定时段放电）。

## Quick Start
```bash
python templates/python/svr_rv_plating.py \
   --charge data_samples/input/charge.csv \
   --discharge data_samples/input/discharge.csv \
   --output output/c3_14_li.json
```

## How it works
算法将两个独立的 CSV (充电和放电) 按照注入容量/SOC 对齐拼接。
计算对称滞回压差 $\Delta V_{sv}(Q)$ 以及其对应的增量斜率。
提取斜率在高电量区的畸变峰，标记为析锂预警。
