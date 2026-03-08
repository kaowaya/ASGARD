---
name: A4.2-家庭储能优化
description: |
  智能家庭能源管理系统，集成光伏发电、储能电池和电网交互的优化调度。

  该Skill通过预测家庭负荷和光伏发电，优化储能充放电策略，实现：
  - 最大化自发自用比例（Self-consumption）
  - 最小化电费支出
  - 参与电网需求响应获得收益
  - 备用电源保障（UPS功能）

  支持与智能家居系统联动，可控制空调、电动车充电桩等负载，
  实现全屋能源最优管理。

version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion]
tier: L4
category: 储能管理
deployment: 移动APP/Web/Edge Gateway
compute_requirement: <50MHz
pricing: Pro
tags: [home-energy, solar-optimization, load-shifting, demand-response]
visibility: public
---

## 功能概述

家庭储能优化系统帮助用户实现能源自给自足，降低电费支出，提高能源利用效率。

### 核心特性

1. **光伏发电优化**
   - 发电量预测（基于天气和历史数据）
   - MPPT最大功率点跟踪
   - 光伏优先自用策略

2. **负荷智能管理**
   - 负荷预测与分类（可控/不可控）
   - 负载优先级调度
   - 需求响应（Demand Response）

3. **储能智能调度**
   - 峰谷电价套利
   - 光伏消纳优化
   - 备用电源模式
   - 电池健康保护

4. **多能源协同**
   - 光伏 + 储能 + 电网 + 电动车
   - 能量流向优化
   - 实时功率平衡

5. **应急备用**
   - 断电自动切换（UPS功能）
   - 备用模式SOC管理
   - 关键负载保障

## 算法原理

### 1. 能量管理优化

目标函数：

```
min C_total = Σ(C_grid_buy - C_grid_sell + C_degradation)

其中：
C_grid_buy = Σ(P_grid[i] × price_buy[i])
C_grid_sell = Σ(P_sell[i] × price_sell[i])
C_degradation = battery_degradation_cost()
```

### 2. 光伏消纳策略

自发自用优先级：

1. 满足即时负载需求
2. 给储能充电
3. 多余电力上网

```
if P_solar > P_load:
    P_to_battery = min(P_solar - P_load, P_charge_max)
    P_to_grid = P_solar - P_load - P_to_battery
else:
    P_from_battery = min(P_load - P_solar, P_discharge_max)
    P_from_grid = P_load - P_solar - P_from_battery
```

### 3. 负荷调度优化

可控负载调度模型：

```
max Σ(U_load[i] × priority[i])
subject to:
  Σ(P_scheduled[i]) ≤ P_available
  t_start[i] ≤ t_schedule[i] ≤ t_end[i]
```

### 4. 备用电源模式

备用SOC计算：

```
SOC_reserve = max(
    P_critical × T_backup / C_batt,
    SOC_min_reserve
)

其中：
P_critical: 关键负载功率
T_backup: 备用时长（通常4-8小时）
SOC_min_reserve: 最小备用SOC（通常20-30%）
```

## 参数说明

### 系统配置参数

| 参数名 | 类型 | 范围 | 说明 |
|--------|------|------|------|
| solar_capacity | float | 3-20 kWp | 光伏装机容量 |
| battery_capacity | float | 5-20 kWh | 电池容量 |
| battery_soc | float | 0-100% | 当前SOC |
| pv_generation | array | - | 光伏发电预测 (kW) |
| load_forecast | array | - | 负荷预测 (kW) |
| price_schedule | array | - | 电价计划 (¢/kWh) |
| backup_mode | bool | - | 是否启用备用模式 |
| backup_hours | float | 2-8 hours | 备用时长 |
| export_limit | float | 0-10 kW | 上网功率限制 |

### 负载配置参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| load_name | string | 负载名称 |
| power_rating | float | 额定功率 (kW) |
| energy_demand | float | 能量需求 (kWh) |
| controllable | bool | 是否可控 |
| priority | int | 优先级 (1-5) |
| time_window | tuple | 可调度时段 |

### 输出结果

| 参数名 | 类型 | 说明 |
|--------|------|------|
| energy_schedule | object | 能量调度计划 |
| battery_soc_profile | array | SOC变化曲线 |
| cost_savings | object | 费用节约详情 |
| self_sufficiency | float | 自给率 (%) |
| solar_consumption | float | 光伏自用率 (%) |
| backup_status | object | 备用状态 |

## 使用场景

### 场景1：日常经济运行
- 目标：最小化电费
- 策略：谷电充电，峰电放电，光伏优先自用
- 预期节约：30-50%

### 场景2：光伏最大化消纳
- 目标：提高自给率
- 策略：白天充满电池，晚上放电
- 自给率：>80%

### 场景3：备用电源模式
- 目标：断电保障
- 策略：保持SOC>30%，优先保障关键负载
- 备用时长：4-8小时

### 场景4：需求响应
- 目标：电网辅助服务收益
- 策略：削峰填谷，频率调节
- 年收益：$200-500

## 限制与约束

### 电池安全约束
- SOC范围：10-90%（日常），20-100%（备用）
- 充放电倍率：≤1C
- 温度范围：-10~45°C

### 电网约束
- 上网功率：≤逆变器容量
- 功率因数：>0.9
- 频率范围：49.5-50.5 Hz

### 备用模式约束
- 最小备用SOC：20-30%
- 关键负载优先级：最高
- 非关键负载可被切断

## 部署要求

### 硬件要求
- **边缘网关**：ARM Cortex-A53, 1GB RAM
- **云服务器**：AWS IoT Greengrass / Azure IoT Edge

### 软件依赖
```python
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
scikit-learn>=1.0.0
pvlib>=0.9.0
```

### API接口
```python
# REST API
POST /api/v1/home-energy/optimize
GET /api/v1/home-energy/status
PUT /api/v1/home-energy/control

# MQTT
home/energy/schedule
home/energy/control
home/energy/status
```

## 系统集成

### 支持的设备
- 逆变器：SolarEdge, SMA, Huawei, Growatt
- 电池：Tesla Powerwall, LG Chem, BYD
- 电表：智能电表（Modbus/RS485）
- EV充电桩：OCPP协议

### 智能家居集成
- Home Assistant
- Apple HomeKit
- Google Home
- Amazon Alexa

## 更新日志

### v1.0.0 (2025-03-08)
- 初始版本发布
- 光伏+储能优化
- 负荷预测与调度
- 备用电源功能
- 需求响应支持

## 许可证

ASGARD Pro License - See LICENSE.md for details

## 联系方式

- 文档：https://docs.asgard.ai/bas/skills/a4.2
- 支持：support@asgard.ai
- GitHub：https://github.com/ASGARD-AI/bas-skills
