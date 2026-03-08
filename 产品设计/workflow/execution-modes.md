# Workflow执行模式详解

> 版本：V1.0
> 核心内容：三种执行模式的架构、适用场景和实现方案

---

## 概述

ASGARD Workflow引擎支持三种执行模式：在线执行（Online）、离线执行（Offline）和混合执行（Hybrid）。不同的执行模式适用于不同的业务场景，在延迟、吞吐量、精度等方面有不同的权衡。

---

## 三种执行模式对比

| 维度 | Online（在线） | Offline（离线） | Hybrid（混合） |
|-----|---------------|----------------|---------------|
| **执行位置** | 边缘端（BMS/EMS） | 云端 | 边缘端 + 云端 |
| **数据驱动** | 实时数据流 | 批量历史数据 | 实时 + 批量 |
| **响应延迟** | < 100ms | 分钟级 | 边缘<100ms，云端小时级 |
| **适用场景** | 实时控制、安全预警 | 质量检测、RUL预测 | 健康管理、故障诊断 |
| **算力需求** | 低（嵌入式） | 高（服务器集群） | 中（边缘 + 云端） |
| **精度要求** | 中（追求速度） | 高（追求准确） | 高（实时+深度） |
| **网络依赖** | 无 | 无（离线） | 有（数据上传） |

---

## 1. 在线执行模式（Online）

### 架构

```
边缘端（Edge Device - BMS/EMS）
├─ 数据采集模块（10Hz）
│  ├─ 电压、电流、温度传感器
│  └─ 实时数据缓冲区
├─ BAS模型仓库（ONNX Runtime）
│  ├─ B2.1 MCC充电控制
│  ├─ B2.5 析锂检测
│  ├─ C3.4 香农熵异常检测
│  └─ C3.2 MEMS热失控预警
├─ 推理引擎（ONNX Runtime）
│  ├─ 量化模型（INT8）
│  └─ 算子融合优化
└─ 决策输出（<100ms）
   ├─ 充电电流调整
   ├─ 安全策略执行
   └─ 本地告警
```

### 特点

- **低延迟**：响应时间 < 100ms
- **实时性**：10Hz数据采集与处理
- **本地化**：无需网络，完全离线运行
- **轻量化**：模型量化（INT8），算子融合
- **高可靠**：无网络依赖，独立运行

### 适用场景

| 场景 | 说明 | 示例 |
|-----|------|------|
| **BMS实时控制** | 充电电流、功率调整 | B2.1 MCC充电控制 |
| **热失控实时预警** | L3/L4级紧急响应 | C3.2 + B2.7 |
| **析锂实时检测** | 充电过程中动态调整 | B2.5 析锂检测 |
| **安全联锁控制** | 紧急停机、限流保护 | B2.7 主动安全控制 |

### 实现方案

```python
def online_workflow_execution():
    """
    在线Workflow执行
    """
    # 初始化推理引擎
    inference_engine = ONNXRuntimeEngine()

    # 加载量化模型
    models = {
        'C3.4': inference_engine.load_model('models/c3.4_quantized.onnx'),
        'B2.5': inference_engine.load_model('models/b2.5_quantized.onnx'),
        'C3.2': inference_engine.load_model('models/c3.2_quantized.onnx'),
        'B2.7': inference_engine.load_model('models/b2.7_quantized.onnx')
    }

    # 实时监控循环（10Hz）
    WHILE True:
        start_time = current_time()

        # Step 1: 数据采集
        sensor_data = collect_sensor_data()

        # Step 2: 并行推理
        fault_level = inference_engine.infer(models['C3.4'], sensor_data)
        anode_potential = inference_engine.infer(models['B2.5'], sensor_data)
        tr_risk = inference_engine.infer(models['C3.2'], sensor_data)

        # Step 3: 安全决策
        safety_action = inference_engine.infer(models['B2.7'], {
            'fault_level': fault_level,
            'anode_potential': anode_potential,
            'tr_risk': tr_risk
        })

        # Step 4: 执行安全策略
        execute_safety_action(safety_action)

        # Step 5: 性能监控
        execution_time = current_time() - start_time
        IF execution_time > 100ms:
            log_warning(f"执行超时：{execution_time}ms")

        # 10Hz循环
        sleep(100ms - execution_time)
```

### 性能优化

1. **模型量化**：FP32 → INT8，加速3-4x
2. **算子融合**：Conv+BN+ReLU融合，减少内存访问
3. **批处理**：多传感器数据打包推理
4. **缓存机制**：缓存推理结果，避免重复计算

---

## 2. 离线执行模式（Offline）

### 架构

```
云端（Cloud - 数据中心）
├─ 数据湖（Data Lake）
│  ├─ 历史充放电数据
│  ├─ 电池全生命周期数据
│  └─ 多维度元数据
├─ 批处理引擎（Apache Spark）
│  ├─ 数据清洗与预处理
│  ├─ 特征工程
│  └─ 批量BAS推理
├─ Workflow调度器（Apache Airflow）
│  ├─ 定时任务调度
│  ├─ DAG依赖管理
│  └─ 任务重试与容错
└─ 结果存储（数据仓库）
   ├─ SOH/RUL预测结果
   ├─ 质量分级报告
   └─ 趋势分析报告
```

### 特点

- **高吞吐**：批量处理百万级数据
- **高精度**：使用完整历史数据，深度分析
- **定时执行**：按小时/天/周调度
- **可扩展**：分布式计算，横向扩展
- **成本优化**：共享资源，降低单次成本

### 适用场景

| 场景 | 说明 | 示例 |
|-----|------|------|
| **生产质量检测** | 电池生产线下线检测 | M1.x系列Skills |
| **SOH/RUL预测** | 基于全历史数据的寿命预测 | C3.3 + C3.5 |
| **电池银行评估** | 退役电池批量评估 | 04-电池银行评估Workflow |
| **大模型训练** | BAS个性化模型训练 | 模型微调 |

### 实现方案

```python
def offline_workflow_execution(spark_session, airflow_dag):
    """
    离线Workflow执行
    """
    # Step 1: 从数据湖加载历史数据
    historical_data = spark_session.read.parquet("s3://battery-data/historical/")

    # Step 2: 数据清洗与预处理
    cleaned_data = clean_data(historical_data)
    features = extract_features(cleaned_data)

    # Step 3: 批量BAS推理（分布式）
    # SOH估计
    soh_results = features.mapPartitions(
        lambda batch: batch_inference(model_C3_5, batch)
    ).collect()

    # RUL预测
    rul_results = features.mapPartitions(
        lambda batch: batch_inference(model_C3_3, batch)
    ).collect()

    # Step 4: 结果聚合
    aggregated_results = aggregate_results(soh_results, rul_results)

    # Step 5: 生成报告
    report = generate_report(aggregated_results)

    # Step 6: 保存到数据仓库
    report.save_to_datawarehouse("battery_health_reports")

    return report
```

### 性能优化

1. **分布式计算**：Spark集群并行处理
2. **分区策略**：按时间/设备ID分区
3. **内存管理**：合理配置executor内存
4. **缓存策略**：缓存常用模型和数据

---

## 3. 混合执行模式（Hybrid）

### 架构

```
边缘端（实时）                    云端（深度分析）
┌───────────────────┐          ┌──────────────────┐
│ 实时数据采集（10Hz）│ ─上传──> │ 数据湖（时序数据）│
│         │          │          │         │        │
│         ↓          │          │         ↓        │
│ 快速推理（<100ms）│          │ SOS深度分析      │
│    ├─ C3.4        │          │    ├─ C3.1       │
│    ├─ C3.6        │          │    ├─ C3.7       │
│    └─ B2.7        │          │    └─ C3.8       │
│         │          │          │         │        │
│         ↓          │          │         ↓        │
│ 本地决策（L0-L2）│          │ 优化策略生成      │
│    └─ 限流/告警   │<──下发───│    └─ 参数调优   │
└───────────────────│          └──────────────────┘
```

### 特点

- **实时+深度**：边缘端快速响应 + 云端深度分析
- **协同工作**：边缘端执行高频任务，云端执行低频复杂任务
- **数据闭环**：边缘数据上传云端，云端优化策略下发边缘
- **最优平衡**：延迟与精度的最佳权衡

### 适用场景

| 场景 | 边缘端任务 | 云端任务 | 示例 |
|-----|-----------|---------|------|
| **储能电站健康管理** | 实时监控（10Hz） | 每日SOS分析 | 03-储能电站健康管理Workflow |
| **营运车辆远程运维** | 实时充电控制 | 每周健康报告 | 02-析锂延寿Workflow |
| **复杂故障诊断** | 快速异常识别 | 根因分析 | 热失控预防Workflow |
| **自适应优化** | 实时策略执行 | 定期策略优化 | 所有Workflow |

### 实现方案

```python
def hybrid_workflow_execution():
    """
    混合Workflow执行
    """
    # 边缘端：实时监控循环
    WHILE True:
        # Step 1: 实时数据采集
        sensor_data = collect_sensor_data()

        # Step 2: 快速推理（边缘端）
        fault_level = edge_infer(model_C3_4, sensor_data)

        # Step 3: 本地决策
        IF fault_level >= 'L2':
            # 异常检测到，执行本地安全策略
            execute_safety_action(model_B2_7, fault_level)

            # 上传异常数据到云端
            upload_to_cloud(anomaly_data)

        # 10Hz循环
        sleep(100ms)

    # 云端：深度分析任务（每日执行）
    SCHEDULE(every_day_at_2am):
        # Step 1: 从云端数据湖加载全量数据
        full_data = load_from_data_warehouse()

        # Step 2: 深度分析（云端）
        sos_result = cloud_infer(model_C3_1, full_data)

        # Step 3: 生成优化策略
        optimized_params = generate_optimization_strategy(sos_result)

        # Step 4: 下发策略到边缘端
        push_to_edge(optimized_params)
```

### 数据流与同步

```python
def edge_cloud_synchronization():
    """
    边缘-云端数据同步
    """
    # 边缘端 → 云端（数据上传）
    # 1. 实时数据流（10Hz）
    upload_realtime_stream(sensor_data, frequency='10Hz')

    # 2. 异常事件（立即上传）
    IF detect_anomaly():
        upload_anomaly_event(anomaly_data, priority='HIGH')

    # 3. 历史数据（每小时批量上传）
    SCHEDULE(every_hour):
        upload_historical_batch(buffer_data)

    # 云端 → 边缘端（策略下发）
    # 1. 模型更新（每周）
    SCHEDULE(every_week):
        new_model = cloud_train_retrain_model()
        push_model_update_to_edge(new_model)

    # 2. 参数调优（每天）
    SCHEDULE(every_day):
        optimized_params = cloud_optimize_parameters()
        push_params_to_edge(optimized_params)
```

### 性能优化

1. **边缘端优化**：模型量化、算子融合
2. **云端优化**：分布式计算、缓存策略
3. **网络优化**：数据压缩、增量同步
4. **协同优化**：智能任务分配、负载均衡

---

## 执行模式选择指南

### 决策树

```
是否需要实时响应（<100ms）？
├─ 是 → Online模式
│   ├─ BMS实时控制
│   ├─ 热失控紧急响应
│   └─ 析锂实时抑制
└─ 否 → 是否需要深度分析（全历史数据）？
    ├─ 是 → Hybrid模式
    │   ├─ 储能电站健康管理
    │   ├─ 营运车辆远程运维
    │   └─ 复杂故障诊断
    └─ 否 → Offline模式
        ├─ 生产质量检测
        ├─ 电池银行评估
        └─ SOH/RUL批量预测
```

### 选择矩阵

| 需求特征 | 推荐模式 | 理由 |
|---------|---------|------|
| 延迟<100ms | Online | 实时响应 |
| 批量处理（>1000条） | Offline | 高吞吐 |
| 需要全历史数据 | Offline/Hybrid | 深度分析 |
| 网络不稳定 | Online | 本地执行 |
| 算力受限 | Online | 轻量化模型 |
| 追求最高精度 | Hybrid | 实时+深度 |
| 成本敏感 | Offline | 资源共享 |

---

## 延伸阅读

- [Workflow组件详解](./components/)
- [Meta-Workflow设计](./meta-workflows/)
- [Workflow案例与示例](./examples/)
