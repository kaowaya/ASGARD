---
name: I5.2 V2G双向优化系统
description: |
  Vehicle-to-Grid (V2G) 双向充放电优化系统，实现电动汽车与电网的智能互动。
  协调车辆出行需求与电网辅助服务，最大化车主收益的同时支持电网稳定运行。

  核心功能：
  - 车辆出行模式学习与预测
  - 双向充放电时机优化（调频/备用/削峰填谷）
  - 电池寿命衰减权衡分析
  - 车主收益最大化算法
  - 电网需求响应集成

version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Semi-Solid, Solid-State]
tier: L5
category: 能源管理
deployment: 企业SaaS
compute_requirement: Edge + Cloud
pricing: Enterprise
tags: [v2g, ev, smart-charging, frequency-regulation, vehicle-to-grid]
visibility: public
---

# I5.2 V2G双向优化系统

## 概述

V2G (Vehicle-to-Grid) 技术使电动汽车不仅作为负荷，也能作为移动储能单元向电网反向送电，参与电网辅助服务获取收益。本系统优化充放电策略，在满足车主出行需求的前提下，最大化V2G收益并最小化电池衰减。

## 商业价值

### 车主收益
- **电费套利**：峰谷价差充电，节省充电成本30-50%
- **辅助服务收益**：参与电网调频调峰，年收益2000-5000元
- **补贴激励**：参与V2G项目获得政府/电网补贴
- **碳积分**：新能源车V2G获得碳减排收益

### 电网价值
- **调频资源**：秒级响应，提供优质调频服务
- **备用容量**：增加电网备用容量，提升可靠性
- **削峰填谷**：缓解高峰负荷，延缓电网投资
- **新能源消纳**：消纳过剩风光电，提高可再生能源利用率

### 社会价值
- **降低碳排放**：促进可再生能源消纳
- **电网灵活性**：提供分布式灵活调节资源
- **能源转型**：加速交通电动化与电网清洁化协同

## When to use this skill

### 1. 调频服务（Frequency Regulation）

**AGC调频**
- 响应时间：< 1秒
- 调节精度：±2%
- 收益模式：容量+电量补偿

**技术特点**：
```python
# V2G调频控制
if grid_frequency > 50.1:
    # 电网频率偏高，增加充电
    P_charge += ΔP_regulation
elif grid_frequency < 49.9:
    # 电网频率偏低，放电支持
    P_discharge += ΔP_regulation
```

### 2. 峰谷套利（Peak Shaving）

**场景**：
- 谷电时段（0:00-6:00）：充电
- 峰电时段（8:00-12:00, 18:00-21:00）：放电

**收益计算**：
```
Daily_Profit = Σ(P_discharge × Price_peak - P_charge × Price_valley)
```

### 3. 备用容量（Reserve Capacity）

**旋转备用**：
- 10分钟响应能力
- 容量补偿为主
- 实际调用概率<5%

### 4. 需量响应（Demand Response）

**削峰需求响应**：
- 电网高峰时段减少充电或反向送电
- 获得需求响应补贴
- 通常夏季午后

## 算法原理

### 1. 车辆出行预测

#### 出行时间预测
```python
from statsmodels.tsa.arima.model import ARIMA

# 预测下次出发时间
departure_model = ARIMA(history_departure_times, order=(2,1,2))
predicted_departure = departure_model.forecast(steps=1)
```

#### 行程能耗预测
```python
def estimate_trip_energy(distance, temperature, driving_style):
    """
    估算行程能耗

    Args:
        distance: 行驶距离 (km)
        temperature: 环境温度 (°C)
        driving_style: 驾驶风格 (0-1, 1=激进)

    Returns:
        能耗 (kWh)
    """
    base_consumption = 0.15  # kWh/km
    temp_factor = 1 + 0.005 * (20 - temperature)**2  # 温度影响
    style_factor = 1 + 0.3 * driving_style

    return distance * base_consumption * temp_factor * style_factor
```

### 2. V2G优化模型

#### 目标函数
```
maximize: Σ(Revenue_regulation + Revenue_arbitrage - Battery_degradation_cost)
```

#### 约束条件
```python
# 1. SOC约束
SOC_min_trip ≤ SOC[t] ≤ SOC_max

# 2. 功率约束
P_charge_min ≤ P_charge[t] ≤ P_charge_max
P_discharge_min ≤ P_discharge[t] ≤ P_discharge_max

# 3. 出行保障
SOC[departure_time] × Capacity ≥ Trip_energy + Safety_margin

# 4. V2G互斥
Σ(P_charge + P_discharge + P_v2g) ≤ P_max

# 5. 电池寿命
Daily_cycles ≤ Max_allowed_cycles
```

### 3. 电池衰减模型

#### 循环寿命
```python
def calculate_degradation(cycle_depth, cycle_count, temperature):
    """
    电池寿命衰减计算

    基于Arrhenius方程和雨流计数法
    """
    # 参考循环寿命 (80% DOD, 25°C)
    ref_cycle_life = 3000  # NCM电池

    # DOD影响
    dod_factor = (cycle_depth / 0.8) ** 1.5

    # 温度影响
    temp_factor = np.exp(-Ea/R * (1/temperature - 1/298))

    # 实际循环寿命
    actual_cycle_life = ref_cycle_life / (dod_factor * temp_factor)

    # 容量损失
    capacity_loss = (cycle_count / actual_cycle_life) * 0.2  # 20%衰减

    return capacity_loss
```

#### 成本计算
```python
battery_cost = 800  # 元/kWh (NCM)
degradation_cost_per_kwh = battery_cost / cycle_life / 2  # 考虑DOD

total_cost = (throughput * degradation_cost_per_kwh +
              fixed_cost +
              opportunity_cost)
```

### 4. 实时优化算法

#### 模型预测控制（MPC）
```python
class V2G_MPC:
    def __init__(self, horizon=24):
        self.horizon = horizon

    def optimize(self, current_state, predictions):
        """
        滚动优化
        """
        for t in range(self.horizon):
            # 预测未来状态
            state_future = predict_state(current_state, predictions[t:t+window])

            # 求解局部优化
            control = solve_local_optimization(state_future)

            # 应用第一步控制
            apply_control(control[0])

            # 更新状态
            current_state = update_state(current_state, control[0])

        return control_sequence
```

## 参数配置

### 车辆参数
```yaml
vehicle_config:
  battery_capacity_kwh: 60        # 电池容量
  max_charge_power_kw: 120        # 最大充电功率
  max_discharge_power_kw: 60      # 最大放电功率 (V2G)
  max_v2g_power_kw: 40            # V2G最大功率
  soc_min: 0.1                    # SOC下限
  soc_max: 0.9                    # SOC上限
  charge_efficiency: 0.95         # 充电效率
  discharge_efficiency: 0.95      # 放电效率
  battery_type: "NCM"             # 电池类型
  cycle_life_80dod: 3000          # 循环寿命 (80%DOD)
  battery_cost_yuan_kwh: 800      # 电池成本
```

### 出行模式
```yaml
mobility_pattern:
  work_start_time: "08:00"
  work_end_time: "18:00"
  home_charging_hours: [0, 1, 2, 3, 4, 5, 6, 22, 23]
  average_daily_distance_km: 50
  trip_uncertainty: 0.2           # 行程不确定性
  minimum_trip_soc: 0.3           # 出行最低SOC
```

### V2G服务配置
```yaml
v2g_services:
  frequency_regulation:
    enabled: true
    response_time_ms: 500
    payment_mode: "performance"    # capacity/energy/mileage
    capacity_price_yuan_kw_month: 60
    energy_price_yuan_kwh: 0.4

  peak_shaving:
    enabled: true
    peak_hours: [10, 11, 12, 13, 14, 15, 16, 17]
    valley_hours: [0, 1, 2, 3, 4, 5, 6]
    price_peak_yuan_kwh: 1.2
    price_valley_yuan_kwh: 0.4

  reserve_capacity:
    enabled: true
    response_time_min: 10
    availability: 0.95
    capacity_price_yuan_kw_year: 300
```

### 优化参数
```yaml
optimization_config:
  time_step_minutes: 15
  optimization_horizon_hours: 48
  update_interval_minutes: 30

  weights:
    revenue: 1.0                   # 收益权重
    battery_health: 0.6            # 电池健康权重
    user_convenience: 0.8          # 便利性权重

  constraints:
    max_daily_v2g_cycles: 3        # 每日最大V2G循环次数
    max_daily_throughput_kwh: 40   # 每日最大吞吐量
    minimum_reserve_soc: 0.2       # 最低备用SOC
```

## API接口

### 1. V2G注册
```http
POST /api/v1/v2g/register
Content-Type: application/json

{
  "vehicle_id": "EV_20250308_001",
  "battery_capacity_kwh": 60,
  "max_charge_power_kw": 120,
  "max_v2g_power_kw": 40,
  "home_charging_location": {
    "latitude": 31.2304,
    "longitude": 121.4737
  },
  "mobility_pattern": {
    "work_start_hour": 8,
    "work_end_hour": 18,
    "average_daily_km": 50
  }
}
```

### 2. 优化请求
```http
POST /api/v1/v2g/optimize
Content-Type: application/json

{
  "vehicle_id": "EV_20250308_001",
  "current_time": "2025-03-08T14:30:00",
  "current_soc": 0.65,
  "next_departure_time": "2025-03-09T08:00:00",
  "estimated_trip_distance_km": 50,
  "connected": true
}
```

### 3. 实时控制指令
```http
POST /api/v1/v2g/control
Content-Type: application/json

{
  "vehicle_id": "EV_20250308_001",
  "service_type": "frequency_regulation",
  "power_setpoint_kw": 15,  # 正值充电，负值放电
  "duration_minutes": 15,
  "emergency_override": false
}
```

### 4. 收益查询
```http
GET /api/v1/v2g/revenue?vehicle_id=EV_20250308_001&period=month
Response:
{
  "vehicle_id": "EV_20250308_001",
  "period": "2025-03",
  "total_revenue_yuan": 328.50,
  "breakdown": {
    "frequency_regulation": 185.00,
    "peak_shaving": 120.00,
    "reserve_capacity": 23.50
  },
  "battery_degradation_cost": 45.20,
  "net_profit": 283.30,
  "v2g_energy_kwh": 245,
  "co2_reduction_kg": 122.5
}
```

## 性能指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| 年净收益 | 扣除电池衰减成本后的年收益 | ≥3000元 |
| 响应时间 | V2G指令到功率响应的时间 | ≤1秒 |
| 预测准确度 | 出行时间预测准确率 | ≥85% |
| 电池衰减 | 年容量衰减率 | ≤2% |
| 可用率 | 可参与V2G的时间比例 | ≥80% |
| 用户满意度 | SOC需求满足率 | ≥95% |

## 部署要求

### 车端
- OBC (On-Board Charger) 支持V2G
- 车载BMS提供SOC、SOH实时数据
- 4G/5G通信模块

### 桩端
- 双向充电桩 (支持ISO 15118标准)
- 智能电表 (计量V2G电量)
- 网关设备 (协议转换)

### 云端
- V2G优化引擎
- 车队管理平台
- 电网接口 (AGC系统)
- 结算系统

## 使用示例

```python
from asgard.bas.l5.v2g import V2GOptimizer

# 初始化V2G优化器
optimizer = V2GOptimizer(config_path="config/v2g.yaml")

# 车辆注册
vehicle = optimizer.register_vehicle(
    vehicle_id="EV_001",
    battery_capacity=60,
    max_charge_power=120,
    max_v2g_power=40,
    mobility_pattern={
        "work_start_hour": 8,
        "work_end_hour": 18,
        "average_daily_km": 50
    }
)

# 运行优化
schedule = optimizer.optimize(
    vehicle_id="EV_001",
    current_time="2025-03-08T14:30:00",
    current_soc=0.65,
    next_departure="2025-03-09T08:00:00",
    trip_distance=50
)

# 查看优化结果
print(f"预计收益: {schedule.revenue:.2f} 元")
print(f"电池衰减成本: {schedule.degradation_cost:.2f} 元")
print(f"净收益: {schedule.net_profit:.2f} 元")
print(f"V2G电量: {schedule.v2g_energy:.1f} kWh")

# 实时控制
control = optimizer.realtime_control(
    vehicle_id="EV_001",
    service_type="frequency_regulation",
    grid_frequency=49.85,
    current_soc=0.65
)

print(f"控制指令: {control.action}")
print(f"目标功率: {control.power} kW")
```

## 更新日志

### v1.0.0 (2025-03-08)
- 初始版本发布
- 支持调频、峰谷套利、备用容量三种服务
- 实现电池寿命衰减模型
- 支持出行模式学习
