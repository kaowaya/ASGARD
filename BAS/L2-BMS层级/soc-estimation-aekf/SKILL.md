---
name: B2.4-SOC估计-AEKF
description: >
  基于自适应扩展卡尔曼滤波(AEKF)的SOC在线估计算法。
  通过Sage-Husa估计器实时修正噪声协方差矩阵，抵抗电池老化与工况剧烈变化带来的模型失配风险。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion]
tier: L2
compute_requirement: <50MHz
pricing: Premium
tags:
  - soc-estimation
  - adaptive-kalman-filter
  - aekf
  - bms
visibility: public
---

# B2.4 SOC估计 - 自适应扩展卡尔曼滤波 (AEKF)

## When to use this skill

Use this skill when:
- 电池面临**剧烈波动的工况**（如赛道、频繁急加速/急减速）。
- 电池已经进入**生命周期中后期**（SOH < 90%），固化的模型参数无法表征真实内阻和电容。
- BMS 算力相对充足（例如带有 FPU 浮点运算单元的 32-bit MCU，主频 > 50MHz）。
- 要求极高的 SOC 估计精度界限 (±1.5%)。

**替代方案**:
- 若车机算力极其受限，或仅仅用于小型低速车，请降级使用参数固定的 `B2.3-SOC估计-EKF`。

## Quick Start
1. **准备输入数据**: CSV文件，包含 `current, voltage, temperature` 列。
2. **选择电池基础参数**:
   - `reference/battery_mapping/lfp_default.yaml`
3. **运行估计**:
   ```bash
   python templates/python/core.py \
       --input data_samples/input/dynamic_drive.csv \
       --output output/soc_result.csv \
       --battery lfp_default
   ```

## Decision Points

| 场景特征 | 条件 | 推荐动作 | 替代方案 |
|---------|------|---------|---------|
| 算法发散边缘 | `trace(P) > 100` 或新息持续巨大 | 触发滤波重置，临时退化为安时积分 | 使用UKF作为更强非线性滤波器 |
| 工况急剧突变 | `|dI/dt| > 200A/s`| 临时减小 Sage-Husa 的遗忘因子 `b`，加速噪声矩阵收敛 | 扩大容差窗口 |
| 低温大极化 | `temperature < -10°C`  | 采用低温专用初始 R 矩阵，防止误收敛 | 冻结自适应更新 |

## How it works

### 核心原理
与基础版 EKF (`B2.3`) 使用完全一样的状态空间模型（2RC等效电路）。其核心差异在于加入了 **Sage-Husa 噪声统计自适应估计器**。

在标准 EKF 中，过程噪声协方差矩阵 $Q$ （代表模型误差）和观测噪声协方差矩阵 $R$ （代表测量误差）是固定的常数。但是电池在老化后内阻增加，原本的 $Q$ 不再适用，导致滤波变差。

**Sage-Husa 递推公式**利用滤波器每一步产生的新息（实际电压测量值与模型预测电压的差值 $\epsilon_k = V_{meas} - V_{pred}$）来实时反推和修正 $Q$ 和 $R$：

$$
d_k = \frac{1 - b}{1 - b^{k+1}}
$$
$$
R_k = (1 - d_k) \cdot R_{k-1} + d_k \cdot (\epsilon_k \cdot \epsilon_k^T)
$$
$$
Q_k = (1 - d_k) \cdot Q_{k-1} + d_k \cdot (K_k \cdot \epsilon_k \cdot \epsilon_k^T \cdot K_k^T)
$$

其中 $b$ 为遗忘因子（通常取 `0.95 ~ 0.99`），用来控制系统“遗忘历史数据”的速度。这就赋予了算法自适应抵抗未知扰动的能力。

### 工业级工程鲁棒性设计
1. **协方差矩阵防呆**: 必须强制保证 $P$, $Q$, $R$ 矩阵在每步更新后**对称且正定**。工程中会注入一个包含极小值的对角矩阵 `eps * I` 防止数值降维崩溃。
2. **更新上限钳位 (Saturation)**: Sage-Husa 容易受到单次巨大尖峰干扰而发散。必须对估算出的 $Q, R$ 设定上下界 `[Q_min, Q_max]` 和 `[R_min, R_max]`，超出即被截断。

## Inputs & Outputs

### Inputs

| 参数 | 格式 | 要求 | 示例 |
|-----|------|------|------|
| 时间戳 | CSV列 | 秒 | `0, 0.1, 0.2, ...` |
| 电流I | CSV列 | 单位A，充电为负，放电为正 | `120, -50, -30, ...` |
| 电压V | CSV列 | 单位V | `3.2, 3.32, 3.31, ...` |
| 温度T | CSV列 | 单位°C | `25, 25, 25, ...` |

### Outputs

| 输出 | 格式 | 说明 |
|-----|------|------|
| SOC | CSV列 | (0~1)的连续平滑曲线 |
| V_est | CSV列 | 模型预测的电压，可用于上位机诊断 |
| R_obs | CSV列 | 实时自适应得到的观测噪声R的对角值，监控传感质量 |

## Parameters
| 参数 | 默认值 | 范围 | 说明 |
|-----|--------|------|------|
| Forget_Factor (b)| 0.97 | 0.90 - 0.999 | 影响自适应速度。越小适应越快但在稳态时震荡变大。 |

## Quality Checklist
- [ ] 确保即使在剧烈测试工况下 $Q$ 和 $R$ 矩阵也不会出现负数或负对角元素。
- [ ] 保证算法的堆栈开销（由于增加了一系列矩阵乘法）不会在目标 MCU 上导致栈溢出。

## Extended References
- **代码实现**: [templates/python/core.py](templates/python/core.py)
- **底层C++头文件**: [templates/cpp/soc_aekf_core.h](templates/cpp/soc_aekf_core.h)
