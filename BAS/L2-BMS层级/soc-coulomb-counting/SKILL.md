---
name: B2.1-SOC估计-安时积分
description: >
  基于安时积分法的锂离子电池SOC在线估计。
  适用场景：BMS板端极低算力环境（<10MHz）、可作为高阶估计算法的基础降级方案。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Semi-Solid, Solid-State]
tier: L2
compute_requirement: <10MHz
pricing: Free
tags:
  - soc-estimation
  - coulomb-counting
  - bms
visibility: public
---

# B2.1 SOC估计 - 安时积分法 (Coulomb Counting)

## When to use this skill

Use this skill when:
- 算力资源受到极大限制（如低端MCU，主频 <10MHz）
- 需要极快速的执行时间和极小的内存占用
- 作为其他高阶算法（如EKF、AEKF）中的核心过程模型组件
- 需要一个最稳定、没有矩阵发散风险的"兜底"估计策略

**替代方案**:
- 若算力支持（>10MHz），强烈建议使用闭环反馈方案 `B2.3-SOC估计-EKF` 或 `B2.4-SOC估计-AEKF` 以消除电流积分引入的累积误差。

## Quick Start

1. **准备输入数据**: CSV文件，包含 `current, temperature` 列
2. **选择初值配置**: 选择额定容量与初始SOC
3. **运行估计**:
   ```bash
   python templates/python/core.py \
       --input data_samples/input/discharge_cycle.csv \
       --output output/soc_result.csv \
       --capacity 235.0 \
       --init-soc 1.0
   ```
4. **查看结果**:
   - `output/soc_result.csv`: SOC时序数据

## Decision Points

| 场景特征 | 条件 | 推荐动作 | 替代方案 |
|---------|------|---------|---------|
| 电流长时间过小 | `abs(I) < 0.05C 且超1小时` | 重置/修正积分基准点 (查OCV表) | 使用静态 OCV 查表法 |
| 极端低温工况 | `temperature < -10°C` | 将放电库伦效率 $\eta$ 降低至0.95 | - |
| 传感器零漂大 | 在断电/静置时电流仍 `>0.1A`| 触发零点校准逻辑，不参与积分 | 报警传感器故障 |

## How it works

### 核心原理
**安时积分法 (Coulomb Counting)** 或称电流积分法，是通过累加电池充放电电流随时间的变化量，推算电池目前剩余容量（SOC）的一种开环估计方法。

基本演化方程：
$$
SOC(t) = SOC(t_0) - \frac{1}{C_n \times 3600} \int_{t_0}^{t} \eta(I, T) \cdot I(\tau) d\tau
$$

其中:
- $SOC(t_0)$: 积分起点的初始SOC配置
- $C_n$: 额定容量（单位 Ah，乘以3600转化为库伦/安秒）
- $\eta(I, T)$: 库仑效率。充电时接近100%；放电时随温度降低而略微下降。
- $I(\tau)$: 瞬时电流（在此系统中，我们约定**放电为正，充电为负**。如果是相反约定，公式需将负号改为正号）

### 工程鲁棒性设计（工业级）
为了保证工业级交付，此算法实现了以下安全防御机制：
1. **边界钳位 (Clamping)**: SOC 结果严格限制在 `[0.0, 1.0]` 闭区间内。
2. **异常零点过滤 (Deadband)**: 如果检测到极小电流（低于传感器底噪，例如 <0.01A），设为 0。
3. **时间戳防呆**: 自动处理不规则的数据采集间隔（动态计算 `dt`），而非写死固定频率。

## Inputs & Outputs

### Inputs

| 参数 | 格式 | 要求 | 示例 |
|-----|------|------|------|
| 时间戳 | CSV列 | 单位秒 (必须单调递增) | `0, 1.2, 2.5, ...` |
| 电流I | CSV列 | 单位A，充电为负，放电为正 | `50, 50, -30, ...` |
| 温度T | CSV列 | 单位°C | `25, 25, 25, ...` |

### Outputs

| 输出 | 格式 | 说明 |
|-----|------|------|
| SOC | CSV列 | 0-1范围绝对值（如0.75表示75%） |

## Parameters

| 参数 | 默认值 | 范围 | 说明 |
|-----|--------|------|------|
| Capacity_Ah | 100Ah | 1-1000Ah | 电池额定容量 |
| Init_Soc | 0.5 | 0.0 - 1.0 | 初始 SOC 猜测值 |

## Quality Checklist

- [ ] 确保电流方向符号的约定与实际硬件采集信号一致。
- [ ] 确保计算时间间隔 `dt` 转换为了正确的秒单位。
- [ ] 必须定期在车辆静置 (Key-Off) 时期利用 OCV 刷新初始 SOC，否则开环积分误差将无限累加发散。

## Extended References

- **代码实现**: [templates/python/core.py](templates/python/core.py)
- **底层C++头文件**: [templates/cpp/soc_coulomb_counting.h](templates/cpp/soc_coulomb_counting.h)
