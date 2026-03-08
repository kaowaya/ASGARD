---
name: B2.3-SOC估计-EKF
description: >
  扩展卡尔曼滤波算法，用于锂离子电池SOC在线估计。
  适用场景：BMS板端实时估计、算力有限（<10MHz）、参数固定的常规工况。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion]
tier: L2
compute_requirement: <10MHz
pricing: Free
tags:
  - soc-estimation
  - kalman-filter
  - bms
visibility: public
---

# B2.3 SOC估计 - EKF

## When to use this skill

Use this skill when:
- 需要BMS板端实时SOC估计（频率≥1Hz）
- 算力资源极其有限（<10MHz，基础MCU即可运行）
- 电池处于全生命周期早期（模型参数未发生明显漂移）
- 不需要同时在线辨识模型参数

**替代方案**:
- 若算力支持（<50MHz）且电池老化明显，推荐升级使用 `B2.4-SOC估计-AEKF`。
- 若只需粗略计算，使用 `B2.1-SOC估计-安时积分`。

## Quick Start

1. **准备输入数据**: CSV文件，包含 `current, voltage, temperature` 列（推荐1Hz采样）
2. **选择电池参数**:
   - LFP: `reference/battery_mapping/lfp_default.yaml`
   - NCM: `reference/battery_mapping/ncm_default.yaml`
3. **运行估计**:
   ```bash
   python templates/python/core.py \
       --input data_samples/input/standard_cycle.csv \
       --output output/soc_result.csv \
       --battery lfp_default
   ```
4. **查看结果**:
   - `output/soc_result.csv`: SOC时序数据
   - 控制台输出: 最终SOC、均方根误差(RMSE)

## Decision Points

| 场景特征 | 条件 | 推荐动作 | 替代方案 |
|---------|------|---------|---------|
| 电池老化严重 | `SOH < 85%` | 升级使用B2.4 SOC估计-AEKF | 定期离线校准本EKF参数表 |
| 极端低温工况 | `temperature < -10°C` | 调整低温参数表 | 降低滤波信任度（增大R） |
| MCU算力极低 | `compute_resource < 1MHz` | 使用B2.1 安时积分法 | 降低EKF运行频率至0.1Hz |

## How it works

### 核心原理
基于双极化（DP）等效电路模型，使用扩展卡尔曼滤波（EKF）融合安时积分（过程模型）与OCV测量（观测模型）。

**状态方程**:
$$
x_{k+1} = A x_k + B u_k + w_k
$$
其中状态变量 $x = [SOC, U_{p1}, U_{p2}]^T$，$u_k$ 为电流 $I_k$。

**观测方程**:
$$
y_k = OCV(SOC_k) - U_{p1,k} - U_{p2,k} - I_k R_0 + v_k
$$

与AEKF的区别在于：**模型参数（R0, R1, C1, R2, C2）在此算法中为查表所得的常数**，不随状态实时更新。

### 算法流程
1. 初始化状态 $x_0$ 和协方差 $P_0$
2. **时间更新**：计算先验状态估计和先验误差协方差
3. **测量更新**：计算卡尔曼增益 $K_k$
4. **状态更新**：根据实际电压测量更新SOC估计值
5. **协方差更新**：更新误差协方差矩阵供下一步使用

## Inputs & Outputs

### Inputs

| 参数 | 格式 | 要求 | 示例 |
|-----|------|------|------|
| 电流I | CSV列 | 单位A，充电为负/正（需统一符号约定） | `-50, -50, -50, ...` |
| 电压V | CSV列 | 单位V | `3.2, 3.25, 3.31, ...` |
| 温度T | CSV列 | 单位°C | `25, 25, 25, ...` |
| 采样间隔 | 数字 | 秒，推荐1 | `dt=1.0` |

### Outputs

| 输出 | 格式 | 说明 |
|-----|------|------|
| SOC | CSV列 | 0-1范围（如0.75表示75%） |
| V_est | CSV列 | EKF预测的端电压，用于对比实际电压判断收敛 |

## Parameters

| 参数 | 默认值 | 范围 | 说明 |
|-----|--------|------|------|
| Qn | 100Ah | 5-500Ah | 额定容量 |
| Q_matrix | 对角阵 | - | 状态过程噪声协方差矩阵（调优关键点） |
| R_scalar | 1e-2 | 1e-4 - 1 | 观测（电压测量）噪声协方差 |

## Quality Checklist

- [ ] 确保电流方向符号与代码实现（安时积分部分）一致。
- [ ] OCV-SOC 插值表的精度直接决定 EKF 的上限。
- [ ] 检查滤波启动前期的收敛情况，若震荡过大需减小 Q 中对应 SOC 的噪声项。

## Extended References

- **代码实现**: [templates/python/core.py](templates/python/core.py)
- **底层算法参考**: [D:\ASGARD\算法参考\SOC-EKF_C_V3] 和 [SOC-EKF_C_V4] (历史实现代码)
