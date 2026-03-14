---
name: A4.3-储能场站智能巡检
description: |
  基于计算机视觉和物联网传感器的储能场站智能巡检系统。

  该Skill通过无人机/机器人巡检、热成像分析、声音识别等多维度
  数据采集，实现储能场站的自动化、智能化巡检。

  核心功能：
  - 电池外观缺陷检测（鼓包、漏液、变形）
  - 热成像异常检测（热点、温差）
  - 设备运行状态识别（仪表读数、指示灯）
  - 安全隐患识别（烟雾、火苗、杂物）
  - 巡检路径优化
  - 缺陷自动分级与告警

  支持多种巡检方式：
  - 无人机巡检（ aerial inspection ）
  - 地面机器人巡检（ ground robot ）
  - 固定摄像头巡检（ fixed camera ）
  - 手持终端巡检（ handheld device ）

version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Semi-Solid, Solid-State]
tier: L4
category: 运维工具
deployment: 移动APP/边缘计算设备
compute_requirement: Cloud GPU / Edge AI Module
pricing: Enterprise
tags: [inspection, computer-vision, thermal-imaging, predictive-maintenance]
visibility: public
---

## 功能概述

储能场站智能巡检系统通过AI视觉技术替代传统人工巡检，提高巡检效率和准确性。

### 核心特性

1. **多模态数据采集**
   - 可见光图像采集
   - 热成像温度检测
   - 声音信号分析
   - 气体传感器数据

2. **AI智能识别**
   - 电池外观缺陷检测
   - 热斑异常识别
   - 设备状态识别
   - 安全隐患检测

3. **智能路径规划**
   - 基于风险的热点巡检
   - 最短路径优化
   - 多机协同巡检

4. **缺陷管理系统**
   - 缺陷自动分级
   - 维修工单生成
   - 缺陷趋势分析

## 算法原理

### 1. 目标检测算法

使用YOLOv8进行目标检测：

```python
model = YOLOv8n-Inspection.pt
classes = [
    'battery_module', 'thermal_hotspot', 'smoke',
    'fire', 'leakage', 'deformation', 'indicator'
]
```

### 2. 热成像分析

热异常检测算法：

```
ΔT = T_max - T_avg
if ΔT > threshold:
    alert_level = classify_by_delta(ΔT)
```

温差分级标准：
- 正常：ΔT < 5°C
- 注意：5°C ≤ ΔT < 10°C
- 警告：10°C ≤ ΔT < 15°C
- 严重：ΔT ≥ 15°C

### 3. 缺陷检测模型

#### 电池鼓包检测

```python
def detect_bulge(image):
    # 1. 边缘检测
    edges = canny(image)

    # 2. 轮廓提取
    contours = find_contours(edges)

    # 3. 形状分析
    for contour in contours:
        area = contour_area(contour)
        perimeter = contour_perimeter(contour)
        circularity = 4 * π * area / perimeter²

        # 鼓包特征：圆形凸起
        if circularity > 0.8 and is_convex(contour):
            return True, contour
    return False, None
```

#### 漏液检测

```python
def detect_leakage(image):
    # HSV颜色空间检测
    hsv = rgb_to_hsv(image)

    # 检测异常颜色（电解液颜色）
    mask = (
        (hsv.hue in [180, 220]) &  # 蓝绿色范围
        (hsv.saturation > 0.3) &
        (hsv.value > 0.2)
    )

    if mask.sum() > threshold:
        return True, mask
    return False, None
```

### 4. 声音异常检测

使用MFCC特征 + LSTM检测异常声音：

```python
def detect_audio_anomaly(audio):
    # 提取MFCC特征
    mfcc = extract_mfcc(audio, n_mfcc=13)

    # LSTM模型检测
    model = AudioAnomalyLSTM()
    prediction = model.predict(mfcc)

    if prediction > 0.8:  # 异常置信度
        return True, classify_anomaly_type(audio)
    return False, None
```

## 参数说明

### 巡检配置参数

| 参数名 | 类型 | 范围 | 说明 |
|--------|------|------|------|
| inspection_mode | string | - | 巡检模式：drone/robot/camera |
| flight_altitude | float | 5-50 m | 无人机飞行高度 |
| flight_speed | float | 1-10 m/s | 飞行速度 |
| image_resolution | int | 1-20 MP | 图像分辨率 |
| thermal_sensitivity | float | 0.05-0.1°C | 热成像灵敏度 |
| detection_threshold | float | 0.5-0.95 | 检测置信度阈值 |
| overlap_ratio | float | 0.3-0.7 | 图像重叠率 |

### 检测阈值参数

| 参数名 | 类型 | 范围 | 说明 |
|--------|------|------|------|
| temp_diff_warning | float | 5-15°C | 温差警告阈值 |
| temp_diff_critical | float | 10-20°C | 温差严重阈值 |
| deformation_threshold | float | 1-5 mm | 变形检测阈值 |
| gas_leak_threshold | float | 10-100 ppm | 气体泄漏阈值 |

### 输出结果

| 参数名 | 类型 | 说明 |
|--------|------|------|
| defects_found | array | 检测到的缺陷列表 |
| defect_locations | array | 缺陷位置坐标 |
| severity_levels | array | 缺陷严重程度 |
| thermal_map | object | 热成像数据 |
| inspection_route | array | 巡检路径 |
| recommended_actions | array | 建议处理措施 |

## When to use this skill

### 场景1：日常例行巡检
- 频率：每日/每周
- 目标：及时发现潜在问题
- 内容：外观检查、温度检测、设备状态

### 场景2：故障后巡检
- 频率：事件触发
- 目标：评估故障影响范围
- 内容：重点区域详细检查

### 场景3：预防性巡检
- 频率：每月/每季
- 目标：深度检查、趋势分析
- 内容：全面检测、性能评估

### 场景4：应急巡检
- 频率：告警触发
- 目标：快速定位问题
- 内容：高风险区域优先巡检

## 限制与约束

### 环境约束
- 风速：<6级（无人机）
- 温度：-20~50°C
- 湿度：<90% RH
- 光照：>100 lux

### 设备约束
- 无人机续航：20-40分钟
- 相机视场角：60-120°
- 热像仪分辨率：160×120 ~ 640×480

### 检测精度约束
- 小目标检测：>20×20 pixels
- 缺陷分类准确率：>90%
- 定位误差：<0.5m

## 部署要求

### 硬件要求
- **边缘设备**：NVIDIA Jetson Orin, Intel Core i7 + GPU
- **无人机**：DJI Mavic 3 Enterprise / DJI Matrice 300
- **热像仪**：FLIR / DJI H20T

### 软件依赖
```python
torch>=2.0.0
torchvision>=0.15.0
ultralytics>=8.0.0
opencv-python>=4.7.0
numpy>=1.24.0
scipy>=1.10.0
```

### API接口
```python
# REST API
POST /api/v1/inspection/start
GET /api/v1/inspection/status/{task_id}
POST /api/v1/inspection/upload
GET /api/v1/inspection/report/{task_id}

# WebSocket
WS /api/v1/inspection/realtime
```

## 缺陷分级标准

### 1级 - 正常
- 无明显异常
- 温差<5°C
- 设备运行正常

### 2级 - 注意
- 轻微外观异常
- 温差5-10°C
- 需要持续关注

### 3级 - 警告
- 明显外观缺陷
- 温差10-15°C
- 需要计划维修

### 4级 - 严重
- 严重外观缺陷
- 温差>15°C
- 需要立即处理

### 5级 - 危急
- 安全隐患（漏液、冒烟）
- 温差>20°C或有明火
- 需要紧急停机

## 更新日志

### v1.0.0 (2025-03-08)
- 初始版本发布
- 支持可见光+热成像检测
- 无人机巡检功能
- 缺陷自动分级
- 巡检报告自动生成

## 许可证

ASGARD Enterprise License - See LICENSE.md for details

## 联系方式

- 文档：https://docs.asgard.ai/bas/skills/a4.3
- 支持：support@asgard.ai
- GitHub：https://github.com/ASGARD-AI/bas-skills
