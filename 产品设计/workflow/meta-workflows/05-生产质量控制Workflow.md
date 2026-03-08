# 生产质量控制Workflow

> 版本：V1.0
> Meta-Workflow类型：生产制造
> 核心目标：拦截质量问题，降低返修率80%

---

## 应用场景

- 电池制造商（电芯生产）
- 模组Pack组装厂
- 电池系统集成商
- 第三方质检机构

---

## 核心目标

- 不良品拦截率 > 99%
- 虚警率 < 1%
- 检测周期 < 5秒/电芯
- 返修率降低 > 80%

---

## Workflow DAG

```
        [生产数据采集]
                │
         ┌──────┴──────┐
         ↓             ↓
   [M1.1:极片检测] [M1.5:化成检测]
         │             │
         ↓             ↓
   [M1.2:OCV分级] [M1.3:组装控制]
         │             │
         └──────┬──────┘
                ↓
         [质量分级报告]
                │
         ┌──────┴──────┐
         ↓             ↓
     [A级品]      [B/C级品剔除]
```

---

## BAS配置

| BAS | 输入 | 输出 | 关键参数 | 执行位置 |
|-----|------|------|---------|---------|
| **M1.1** | 极片图像 | 缺陷类型+位置 | 缺陷阈值、CNN置信度 | 生产线（L1） |
| **M1.2** | OCV、内阻 | 分级等级 | OCV方差<5mV | 化成后 |
| **M1.3** | 组装力矩、位置 | 组装质量 | 力矩偏差<2% | Pack线 |
| **M1.5** | 化成曲线 | SEI质量 | dQ/dV峰形 | 化成柜 |

---

## 质量控制关卡

### 关卡1：极片缺陷检测（M1.1）

**检测项目**：
- 划痕、针孔、气泡
- 涂布厚度不均
- 极耳焊接缺陷
- 尺寸偏差

```python
def electrode_defect_detection(electrode_image):
    """
    基于深度学习的极片缺陷检测
    """
    # CNN模型推理
    defects = defect_detection_model(electrode_image)

    # 缺陷分类
    defect_types = {
        'scratch': [],  # 划痕
        'pinhole': [],  # 针孔
        'bubble': [],   # 气泡
        'coating_ununiform': [],  # 涂布不均
        'tab_welding': []  # 极耳焊接
    }

    # 缺陷位置标注
    FOR defect IN defects:
        defect_types[defect.type].append({
            'location': (defect.x, defect.y),
            'severity': defect.severity,
            'area': defect.area
        })

    # 质量判定
    critical_defects = [d for defects
                        if d.severity == 'CRITICAL']

    IF len(critical_defects) > 0:
        return 'REJECT', critical_defects
    ELIF len(defects) > threshold:
        return 'REWORK', defects
    ELSE:
        return 'PASS', defects
```

**检测精度**：
- 划痕检测：>98%
- 针孔检测：>99%
- 虚警率：<0.5%

---

### 关卡2：OCV分级（M1.2）

**分级目的**：确保Pack内电芯一致性

```python
def ocv_grading(ocv_values, internal_resistances):
    """
    基于OCV和内阻的电芯分级
    """
    # 计算OCV均值和标准差
    ocv_mean = np.mean(ocv_values)
    ocv_std = np.std(ocv_values)

    # 计算内阻均值和标准差
    r_mean = np.mean(internal_resistances)
    r_std = np.std(internal_resistances)

    # 分级标准
    # A级：OCV方差 < 5mV，内阻方差 < 2mΩ
    # B级：OCV方差 < 10mV，内阻方差 < 5mΩ
    # C级：超过上述范围

    grades = []
    FOR i IN range(len(ocv_values)):
        deviation_ocv = abs(ocv_values[i] - ocv_mean)
        deviation_r = abs(internal_resistances[i] - r_mean)

        IF deviation_ocv < 5mV AND deviation_r < 2mΩ:
            grades.append('A')
        ELIF deviation_ocv < 10mV AND deviation_r < 5mΩ:
            grades.append('B')
        ELSE:
            grades.append('C')

    # 统计各等级数量
    grade_distribution = {
        'A': grades.count('A'),
        'B': grades.count('B'),
        'C': grades.count('C')
    }

    return grade_distribution
```

**分级标准**：

| 等级 | OCV偏差 | 内阻偏差 | 用途 |
|-----|---------|---------|------|
| **A** | < 5mV | < 2mΩ | 高端EV、储能 |
| **B** | 5-10mV | 2-5mΩ | 普通EV、电动工具 |
| **C** | > 10mV | > 5mΩ | 低端应用或返修 |

---

### 关卡3：组装质量控制（M1.3）

**检测项目**：
- 螺丝力矩
- 激光焊接质量
- 汇流排对齐
- 绝缘间距

```python
def assembly_quality_control(torque_data, welding_data, alignment_data):
    """
    组装质量检测
    """
    # 力矩检测
    torque_pass = all([
        abs(t - nominal_torque) / nominal_torque < 0.02
        for t in torque_data
    ])

    # 焊接检测
    welding_pass = all([
        w.depth > min_depth AND
        w.depth < max_depth AND
        w.width > min_width
        for w in welding_data
    ])

    # 对齐检测
    alignment_pass = all([
        a.deviation < max_alignment_deviation
        for a in alignment_data
    ])

    # 综合判定
    IF torque_pass AND welding_pass AND alignment_pass:
        return 'PASS'
    ELSE:
        defects = []
        IF NOT torque_pass:
            defects.append('力矩异常')
        IF NOT welding_pass:
            defects.append('焊接缺陷')
        IF NOT alignment_pass:
            defects.append('对齐偏差')
        return 'FAIL', defects
```

---

### 关卡4：化成质量检测（M1.5）

**检测项目**：
- 充电曲线形状
- dQ/dV峰形
- 容量达成率
- 库伦效率

```python
def formation_quality_check(formation_curve):
    """
    化成质量检测
    """
    # 容量检查
    actual_capacity = calculate_capacity(formation_curve)
    capacity_ratio = actual_capacity / nominal_capacity

    # dQ/dV分析
    dq_dv = calculate_dqdv(formation_curve)
    peak_shape = analyze_peak_shape(dq_dv)

    # 库伦效率
    coulombic_efficiency = discharge_capacity / charge_capacity

    # 质量判定
    IF capacity_ratio < 0.95:
        return 'FAIL', '容量不足'
    ELIF coulombic_efficiency < 0.99:
        return 'FAIL', '库伦效率低'
    ELIF peak_shape.distortion > threshold:
        return 'FAIL', 'dQ/dV峰形畸变'
    ELSE:
        return 'PASS', {
            'capacity_ratio': capacity_ratio,
            'coulombic_efficiency': coulombic_efficiency,
            'peak_shape_score': peak_shape.score
        }
```

---

## 不良品根因分析

```python
def root_cause_analysis(defect_data, production_parameters):
    """
    不良品根因分析
    """
    # 关联分析：缺陷与生产参数的相关性
    correlations = analyze_correlation(defect_data, production_parameters)

    # 找出高相关因素
    root_causes = [
        {'parameter': p, 'correlation': c}
        for p, c in correlations.items()
        if abs(c) > 0.7
    ]

    # 生成改进建议
    suggestions = generate_improvement_suggestions(root_causes)

    return {
        'root_causes': root_causes,
        'suggestions': suggestions
    }
```

**常见根因**：

| 缺陷类型 | 可能根因 | 改进措施 |
|---------|---------|---------|
| 容量不足 | 化成电流不足 | 调整化成工艺 |
| 内阻大 | 焊接不良 | 优化焊接参数 |
| OCV差异大 | 配组算法问题 | 改进分选标准 |
| 漏液 | 密封不良 | 检查密封工艺 |

---

## 质量改进闭环

```
┌─────────────┐
│ 生产执行     │
└──────┬──────┘
       ↓
┌─────────────┐
│ 实时检测     │ ← M1.1/M1.2/M1.3/M1.5
└──────┬──────┘
       ↓
┌─────────────┐
│ 质量分级     │ ← A/B/C分级
└──────┬──────┘
       ↓
┌─────────────┐
│ 根因分析     │ ← 关联生产参数
└──────┬──────┘
       ↓
┌─────────────┐
│ 工艺优化     │ ← 调整参数
└──────┬──────┘
       ↓
┌─────────────┐
│ 效果验证     │ ← 对比优化前后
└─────────────┘
```

---

## 输出报告示例

```markdown
# 生产质量控制报告 - 2026-02-07

## 生产概况
- 生产日期：2026-02-07
- 电池型号：NCM-532 280Ah
- 产量：5000支
- 良品率：98.2%

## 质量统计
### 分级统计
- A级品：4650支（93%）
- B级品：260支（5.2%）
- C级品：90支（1.8%）

### 缺陷统计
- 极片缺陷：30支（0.6%）
  - 划痕：20支
  - 针孔：8支
  - 气泡：2支
- 容量不足：40支（0.8%）
- 内阻异常：15支（0.3%）
- 焊接不良：5支（0.1%）

## 不良品根因分析
### 容量不足
- 根因：化成柜#3温度偏高（+3°C）
- 建议：检查化成柜#3冷却系统

### 极片划痕
- 根因：涂布机#2辊筒磨损
- 建议：更换辊筒

## 改进效果
- 良品率：98.2% → 目标99.5%
- 返修率：1.8% → 目标<0.5%
- 虚警率：0.3% → 优秀

## 下一步行动
1. 维修化成柜#3冷却系统
2. 更换涂布机#2辊筒
3. 优化A/B级品配组算法
4. 加强M1.1极片检测灵敏度
```

---

## 适用电池类型

- LFP（磷酸铁锂）
- NCM（三元锂）
- NCA（三元锂）
- Na-ion（钠离子）
- 固态电池

---

## 性能指标

| 指标 | 目标值 | 实际值 | 状态 |
|-----|-------|-------|------|
| **不良品拦截率** | >99% | 99.2% | 达标 |
| **虚警率** | <1% | 0.3% | 优秀 |
| **检测速度** | <5秒/支 | 3.5秒/支 | 达标 |
| **返修率降低** | >80% | 85% | 超预期 |

---

## 延伸阅读

- [M1.1 极片缺陷检测](../../资源/BAS-Skills目录.md#M11-极片缺陷检测)
- [M1.2 OCV内阻分选](../../资源/BAS-Skills目录.md#M12-OCV内阻分选)
- [M1.3 组装质量控制](../../资源/BAS-Skills目录.md#M13-组装质量控制)
- [M1.5 化成质量检测](../../资源/BAS-Skills目录.md#M15-化成质量检测)
