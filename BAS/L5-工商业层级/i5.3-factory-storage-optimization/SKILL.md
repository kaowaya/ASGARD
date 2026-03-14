---
name: I5.3 工厂配储优化系统
description: |
  工业用户侧储能配置与运行优化系统，基于工厂生产模式、负荷特性、电价政策，
  优化储能容量配置和运行策略，实现投资回报最大化。

  核心功能：
  - 储能容量优化配置（CAPEX决策）
  - 生产-储能协同调度
  - 需量管理与基本电费优化
  - 投资回报率分析
  - 全生命周期经济性评估

version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Semi-Solid]
tier: L5
category: 能源管理
deployment: 企业SaaS
compute_requirement: Cloud
pricing: Enterprise
tags: [factory, storage-sizing, demand-management, roi-optimization]
visibility: public
---

# I5.3 工厂配储优化系统

## 概述

针对工业用户的储能配置与运行优化系统，综合考虑工厂生产模式、负荷特性、电价政策、储能成本等多因素，优化储能容量配置和运行策略，实现投资回报最大化。

## 商业价值

### 经济效益
- **降低电费**：峰谷套利 + 需量管理，电费节省20-40%
- **最优配置**：避免过投资或欠配置
- **快速回本**：投资回收期2-4年
- **增值服务**：参与辅助服务增加收益

### 技术优势
- **生产协同**：考虑生产计划与储能协同
- **需量管理**：精准控制最大需量
- **全生命周期**：考虑电池衰减与残值
- **风险评估**：投资风险量化分析

## When to use this skill

### 1. 高耗能行业
- 钢铁、水泥、化工
- 大功率设备冲击负荷
- 需量费用占比高

### 2. 精密制造
- 半导体、电子制造
- 供电质量要求高
- UPS备电需求

### 3. 连续生产
- 化工、冶金
- 24小时连续运行
- 峰平谷电价差异大

## 算法原理

### 1. 储能容量优化
```
Objective: Maximize NPV
= Σ(Annual_Savings - Annual_O&M) × Annuity_Factor - CAPEX

Subject to:
- SOC_min ≤ SOC ≤ SOC_max
- P_min ≤ P ≤ P_max
- 储能寿命 ≥ 最小要求
- IRR ≥ 目标收益率
```

### 2. 生产协同
```python
def coordinate_with_production(production_schedule, load_profile):
    """
    基于生产计划的储能调度
    """
    for shift in production_schedule:
        if shift.is_peak_production:
            # 峰值生产时段，储能放电支持
            discharge(shift.duration)
        elif shift.is_idle:
            # 闲置时段，充电
            charge(shift.duration)
```

### 3. 需量管理
```
Demand_Charge = max(Peak_Load) × Demand_Price

储能控制策略：
if Load_Power + Battery_Power > Demand_Contract:
    Battery_Power = Demand_Contract - Load_Power
```

## API接口

### 优化请求
```http
POST /api/v1/factory-storage/optimize
{
  "factory_id": "FAC_001",
  "load_profile": [...],
  "production_schedule": [...],
  "electricity_price": {...},
  "optimization_objective": "npv"  # npv/irr/payback
}
```

## 使用示例

```python
from asgard.bas.l5.factory_storage import FactoryStorageOptimizer

optimizer = FactoryStorageOptimizer(config)
result = optimizer.optimize_capacity(
    load_profile=daily_load,
    price_schedule=tou_price,
    production_shifts=shifts
)

print(f"最优容量: {result.capacity_mw} MW/{result.capacity_mwh} MWh")
print(f"投资回收期: {result.payback_period} 年")
print(f"内部收益率: {result.irr:.1%}")
```
