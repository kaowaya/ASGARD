---
name: C3.2-内短路诊断-P2D
description: >
  基于简化的电化学单颗粒模型(SPM)与伪二维(P2D)方程组的云端内短路诊断算子。
  通过拟合充电末端的长时松弛电压曲线(Relaxation Voltage)，精准辨识微电流级别的异常欧姆漏电行为。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion]
tier: L3
compute_requirement: >2GB RAM, Python/SciPy Optimization, x86/ARM64 Server
pricing: Premium
tags:
  - isc-detection
  - p2d-model
  - relaxation-analysis
  - cloud-native
visibility: public
---

# C3.2 内短路诊断 (P2D电化学机理模型)

## When to use this skill

Use this skill when:
- 需要对高安全等级的电池包（纯电动汽车、储能电站）进行深度、无损的早期内短路 (ISC) 检测。
- 有充分的静置松弛数据（例如充电完成拔枪后，或场站待机休眠期，电流严格为 0）。
- C3.1 基于统计的诊断报告了疑似故障，需要通过严谨的电化学机理模型进行确认（交叉验伪）。

**替代方案**:
- 若电池包缺乏稳定的静置时长，或者算力极度受限且仅接受轻量级诊断，请使用 `C3.1 内短路诊断-SOS` 或基于等效电路模型的 `C3.4`。

## Quick Start
1. **输入准备**: 必须是经过 `C3.0-Data-Pipeline` 清洗好的、包含连续静置阶段特征的 DataFrame。
2. **运行电化学诊断**:
   ```bash
   python templates/python/p2d_isc_diagnosis.py \
       --input data_samples/input/clean_relaxation_segment.csv \
       --output output/isc_p2d_report.json
   ```

## Decisions Points
- **模型降阶 (Occam's Razor)**: 完整的 P2D 偏微分方程组在云端对海量车辆求解成本极其高昂。本算子剥离了复杂的液相浓度梯度，降阶为 **带自放电漏电流项的单颗粒模型 (SPM-with-Leakage)**。
- **触发条件**: 算法在输入特征矩阵中自动寻找 $I \approx 0$ 且持续时间 $> 30$ 分钟的松弛段（Relaxation）进行分析。

## How it works
1. 正常电芯的弛豫（Relaxation）仅由固相扩散现象主导，电压最终无限逼近 OCV 平衡态。
2. 若存在内短路（即并联的寄生电阻 $R_{isc}$），在外部 $I=0$ 时，内部会产生一个稳定的、消耗 OCV 的自放电漏电流 $I_{leak} = V/R_{isc}$。
3. 算子读取松弛曲线，使用 `scipy.optimize` 利用非线性最小二乘法，同时拟合扩散时间常数 $\tau$ 和漏电流参数 $I_{leak}$。
4. 若 $I_{leak}$ 大于设备底噪（例如 $> 1mA$）且呈现发散趋势，则以第一性原理确认为内短路失效。

## Quality Checklist
- [ ] 算法必须自动且稳健地从连续时间序列中裁剪出有效的 $I=0$ 静置窗口。
- [ ] 优化求解器 (Optimizer) 应当具备合理的惩罚项与物理边界约束，避免求解陷入物理不切实际的局部最优。
- [ ] 报告需以 JSON 输出被诊断出的 $R_{eq}$ 和漏电流大小。

## Extended References
- [产品逻辑设计文档](../../../产品设计/BAS design/L3-云端层级/C3.2-内短路诊断-P2D.md)
- [templates/python/p2d_isc_diagnosis.py](templates/python/p2d_isc_diagnosis.py)
