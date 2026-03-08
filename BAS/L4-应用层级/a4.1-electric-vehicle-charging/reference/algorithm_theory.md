# 电动汽车充电优化算法理论

## 1. 算法概述

电动汽车充电优化是一个多目标优化问题，需要同时考虑：
- **经济性**：最小化充电成本
- **时效性**：满足用户的时间需求
- **电池健康**：最小化电池老化
- **电网友好**：平滑充电负荷曲线

## 2. 数学模型

### 2.1 目标函数

综合优化目标函数：

```
min J = w1·J_cost + w2·J_time + w3·J_degrad + w4·J_grid

其中：
J_cost = Σ(P[i]·price[i]·Δt)              充电成本
J_time = Σ(max(0, T_target - t[i]))       时间惩罚
J_degrad = ΣDeg(SOC[i], T[i], I[i])       电池老化
J_grid = Σ(P[i] - P_avg)²                 负荷波动
```

权重系数根据用户优先级动态调整：
- 成本优先：w1=0.5, w2=0.2, w3=0.2, w4=0.1
- 速度优先：w1=0.2, w2=0.5, w3=0.2, w4=0.1
- 健康优先：w1=0.2, w2=0.2, w3=0.5, w4=0.1

### 2.2 约束条件

#### 电池约束
```
SOC_min ≤ SOC[i] ≤ SOC_max          (通常: 10% ≤ SOC ≤ 90%)
I_min ≤ I[i] ≤ I_max                (通常: -3C ≤ I ≤ 3C)
V_min ≤ V[i] ≤ V_max                (通常: 2.5V ≤ V_cell ≤ 4.3V)
T_min ≤ T[i] ≤ T_max                (通常: 0°C ≤ T ≤ 45°C)
```

#### 功率约束
```
0 ≤ P_charge[i] ≤ min(P_rated, P_grid, P_user)
P_v2g ≤ P_v2g_max
```

#### 用户约束
```
SOC[t_end] ≥ SOC_target
t_end ≤ T_deadline
```

## 3. 充电策略

### 3.1 CC-CV充电策略

恒流-恒压（Constant Current-Constant Voltage）充电：

```python
# 阶段1：恒流充电 (CC)
if V_cell < V_cv:
    I_charge = I_constant
else:
    # 阶段2：恒压充电 (CV)
    I_charge = I_constant * exp(-(V_cell - V_cv) / τ)
```

典型参数：
- V_cv = 4.2V (NCM) / 3.65V (LFP)
- I_constant = 0.5C ~ 1.5C
- τ = 5 ~ 10分钟

### 3.2 多阶段充电优化

五阶段充电策略：

1. **预充电阶段** (SOC < 20%)
   - 小电流预充（0.05C）
   - 激活活性物质

2. **快速充电阶段** (20% < SOC < 50%)
   - 最大电流充电（1.5C）
   - 最短时间充入50%电量

3. **连续充电阶段** (50% < SOC < 80%)
   - 中等电流充电（0.8C）
   - 平衡速度与发热

4. **涓流充电阶段** (80% < SOC < 95%)
   - 小电流充电（0.3C）
   - 减少极化

5. **浮充阶段** (SOC > 95%)
   - 恒压浮充
   - 补偿自放电

## 4. 电池健康模型

### 4.1 容量衰减模型

总容量损失 = 循环老化 + 日历老化

```
Q_loss = Q_cycle + Q_calendar

Q_cycle = α·(DOD)^β·exp(-Ea/RT)·Ah_throughput
Q_calendar = γ·exp(-Ea_c/RT)·t^δ
```

参数（NCM电池为例）：
- α = 3.73×10⁻⁵
- β = 0.75
- γ = 7.43×10⁻⁵
- δ = 0.5
- Ea = 39.8 kJ/mol
- Ea_c = 45.3 kJ/mol

### 4.2 SOH估算

State of Health (SOH) 定义：

```
SOH = (Q_current / Q_rated) × 100%

式中：
Q_current: 当前实际容量
Q_rated: 额定容量
```

SOH影响因素：
1. **循环次数**：每500次循环衰减约5-10%
2. **温度**：每升高10°C，老化速率翻倍
3. **SOC范围**：深充深放加速老化
4. **充电倍率**：大电流充电加速老化

### 4.3 内阻增长模型

内阻增长与SOH的关系：

```
R = R_0 · (SOH_0 / SOH)^k

式中：
R_0: 初始内阻
SOH_0: 初始SOH
k: 经验系数，通常为1.5~2.0
```

## 5. V2G优化策略

### 5.1 V2G收益模型

```
max Π = Σ(P_v2g[i]·price_sell[i] - P_charge[i]·price_buy[i])

s.t.:
  SOC_min_v2g ≤ SOC[i] ≤ SOC_max_v2g
  |P_v2g[i]| ≤ P_v2g_max
  ΣP_v2g[i] = 0  (能量平衡)
  Cycle_daily ≤ Cycle_limit
```

### 5.2 辅助服务类型

1. **频率调节** (Frequency Regulation)
   - AGC (Automatic Generation Control)
   - 响应时间：秒级
   - 收益：$10-30/MW

2. **旋转备用** (Spinning Reserve)
   - 10分钟响应
   - 收益：$5-15/MW

3. **峰谷套利** (Arbitrage)
   - 低买高卖
   - 收益：价差 × 效率

4. **电压支持** (Voltage Support)
   - 无功功率调节
   - 收益：容量费用

## 6. 算法实现

### 6.1 动态规划算法

状态定义：
```
State[i] = SOC at time i
```

状态转移方程：
```
SOC[i+1] = SOC[i] + (η·P[i]·Δt) / C_batt
```

价值函数：
```
V[i, SOC] = min(P[i]) { cost[i] + V[i+1, SOC'] }
```

### 6.2 贪心算法（近似解）

按电价从低到高排序，优先在低价时段充电：

```python
sorted_hours = sort_by_price(price_schedule)
energy_needed = calculate_energy_needed()

for hour in sorted_hours:
    if energy_needed <= 0:
        break
    charge_amount = min(max_power, energy_needed)
    schedule[hour] = charge_amount
    energy_needed -= charge_amount
```

### 6.3 模型预测控制 (MPC)

1. 预测未来N小时的电价
2. 在预测窗口内优化充电策略
3. 执行第一步控制
4. 滚动优化

## 7. 参数调优

### 7.1 电池类型参数

| 参数 | LFP | NCM | Na-ion |
|------|-----|-----|--------|
| 充电倍率 | 1-2C | 1-3C | 1-2C |
| 温度范围 | -20~60°C | -20~55°C | -20~55°C |
| 循环寿命 | 2000-5000 | 1000-2000 | 1500-3000 |
| 衰减率 | 0.015%/cycle | 0.03%/cycle | 0.02%/cycle |

### 7.2 优化权重建议

根据场景调整权重：

| 场景 | w1(成本) | w2(时间) | w3(健康) | w4(电网) |
|------|----------|----------|----------|----------|
| 家用充电 | 0.6 | 0.1 | 0.2 | 0.1 |
| 快充站 | 0.2 | 0.5 | 0.2 | 0.1 |
| V2G | 0.3 | 0.2 | 0.3 | 0.2 |
| 微电网 | 0.3 | 0.1 | 0.2 | 0.4 |

### 7.3 安全参数

| 参数 | 建议值 | 原因 |
|------|--------|------|
| 充电截止电压 | 4.1V | 防止析锂 |
| 放电截止电压 | 2.8V | 保护正极 |
| 充电温度上限 | 45°C | 防止热失控 |
| 充电温度下限 | 0°C | 防止锂析出 |
| 充电电流上限 | 2C | 限制极化 |

## 8. 性能评估指标

1. **成本节约率**
   ```
   Saving_rate = (Cost_naive - Cost_optimized) / Cost_naive
   目标：>20%
   ```

2. **充电完成率**
   ```
   Completion_rate = Energy_delivered / Energy_requested
   目标：100%
   ```

3. **电池老化率**
   ```
   Degradation_rate = ΔSOH / Δcycles
   目标：<0.02%/cycle
   ```

4. **算法复杂度**
   ```
   Time_complexity: O(n²) for DP, O(n log n) for greedy
   Space_complexity: O(n)
   ```
