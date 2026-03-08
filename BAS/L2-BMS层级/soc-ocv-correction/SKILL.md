---
name: B2.2-SOC估计-查表修正
description: >
  结合安时积分与定期开路电压(OCV)查表的SOC估计与校准算法。
  适用场景：BMS板端低算力环境（<10MHz）、可获取长静置状态的储能或乘用车。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Semi-Solid, Solid-State]
tier: L2
compute_requirement: <10MHz
pricing: Free
tags:
  - soc-estimation
  - ocv-correction
  - bms
visibility: public
---

# B2.2 SOC估计 - 查表修正法 (OCV-SOC Correction)

## When to use this skill

Use this skill when:
- 算力资源有限（如低端MCU，主频 <10MHz），无法运行卡尔曼滤波等复杂矩阵运算。
- 电池应用场景中包含**长时间的静置期**（通常大于2小时，视具体配方而定，例如插混每天夜间充电后、储能电站的待机时段）。
- 需要比纯安时积分（B2.1）更高的长期精度，防止开环电流积分导致的误差无限累积。

**替代方案**:
- 若电池极少有超过 1 小时的静置机会（比如重卡换电站、不间断充放电的调频储能），此算法将退化为纯安时积分。此时强烈建议升级为闭环实时反馈的 `B2.3-SOC估计-EKF` 或 `B2.4-SOC估计-AEKF`。

## Quick Start
1. **准备输入数据**: CSV文件，包含 `current, voltage, temperature` 列
2. **选择电池参数**:
   - `reference/battery_mapping/lfp_ocv.yaml` (定义了不同温度下的OCV-SOC查找表)
3. **运行估计**:
   ```bash
   python templates/python/core.py \
       --input data_samples/input/driving_with_rest.csv \
       --output output/soc_result.csv \
       --battery lfp_ocv
   ```
4. **查看结果**:
   - 注意观察长静置期间（电流为0达到一定时长后），SOC 是否发生阶跃修正。

## Decision Points

| 场景特征 | 条件 | 推荐动作 | 替代方案 |
|---------|------|---------|---------|
| LFP平坦区 | `SOC在 30%-70% 区间` | 禁用/减弱电压查表修正权重 | 引入历史充放电Ah数进行辅助判定 |
| 低温冷车启动 | `temperature < 0°C`  | 静置时间阈值由2h延长至 4h | - |
| SOC跳变过大 | `|SOC_ocv - SOC_ah| > 10%`| 启动异常报警，限制单次修正幅度不超过 5% | 平滑滤波释放误差（类似AEKF文档） |

## How it works

### 核心原理
此算法采用“**运行期间安时积分 + 静置期间OCV查表校准**”的双模态逻辑：

1. **动态运行模式 (电流 |I| > deadband)**:
   算法执行标准的 `B2.1-SOC估计-安时积分`，仅靠电流推算 SOC 变化。
2. **静置弛豫模式 (电流 |I| < deadband 且持续时间 > threshold)**:
   当电池电流切断后，内部极化开始消散（弛豫过程），端电压逐渐逼近电池的真实热力学开路电压 (OCV)。
   一旦静置时间满足要求（如 2小时），直接读取当前的端电压作为 OCV，并通过电池固有的 **OCV-SOC 关系曲线**（查表）反推出当前绝度的 SOC，并强制将其覆盖（或平滑混合）正在执行的安时积分 SOC，从而消除之前的积分累积误差。

### 工业级工程鲁棒性设计
1. **防跳变平滑层 (Jump Smoothing)**:
   校准发生时，真实的后台内部 SOC 会立刻突变到 OCV 算出的值，但**对外显示的 SOC 必须通过一个低通滤波器或步长限制器缓慢过度**，禁止仪表盘电量瞬间从 40% 跳到 50%。
2. **静置计时器重置 (Rest Timer)**:
   只要在此期间有任何大于死区的微小电流出现，必须立刻重置静置计时器，防止在极化未完全消散时误读 OCV 导致巨大误差。
3. **迟滞效应处理 (Hysteresis)**:
   特别针对 LFP 电池，放电后的弛豫电压轨和充电后的弛豫电压轨存在几十毫伏的插值。实用的工业级查表应该区分 `OCV_Charge` 和 `OCV_Discharge` 曲线，根据最后一次的主电流方向决定查哪张表。

## Inputs & Outputs

### Inputs

| 参数 | 格式 | 要求 | 示例 |
|-----|------|------|------|
| 时间戳 | CSV列 | 秒 | `0, 1.2, 2.5, ...` |
| 电流I | CSV列 | 单位A，充电为负，放电为正 | `50, 0, -30, ...` |
| 电压V | CSV列 | 单位V (在电流0区域即为静置电压) | `3.2, 3.32, 3.31, ...` |
| 温度T | CSV列 | 单位°C | `25, 25, 25, ...` |

### Outputs

| 输出 | 格式 | 说明 |
|-----|------|------|
| SOC_real | CSV列 | 包含修正跳变的真实后台SOC |
| SOC_disp | CSV列 | 对外发送给车辆/系统的平滑显示SOC |
| is_corrected | CSV列 | 标志位：当前迭代是否发生了查表修正（1/0）|

## Parameters
| 参数 | 默认值 | 范围 | 说明 |
|-----|--------|------|------|
| Rest_Time_Sec | 7200 | 1800 - 14400 | 允许采信OCV的最短静置时间 (秒) |
| Max_V_Diff_mv | 2 | 1 - 10 | 判断完全弛豫的电压导数阈值 (dV/dt < X mV/min) |

## Quality Checklist
- [ ] OCV 查找表必须是单调递增的，否则查表算法会出错。
- [ ] 确保在 LFP 的 30~70% 平台区，电压的测量误差没有放大转变为巨大的 SOC 跳变。
- [ ] 显示 SOC (SOC_disp) 必须保证向后兼容性：不允许出现充电时电量倒扣，或放电时电量回升违反常理的现象。

## Extended References
- **代码实现**: [templates/python/core.py](templates/python/core.py)
- **底层C++头文件**: [templates/cpp/soc_ocv_correction.h](templates/cpp/soc_ocv_correction.h)
