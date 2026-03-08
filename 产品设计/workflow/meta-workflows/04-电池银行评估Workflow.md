# 电池银行评估Workflow

> 版本：V1.0
> Meta-Workflow类型：梯次利用
> 核心目标：快速准确评估退役电池健康状态，降低误判率

---

## 应用场景

- 动力电池退役评估（电动车、储能）
- 梯次利用筛选（储能、备用电源）
- 电池回收决策（材料回收）
- 二手电池交易评估

---

## 核心目标

- SOH评估误差 < 3%
- 梯次分级准确率 > 95%
- 评估时间 < 30分钟/批次
- 误判率 < 5%

---

## Workflow DAG

```
      [退役电池入库]
             │
             ↓
      [快速SOH筛选]
             │
      ┌──────┴──────┐
      ↓             ↓
  [SOH>70%]     [SOH≤70%]
      │             │
      ↓             ↓
[C3.7:ICA分析] [I5.6:回收决策]
      │             │
      ↓             ↓
[C3.8:EIS分析]  [材料回收]
      │
      ↓
[C3.3:RUL预测]
      │
      ↓
 [I5.6:梯次分级]
      │
      ↓
  [定价建议]
```

---

## BAS配置

| BAS | 输入 | 输出 | 关键参数 | 执行时间 |
|-----|------|------|---------|---------|
| **快速SOH筛选** | OCV、内阻、外观 | SOH初步估计 | 阈值SOH=70% | 5分钟 |
| **C3.7** | 充放电曲线 | dQ/dV峰值位置 | 峰值左移量 | 10分钟 |
| **C3.8** | EIS谱图 | 内阻、扩散系数 | 等效电路拟合 | 15分钟 |
| **C3.3** | SOH历史 | RUL（月） | 退化模型 | 5分钟 |
| **I5.6** | SOH、RUL、ICA/EIS | 梯次分级+定价 | 分级标准 | 2分钟 |

---

## 梯次分级标准

| 等级 | SOH范围 | RUL | ICA特征 | EIS内阻 | 应用场景 | 定价系数 |
|-----|---------|-----|---------|---------|---------|---------|
| **A级** | SOH ≥ 90% | > 60个月 | 峰值左移<30mV | <1.2倍新电池 | 储能电站 | 0.5-0.6 |
| **B级** | 80% ≤ SOH < 90% | 36-60个月 | 峰值左移30-60mV | 1.2-1.5倍 | 工商业储能 | 0.3-0.5 |
| **C级** | 70% ≤ SOH < 80% | 12-36个月 | 峰值左移60-100mV | 1.5-2.0倍 | 备用电源 | 0.1-0.3 |
| **D级** | SOH < 70% | < 12个月 | 峰值严重畸变 | >2.0倍 | 材料回收 | 0.05-0.1 |

---

## 评估流程

### 第1步：快速筛选（5分钟）

```python
def quick_screening(ocv, internal_resistance, appearance):
    """
    快速筛选，剔除明显不合格的电池
    """
    # OCV检测
    IF ocv < 3.0V OR ocv > 4.3V:
        return 'REJECT', 'OCV异常'

    # 内阻检测
    IF internal_resistance > 2 * nominal_resistance:
        return 'REJECT', '内阻过大'

    # 外观检测
    IF appearance.has_leakage OR appearance.has_deformation:
        return 'REJECT', '外观缺陷'

    # 快速SOH估计（基于OCV和内阻）
    soh_estimate = estimate_soh(ocv, internal_resistance)

    IF soh_estimate < 70%:
        return 'RECYCLE', 'SOH过低，直接回收'
    ELSE:
        return 'PROCEED', '进入详细分析'
```

### 第2步：ICA增量分析（10分钟）

```python
def ica_analysis(charging_curve):
    """
    ICA增量分析，检测析锂和容量衰减
    """
    # 计算dQ/dV曲线
    dq_dv = calculate_dqdv(charging_curve)

    # 识别特征峰
    peaks = identify_peaks(dq_dv)

    # 分析峰位左移量（析锂指标）
    peak_shift = peaks.main_peak_voltage - nominal_peak_voltage

    # 分析峰高衰减（容量损失指标）
    peak_height_ratio = peaks.main_peak_height / nominal_peak_height

    # 评估析锂程度
    IF peak_shift > 100mV:
        plating_status = 'SEVERE'
    ELIF peak_shift > 50mV:
        plating_status = 'MODERATE'
    ELSE:
        plating_status = 'NONE'

    return {
        'peak_shift': peak_shift,
        'peak_height_ratio': peak_height_ratio,
        'plating_status': plating_status
    }
```

### 第3步：EIS阻抗谱分析（15分钟）

```python
def eis_analysis(eis_spectrum):
    """
    EIS阻抗谱分析，检测内阻增加和老化机制
    """
    # 拟合等效电路模型
    fitted_model = fit_equivalent_circuit(eis_spectrum)

    # 提取参数
    parameters = {
        'ohmic_resistance': fitted_model.R0,  # 欧姆内阻
        'charge_transfer_resistance': fitted_model.Rct,  # 电荷传递电阻
        'diffusion_coefficient': fitted_model.Warburg  # 扩散系数
    }

    # 评估老化程度
    IF parameters['ohmic_resistance'] > 2 * nominal_R0:
        aging_mechanism = 'SEMI'  # SEI膜增长
    ELIF parameters['diffusion_coefficient'] < 0.5 * nominal_D:
        aging_mechanism = 'LITHIUM_LOSS'  # 锂损失
    ELSE:
        aging_mechanism = 'MIXED'  # 混合老化

    return {
        'resistance_ratio': parameters['ohmic_resistance'] / nominal_R0,
        'aging_mechanism': aging_mechanism
    }
```

### 第4步：RUL预测（5分钟）

```python
def rul_prediction(soh, degradation_rate, stress_history):
    """
    剩余寿命预测
    """
    # 基于退化率的外推预测
    rul_months = (soh - 80%) / degradation_rate

    # 考虑使用应力的调整
    stress_factor = calculate_stress_factor(stress_history)
    adjusted_rul = rul_months / stress_factor

    return adjusted_rul
```

### 第5步：梯次分级与定价（2分钟）

```python
def cascading_classification(soh, rul, ica_result, eis_result):
    """
    综合分级与定价
    """
    # 计算综合得分
    score = 0
    score += (soh / 100) * 0.4
    score += (rul / 60) * 0.3
    score += (1 - ica_result['peak_shift'] / 100mV) * 0.15
    score += (1 / eis_result['resistance_ratio']) * 0.15

    # 分级
    IF score >= 0.9:
        grade = 'A'
        price_factor = 0.55
    ELIF score >= 0.75:
        grade = 'B'
        price_factor = 0.4
    ELIF score >= 0.6:
        grade = 'C'
        price_factor = 0.2
    ELSE:
        grade = 'D'
        price_factor = 0.08

    # 定价（基于同号新电池价格）
    new_battery_price = get_market_price(battery_type)
    cascading_price = new_battery_price * price_factor * (soh / 100)

    return {
        'grade': grade,
        'score': score,
        'price': cascading_price,
        'recommended_application': get_application(grade)
    }
```

---

## 输出报告示例

```markdown
# 退役电池评估报告 - 批次#20260207-001

## 批次信息
- 电池来源：XX网约车公司
- 电池类型：NCM-532
- 退役时间：2026-01-15
- 服役年限：4年
- 评估时间：2026-02-07

## 评估统计
- 总数量：500个电池包
- A级品：180个（36%）
- B级品：220个（44%）
- C级品：60个（12%）
- D级品（回收）：40个（8%）

## A级品详情
- SOH范围：90%-95%
- 平均RUL：65个月
- 建议应用：储能电站
- 建议定价：新电池价格的55%

## B级品详情
- SOH范围：85%-90%
- 平均RUL：48个月
- 建议应用：工商业储能
- 建议定价：新电池价格的40%

## C级品详情
- SOH范围：70%-85%
- 平均RUL：24个月
- 建议应用：备用电源
- 建议定价：新电池价格的20%

## D级品（回收）
- SOH < 70%
- 建议直接材料回收
- 预计回收价值：5000元/吨

## 典型案例分析（A级品#001）
### ICA分析
- 峰位左移：25mV（优秀）
- 峰高比：0.92（轻微衰减）

### EIS分析
- 内阻比：1.15（略高于新电池）
- 老化机制：SEI膜增长为主

### RUL预测
- 预计剩余寿命：68个月
- 退化率：0.22%/月

### 综合评分
- 总分：0.93
- 定价：2200元（新电池5000元）
```

---

## 适用电池类型

- NCM（三元锂）- 最适用
- LFP（磷酸铁锂）
- NCA（三元锂）

---

## 质量保证

- 评估一致性：同一批次重复评估误差 < 2%
- 溯源性：每个电池建立唯一ID，记录全生命周期
- 质保期：A级品质保2年，B级品质保1年

---

## 延伸阅读

- [C3.7 ICA增量分析](../../资源/BAS-Skills目录.md#C37-ICA增量分析)
- [C3.8 EIS阻抗谱分析](../../资源/BAS-Skills目录.md#C38-EIS阻抗谱分析)
- [C3.3 RUL寿命预测](../../资源/BAS-Skills目录.md#C33-RUL寿命预测)
- [I5.6 梯次利用分级](../../资源/BAS-Skills目录.md#I56-梯次利用分级)
