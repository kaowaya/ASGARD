# 家庭储能优化算法理论

## 1. 算法概述

家庭储能优化是一个多目标能量管理问题，目标是：
- **经济性**：最小化电费支出
- **自给率**：最大化能源自给自足
- **可靠性**：保障关键负载供电
- **舒适性**：满足用户用电需求

## 2. 系统架构

### 2.1 能量流模型

```
                光伏发电
                   |
                   v
            +-------------+
            |   逆变器    |
            +-------------+
                   |
          +--------+--------+
          |        |        |
          v        v        v
       负载     电池     电网
```

### 2.2 功率平衡方程

```
P_solar(t) + P_battery(t) + P_grid(t) = P_load(t)

其中：
P_solar(t): 光伏发电功率
P_battery(t): 电池功率（+放电，-充电）
P_grid(t): 电网功率（+购电，-上网）
P_load(t): 负载功率
```

## 3. 数学模型

### 3.1 目标函数

#### 经济最优模式

```
min J = Σ(C_grid[t] - C_feed_in[t])

其中：
C_grid[t] = P_buy[t] × price_buy[t]
C_feed_in[t] = P_sell[t] × price_sell[t]
```

#### 自给自足模式

```
max J_self = Σ(P_solar_to_load + P_battery_to_load) / ΣP_load

受约束于：
P_solar_to_load ≤ P_solar
P_battery_to_load ≤ P_battery_max
```

#### 多目标优化

```
min J = w1·J_cost + w2·(1 - J_self) + w3·J_degrad

其中：
w1, w2, w3: 权重系数
J_degrad: 电池老化惩罚
```

### 3.2 约束条件

#### 电池约束

```
SOC_min ≤ SOC[t] ≤ SOC_max
-P_charge_max ≤ P_battery[t] ≤ P_discharge_max
SOC[t+1] = SOC[t] + (η·P_battery[t]·Δt) / C_batt
```

#### 功率平衡约束

```
P_solar[t] + P_battery[t] + P_grid[t] = P_load[t]
|P_grid[t]| ≤ P_grid_max
```

#### 负载约束

```
P_load[t] = Σ(P_load_i[t])
P_load_i[t] ∈ [0, P_load_i_rated] for controllable loads
P_load_i[t] = P_load_i_forecast[t] for uncontrollable loads
```

## 4. 光伏发电预测

### 4.1 简化模型

基于太阳位置的简化模型：

```
P_solar(t) = P_rated × η × sin(α(t)) × (1 - degradation)^years

其中：
α(t): 太阳高度角
η: 系统效率
degradation: 年衰减率（0.5%）
```

### 4.2 机器学习模型

使用LSTM进行光伏预测：

```python
model = Sequential([
    LSTM(64, input_shape=(lookback, features)),
    Dropout(0.2),
    LSTM(32),
    Dropout(0.2),
    Dense(1)
])

features = [
    'hour', 'day_of_year',
    'temperature', 'irradiance',
    'cloud_cover', 'wind_speed'
]
```

### 4.3 天气修正系数

| 天气状况 | 修正系数 |
|----------|----------|
| 晴天 | 0.95-1.05 |
| 多云 | 0.4-0.8 |
| 阴天 | 0.1-0.3 |
| 雨天 | 0.05-0.15 |

## 5. 负荷预测

### 5.1 典型负荷曲线

家庭日负荷曲线通常呈现双峰特性：

```
P_load(t) = P_base + P_morning(t) + P_evening(t)

其中：
P_base: 基础负荷（冰箱、待机设备）
P_morning(t): 晨峰（6-9点）
P_evening(t): 晚峰（18-22点）
```

### 5.2 负载分类

按可控性分类：
1. **不可控负载**：照明、冰箱、医疗设备
2. **半可控负载**：空调、热水器（可延时）
3. **完全可控负载**：电动车、洗碗机、洗衣机

按优先级分类：
1. **关键负载**：医疗设备、安全系统
2. **高优先级**：照明、冰箱
3. **中优先级**：空调、电脑
4. **低优先级**：娱乐设备
5. **灵活负载**：电动车、泳池泵

## 6. 优化算法

### 6.1 贪心算法

简单快速的启发式算法：

```python
for t in range(T):
    # 1. 光伏优先满足负载
    if P_solar[t] >= P_load[t]:
        P_solar_to_load[t] = P_load[t]
        remaining_solar = P_solar[t] - P_load[t]

        # 2. 剩余光伏充电
        if SOC[t] < SOC_max:
            P_to_battery = min(remaining_solar, P_charge_max)
            P_solar_to_battery[t] = P_to_battery
    else:
        P_solar_to_load[t] = P_solar[t]
        remaining_load = P_load[t] - P_solar[t]

        # 3. 缺口从电池或电网补充
        if price[t] > price_threshold and SOC[t] > SOC_min:
            P_battery_to_load[t] = min(remaining_load, P_discharge_max)
        else:
            P_grid_to_load[t] = remaining_load
```

### 6.2 动态规划

适用于确定性问题：

```python
# 状态定义
state[t][soc] = minimum_cost_up_to_t_with_soc

# 状态转移
for t in range(T):
    for soc in SOC_range:
        for action in [charge, discharge, idle]:
            next_soc = update_soc(soc, action)
            cost = calculate_cost(action, price[t])
            state[t+1][next_soc] = min(
                state[t+1][next_soc],
                state[t][soc] + cost
            )
```

### 6.3 模型预测控制（MPC）

适用于不确定性环境：

1. **预测**：预测N小时的光伏和负荷
2. **优化**：在预测窗口内优化控制策略
3. **执行**：执行第一个控制动作
4. **滚动**：在每个时间步重复

```python
def mpc_control(current_state, horizon):
    predictions = predict_pv_load(horizon)

    # 求解优化问题
    control_sequence = solve_optimization(
        current_state,
        predictions
    )

    # 只执行第一个动作
    return control_sequence[0]
```

## 7. 备用电源模式

### 7.1 备用SOC计算

```
SOC_reserve = max(
    (P_critical × T_backup) / C_batt,
    SOC_min_reserve
)

其中：
P_critical: 关键负载功率
T_backup: 备用时长（4-8小时）
SOC_min_reserve: 最小备用SOC（20-30%）
```

### 7.2 负载分级策略

断电时按优先级供电：

| 优先级 | 负载类型 | 供电保障 |
|--------|----------|----------|
| 1 | 医疗设备 | 100% |
| 2 | 安防系统 | 100% |
| 3 | 照明 | 100% |
| 4 | 通信设备 | 100% |
| 5 | 冰箱 | 100% |
| 6 | 空调 | 50% |
| 7 | 其他 | 0% |

## 8. 需求响应

### 8.1 削峰（Peak Shaving）

```
if P_total > P_peak_threshold:
    reduce_load(P_total - P_peak_threshold)
    discharge_battery()
```

### 8.2 填谷（Valley Filling）

```
if P_total < P_valley_threshold:
    charge_battery()
    shift_load_to_valley()
```

### 8.3 频率调节

```
if frequency < 49.5 Hz:  # 低频
    reduce_load()  # 减少用电
    discharge_to_grid()  # 向电网放电
elif frequency > 50.5 Hz:  # 高频
    increase_load()  # 增加用电
    charge_from_grid()  # 从电网充电
```

## 9. 性能指标

### 9.1 经济指标

```
净现值（NPV）:
NPV = -C_initial + Σ(C_savings / (1+r)^t)

投资回收期（PB）:
PB = C_initial / C_savings_annual

内部收益率（IRR）:
NPV(IRR) = 0
```

### 9.2 技术指标

```
自给率（Self-Sufficiency）:
SS = (E_solar + E_battery) / E_load × 100%

光伏自用率（Self-Consumption）:
SC = (E_direct + E_battery) / E_solar × 100%

电池循环寿命:
Cycle_life = min(
    E_batt_total / E_batt_capacity,
    Calendar_life
)
```

### 9.3 可靠性指标

```
供电可靠率:
Reliability = (T_total - T_outage) / T_total × 100%

能量缺失期望:
EENS = Σ(P_unserved × t_unserved)
```

## 10. 参数优化

### 10.1 电池容量优化

权衡投资成本与收益：

```
min C_total = C_batt(C_batt) + C_grid(C_batt)

其中：
C_batt: 电池投资成本
C_grid: 电网用电成本
```

经验法则：
- 无光伏：5-10 kWh
- 3-5 kWp光伏：10-13 kWh
- >5 kWp光伏：13-20 kWh

### 10.2 光伏容量优化

```
max C_savings = E_solar × price_grid - C_solar_initial

受约束于：
E_solar ≤ E_load × 1.5  # 避免
```

### 10.3 SOC设定点优化

| 场景 | SOC下限 | SOC上限 | 原因 |
|------|---------|---------|------|
| 日常运行 | 20% | 90% | 延长寿命 |
| 备用模式 | 30% | 100% | 保证备用 |
| 需求响应 | 10% | 95% | 最大化灵活性 |

## 11. 算法复杂度

| 算法 | 时间复杂度 | 空间复杂度 | 适用场景 |
|------|------------|------------|----------|
| 贪心 | O(n) | O(1) | 实时控制 |
| 动态规划 | O(n×SOC_states²) | O(n×SOC_states) | 离线优化 |
| MPC | O(n³) | O(n²) | 滚动优化 |
| 线性规划 | O(n³) | O(n²) | 大规模问题 |
