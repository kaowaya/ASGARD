# BAS Skill 渐进式披露机制设计规范

> **版本**: V1.0
> **日期**: 2026-03-07
> **适用范围**: ASGARD平台所有94个BAS Skills
> **设计理念**: 基于Claude Skills官方规范，通过分层加载降低token消耗、提升召回命中率

---

## 📋 目录

1. [渐进式披露三层架构](#渐进式披露三层架构)
2. [Level 1: YAML Frontmatter元数据规范](#level-1-yaml-frontmatter元数据规范)
3. [Level 2: SKILL.md正文结构规范](#level-2-skillmd正文结构规范)
4. [Level 3: 资源组织规范](#level-3-资源组织规范)
5. [完整示例：SOC估计-AEKF](#完整示例soc估计-aekf)
6. [验证与持续迭代](#验证与持续迭代)

---

## 渐进式披露三层架构

### 🎯 设计原则

```
┌─────────────────────────────────────────────────────────────┐
│  Level 1: 元数据层（始终加载）                                │
│  → Claude启动时自动索引，判断技能相关性                      │
│  → 目标：快速命中，降低误用率                                │
├─────────────────────────────────────────────────────────────┤
│  Level 2: 指令正文层（触发时加载）                            │
│  → Claude判定相关后，加载SKILL.md主内容                      │
│  → 目标：清晰流程，引导决策                                  │
├─────────────────────────────────────────────────────────────┤
│  Level 3: 资源层（按需探索）                                  │
│  → 根据指令正文的线索，按需拉取代码、文档、数据               │
│  → 目标：深度支持，避免上下文过载                            │
└─────────────────────────────────────────────────────────────┘
```

### 📊 Token消耗对比

| 方案 | 元数据 | 正文 | 资源 | 总计 | 命中率 |
|-----|--------|------|------|------|--------|
| **传统单文件** | - | 15,000 | - | 15,000 | 60% |
| **渐进披露** | 300 | 2,000 | 按需 | 2,300 | 95% |

**优势**：
- ✅ 初始token消耗降低85%
- ✅ 召回命中率提升35%
- ✅ 支持动态更新资源层

---

## Level 1: YAML Frontmatter元数据规范

### 📝 必需字段

```yaml
---
name: <技能名称>
description: <能力描述+触发条件>
version: "<版本号>"
author: ASGARD
battery_types: [<支持的电池类型>]
tier: <L0-L5层级>
compute_requirement: <算力需求>
pricing: <定价模式>
tags: [<领域标签>]
visibility: <共享范围>
---
```

### 🔍 字段详解

#### name（技能名称）
- **格式**: 使用名词短语，与技能目录名称一致
- **规范**: `Tier编号-功能简称-算法简称`
- **示例**: `B2.4-SOC估计-AEKF`

#### description（能力描述）
- **格式**: 1-2句完整语句，包含领域关键词
- **必需要素**:
  - ✅ 能力说明（做什么）
  - ✅ 触发条件（何时使用）
  - ✅ 业务场景（解决什么问题）
- **反例**: ❌ "高性能SOC估计"（太简短，缺少关键词）
- **正例**: ✅ "自适应扩展卡尔曼滤波算法，用于锂离子电池SOC在线估计。适用场景：BMS板端实时估计、需同时跟踪模型参数老化。"

#### battery_types（支持的电池类型）
- **格式**: 数组，支持5种体系
- **选项**: `[LFP, NCM, Na-ion, Semi-Solid, Solid-State]`
- **通用性标记**:
  - ✅ 100%通用: 列出全部5种
  - ⚠️ 框架通用: 列出适用的，备注需标定
  - ❌ 专用: 只列出适用的

#### tier（层级）
- **选项**:
  - `L0`: 基础模型层（机器学习/深度学习/强化学习/最优化）
  - `L1`: 生产层级（制造质量控制）
  - `L2`: BMS层级（板端状态估计与控制）
  - `L3`: 云端层级（大数据分析与诊断）
  - `L4`: 应用层级（充电优化/储能管理）
  - `L5`: 工商业层级（能量管理与资产管理）

#### compute_requirement（算力需求）
- **选项**:
  - `<10MHz`: 嵌入式（ARM Cortex-M4可运行）
  - `<50MHz`: 轻量级边缘端
  - `<100MHz`: 标准边缘端
  - `Cloud`: 云端高性能计算

#### pricing（定价模式）
- **选项**:
  - `Free`: 免费基础算法
  - `Pro`: 高级算法（订阅制）
  - `Enterprise`: 企业级定制

#### tags（领域标签）
- **格式**: 数组，2-5个标签
- **标签分类**:
  - **功能类别**: `soc-estimation`, `soh-estimation`, `fault-diagnosis`, `thermal-management`
  - **算法类型**: `kalman-filter`, `machine-learning`, `electrochemical-model`
  - **应用场景**: `ev-charging`, `energy-storage`, `manufacturing`

#### visibility（共享范围）
- **选项**:
  - `public`: 公开社区
  - `team`: ASGARD团队内部
  - `enterprise`: 企业客户专属

### 📋 元数据示例（优秀实践）

```yaml
---
name: B2.4-SOC估计-AEKF
description: >
  自适应扩展卡尔曼滤波算法，用于锂离子电池SOC在线估计与模型参数联合辨识。
  适用场景：BMS板端实时估计、需跟踪内阻老化、复杂工况（快充/低温）。
version: "2.1.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Semi-Solid, Solid-State]
tier: L2
compute_requirement: <50MHz
pricing: Pro
tags:
  - soc-estimation
  - kalman-filter
  - adaptive-algorithm
  - bms
  - parameter-identification
visibility: team
---
```

---

## Level 2: SKILL.md正文结构规范

### 🎯 正文组织原则

SKILL.md承担"第二层披露"责任，需要：
1. **快速定位**: 通过清晰的章节结构，让Claude快速找到所需步骤
2. **决策引导**: 提供决策表，说明不同场景的分支逻辑
3. **质量保证**: 提供检查清单，指导Claude输出前自查
4. **资源链接**: 通过内链引用Level 3资源

### 📐 标准结构模板

```markdown
---
# YAML Frontmatter（见上文）
---

# <技能名称>

## When to use this skill
Use this skill when [具体触发场景和条件]

## Quick Start
[3-5步标准流程]

## Decision Points
[常见分支与触发条件]

## How it works
[算法原理与核心公式]

## Inputs & Outputs
### Inputs
- [输入数据格式与要求]

### Outputs
- [输出格式与预期结果]

## Parameters
| 参数 | 默认值 | 范围 | 说明 |
|-----|--------|------|------|
| ... | ... | ... | ... |

## Battery Type Compatibility
| 电池类型 | 支持级别 | 备注 |
|---------|---------|------|
| LFP | ✅ Full | 默认配置 |
| NCM | ✅ Full | 峰值位置3.65/3.80/3.95V |
| Na-ion | ⚠️ Partial | 需标定OCV曲线 |
| Solid-State | ⚠️ Partial | 使用替代M1.6 |

## Quality Checklist
- [ ] 检查项1
- [ ] 检查项2
- [ ] ...

## Extended References
- 算法原理: [reference/algo-theory.md](reference/algo-theory.md)
- 参数调优: [reference/parameter-tuning.md](reference/parameter-tuning.md)
- 代码实现: [templates/aekf_estimator.py](templates/aekf_estimator.py)
- 示例数据: [data_samples/sample_bms_data.csv](data_samples/sample_data.csv)

## Changelog
- v2.1.0 (2026-02-15): 新增Sage-Husa自适应噪声估计
- v2.0.0 (2026-01-10): 重构为双自适应架构
- v1.0.0 (2025-12-01): 初始版本
```

### 📝 章节写作规范

#### When to use this skill
- **目标**: 帮助Claude快速判断是否应该使用此技能
- **写法**: 列举3-5个典型场景
- **示例**:
  ```
  Use this skill when:
  - 需要BMS板端实时SOC估计（频率≥1Hz）
  - 电池处于老化阶段（SOH<90%），模型参数漂移明显
  - 工况复杂（快充、低温、高倍率放电）
  - 需要同时估计SOC和模型参数（R0、R1、R2、C1、C2）
  - 算力资源有限（<50MHz，ARM Cortex-M4/M7可运行）
  ```

#### Quick Start
- **目标**: 提供"最常用路径"，80%场景只需按此执行
- **写法**: 3-5个编号步骤，明确引用Level 3资源
- **示例**:
  ```markdown
  ## Quick Start
  1. 准备输入数据：电流I、电压V、温度T（1Hz采样）
  2. 运行初始化脚本：
     ```bash
     python templates/aekf_estimator.py --init
     ```
  3. 加载电池参数：
     - 液态电池: `reference/battery_params/lfp_280ah.yaml`
     - 固态电池: `reference/battery_params/solid_state_params.yaml`
  4. 执行估计：
     ```bash
     python templates/aekf_estimator.py --input data_samples/test_data.csv
     ```
  5. 查看输出：`output/soc_estimate.csv`
  ```

#### Decision Points
- **目标**: 处理"剩余20%场景"的分支逻辑
- **格式**: IF-THEN规则表
- **示例**:
  ```markdown
  ## Decision Points

  | 场景特征 | 条件 | 推荐动作 | 替代方案 |
  |---------|------|---------|---------|
  | 电池类型是固态 | battery_type == "Solid-State" | 使用M1.6固态界面质量评估 | 降级使用本技能（精度降低） |
  | 算力极度受限 | compute_resource < "10MHz" | 使用B2.3 SOC估计-EKF | 或使用B2.1安时积分法 |
  | 需要极高精度 | accuracy_requirement == "ultra-high" | 联合云端L3 SOH深度学习 | - |
  | 低温工况 | temperature < -10°C | 调整低温参数表 | 参考[reference/low_temp_tuning.md](reference/low_temp_tuning.md) |
  ```

#### How it works
- **目标**: 让Claude理解算法原理，避免"黑盒调用"
- **深度**: 平衡"可解释性"与"简洁性"
- **建议**:
  - 核心公式：用LaTeX清晰展示
  - 流程图：用Mermaid或文字描述
  - 物理意义：解释关键参数的物理含义
- **示例**:
  ```markdown
  ## How it works

  ### 双自适应机制
  本技能采用**状态-参数联合估计**架构：

  **状态方程**（SOC演化）:
  $$
  SOC(k) = SOC(k-1) - \frac{I(k) \cdot \Delta t}{Q_n}
  $$

  **参数方程**（内阻追踪）:
  $$
  R_0(k) = R_0(k-1) + K_{R0} \cdot \varepsilon(k)
  $$

  **Sage-Husa自适应**（噪声协方差调整）:
  $$
  Q_k = (1-d_k) \cdot Q_{k-1} + d_k \cdot K_k \cdot \varepsilon_k \cdot \varepsilon_k^T \cdot K_k^T
  $$

  ### 算法流程
  ```
  输入: I(k), V(k), T(k)
     ↓
  预测步骤: SOC⁻(k), P⁻(k)
     ↓
  观测更新: 计算卡尔曼增益K(k)
     ↓
  参数自适应: 更新R₀、R₁、R₂、C₁、C₂
     ↓
  后验估计: SOC(k), P(k)
     ↓
  输出: SOC(k) ± 置信区间
  ```

  **关键创新**:
  - ✅ 遗忘因子λ：检测工况突变时，加速模型收敛
  - ✅ 温度补偿：R₀(T)、Cp(T)查表插值
  - ✅ 老化适配：R₀(SOH)随容量衰减动态调整
  ```

#### Quality Checklist
- **目标**: 指导Claude在输出前自查，避免低质量结果
- **分类**: 输入检查、参数检查、输出验证
- **示例**:
  ```markdown
  ## Quality Checklist

  ### 输入数据质量
  - [ ] 电流、电压、温度时间戳对齐（允许误差<100ms）
  - [ ] 采样频率≥1Hz（推荐10Hz）
  - [ ] 数据无缺失（缺失率<1%可插值）

  ### 参数合理性
  - [ ] 初始SOC在0-1范围内
  - [ ] 初始容量Qn与额定容量偏差<10%
  - [ ] 过程噪声Q、观测噪声R均为正定矩阵

  ### 输出验证
  - [ ] SOC估计值在0-1范围内
  - [ ] SOC变化速率与电流方向一致（充电上升、放电下降）
  - [ ] 误差协方差P收敛（对角元素<0.1）

  ### 极端情况处理
  - [ ] 若SOC跳变>10%，检查电流传感器是否异常
  - [ ] 若滤波发散（P持续增大），重置P矩阵
  ```

#### Extended References
- **目标**: 提供"线索"，引导Claude探索Level 3资源
- **格式**: 内链Markdown格式，明确文件用途
- **分类**:
  - **理论文档**: 算法原理、数学推导
  - **实践指南**: 参数调优、故障排查
  - **代码实现**: 算法模板、示例代码
  - **示例数据**: 标注数据、测试数据
- **示例**:
  ```markdown
  ## Extended References

  ### 理论文档
  - **算法推导**: [reference/algo-theory.md](reference/algo-theory.md) - 完整的EKF数学推导、物理意义说明
  - **电池模型**: [reference/battery-model.md](reference/battery-model.md) - Thevenin等效电路模型详解

  ### 实践指南
  - **参数调优**: [reference/parameter-tuning.md](reference/parameter-tuning.md) - Q、R初值设定、收敛判断标准
  - **低温优化**: [reference/low_temp_tuning.md](reference/low_temp_tuning.md) - 低温工况参数自适应策略
  - **故障排查**: [reference/troubleshooting.md](reference/troubleshooting.md) - 常见错误代码与解决方案

  ### 代码实现
  - **核心算法**: [templates/aekf_estimator.py](templates/aekf_estimator.py) - Python实现（含注释）
  - **C++移植版**: [templates/aekf_estimator.cpp](templates/aekf_estimator.cpp) - 嵌入式C++版本（ARM优化）
  - **参数文件**: [templates/battery_params.yaml](templates/battery_params.yaml) - 5种电池体系参数模板

  ### 示例数据
  - **标准工况**: [data_samples/standard_cycle.csv](data_samples/standard_cycle.csv) - 25°C常温充放电数据
  - **快充工况**: [data_samples/fast_charging.csv](data_samples/fast_charging.csv) - 2C快充数据
  - **低温工况**: [data_samples/low_temp.csv](data_samples/low_temp.csv) - -20°C低温数据
  ```

---

## Level 3: 资源组织规范

### 📁 标准目录结构

```
skill-name/
├── SKILL.md                  # Level 2: 指令正文（必需）
├── templates/                # 算法模板代码
│   ├── python/              # Python实现
│   │   ├── core.py          # 核心算法
│   │   ├── utils.py         # 工具函数
│   │   └── config.py        # 配置管理
│   ├── cpp/                 # C++嵌入式实现
│   │   ├── aekf_estimator.h
│   │   └── aekf_estimator.cpp
│   └── battery_params.yaml  # 电池参数模板
├── reference/               # 参考文档
│   ├── algo-theory.md       # 算法原理
│   ├── parameter-tuning.md  # 参数调优指南
│   ├── troubleshooting.md   # 故障排查
│   └── battery_mapping/     # 电池体系映射
│       ├── lfp_280ah.yaml   # LFP参数
│       ├── ncm_100ah.yaml   # NCM参数
│       └── naion_120ah.yaml # 钠离子参数
└── data_samples/            # 示例数据
    ├── input/               # 输入示例
    │   ├── standard_cycle.csv
    │   └── fast_charging.csv
    └── output/              # 期望输出
        └── soc_estimate.csv
```

### 🎨 资源组织原则

#### 1. templates/ 目录
**目标**: 提供可直接运行的算法模板

**文件规范**:
- ✅ **命令行友好**: 支持标准输入输出，Claude可直接调用
- ✅ **幂等性**: 多次运行相同输入，输出一致
- ✅ **诊断日志**: 输出包含执行状态、错误信息、性能指标

**示例代码结构**:
```python
# templates/python/core.py
"""
AEKF SOC估计器核心算法

Usage:
    python core.py --input data.csv --output result.csv --battery lfp_280ah
"""

import argparse
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='AEKF SOC Estimator')
    parser.add_argument('--input', required=True, help='输入CSV文件（I, V, T列）')
    parser.add_argument('--output', required=True, help='输出CSV文件')
    parser.add_argument('--battery', default='lfp_280ah', help='电池参数文件名')
    parser.add_argument('--dt', type=float, default=1.0, help='采样间隔(秒)')
    args = parser.parse_args()

    logger.info(f"🚀 启动AEKF SOC估计")
    logger.info(f"📂 输入文件: {args.input}")
    logger.info(f"🔋 电池类型: {args.battery}")

    # 加载参数
    params = load_battery_params(args.battery)
    logger.info(f"✓ 参数加载完成: Qn={params['Qn']}Ah")

    # 运行估计
    result = run_aekf(args.input, params, args.dt)

    # 保存结果
    result.to_csv(args.output, index=False)
    logger.info(f"✓ 结果已保存: {args.output}")
    logger.info(f"📊 最终SOC: {result['SOC'].iloc[-1]:.2%}")

if __name__ == '__main__':
    main()
```

**命令行调用示例**:
```bash
# 标准调用
python templates/python/core.py \
    --input data_samples/standard_cycle.csv \
    --output output/soc_result.csv \
    --battery lfp_280ah

# 预期输出
[INFO] 🚀 启动AEKF SOC估计
[INFO] 📂 输入文件: data_samples/standard_cycle.csv
[INFO] 🔋 电池类型: lfp_280ah
[INFO] ✓ 参数加载完成: Qn=280Ah
[INFO] ✓ AEKF收敛完成: 耗时0.85s
[INFO] ✓ 结果已保存: output/soc_result.csv
[INFO] 📊 最终SOC: 75.32%
```

#### 2. reference/ 目录
**目标**: 提供深度参考文档，但只在需要时加载

**文档分类**:
| 文档类型 | 文件示例 | 何时加载 |
|---------|---------|---------|
| **算法原理** | `algo-theory.md` | Claude需要理解算法细节时 |
| **参数调优** | `parameter-tuning.md` | 用户反馈精度不足时 |
| **故障排查** | `troubleshooting.md` | 算法报错时 |
| **电池映射** | `battery_mapping/*.yaml` | 切换电池类型时 |

**文档写作规范**:
```markdown
# reference/parameter-tuning.md

## Q、R初值设定指南

### 经验公式
$$
Q_{initial} = \sigma_I^2 \cdot I_{max}^2
$$
$$
R_{initial} = \sigma_V^2
$$

### 推荐配置表
| 场景 | Q | R | 说明 |
|-----|---|---|------|
| 标准工况 | 1e-4 | 1e-2 | 25°C常温 |
| 低温工况 | 1e-3 | 5e-2 | -20°C，噪声增大 |
| 快充工况 | 5e-4 | 2e-2 | 2C充电，动态性强 |

### 调优流程
1. 从标准配置开始
2. 若SOC震荡，增大Q（允许更快的状态更新）
3. 若收敛慢，减小R（提高对观测的信任）
4. 检查误差协方差P是否收敛（<0.1）

## 常见问题

### Q1: SOC跳变
**症状**: SOC在短时间内变化>10%
**原因**:
- 电流传感器异常（零点漂移）
- 过程噪声Q过大

**解决方案**:
1. 检查电流传感器零点
2. 将Q减半
3. 增大异常检测阈值（见`core.py`第150行）
```

#### 3. data_samples/ 目录
**目标**: 提供测试数据，验证算法正确性

**数据规范**:
- ✅ **标准格式**: CSV文件，列名为`timestamp, current, voltage, temperature`
- ✅ **数据标注**: 文件名包含工况信息（如`standard_cycle_25C.csv`）
- ✅ **期望输出**: 提供`output/`目录下的ground truth

**示例数据**:
```csv
# data_samples/input/standard_cycle_25C.csv
timestamp,current,voltage,temperature
0,50,3.2,25
1,50,3.25,25
2,50,3.31,25
...
```

---

## 完整示例：SOC估计-AEKF

### 📁 目录结构

```
B2.4-SOC估计-AEKF/
├── SKILL.md
├── templates/
│   ├── python/
│   │   ├── core.py
│   │   ├── utils.py
│   │   └── config.py
│   ├── cpp/
│   │   ├── aekf_estimator.h
│   │   └── aekf_estimator.cpp
│   └── battery_params.yaml
├── reference/
│   ├── algo-theory.md
│   ├── parameter-tuning.md
│   ├── troubleshooting.md
│   └── battery_mapping/
│       ├── lfp_280ah.yaml
│       ├── ncm_100ah.yaml
│       └── naion_120ah.yaml
└── data_samples/
    ├── input/
    │   ├── standard_cycle_25C.csv
    │   ├── fast_charging_2C.csv
    │   └── low_temp_minus20C.csv
    └── output/
        └── soc_estimate_groundtruth.csv
```

### 📄 SKILL.md 完整内容

```markdown
---
name: B2.4-SOC估计-AEKF
description: >
  自适应扩展卡尔曼滤波算法，用于锂离子电池SOC在线估计与模型参数联合辨识。
  适用场景：BMS板端实时估计、需跟踪内阻老化、复杂工况（快充/低温）。
version: "2.1.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Semi-Solid, Solid-State]
tier: L2
compute_requirement: <50MHz
pricing: Pro
tags:
  - soc-estimation
  - kalman-filter
  - adaptive-algorithm
  - bms
  - parameter-identification
visibility: team
---

# B2.4 SOC估计 - AEKF

## When to use this skill

Use this skill when:
- 需要BMS板端实时SOC估计（频率≥1Hz）
- 电池处于老化阶段（SOH<90%），模型参数漂移明显
- 工况复杂（快充、低温、高倍率放电）
- 需要同时估计SOC和模型参数（R0、R1、R2、C1、C2）
- 算力资源有限（<50MHz，ARM Cortex-M4/M7可运行）

**替代方案**:
- 算力<10MHz: 使用`B2.3-SOC估计-EKF`（参数固定）
- 需要极高精度: 联合`C3.7-SOH深度学习`（云端校正）

## Quick Start

1. **准备输入数据**: CSV文件，包含`current, voltage, temperature`列（1Hz采样）
2. **选择电池参数**:
   - LFP: `reference/battery_mapping/lfp_280ah.yaml`
   - NCM: `reference/battery_mapping/ncm_100ah.yaml`
3. **运行估计**:
   ```bash
   python templates/python/core.py \
       --input data_samples/input/standard_cycle_25C.csv \
       --output output/soc_result.csv \
       --battery lfp_280ah
   ```
4. **查看结果**:
   - `output/soc_result.csv`: SOC时序数据（含置信区间）
   - 控制台输出: 最终SOC、收敛时间、误差统计

## Decision Points

| 场景特征 | 条件 | 推荐动作 | 替代方案 |
|---------|------|---------|---------|
| 固态电池 | `battery_type == "Solid-State"` | 使用M1.6固态界面质量评估 | 降级使用（精度降低15%） |
| 算力<10MHz | `compute_resource < "10MHz"` | 使用B2.3 SOC估计-EKF | 或B2.1安时积分法 |
| 低温工况 | `temperature < -10°C` | 调整Q、R噪声参数 | 见[reference/parameter-tuning.md](reference/parameter-tuning.md) |
| 极快充电 | `charge_rate > 2C` | 减小滤波遗忘因子λ | 加快参数收敛 |
| SOC跳变异常 | `ΔSOC > 10% in 1s` | 检查电流传感器 | 见[reference/troubleshooting.md](reference/troubleshooting.md) |

## How it works

### 双自适应机制

本技能采用**状态-参数联合估计**架构，包含两个EKF并行运行：

```
┌─────────────────────────────────────────────────────┐
│  状态EKF（State EKF）                                │
│  - 状态方程: SOC(k+1) = SOC(k) - I·Δt/Cn            │
│  - 观测方程: V = OCV(SOC) - I·R0 - Vp               │
│  - 输出: SOC估计值                                   │
└─────────────────────────────────────────────────────┘
                    ↓ 协同
┌─────────────────────────────────────────────────────┐
│  参数EKF（Parameter EKF）                            │
│  - 参数辨识: R₀、Cp在线更新                          │
│  - 遗忘因子λ: 动态调节历史数据权重                   │
│  - 输出: 实时模型参数                                │
└─────────────────────────────────────────────────────┘
```

### 核心公式

**状态转移矩阵 A**:
$$
A = \begin{bmatrix}
1 & 0 & 0 & 0 \\
-\frac{\Delta u_{ocv}}{U_{ocv}^2} \cdot u_0 & 1 & 0 & 0 \\
0 & 0 & e^{-\Delta t/\tau_1} & 0 \\
0 & 0 & 0 & e^{-\Delta t/\tau_2}
\end{bmatrix}
$$

**Sage-Husa自适应噪声更新**:
$$
Q_k = (1-d_k) \cdot Q_{k-1} + d_k \cdot K_k \cdot \varepsilon_k \cdot \varepsilon_k^T \cdot K_k^T
$$

其中:
- $d_k = \frac{1-b}{1-b^{k+1}}$（遗忘因子，b=0.97）
- $\varepsilon_k = V_{measured} - V_{predicted}$（新息）

### 关键创新点

1. **遗忘因子λ自适应**: 检测工况突变时，λ从0.99降至0.9，加速模型收敛
2. **温度补偿**: R₀(T)、Cp(T)通过查表+插值实现
3. **老化适配**: R₀(SOH)随容量衰减动态调整
4. **日历老化建模**: 分离循环老化和时间老化

## Inputs & Outputs

### Inputs

| 参数 | 格式 | 要求 | 示例 |
|-----|------|------|------|
| 电流I | CSV列 | 单位A，充电为正 | `50, 50, 50, ...` |
| 电压V | CSV列 | 单位V，范围2.5-4.2V | `3.2, 3.25, 3.31, ...` |
| 温度T | CSV列 | 单位°C，范围-30-60°C | `25, 25, 25, ...` |
| 采样间隔 | 数字 | 秒，推荐1 | `dt=1.0` |

**数据质量要求**:
- 时间戳对齐误差<100ms
- 采样频率≥1Hz（推荐10Hz）
- 数据缺失率<1%

### Outputs

| 输出 | 格式 | 说明 |
|-----|------|------|
| SOC | CSV列 | 0-1范围（如0.75表示75%） |
| SOC_std | CSV列 | 标准差（不确定性估计） |
| R0 | CSV列 | 欧姆内阻（Ω）实时追踪 |
| 收敛标志 | 日志 | "✓ AEKF收敛完成" |

**示例输出**:
```csv
timestamp,SOC,SOC_std,R0,R1,R2,C1,C2
0,0.5000,0.0100,0.001,0.002,0.003,1000,2000
1,0.4982,0.0098,0.001,0.002,0.003,1000,2000
...
```

## Parameters

| 参数 | 默认值 | 范围 | 说明 |
|-----|--------|------|------|
| Qn | 280Ah | 50-500Ah | 额定容量 |
| R0_initial | 0.001Ω | 0.0005-0.005Ω | 初始欧姆内阻 |
| Q_initial | 1e-4 | 1e-6 - 1e-2 | 过程噪声协方差 |
| R_initial | 1e-2 | 1e-4 - 1 | 观测噪声协方差 |
| 遗忘因子b | 0.97 | 0.9-0.999 | Sage-Husa遗忘因子 |
| dt | 1.0s | 0.1-10s | 采样间隔 |

**参数调优**: 见[reference/parameter-tuning.md](reference/parameter-tuning.md)

## Battery Type Compatibility

| 电池类型 | 支持级别 | 备注 |
|---------|---------|------|
| LFP | ✅ Full | 默认配置，OCV曲线平坦区间需特殊处理 |
| NCM | ✅ Full | 峰值位置3.65/3.80/3.95V |
| Na-ion | ⚠️ Partial | 需标定OCV曲线，硬碳平台区特殊处理 |
| Semi-Solid | ⚠️ Partial | 界面阻抗模型需调整 |
| Solid-State | ⚠️ Partial | 建议使用M1.6固态界面质量评估 |

## Quality Checklist

### 输入数据质量
- [ ] 电流、电压、温度时间戳对齐（误差<100ms）
- [ ] 采样频率≥1Hz
- [ ] 数据缺失率<1%
- [ ] 电压范围在2.5-4.2V内
- [ ] 温度范围在-30-60°C内

### 参数合理性
- [ ] 初始SOC在0-1范围内
- [ ] 初始容量Qn与额定容量偏差<10%
- [ ] 过程噪声Q、观测噪声R均为正定矩阵
- [ ] 遗忘因子b在0.9-0.999范围内

### 输出验证
- [ ] SOC估计值在0-1范围内
- [ ] SOC变化速率与电流方向一致（充电↑、放电↓）
- [ ] 误差协方差P收敛（对角元素<0.1）
- [ ] R0随老化缓慢增大（非突变）

### 极端情况处理
- [ ] 若SOC跳变>10%，检查电流传感器零点
- [ ] 若滤波发散（P持续增大），重置P矩阵
- [ ] 若SOC超出[0,1]，截断至边界值

## Extended References

### 理论文档
- **算法推导**: [reference/algo-theory.md](reference/algo-theory.md)
  - 完整EKF数学推导
  - Sage-Husa自适应原理
  - 物理意义解释
- **电池模型**: [reference/battery-model.md](reference/battery-model.md)
  - Thevenin等效电路详解
  - OCV-SOC曲线特性
  - 温度影响机理

### 实践指南
- **参数调优**: [reference/parameter-tuning.md](reference/parameter-tuning.md)
  - Q、R初值设定经验公式
  - 不同工况推荐配置表
  - 调优流程（4步法）
- **低温优化**: [reference/low_temp_tuning.md](reference/low_temp_tuning.md)
  - 低温工况参数自适应策略
  - 加热控制建议
- **故障排查**: [reference/troubleshooting.md](reference/troubleshooting.md)
  - 常见错误代码（E001-E010）
  - SOC跳变/发散/震荡解决方案
  - 日志分析指南

### 代码实现
- **Python核心**: [templates/python/core.py](templates/python/core.py)
  - 完整AEKF实现（含注释）
  - 命令行接口
  - 单元测试用例
- **C++嵌入式**: [templates/cpp/aekf_estimator.cpp](templates/cpp/aekf_estimator.cpp)
  - ARM Cortex-M4优化
  - 定点数实现（节省算力）
  - 内存占用<50KB
- **参数模板**: [templates/battery_params.yaml](templates/battery_params.yaml)
  - 5种电池体系参数
  - 温度系数表
  - 老化系数表

### 示例数据
- **标准工况**: [data_samples/input/standard_cycle_25C.csv](data_samples/input/standard_cycle_25C.csv)
  - 25°C常温，1C充放电
  - 期望输出: `output/standard_cycle_groundtruth.csv`
- **快充工况**: [data_samples/input/fast_charging_2C.csv](data_samples/input/fast_charging_2C.csv)
  - 2C快充，测试参数追踪能力
- **低温工况**: [data_samples/input/low_temp_minus20C.csv](data_samples/input/low_temp_minus20C.csv)
  - -20°C低温，测试鲁棒性

## Changelog

- **v2.1.0** (2026-02-15):
  - ✨ 新增Sage-Husa自适应噪声估计
  - ✨ 新增低温工况参数模板
  - 🐛 修复SOC跳变问题（#145）
  - 📝 完善reference/parameter-tuning.md

- **v2.0.0** (2026-01-10):
  - ♻️ 重构为双自适应架构（状态EKF + 参数EKF）
  - ✨ 新增日历老化建模
  - ✨ 新增遗忘因子自适应

- **v1.0.0** (2025-12-01):
  - 🎉 初始版本发布
  - ✨ 基础AEKF实现
  - ✨ 支持LFP/NCM体系
```

### 📄 reference/algo-theory.md 示例

```markdown
# AEKF算法原理详解

## 1. 扩展卡尔曼滤波（EKF）基础

### 1.1 非线性系统状态方程

电池系统是非线性的，主要非线性来自OCV-SOC关系：

$$
\begin{cases}
X_k = f(X_{k-1}, u_k) + w_k & \text{（状态方程）} \\
Y_k = h(X_k) + v_k & \text{观测方程）}
\end{cases}
$$

其中:
- $X_k = [Q_{loss}, U_{ocv}, U_1, U_2]^T$（状态向量）
- $u_k = I_k$（控制输入：电流）
- $Y_k = V_k$（观测输出：端电压）
- $w_k \sim N(0, Q)$（过程噪声）
- $v_k \sim N(0, R)$（观测噪声）

### 1.2 EKF线性化

对非线性函数$f$和$h$在当前估计值处一阶泰勒展开：

$$
F_k = \frac{\partial f}{\partial X}\Big|_{X_{k-1}=\hat{X}_{k-1}, u_k}
$$

$$
H_k = \frac{\partial h}{\partial X}\Big|_{X_k=\hat{X}_k^-}
$$

## 2. 自适应机制（Adaptive）

### 2.1 Sage-Husa噪声估计器

传统EKF假设Q、R已知且恒定，但实际上：
- Q与工况相关（快充时噪声大）
- R随传感器老化漂移

Sage-Husa方法通过**新息序列**在线估计Q、R：

$$
\varepsilon_k = Y_k - h(\hat{X}_k^-)
$$

$$
\hat{R}_k = (1-d_k)\hat{R}_{k-1} + d_k(\varepsilon_k \varepsilon_k^T - H_k P_k^- H_k^T)
$$

$$
\hat{Q}_k = (1-d_k)\hat{Q}_{k-1} + d_k(K_k \varepsilon_k \varepsilon_k^T K_k^T + P_k - A_k P_{k-1} A_k^T)
$$

其中遗忘因子：

$$
d_k = \frac{1-b}{1-b^{k+1}}, \quad b=0.97
$$

### 2.2 遗忘因子自适应

检测工况突变（如电流阶跃）：

```python
def detect_transient(I_current, I_prev, threshold=10):
    """检测工况突变"""
    if abs(I_current - I_prev) > threshold:
        return True  # 工况突变，减小遗忘因子
    else:
        return False  # 稳态工况，保持大遗忘因子

# 动态调整遗忘因子
lambda_factor = 0.9 if is_transient else 0.99
```

## 3. 物理意义解释

### 3.1 状态变量

| 状态变量 | 物理意义 | 典型值 |
|---------|---------|--------|
| $Q_{loss}$ | 累计容量损失（Ah） | 0-28Ah（LFP 280Ah衰减至80%） |
| $U_{ocv}$ | 开路电压（V） | 3.0-3.6V（LFP） |
| $U_1$ | 第一个RC环节电压（V） | ±0.5V |
| $U_2$ | 第二个RC环节电压（V） | ±0.2V |

### 3.2 参数物理意义

| 参数 | 物理意义 | 影响 |
|-----|---------|------|
| $R_0$ | 欧姆内阻（Ω） | SOC估计滞后程度 |
| $\tau_1=R_1C_1$ | 电化学极化时间常数 | 短期动态响应 |
| $\tau_2=R_2C_2$ | 浓差极化时间常数 | 长期动态响应 |

## 4. 数学推导

### 4.1 Thevenin等效电路

```
   I(t)
    ↓
  ┌────┐
  │    │
  │  R0│
  │    │
  └────┘
    │ ←──────────────┐
    │                │
    ↓                ↓
  [Cathode]        [Anode]
    │                │
    └── R1 ── C1 ────┘
    │
    └── R2 ── C2 ────┘

端电压: V = OCV(SOC) - I·R0 - U1 - U2
```

### 4.2 状态转移矩阵推导

由KCL和KVL:

$$
\frac{dU_1}{dt} = -\frac{U_1}{R_1 C_1} + \frac{I}{C_1}
$$

离散化（欧拉法）:

$$
U_1(k+1) = U_1(k)e^{-\Delta t/\tau_1} + R_1(1-e^{-\Delta t/\tau_1})I(k)
$$

其中$\tau_1 = R_1 C_1$。

## 5. 与标准EKF对比

| 特性 | 标准EKF | AEKF |
|-----|---------|------|
| 参数 | 恒定 | 在线更新 |
| 老化适应 | ❌ | ✅ |
| 计算量 | 低 | 中（+30%） |
| 精度 | ±2% | ±1.5% |
| 工况鲁棒性 | 一般 | 优秀 |

## 参考文献

1. Sage, A. P., & Husa, G. W. (1969). "Adaptive filtering with unknown prior statistics." Joint Automatic Control Conference.
2. Plett, G. L. (2004). "Extended Kalman filtering for battery management systems of LiPB-based HEV battery packs." Journal of Power Sources.
3. Xiong, R., et al. (2018). "A data-driven adaptive state of charge and power capability estimation approach for lithium-ion battery." Energy.
```

---

## 验证与持续迭代

### 🧪 验证清单

开发完BAS Skill后，需通过以下验证：

#### Level 1 验证：元数据质量
- [ ] `name`与目录名称一致
- [ ] `description`包含"能力+触发条件+业务场景"
- [ ] `battery_types`准确标注（通用/部分/专用）
- [ ] `tags`包含3-5个领域标签
- [ ] `tier`与实际部署位置匹配

#### Level 2 验证：正文质量
- [ ] Quick Start可在一分钟内执行完成
- [ ] Decision Points覆盖80%分支场景
- [ ] How it works包含核心公式（LaTeX）
- [ ] Quality Checklist包含5+检查项
- [ ] Extended References内链可访问

#### Level 3 验证：资源可用性
- [ ] `templates/`代码可直接运行（`python xxx.py --help`正常）
- [ ] `reference/`文档Markdown格式正确
- [ ] `data_samples/`示例数据格式规范（CSV列名正确）
- [ ] 所有内链指向的文件存在

#### 功能验证：实际任务回放
- [ ] 准备5个真实任务场景
- [ ] 记录Claude的操作路径
- [ ] 检查是否在正确时机触发技能
- [ ] 检查是否误用或遗漏步骤
- [ ] 检查资源加载顺序是否符合渐进披露

### 📈 持续迭代指标

定期统计以下指标，优化技能设计：

| 指标 | 定义 | 目标值 |
|-----|------|--------|
| **召回命中率** | 正确触发次数 / 应触发总次数 | >90% |
| **误用率** | 错误触发次数 / 触发总次数 | <5% |
| **平均token消耗** | 单次对话平均加载tokens | <3000 |
| **执行成功率** | 任务完成次数 / 总尝试次数 | >95% |
| **资源加载率** | Level 3资源被访问次数 / 总对话次数 | 20-40% |

### 🔄 迭代流程

```
┌─────────────────┐
│  收集实际任务日志  │
└────────┬────────┘
         ↓
┌─────────────────┐
│  分析失败案例     │
│  - 何时未触发？   │
│  - 何时误用？     │
│  - 哪里卡住？     │
└────────┬────────┘
         ↓
┌─────────────────┐
│  优化技能设计     │
│  - 调整tags      │
│  - 重写description│
│  - 补充Decision  │
└────────┬────────┘
         ↓
┌─────────────────┐
│  回归测试        │
│  - 重跑历史任务   │
│  - 确保无退化     │
└─────────────────┘
```

### 📝 文档维护日志

每次迭代后，更新SKILL.md的Changelog：

```markdown
## Changelog

- **v2.2.0** (2026-03-01):
  - ✨ 新增钠离子电池支持（tags添加`na-ion`）
  - ♻️ 重写description，提高召回率（60%→85%）
  - 🐛 修复Decision Points遗漏"快充"场景
  - 📝 新增reference/na-ion-tuning.md
  - 📊 回归测试: 50个任务，成功率92%→96%

- **v2.1.0** (2026-02-15):
  - ...
```

---

## 附录：常见问题

### Q1: 如何判断一个技能是否需要拆分？

**答**: 参考以下标准：

| 场景 | 拆分 | 保持合并 |
|-----|------|---------|
| 算法独立完整 | ✅ 如SOC估计与SOH估计分开 | ❌ 如SOC估计的不同方法（EKF/AEKF/UKF）作为同一技能的变体 |
| 部署位置不同 | ✅ 如板端EKF与云端深度学习分开 | - |
| 电池体系专用 | ✅ 如固态电池界面评估单独技能 | ❌ 通用框架只需在reference/提供不同参数文件 |
| 输入输出差异大 | ✅ 如图像分类（输入图像）与时序估计（输入CSV）分开 | - |

### Q2: Level 3资源应该在何时加载？

**答**: 遵循"按需探索"原则：

| 资源类型 | 触发条件 | 示例 |
|---------|---------|------|
| **理论文档** | Claude需要解释算法原理时 | 用户问"为什么AEKF比EKF准？" |
| **实践指南** | 出现问题或特殊场景时 | 用户反馈"低温下SOC跳变" |
| **代码实现** | 需要运行或修改算法时 | 用户要求"把Q初值调大" |
| **示例数据** | 测试或验证时 | 用户说"先跑一个标准测试" |

### Q3: 如何避免Level 2正文过长？

**答**: 使用"锚点+展开"技术：

```markdown
## How it works

[核心公式和流程图（200字）]

<details>
<summary>📖 深度阅读：完整数学推导（可选展开）</summary>

### 详细的矩阵推导
...（500字详细推导）

</details>
```

### Q4: 标签（tags）应该如何设计？

**答**: 遵循三级标签体系：

| 级别 | 示例 | 用途 |
|-----|------|------|
| **L1 功能类别** | `soc-estimation`, `fault-diagnosis` | 粗粒度分类 |
| **L2 算法类型** | `kalman-filter`, `machine-learning` | 中粒度区分 |
| **L3 应用场景** | `ev-charging`, `low-temperature` | 细粒度触发 |

**推荐**: 每个技能包含1个L1 + 1-2个L2 + 0-2个L3标签

### Q5: 如何处理"一个技能，多种变体"？

**答**: 使用参数化设计，而非拆分成多个技能：

```markdown
## Quick Start

1. 选择算法变体:
   ```bash
   # 标准AEKF
   python core.py --mode standard

   # 强跟踪AEKF（快充场景）
   python core.py --mode strong-tracking

   # Sage-Husa AEKF（老化电池）
   python core.py --mode sage-husa
   ```

2. 所有变体共享同一套理论文档和参数模板
```

在`description`中明确说明支持多种模式：

```yaml
description: >
  自适应扩展卡尔曼滤波算法，支持3种工作模式：
  1) 标准AEKF（通用），2) 强跟踪AEKF（快充），3) Sage-Husa AEKF（老化电池）。
  适用场景：BMS板端实时SOC估计、模型参数联合辨识。
```

---

## 总结

渐进式披露机制的核心在于：

1. **Level 1精准匹配**: 通过丰富的元数据，让Claude快速找到相关技能
2. **Level 2高效执行**: 通过清晰的章节和决策表，让Claude快速完成任务
3. **Level 3按需探索**: 通过内链和资源组织，让Claude在需要时深入探索

**最终目标**: 用最少的tokens，完成最准确的任务召回和执行。

---

**文档作者**: ASGARD产品设计团队
**更新日期**: 2026-03-07
**下次评审**: 2026-04-01
