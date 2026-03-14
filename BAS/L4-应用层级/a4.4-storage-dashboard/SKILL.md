---
name: A4.4-储能大屏
description: |
  储能场站实时监控大屏系统，提供全景可视化监控。

  该Skill通过WebSocket实时数据推送，展示储能场站的：
  - 实时功率流向与能量流
  - 电池簇SOC/SOH状态
  - 关键参数趋势曲线
  - 告警信息与事件日志
  - 经济效益分析
  - 碳减排统计

  支持多屏联动、响应式布局，适配4K大屏显示。

version: "1.0.0"
author: ASGARD
battery_types: [LFP, NCM, Na-ion, Semi-Solid, Solid-State]
tier: L4
category: 运维工具
deployment: Web Dashboard
compute_requirement: Cloud
pricing: Pro / Enterprise
tags: [visualization, dashboard, real-time-monitoring, data-analytics]
visibility: public
---

## 功能概述

储能大屏提供直观的可视化界面，帮助运维人员实时掌握储能场站运行状态。

## When to use this skill

Use this skill when:
- 需要对场站进行全景式实时监控，特别是 4K 大屏展示环境。
- 运维团队需要实时洞察功率流向、SOC/SOH 分布及异常告警。
- 向业主或管理者展示场站运行成果与经济效益。

### 核心特性

1. **实时监控**
   - 功率流向动态展示
   - 电池状态实时更新
   - 告警信息即时推送

2. **数据可视化**
   - 趋势曲线图
   - 能量流桑基图
   - 热力图展示
   - 3D场站模型

3. **多维度分析**
   - 经济效益分析
   - 性能指标统计
   - 对比分析
   - 预测曲线

4. **告警管理**
   - 实时告警列表
   - 告警级别分类
   - 告警统计图表
   - 快速跳转定位

## 技术架构

### 前端技术栈
- React 18 + TypeScript
- ECharts 5 / D3.js
- WebSocket (Socket.io)
- Ant Design Pro

### 后端技术栈
- FastAPI / Node.js
- WebSocket Server
- InfluxDB (时序数据库)
- Redis (缓存)

### 数据流架构
```
BMS/EMS → MQTT Broker → API Gateway → WebSocket → Frontend
                ↓
           InfluxDB
```

## 仪表盘布局

### 主屏布局
```
+------------------------------------------+
|              Header: 场站名称、时间         |
+------------------+-----------------------+
|  场站3D模型       |      功率流向图        |
|                  |                       |
+------------------+-----------------------+
|   电池簇SOC/SOH  |    告警列表  | 经济指标|
|                  |             |        |
+------------------+-----------------------+
|        趋势曲线图（SOC、功率、温度）        |
|                                           |
+------------------+------------------------+
|   设备状态树      |    统计卡片   | 日志   |
+------------------------------------------+
```

## 关键指标

### 运行指标
- 当前功率（MW）
- 今日充放电量（MWh）
- 实时效率（%）
- 可用容量（MWh）

### 经济指标
- 今日收益（元）
- 累计收益（元）
- 度电成本（元/kWh）
- 投资回收率（%）

### 性能指标
- 平均SOH（%）
- 平均SOC（%）
- 最高温度（°C）
- 最大温差（°C）

### 环保指标
- 今日减排（吨CO2）
- 累计减排（吨CO2）
- 相当于植树（棵）

## API接口

### WebSocket接口
```javascript
// 连接WebSocket
const ws = new WebSocket('wss://api.asgard.ai/dashboard/ws');

// 订阅实时数据
ws.send(JSON.stringify({
  action: 'subscribe',
  topics: ['power', 'soc', 'soh', 'alarms']
}));

// 接收数据更新
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  updateDashboard(data);
};
```

### REST API
```python
# 获取历史数据
GET /api/v1/dashboard/history?start=<timestamp>&end=<timestamp>

# 获取统计数据
GET /api/v1/dashboard/statistics?period=day

# 获取告警列表
GET /api/v1/dashboard/alarms?level=warning
```

## 部署要求

### 服务器配置
- **CPU**: 4核心+
- **内存**: 8GB+
- **存储**: 100GB+ SSD
- **网络**: 100Mbps+

### 显示设备
- **分辨率**: 1920×1080 (最低) / 3840×2160 (推荐)
- **刷新率**: 60Hz
- **尺寸**: 55"以上

## 许可证

ASGARD Pro License - See LICENSE.md for details
