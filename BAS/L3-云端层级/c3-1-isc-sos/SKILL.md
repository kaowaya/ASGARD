---
name: C3.1-内短路诊断-SOS
description: >
  基于基因图谱 (Safety Gene) 特征提取原则的早期内短路 (ISC) 诊断算法。
  从电压香农熵、温升梯度、自放电等维度，使用无监督打分制评估短路风险。
version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Semi-Solid, Solid-State]
tier: L3
compute_requirement: >2GB RAM (Pandas DataFrame)
pricing: Premium
tags:
  - internal-short-circuit
  - safety-gene
  - anomaly-detection
visibility: public
---

# C3.1 内短路诊断 - SOS (Safety Gene)

## When to use this skill

Use this skill when:
- 想要在热失控发生的 **30~60天前** 就能筛选出高风险的“潜在内短路”电芯。
- 只有常规的车联网时序数据 (V, I, T, SOC)，没有高精度的电化学检测设备。
- 追求高鲁棒性和强业务解释性（发现异常可以直接解释是压降、温升还是自放电导致的），而不像黑盒子深度学习模型。

**前置依赖**:
- 本算法强烈依赖连续平滑的时序特征，**必须先经过基于 `C3.0-云端异常清洗数据流` 的过滤处理**。如果直接灌入车联网脏数据，将导致香农熵 (Shannon Entropy) 剧烈误报。

## Quick Start
1. **预处理**: 使用 C3.0 生成特征矩阵 `clean_features.csv`。
2. **运行基因诊断**:
   ```bash
   python templates/python/sos_diagnosis.py \
       --input ../c3-0-data-pipeline/data_samples/output/clean_features.csv \
       --output output/sos_report.json
   ```

## Decisions Points
- **误报与漏报权衡**: 对于运营车辆而言，漏报往往比偶尔一次误报代价更惨重（起火）。基因权重的配置需要通过大量正常车辆的统计基线（Z-Score 或 99% 分位数）来确定，不要使用定死的常数阈值。
- **电芯一致性 (Cell Consistency)**: 云端最好输入所有单体(Cell)的数据。如果有 100 串电芯，本算法会计算 100 串香农熵的总离散度。单串异常更容易被捕获。这里为了示例，采用单一电芯的时序分析。

## How it works
它类比生物学的致病基因，将“短路”拆解为多个子特征图谱：
1. **g1 (电压香农熵)**: 正常情况充电或放电，电压变化有规律且分散，熵大。如果某个电芯发生微短路漏电，它会始终趋向于一个较低的同质电压，分布变窄，熵下降。
2. **g2 (温度特征 dT_dt)**: 内短路发热会导致不正常的 `dT/dt` 偏高。
3. **g3 (表观自放电 dQ/dt)**: 相同满充条件下静置，发现压降特别大（隐含自放电消耗）。
4. **决策融合**: 采用层次分析法或简单的加权积分，将 $g_1 \dots g_n$ 输出一个 `0~1` 的综合 Risk Score。

## Quality Checklist
- [ ] 确保香农熵的计算是在合理分箱 (Binning) 策略下进行的。如果直接使用连续浮点数算概率密度会退化。
- [ ] 代码具备无状态特征，能直接返回 JSON 供大屏分析或上游决策树调用。

## Extended References
- [templates/python/sos_diagnosis.py](templates/python/sos_diagnosis.py)
