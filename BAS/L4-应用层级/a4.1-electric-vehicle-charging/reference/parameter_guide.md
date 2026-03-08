# 电动汽车充电优化参数指南

## 1. 输入参数详解

### 1.1 电池参数

#### battery_capacity (电池容量)
- **类型**: float
- **单位**: kWh
- **范围**: 40-100 kWh
- **典型值**:
  - 紧凑型EV: 40-50 kWh (如比亚迪海豚)
  - 中型EV: 60-75 kWh (如特斯拉Model 3)
  - 大型EV: 80-100 kWh (如奔驰EQS)

**影响**: 直接决定充电时间和能量需求

#### current_soc (当前SOC)
- **类型**: float
- **单位**: %
- **范围**: 0-100%
- **精度**: ±1%

**注意事项**:
- SOC<20%时需小电流预充
- SOC>80%时充电功率需降低
- 建议日常使用范围: 20-80%

#### target_soc (目标SOC)
- **类型**: float
- **单位**: %
- **范围**: 0-100%
- **推荐值**:
  - 日常通勤: 80%
  - 长途出行: 90-95%
  - V2G模式: 50-60%

#### current_soh (当前健康状态)
- **类型**: float
- **单位**: %
- **范围**: 60-100%
- **阈值**:
  - SOH>80%: 正常使用
  - 70%<SOH<80%: 老化明显，建议降低充电倍率
  - SOH<70%: 需要更换电池

#### battery_type (电池类型)
- **类型**: string
- **可选值**: 'LFP', 'NCM', 'Na-ion', 'Semi-Solid', 'Solid-State'

**特性对比**:

| 特性 | LFP | NCM | Na-ion | Semi-Solid |
|------|-----|-----|--------|------------|
| 能量密度 | 150 Wh/kg | 250 Wh/kg | 140 Wh/kg | 300 Wh/kg |
| 循环寿命 | 3000+ | 1500+ | 2000+ | 1000+ |
| 充电倍率 | 1-2C | 1-3C | 1-2C | 2-4C |
| 工作温度 | -20~60°C | -20~55°C | -20~55°C | -30~60°C |
| 成本 | 低 | 中 | 低 | 高 |

### 1.2 充电约束参数

#### time_window (充电时间窗口)
- **类型**: int
- **单位**: hours
- **范围**: 1-24
- **典型场景**:
  - 家用过夜充: 8-10 hours
  - 办公室充电: 4-8 hours
  - 快充站: 0.5-1 hour
  - 高速服务区: 0.25-0.5 hour

#### charge_rate_limit (充电功率限制)
- **类型**: float
- **单位**: kW
- **充电等级**:
  - Level 1: 1.4 kW (家用插座)
  - Level 2: 7-22 kW (家用充电桩)
  - DC快充: 50-150 kW
  - 超充: 250-350 kW

### 1.3 电价参数

#### price_schedule (电价计划)
- **类型**: array
- **单位**: $/kWh
- **典型电价**:
  - 居民电价: $0.12-0.20/kWh
  - 工商业电价: $0.08-0.15/kWh
  - 峰谷价差: 2-4倍

**峰谷时段划分**:
- 谷电: 23:00-07:00 (0.5×基础电价)
- 平电: 07:00-10:00, 15:00-18:00 (1.0×)
- 峰电: 10:00-15:00, 18:00-23:00 (1.5×)

#### enable_v2g (启用V2G)
- **类型**: bool
- **要求**:
  - 双向充电桩
  - 电网运营商许可
  - 适合的峰谷价差 (>30%)

#### v2g_power_limit (V2G功率限制)
- **类型**: float
- **单位**: kW
- **典型值**: 7-22 kW
- **约束**: 通常≤充电功率

### 1.4 优化策略参数

#### priority (优化优先级)
- **类型**: string
- **可选值**: 'cost', 'speed', 'health'

**权重配置**:

| 优先级 | w1(成本) | w2(时间) | w3(健康) | w4(电网) |
|--------|----------|----------|----------|----------|
| cost | 0.6 | 0.1 | 0.2 | 0.1 |
| speed | 0.2 | 0.5 | 0.2 | 0.1 |
| health | 0.2 | 0.2 | 0.5 | 0.1 |

## 2. 输出结果说明

### 2.1 充电计划 (charging_schedule)
- **格式**: array [kW]
- **长度**: time_window
- **示例**: [0, 0, 7, 7, 11, 0, 0, 0]

**解读**:
- 正值: 充电功率
- 负值: V2G放电功率
- 0: 空闲

### 2.2 SOC轨迹 (soc_trajectory)
- **格式**: array [%]
- **长度**: time_window + 1
- **示例**: [20, 20, 31, 42, 53, 64, 75, 86, 90]

**关键点**:
- soc_trajectory[0] = 初始SOC
- soc_trajectory[-1] = 最终SOC
- 单调递增（不考虑V2G）

### 2.3 成本估算 (estimated_cost)
- **格式**: float
- **单位**: $
- **计算**:
  ```
  cost = Σ(charging_schedule[i] × price[i])
  ```

### 2.4 V2G收益 (v2g_revenue)
- **格式**: float
- **单位**: $
- **计算**:
  ```
  revenue = Σ(discharge[i] × sell_price[i])
  ```
- **净收益**: revenue - cost

### 2.5 电池老化 (battery_degradation)
- **格式**: float
- **单位**: % SOH
- **组成**:
  - 循环老化: 0.01-0.05% / cycle
  - 日历老化: 0.0002% / day

### 2.6 优化建议 (recommendations)

#### best_charging_hours
- **类型**: List[int]
- **含义**: 最佳充电时段索引
- **示例**: [2, 3, 4, 5] (凌晨2-5点)

#### average_price
- **类型**: float
- **单位**: $/kWh
- **含义**: 平均充电电价

#### cost_saving_potential
- **类型**: string
- **含义**: 相比即时充电的成本节约潜力
- **范围**: 10-40%

#### battery_health_tip
- **类型**: string
- **示例**: "建议保持SOC在20-80%之间"

#### preconditioning
- **类型**: string
- **示例**: "建议充电前预热电池至25°C"

## 3. 参数调优策略

### 3.1 成本优化调优

**目标**: 最小化充电成本

**参数设置**:
```python
{
    'priority': 'cost',
    'time_window': 12,  # 延长窗口以覆盖低价时段
    'target_soc': 80,  # 避免高SOC区的低效率
    'enable_v2g': False
}
```

**预期效果**:
- 成本降低: 20-40%
- 充电时间: 增加2-4小时

### 3.2 速度优化调优

**目标**: 最短充电时间

**参数设置**:
```python
{
    'priority': 'speed',
    'time_window': 4,  # 缩短窗口
    'charge_rate_limit': 150,  # 最大快充功率
    'target_soc': 80  # 80%即可满足大多数需求
}
```

**预期效果**:
- 充电时间: 20-30分钟 (20-80%)
- 成本增加: 10-20%
- 电池老化: +15%

### 3.3 健康优化调优

**目标**: 最小化电池老化

**参数设置**:
```python
{
    'priority': 'health',
    'target_soc': 80,  # 避免满充
    'charge_rate_limit': 22,  # 限制充电倍率
    'current_soc_range': [20, 80]  # SOC工作区间
}
```

**预期效果**:
- 电池老化: 降低30-50%
- 充电时间: 增加50-100%
- 成本: 持平或略降

### 3.4 V2G优化调优

**目标**: 最大化V2G收益

**参数设置**:
```python
{
    'priority': 'cost',
    'enable_v2g': True,
    'v2g_power_limit': 11,
    'price_spread_threshold': 0.3,  # 价差>30%才启动V2G
    'soc_v2g_range': [30, 80]  # V2G允许的SOC范围
}
```

**预期效果**:
- V2G收益: $50-200/月
- 电池老化: 增加10-20%
- 充电效率: 降低5-10%

## 4. 特殊场景参数

### 4.1 极寒环境 (T < 0°C)
```python
{
    'preheating': True,  # 预热电池
    'charge_rate_limit': 11,  # 降低充电功率
    'target_soc': 80  # 避免满充
}
```

### 4.2 高温环境 (T > 35°C)
```python
{
    'charge_rate_limit': 50,  # 限制充电功率
    'thermal_management': 'active',  # 主动冷却
    'target_soc': 80
}
```

### 4.3 电池老化严重 (SOH < 80%)
```python
{
    'priority': 'health',
    'charge_rate_limit': 22,  # 保守充电
    'soc_range': [30, 70],  # 缩小SOC范围
    'frequency': 'weekly'  # 减少充放电频率
}
```

### 4.4 微电网场景
```python
{
    'priority': 'grid',
    'enable_v2g': True,
    'grid_support': True,  # 支持电网
    'renewables_integration': True  # 配合可再生能源
}
```

## 5. 参数验证规则

### 5.1 输入验证
```python
assert 0 <= current_soc <= 100, "SOC must be in [0, 100]"
assert current_soc < target_soc, "Target SOC must be greater than current"
assert 1 <= time_window <= 24, "Time window must be in [1, 24]"
assert len(price_schedule) >= time_window, "Price schedule too short"
```

### 5.2 物理约束
```python
assert energy_needed <= battery_capacity * 0.9, "Cannot charge >90%"
assert charge_rate_limit <= battery_capacity * 3, "Cannot exceed 3C"
assert abs(temperature) <= 50, "Temperature out of safe range"
```

### 5.3 电网约束
```python
assert sum(charging_schedule) <= energy_needed * 1.05, "Overcharging"
assert all(p <= max_grid_power for p in charging_schedule), "Grid limit exceeded"
```

## 6. 参数敏感性分析

### 6.1 对成本的影响
- **电价波动**: ±10% → 成本变化 ±8%
- **充电窗口**: ±2h → 成本变化 ±15%
- **目标SOC**: ±10% → 成本变化 ±12%

### 6.2 对时间的影响
- **充电功率**: ±20% → 时间变化 ±17%
- **目标SOC**: ±10% → 时间变化 ±10%
- **电池容量**: ±10% → 时间变化 ±10%

### 6.3 对健康的影响
- **充电倍率**: ±0.5C → 老化变化 ±25%
- **SOC范围**: ±10% → 老化变化 ±15%
- **温度**: ±10°C → 老化变化 ±50%
