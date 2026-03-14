---
name: A4.5-储能运维报告自动化
description: |
  自动生成储能场站运维分析报告，包括日报、周报、月报和年报。

  该Skill自动采集BMS/EMS数据，进行统计分析，生成包含以下内容的报告：
  - 运行概况总结
  - 性能指标分析
  - 故障与告警统计
  - 经济效益分析
  - 设备健康评估
  - 维护建议

  支持多种输出格式：PDF、Excel、Word、HTML。

version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Semi-Solid, Solid-State]
tier: L4
category: 运维工具
deployment: 后台服务
compute_requirement: <100MHz
pricing: Enterprise
tags: [report-generation, data-analytics, automation, pdf-generation]
visibility: public
---

## 功能概述

自动报告生成系统替代人工编写报告，提高运维效率，保证数据准确性。

## When to use this skill

Use this skill when:
- 需要定期导出标准化的运维日报、周报、月报以便存档。
- 场站运维由于数据量庞大，人工统计耗费过多精力且易出错。
- 需要通过不同格式（PDF, Excel, Word）向不同部门（技术/财务/管理）汇报。

### 核心特性

1. **多周期报告**
   - 日报（Daily Report）
   - 周报（Weekly Report）
   - 月报（Monthly Report）
   - 年报（Annual Report）

2. **多维度分析**
   - 运行指标统计
   - 性能趋势分析
   - 故障分析
   - 经济效益分析

3. **智能洞察**
   - 异常检测
   - 趋势预测
   - 对比分析
   - 根因分析

4. **多格式输出**
   - PDF（用于打印/存档）
   - Excel（用于二次分析）
   - Word（用于编辑）
   - HTML（用于在线查看）

## 报告模板

### 日报模板
1. **运行概况**
   - 充放电量统计
   - 运行时长
   - 能量效率
   - 峰值功率

2. **告警统计**
   - 告警级别分布
   - 告警时长统计
   - Top 10告警

3. **经济指标**
   - 今日收益
   - 度电成本
   - 辅助服务收益

4. **设备状态**
   - 电池簇SOC/SOH
   - 温度分布
   - 健康指数

### 周报/月报模板
1. **趋势分析**
   - 充放电量趋势
   - 收益趋势
   - SOH衰减趋势

2. **对比分析**
   - 同比/环比
   - 与预测值对比
   - 与行业标杆对比

3. **故障分析**
   - 故障分类统计
   - MTBF/MTTR
   - 故障根因分析

4. **维护建议**
   - 需要关注的设备
   - 预防性维护建议
   - 备件更换建议

### 年报模板
1. **年度总结**
   - 关键指标达成情况
   - 重大事件回顾
   - 投资收益分析

2. **性能评估**
   - 全年性能曲线
   - 可靠性分析
   - 生命周期评估

3. **经济分析**
   - 全年收益汇总
   - 投资回报率
   - 下一年度预测

4. **改进建议**
   - 系统优化建议
   - 升级改造建议
   - 运营管理建议

## 数据处理流程

```
数据采集 → 数据清洗 → 统计分析 → 报告生成 → 自动发送
   ↓           ↓          ↓          ↓          ↓
 InfluxDB   异常处理   算法引擎   模板引擎   Email/FTP
```

## 算法实现

### 1. 数据聚合
```python
def aggregate_data(period, start_time, end_time):
    query = f"""
    SELECT
        mean(power) as avg_power,
        max(power) as peak_power,
        sum(energy) as total_energy
    FROM battery_metrics
    WHERE time >= '{start_time}' AND time <= '{end_time}'
    GROUP BY time({period})
    """
    return influxdb.query(query)
```

### 2. 趋势分析
```python
def analyze_trend(data):
    # 线性回归
    x = np.arange(len(data))
    coeffs = np.polyfit(x, data, 1)
    trend = coeffs[0]

    # 判断趋势
    if trend > threshold:
        return '上升'
    elif trend < -threshold:
        return '下降'
    else:
        return '平稳'
```

### 3. 异常检测
```python
def detect_anomalies(data):
    mean = np.mean(data)
    std = np.std(data)

    anomalies = []
    for i, value in enumerate(data):
        z_score = abs(value - mean) / std
        if z_score > 3:  # 3σ原则
            anomalies.append((i, value))

    return anomalies
```

## 报告生成配置

### 调度配置
```yaml
report_schedules:
  daily:
    time: "08:00"
    format: ["pdf", "html"]
    recipients: ["operator@asgard.ai"]

  weekly:
    day: "Monday"
    time: "09:00"
    format: ["pdf", "excel"]
    recipients: ["manager@asgard.ai"]

  monthly:
    day: 1
    time: "10:00"
    format: ["pdf", "word", "excel"]
    recipients: ["director@asgard.ai"]
```

### 报告样式配置
```yaml
style:
  theme: "professional"
  logo: "/assets/logo.png"
  primary_color: "#1890ff"
  font_family: "Arial"
  page_size: "A4"
  margin: "2cm"
```

## 部署要求

### 软件依赖
```python
python>=3.9
pandas>=1.5.0
numpy>=1.23.0
matplotlib>=3.6.0
reportlab>=3.6.0
openpyxl>=3.0.0
python-docx>=0.8.11
jinja2>=3.1.0
```

### 系统资源
- **CPU**: 2核心+
- **内存**: 4GB+
- **存储**: 50GB+
- **网络**: 稳定连接

## 许可证

ASGARD Enterprise License - See LICENSE.md for details
