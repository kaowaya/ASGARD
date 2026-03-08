---
name: I5.1 微网能量管理系统
description: |
  工商业微网综合能量管理系统，集成光伏、储能、负荷预测、电网交互等多维度优化。
  支持多种运行模式（削峰填谷、需量控制、新能源消纳、应急备电），实现微网经济性最优运行。

  核心功能：
  - 多时间尺度优化（日前/实时/日内滚动）
  - 多目标优化（经济性/碳排放/可靠性）
  - 多种约束条件（电池SOC/功率/充放电次数）
  - 实时功率平衡与调度指令下发
  - 微网运行状态监控与告警

version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Semi-Solid, Solid-State]
tier: L5
category: 能源管理
deployment: 企业SaaS
compute_requirement: Cloud
pricing: Enterprise
tags: [microgrid, energy-management, optimization, pv-storage, peak-shaving]
visibility: public
---

# I5.1 微网能量管理系统

## 概述

微网能量管理系统是工商业储能的核心应用层算法，通过智能调度实现微网内多种能源设备（光伏、储能、负荷、电网）的协调运行，最大化经济效益和新能源利用率。

## 商业价值

### 经济效益
- **电费优化**：通过峰谷价差套利，降低企业用电成本15-30%
- **需量管理**：控制最大需量，降低基本电费
- **新能源消纳**：提高光伏自发自用比例，减少购电成本
- **辅助服务**：参与电网调频调峰，获取额外收益

### 技术优势
- **多时间尺度**：日前计划（24h）、日内滚动（4h）、实时控制（5min）
- **多目标优化**：经济性、碳排放、供电可靠性的加权平衡
- **自适应算法**：基于历史数据学习和预测误差修正
- **快速响应**：毫秒级功率指令下发

## 应用场景

### 1. 工业园区
- 高峰负荷平抑
- 需量控制
- 光伏消纳

### 2. 商业综合体
- 峰谷套利
- 应急备电
- 绿电认证

### 3. 数据中心
- 供电可靠性保障
- 能耗优化
- 碳排放追踪

### 4. 充电站
- 光储充一体化
- 负荷预测
- 柔性充电

## 算法原理

### 1. 负荷预测
```python
# 基于LSTM的时间序列预测
model = LSTM_Load_Predictor(
    lookback=168,  # 过去7天数据
    features=['temp', 'humidity', 'day_of_week', 'hour', 'holiday']
)
```

### 2. 混合整数线性规划（MILP）
```python
from scipy.optimize import milp, LinearConstraint, Bounds

# 决策变量
# P_grid[t]: 电网购电功率
# P_pv[t]: 光伏发电功率
# P_charge[t]: 储能充电功率
# P_discharge[t]: 储能放电功率
# SOC[t]: 电池荷电状态

# 目标函数
minimize: sum(C_electricity[t] * P_grid[t] * dt)  # 最小化电费

# 约束条件
# - 功率平衡约束
# - SOC动态约束
# - 电池功率约束
# - 需量约束
```

### 3. 实时修正
```python
# 滚动优化策略
def rolling_optimization(current_time, prediction_horizon=4):
    # 获取最新预测
    load_forecast = predict_load(current_time, prediction_horizon)
    pv_forecast = predict_pv(current_time, prediction_horizon)

    # 求解优化问题
    optimal_schedule = solve_milp(load_forecast, pv_forecast)

    # 仅执行第一个时间步
    execute_control(optimal_schedule[0])

    # 每小时滚动更新
    schedule_next_roll(current_time + timedelta(hours=1))
```

## 参数配置

### 系统配置
```yaml
microgrid_config:
  # 储能系统
  storage:
    capacity_kwh: 2000        # 电池容量
    max_power_kw: 1000        # 最大充放电功率
    soc_min: 0.1              # SOC下限
    soc_max: 0.9              # SOC上限
    efficiency: 0.95          # 循环效率
    cycle_life: 6000          # 循环寿命

  # 光伏系统
  pv:
    capacity_kw: 1500         # 装机容量
    degradation_rate: 0.005   # 年衰减率

  # 电网参数
  grid:
    max_import_kw: 2000       # 最大购电功率
    max_export_kw: 1000       # 最大卖电功率
    demand_charge_rate: 40    # 需量电费（元/kW/月）

  # 电价
  electricity_price:
    type: "TOU"               # 分时电价
    peak_price: 1.2           # 峰电价（元/kWh）
    valley_price: 0.4         # 谷电价（元/kWh）
    flat_price: 0.7           # 平电价（元/kWh）
```

### 优化参数
```yaml
optimization_config:
  time_resolution: 0.25       # 时间步长（小时）
  optimization_horizon: 24    # 优化时域（小时）
  rolling_interval: 1         # 滚动间隔（小时）

  objective_weights:
    cost: 1.0                 # 经济性权重
    carbon: 0.3               # 碳排放权重
    reliability: 0.5          # 可靠性权重

  constraints:
    max_cycle_per_day: 2      # 每日最大充放电次数
    reserve_capacity: 0.2     # 备用容量比例
```

## API接口

### 1. 运行优化
```http
POST /api/v1/microgrid/optimize
Content-Type: application/json

{
  "start_time": "2025-03-08T00:00:00",
  "horizon_hours": 24,
  "mode": "economic",  # economic/carbon/reliability
  "current_soc": 0.5,
  "load_forecast": [...],
  "pv_forecast": [...]
}
```

### 2. 实时控制
```http
POST /api/v1/microgrid/control
Content-Type: application/json

{
  "timestamp": "2025-03-08T14:30:00",
  "current_load": 850,
  "current_pv": 320,
  "current_soc": 0.65,
  "grid_price": 1.15
}
```

### 3. 数据查询
```http
GET /api/v1/microgrid/status
Response:
{
  "soc": 0.68,
  "power": 150,  # 正值充电，负值放电
  "grid_import": 520,
  "grid_export": 0,
  "pv_generation": 380,
  "load": 750,
  "mode": "peak_shaving",
  "daily_savings": 328.50  # 元
}
```

## 数据要求

### 输入数据
- **负荷数据**：历史15分钟级负荷曲线（至少3个月）
- **光伏数据**：历史15分钟级发电数据（至少3个月）
- **电价数据**：分时电价表（TOU/实时电价）
- **气象数据**：温度、辐照度、天气预报
- **设备参数**：电池容量、功率、效率等

### 输出数据
- **优化调度**：24小时充放电功率曲线
- **SOC轨迹**：24小时SOC变化曲线
- **功率平衡**：各时段功率流向
- **经济分析**：电费节省、收益分析
- **碳排放**：CO2减排量

## 性能指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| 电费节省率 | 相比无储能的电费节省比例 | ≥15% |
| 光伏消纳率 | 自发自用比例 | ≥80% |
| 需量削减率 | 最大需量降低比例 | ≥20% |
| 预测准确度 | 负荷预测MAPE | ≤10% |
| 响应时间 | 控制指令下发延迟 | ≤100ms |
| 计算时间 | 优化求解时间 | ≤30s |

## 部署要求

### 软件环境
- Python 3.9+
- SciPy 1.9+, Pyomo 6.0+
- Redis（实时数据缓存）
- PostgreSQL（历史数据存储）
- Kafka（消息队列）

### 硬件要求
- CPU: 8核+ （优化求解）
- 内存: 32GB+
- 存储: 500GB SSD

### 网络要求
- 与SCADA系统通信（Modbus/OPC UA）
- 与EMS系统集成（REST API）
- 与气象数据接口（HTTP API）

## 使用示例

```python
from asgard.bas.l5.microgrid import MicrogridManager

# 初始化微网管理器
mgr = MicrogridManager(config_path="config/microgrid.yaml")

# 运行日前优化
schedule = mgr.run_day_ahead_optimization(
    date="2025-03-08",
    mode="economic"
)

# 获取优化结果
print(f"预计节省电费: {schedule.savings:.2f} 元")
print(f"光伏消纳率: {schedule.pv_self_consumption_rate:.1%}")

# 实时控制
control_action = mgr.realtime_control(
    current_time="2025-03-08T14:30:00",
    current_load=850,
    current_pv=320,
    current_soc=0.65
)

print(f"控制指令: {control_action.action}")
print(f"目标功率: {control_action.target_power} kW")
```

## 更新日志

### v1.0.0 (2025-03-08)
- 初始版本发布
- 支持MILP优化算法
- 实现日前/日内/实时三层优化
- 支持多种运行模式
