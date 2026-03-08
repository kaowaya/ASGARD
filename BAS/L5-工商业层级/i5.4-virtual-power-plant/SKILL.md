---
name: I5.4 虚拟电站VPP系统
description: |
  Virtual Power Plant (VPP) 虚拟电站聚合管理系统，将分布式储能、可控负荷、分布式电源等
  聚合为虚拟电厂参与电力市场交易，实现规模化调度与协同优化。

  核心功能：
  - 分布式资源聚合与建模
  - 多目标协同优化调度
  - 电力市场竞价策略
  - 聚合收益分配机制
  - 可视化监控与指挥

version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion]
tier: L5
category: 能源管理
deployment: 企业SaaS
compute_requirement: Cloud
pricing: Enterprise
tags: [vpp, virtual-power-plant, aggregation, market-bidding]
visibility: public
---

# I5.4 虚拟电站VPP系统

## 概述

VPP系统将地理上分散的分布式储能、可控负荷、分布式电源等聚合为虚拟电厂，统一参与电力市场交易和电网调度，实现规模化效益。

## 商业价值

### 电网价值
- **灵活调节**：提供调频调峰能力
- **延缓投资**：减少电网升级需求
- **新能源消纳**：提高可再生能源利用率

### 用户价值
- **规模收益**：聚沙成塔，提升议价能力
- **收益分成**：参与VPP获得额外收益
- **专业化运营**：无需专业运营团队

## 应用场景

### 1. 调频市场
- AGC调频服务
- 快速频率响应
- 惯量支撑

### 2. 备用市场
- 旋转备用
- 非旋转备用
- 替代备用

### 3. 能量市场
- 日前市场竞价
- 实时平衡
- 峰谷套利

## 算法原理

### 1. 资源聚合
```
P_vpp_total = Σ(P_storage_i + P_load_i + P_dg_i)

约束条件：
- 通信延迟 ≤ 要求
- 响应时间 ≤ 要求
- 可用率 ≥ 阈值
```

### 2. 市场竞价
```python
def optimize_bidding(market_prices, resource_costs, constraints):
    """
    市场竞价优化
    """
    objective = maximize(revenue - costs)

    # 出力约束
    sum(P_i) = P_vpp
    P_min_i ≤ P_i ≤ P_max_i

    # 网络约束
    power_flow_within_limits

    return bid_curve
```

### 3. 收益分配
```
收益分配方法：
1. 按贡献比例分配
2. Shapley值分配
3. 核心解分配
```

## API接口

```http
POST /api/v1/vpp/aggregate
{
  "vpp_id": "VPP_001",
  "resources": ["ESS_001", "ESS_002", ...],
  "market": "frequency_regulation",
  "period": "2025-03-08"
}

POST /api/v1/vpp/bid
{
  "vpp_id": "VPP_001",
  "market": "day_ahead",
  "bids": [...]
}
```

## 使用示例

```python
from asgard.bas.l5.vpp import VirtualPowerPlant

vpp = VirtualPowerPlant(config)

# 聚合资源
vpp.aggregate_resources(resource_list)

# 市场竞价
bid = vpp.generate_bid(market_type='frequency_regulation')

# 下发调度指令
vpp.dispatch(bid_quantity)
```
