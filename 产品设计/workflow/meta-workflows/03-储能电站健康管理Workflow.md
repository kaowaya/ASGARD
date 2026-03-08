# 储能电站健康管理Workflow

> 版本：V1.0
> Meta-Workflow类型：资产管理
> 核心目标：全生命周期健康管理，最大化电站收益

---

## 应用场景

- 工商业储能（工厂、商场、数据中心）
- 电网侧储能（调频、调峰、备用）
- 户用储能（光储一体）
- 集中式储能电站

---

## 核心目标

- SOH预测误差 < 5%
- RUL预测误差 < 10%
- 故障预警提前量 > 1个月
- 电站收益率提升 > 15%

---

## Workflow DAG

```
         [全量数据采集]
                │
         ┌──────┴──────┐
         ↓             ↓
   [C3.5:SOH集成]  [C3.3:RUL预测]
         │             │
         ↓             ↓
   [C3.1:SOS诊断]  [I5.5:资产评估]
         │             │
         └──────┬──────┘
                ↓
         [运维决策引擎]
                │
         ┌──────┴──────┐
         ↓             ↓
   [运维建议]    [财务分析]
```

---

## BAS配置

| BAS | 输入 | 输出 | 关键参数 | 执行频率 |
|-----|------|------|---------|---------|
| **C3.5** | 充放电曲线、温度 | SOH值、容量衰减率 | 集成算法权重 | 每周 |
| **C3.3** | SOH历史、工况数据 | RUL（剩余寿命） | 退化模型参数 | 每月 |
| **C3.1** | 全量历史数据 | 异常电芯列表 | 基因演化阈值 | 每日 |
| **I5.5** | SOH、RUL、电价 | 资产价值、优化建议 | NPV、IRR计算 | 每月 |

---

## 运维决策引擎

```python
def maintenance_decision(soh, rul, sos_results, asset_value):
    # 健康状态评估
    IF soh < 80%:
        urgency = "HIGH"
        action = "建议更换"
    ELIF soh < 90%:
        urgency = "MEDIUM"
        action = "密切关注"
    ELSE:
        urgency = "LOW"
        action = "正常运行"

    # SOS异常电芯识别
    abnormal_cells = [cell for cell in sos_results
                     if cell.anomaly_score > threshold]

    # 资产价值评估
    residual_value = asset_value * (soh / 100) * (rul / design_life)

    return {
        'urgency': urgency,
        'action': action,
        'abnormal_cells': abnormal_cells,
        'residual_value': residual_value,
        'recommendations': generate_recommendations()
    }
```

---

## 健康状态分级

| SOH范围 | 状态等级 | 运维策略 | 建议动作 |
|---------|---------|---------|---------|
| SOH ≥ 95% | 优秀 | 正常运行 | 继续监控 |
| 90% ≤ SOH < 95% | 良好 | 正常运行 | 继续监控 |
| 85% ≤ SOH < 90% | 注意 | 增加监控频率 | 检查异常电芯 |
| 80% ≤ SOH < 85% | 预警 | 优化充放电策略 | 准备维护计划 |
| SOH < 80% | 警报 | 限制充放电功率 | 安排更换 |

---

## 资产价值评估模型

```python
def asset_valuation(soh, rul, electricity_price, peak_shaving_revenue):
    """
    储能电站资产价值评估

    输入：
    - soh: 当前健康状态（%）
    - rul: 剩余寿命（月）
    - electricity_price: 电价（元/kWh）
    - peak_shaving_revenue: 削峰填谷收益（元/月）

    输出：
    - npv: 净现值
    - irr: 内部收益率
    - residual_value: 剩余价值
    """

    # 剩余价值计算
    residual_value = initial_investment * (soh / 100) * (rul / design_life)

    # 未来收益预测（考虑容量衰减）
    future_revenue = 0
    FOR month IN range(1, rul+1):
        # 每月衰减率
        degradation_rate = (100 - soh) / age_in_months
        month_soh = soh - degradation_rate * month

        # 该月收益（与SOH成正比）
        month_revenue = peak_shaving_revenue * (month_soh / 100)
        future_revenue += month_revenue / (1 + discount_rate)**month

    # 净现值
    npv = residual_value + future_revenue - maintenance_cost

    # 内部收益率
    irr = calculate_irr(cash_flows)

    return {
        'residual_value': residual_value,
        'npv': npv,
        'irr': irr,
        'recommendation': 'continue' if irr > 0.08 else 'replace'
    }
```

---

## 输出报告示例

```markdown
# 储能电站健康管理报告 - 2026年2月

## 电站概况
- 电站名称：XX工业园区储能站
- 投运时间：2023-06-01
- 电池类型：LFP 280Ah
- 额定容量：10MWh

## 健康状态评估
### 整体SOH
- 当前SOH：87.3%
- 衰减率：0.23%/月
- 预计寿命：剩余48个月

### RUL预测
- 剩余寿命：48个月（4年）
- 置信区间：[42, 54]个月（90%置信度）
- 终止条件：SOH降至80%

### 异常电芯诊断（SOS）
- 异常电芯数量：12个
- 最严重异常：3号模组5号电芯
  - 漏电流：5mA（正常<2mA）
  - 本征衰减率：1.8x正常值
  - 建议：3个月内更换

## 资产价值评估
- 剩余价值：680万元
- NPV（净现值）：520万元
- IRR（内部收益率）：8.5%

## 运维建议
1. 1个月内更换3号模组5号电芯
2. 优化充放电策略，降低深度放电次数
3. 增加日常巡检频率至每周1次
4. 关注夏季高温对SOH的影响

## 收益优化
- 建议参与峰谷套利（电价差>0.8元/kWh）
- 建议提供调频服务（辅助服务市场）
- 预计年收益提升：15%
```

---

## 收益优化策略

### 1. 峰谷套利优化

```python
def peak_shaving_optimization(soh, electricity_price_curve):
    """
    基于SOH和电价曲线的充放电优化
    """
    # 充电时段：谷电时段（电价最低）
    charging_hours = [hour for hour in range(24)
                     if electricity_price_curve[hour] < threshold]

    # 放电时段：峰电时段（电价最高）
    discharging_hours = [hour for hour in range(24)
                        if electricity_price_curve[hour] > threshold]

    # 考虑SOH衰减，调整充放电深度
    max_dod = 0.9 * (soh / 100)  # SOH越低，DOD越小

    return {
        'charging_schedule': charging_hours,
        'discharging_schedule': discharging_hours,
        'max_dod': max_dod
    }
```

### 2. 调频服务策略

```python
def frequency_regulation_strategy(soh, grid_frequency):
    """
    频率调节服务
    """
    # SOH越高，提供更多调频服务
    IF soh > 90%:
        power_capacity = rated_power * 0.5  # 50%功率参与调频
    ELIF soh > 80%:
        power_capacity = rated_power * 0.3  # 30%功率参与调频
    ELSE:
        power_capacity = rated_power * 0.1  # 10%功率参与调频

    return power_capacity
```

---

## 适用电池类型

- LFP（磷酸铁锂）- 最适用
- NCM（三元锂）
- Na-ion（钠离子）

---

## 延伸阅读

- [C3.5 SOH集成估计](../../资源/BAS-Skills目录.md#C35-SOH集成估计)
- [C3.3 RUL寿命预测](../../资源/BAS-Skills目录.md#C33-RUL寿命预测)
- [C3.1 SOS内短路诊断](../../资源/BAS-Skills目录.md#C31-SOS内短路诊断)
- [I5.5 资产价值评估](../../资源/BAS-Skills目录.md#I55-资产价值评估)
