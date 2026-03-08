---
name: B2.5-SOC估计-UKF
description: >
  基于无迹卡尔曼滤波(UKF)的SOC在线估计算法。
  通过无迹变换(UT)直接逼近隐马尔可夫模型的非线性概率分布，避免了雅可比矩阵求导误差，适用于强非线性电池(如LFP平台区或固态电池)。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Solid-State]
tier: L2
compute_requirement: <100MHz
pricing: Premium
tags:
  - soc-estimation
  - unscented-kalman-filter
  - ukf
  - bms
visibility: public
---

# B2.5 SOC估计 - 无迹卡尔曼滤波 (UKF)

## When to use this skill

Use this skill when:
- 电池材料的开路电压(OCV)曲线表现出**极强的非线性**（如磷酸铁锂 LFP 的长平坦区边缘，或者某些硅碳负极/固态电池在特定深度的电压陡变）。
- 使用 EKF (扩展卡尔曼滤波) 时，由于对非线性观测方程 $H$ 的一阶泰勒展开导致模型截断误差过大，滤波发散。
- BMS MCU 计算资源充裕（带有硬件浮点运算的支持，最好主频 > 100MHz），因为UKF需要对每一维状态生成多个 Sigma 点并分别代入非线性方程计算。
- 追求极致的 SOC 估计精度 (±1%)。

**替代方案**:
- 若电池是非典型的强非线性，但 BMS 算力有限 (`<50MHz`)，请降级使用包含在线参数辨识能力的 `B2.4-SOC估计-AEKF`。
- 若只需最基本的估计，使用 `B2.3-SOC估计-EKF`。

## Quick Start
1. **准备输入数据**: CSV文件，包含 `current, voltage, temperature` 列。
2. **选择电池基础参数**:
   - `reference/battery_mapping/lfp_default.yaml`
3. **运行估计**:
   ```bash
   python templates/python/core.py \
       --input data_samples/input/nonlinear_test.csv \
       --output output/soc_result.csv \
       --battery lfp_default
   ```

## Decision Points

| 场景特征 | 条件 | 推荐动作 | 替代方案 |
|---------|------|---------|---------|
| 算法耗时超标 | `T_exec > T_sampling / 2` | 简化UKF状态维度（如降级为1RC模型） | 退回到EKF |
| Sigma点越界 | `协方差矩阵P非正定`| 触发Cholesky分解重置保护，强制对角化P | 停机报警 |
| 高信噪比例 | 测量噪声巨大 | 增加中心点权重缩小采样分布范围 | 混合安时积分权重 |

## How it works

### 核心原理
与 EKF (B2.3) 使用解析方法求雅可比矩阵（一阶泰勒展开）来近似非线性函数的后验概率分布不同，**UKF 采用统计线性化方法（无迹变换 Unscented Transform, UT）**。

1. **Sigma 点采样**: 
   在当前状态估计 $x$ 周围，按照协方差矩阵 $P$ 的分布，以确定性而非随机抽样的方式提取出一组（共 $2n+1$ 个，$n$ 为状态数）Sigma 点。
2. **非线性传播**:
   将这组 Sigma 点**直接代入原本的无偏非线性电池系统方程**（状态方程与观测方程）进行演化。
3. **加权重构**:
   将经过非线性函数映射后的 Sigma 点的输出结果结合对应的权重 $W_m, W_c$ 重新求加权均值和协方差，从而得到先验状态和新息协方差。

这种方法无需任何求导，理论上能达到非线性函数**三阶泰勒展开**的逼近精度（而 EKF 只有一阶精度）。

### 工业级工程鲁棒性设计
1. **Cholesky 分解失败保护**:
   寻找 Sigma 点时需要求协方差矩阵 $P$ 的平方根（通常用 Cholesky 分解）。在实车定点运算或浮点精度不足时，$P$ 常常失去正定性导致分解崩溃。工业级实现中必须包含对梯形分解对角线的监测（遇负数或零强制取小正数）以及 SVD 备份机制或 `cholupdate` 修复。
2. **无物理意义状态裁剪 (Physically meaningful states)**:
   Sigma 点在散开时，可能会导致部分点代表的 SOC < 0 或 SOC > 1。把这些反物理的值带入 OCV 查找表会导致严重异常。算法中必须在代入非线性方程前对散开的散点进行物理域截断。

## Inputs & Outputs

### Inputs

| 参数 | 格式 | 要求 | 示例 |
|-----|------|------|------|
| 时间戳 | CSV列 | 秒 | `0, 0.1, 0.2, ...` |
| 电流I | CSV列 | 约定放正充负 | `120, -50, -30, ...` |
| 电压V | CSV列 | 单位V | `3.2, 3.32, 3.31, ...` |

### Outputs

| 输出 | 格式 | 说明 |
|-----|------|------|
| SOC | CSV列 | (0~1)的连续平滑曲线 |
| V_est | CSV列 | Sigma加权预测的电压中心 |

## Parameters
| 参数 | 默认值 | 范围 | 说明 |
|-----|--------|------|------|
| Alpha ($\alpha$) | 1e-3 | 1e-4 - 1 | 控制Sigma点分布的扩散程度。太小精度高但容易数值发散，太大失去高阶逼近。 |
| Beta ($\beta$) | 2.0 | 2.0 | 对高斯分布而言，由于高斯先验的截尾特性，$\beta=2$是最优选择。 |
| Kappa ($\kappa$) | 0.0 | 0.0 | 二次缩放参数 |

## Extended References
- **代码实现**: [templates/python/core.py](templates/python/core.py)
- **底层C++代码架构预留**: [templates/cpp/soc_ukf_core.h](templates/cpp/soc_ukf_core.h)
