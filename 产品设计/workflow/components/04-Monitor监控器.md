# Workflow Monitor（工作流监控器）

> 核心组件：Workflow引擎的监控与运维中心
> 主要职责：实时监控Workflow执行，异常检测，性能分析

---

## 概述

Workflow Monitor负责Workflow执行过程中的实时监控、异常检测、性能分析和日志审计。它是Workflow引擎的"监控层"，确保Workflow稳定、可靠、高效地运行。

---

## 核心职责

1. **实时监控**：监控Workflow执行状态和性能指标
2. **异常检测**：自动检测并处理执行异常
3. **性能分析**：分析Workflow性能瓶颈
4. **日志审计**：记录完整的执行日志
5. **告警通知**：在异常情况下及时通知相关人员

---

## 监控指标体系

### 1. 性能指标

| 指标 | 说明 | 告警阈值 | 采集频率 |
|-----|------|---------|---------|
| **节点执行时间** | 单个BAS的执行时间 | > 预期150% | 实时 |
| **端到端延迟** | Workflow总执行时间 | > SLA | 每次执行 |
| **吞吐量** | 单位时间处理的Workflow数量 | < 阈值 | 每分钟 |
| **队列长度** | 待处理的Workflow队列长度 | > 100 | 每分钟 |

### 2. 质量指标

| 指标 | 说明 | 告警阈值 | 采集频率 |
|-----|------|---------|---------|
| **BAS推理精度** | BAS输出的准确性 | < 阈值 | 每次执行 |
| **Workflow输出一致性** | 相同输入的输出一致性 | 波动>10% | 每次执行 |
| **数据质量** | 输入数据的完整性 | 缺失>5% | 每次执行 |
| **模型漂移** | 模型性能随时间的变化 | > 5% | 每天 |

### 3. 资源指标

| 指标 | 说明 | 告警阈值 | 采集频率 |
|-----|------|---------|---------|
| **CPU占用率** | CPU使用百分比 | > 80% | 每秒 |
| **内存占用** | 内存使用量 | > 可用内存90% | 每秒 |
| **GPU利用率** | GPU使用百分比 | < 50% | 每秒 |
| **磁盘I/O** | 磁盘读写速度 | > 阈值 | 每分钟 |

### 4. 业务指标

| 指标 | 说明 | 告警阈值 | 采集频率 |
|-----|------|---------|---------|
| **热失控预警L3+** | L3及以上级别预警 | 触发即告警 | 实时 |
| **容量衰减率** | 电池容量每月衰减 | > 5%/月 | 每天 |
| **析锂发生率** | 析锂检测阳性率 | > 20% | 每天 |
| **Workflow失败率** | Workflow执行失败比例 | > 1% | 每天 |

---

## 实时监控

### 执行状态跟踪

```python
class WorkflowExecutionMonitor:
    """
    Workflow执行监控器
    """
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.status = 'PENDING'
        self.start_time = None
        self.end_time = None
        self.current_node = None
        self.completed_nodes = []
        self.failed_nodes = []
        self.metrics = {}

    def start_execution(self):
        """
        开始执行
        """
        self.status = 'RUNNING'
        self.start_time = current_time()
        log_info(f"Workflow {self.workflow_id} 开始执行")

    def complete_node(self, node_id, execution_time, result):
        """
        完成节点
        """
        self.completed_nodes.append({
            'node_id': node_id,
            'execution_time': execution_time,
            'completed_at': current_time(),
            'result': result
        })
        log_info(f"节点 {node_id} 执行完成，耗时 {execution_time}ms")

    def fail_node(self, node_id, error):
        """
        节点失败
        """
        self.failed_nodes.append({
            'node_id': node_id,
            'error': str(error),
            'failed_at': current_time()
        })
        log_error(f"节点 {node_id} 执行失败：{str(error)}")

    def complete_execution(self):
        """
        完成执行
        """
        self.end_time = current_time()
        self.status = 'COMPLETED'
        total_time = self.end_time - self.start_time
        log_info(f"Workflow {self.workflow_id} 执行完成，总耗时 {total_time}ms")

    def get_metrics(self):
        """
        获取指标
        """
        return {
            'workflow_id': self.workflow_id,
            'status': self.status,
            'total_time': self.end_time - self.start_time IF self.end_time ELSE None,
            'completed_nodes': len(self.completed_nodes),
            'failed_nodes': len(self.failed_nodes),
            'node_metrics': self._calculate_node_metrics()
        }
```

### Dashboard展示

```python
def generate_dashboard(workflow_executions):
    """
    生成监控Dashboard
    """
    dashboard = {
        'overview': {
            'total_executions': len(workflow_executions),
            'running': len([e for e in workflow_executions IF e.status == 'RUNNING']),
            'completed': len([e for e in workflow_executions IF e.status == 'COMPLETED']),
            'failed': len([e for e in workflow_executions IF e.status == 'FAILED'])
        },
        'performance': {
            'avg_execution_time': average([e.total_time for e in workflow_executions IF e.total_time]),
            'p95_execution_time': percentile([e.total_time for e in workflow_executions IF e.total_time], 95),
            'p99_execution_time': percentile([e.total_time for e in workflow_executions IF e.total_time], 99)
        },
        'resources': {
            'cpu_usage': get_cpu_usage(),
            'memory_usage': get_memory_usage(),
            'gpu_usage': get_gpu_usage()
        },
        'recent_executions': [
            {
                'workflow_id': e.workflow_id,
                'status': e.status,
                'total_time': e.total_time,
                'completed_nodes': len(e.completed_nodes)
            }
            for e in workflow_executions[-10:]
        ]
    }

    return dashboard
```

---

## 异常检测

### 异常类型

| 异常类型 | 说明 | 检测方法 | 处理策略 |
|---------|------|---------|---------|
| **性能异常** | 执行时间超时 | 统计分析 | 重试/降级 |
| **精度异常** | 输出精度下降 | 模型验证 | 使用备用模型 |
| **数据异常** | 输入数据缺失 | 数据质量检查 | 请求补传 |
| **资源异常** | CPU/内存不足 | 资源监控 | 限流/扩容 |
| **业务异常** | 热失控预警 | 业务规则 | 紧急响应 |

### 异常检测算法

```python
def detect_anomaly(workflow_execution, baseline_metrics):
    """
    异常检测
    """
    anomalies = []

    # 1. 性能异常检测
    IF workflow_execution.total_time > baseline_metrics.avg_time * 1.5:
        anomalies.append({
            'type': 'PERFORMANCE',
            'severity': 'MEDIUM',
            'description': f"执行时间异常：{workflow_execution.total_time}ms > {baseline_metrics.avg_time * 1.5}ms"
        })

    # 2. 资源异常检测
    cpu_usage = get_cpu_usage()
    IF cpu_usage > 80%:
        anomalies.append({
            'type': 'RESOURCE',
            'severity': 'HIGH',
            'description': f"CPU占用过高：{cpu_usage}%"
        })

    # 3. 精度异常检测
    FOR node IN workflow_execution.completed_nodes:
        IF node.result.accuracy < baseline_metrics.min_accuracy:
            anomalies.append({
                'type': 'ACCURACY',
                'severity': 'HIGH',
                'description': f"节点 {node.node_id} 精度不足：{node.result.accuracy} < {baseline_metrics.min_accuracy}"
            })

    # 4. 业务异常检测
    IF workflow_execution.has_business_alert():
        anomalies.append({
            'type': 'BUSINESS',
            'severity': 'CRITICAL',
            'description': workflow_execution.business_alert
        })

    return anomalies
```

### 异常处理

```python
def handle_anomaly(anomaly, workflow_execution):
    """
    异常处理
    """
    severity = anomaly['severity']

    # Step 1: 记录异常
    log_anomaly(anomaly, workflow_execution)

    # Step 2: 评估严重性
    IF severity == 'LOW':
        # 低危：重试
        action = retry_node(workflow_execution.failed_node)

    ELIF severity == 'MEDIUM':
        # 中危：跳过当前节点，使用默认值
        action = skip_node_and_use_default(workflow_execution.failed_node)

    ELIF severity == 'HIGH':
        # 高危：暂停Workflow，通知人工介入
        action = pause_workflow(workflow_execution)
        notify_stakeholder(anomaly, workflow_execution)

    ELIF severity == 'CRITICAL':
        # 严重：紧急停止，执行应急预案
        action = emergency_stop(workflow_execution)
        execute_emergency_plan(anomaly)

    # Step 3: 更新监控状态
    update_monitoring_status(anomaly, action)

    return action
```

---

## 性能分析

### 瓶颈识别

```python
def identify_bottlenecks(workflow_executions):
    """
    识别性能瓶颈
    """
    # 统计每个节点的平均执行时间
    node_times = {}
    FOR execution IN workflow_executions:
        FOR node IN execution.completed_nodes:
            IF node.node_id NOT IN node_times:
                node_times[node.node_id] = []
            node_times[node.node_id].append(node.execution_time)

    # 计算平均时间和方差
    node_stats = {}
    FOR node_id, times IN node_times.items():
        node_stats[node_id] = {
            'avg_time': average(times),
            'max_time': max(times),
            'min_time': min(times),
            'std_time': std(times),
            'cv': std(times) / average(times)  # 变异系数
        }

    # 识别瓶颈（平均时间最长的节点）
    bottleneck = max(node_stats.items(), key=lambda x: x[1]['avg_time'])

    # 识别不稳定节点（变异系数最大的节点）
    unstable_node = max(node_stats.items(), key=lambda x: x[1]['cv'])

    return {
        'bottleneck': bottleneck,
        'unstable_node': unstable_node,
        'all_node_stats': node_stats
    }
```

### 优化建议生成

```python
def generate_optimization_recommendations(bottleneck_analysis):
    """
    生成优化建议
    """
    recommendations = []

    # 瓶颈优化
    bottleneck_node = bottleneck_analysis['bottleneck']
    IF bottleneck_node[1]['avg_time'] > 1000:  # 超过1秒
        recommendations.append({
            'type': 'OPTIMIZE_NODE',
            'node_id': bottleneck_node[0],
            'suggestion': '考虑模型量化或剪枝以减少推理时间',
            'expected_improvement': '30-50%'
        })

    # 不稳定节点优化
    unstable_node = bottleneck_analysis['unstable_node']
    IF unstable_node[1]['cv'] > 0.3:  # 变异系数>30%
        recommendations.append({
            'type': 'STABILIZE_NODE',
            'node_id': unstable_node[0],
            'suggestion': '检查输入数据质量，考虑增加数据预处理',
            'expected_improvement': '降低执行时间波动'
        })

    # 并行化建议
    recommendations.append({
        'type': 'PARALLELIZE',
        'suggestion': '识别可并行执行的节点以提升吞吐量',
        'expected_improvement': '2-4x'
    })

    return recommendations
```

---

## 日志审计

### 日志记录

```python
class AuditLogger:
    """
    审计日志记录器
    """
    def __init__(self, log_file='workflow_audit.log'):
        self.log_file = log_file

    def log_workflow_start(self, workflow_id, workflow_config, input_data):
        """
        记录Workflow开始
        """
        log_entry = {
            'timestamp': current_time(),
            'event': 'WORKFLOW_START',
            'workflow_id': workflow_id,
            'config': workflow_config,
            'input_data_hash': hash(input_data),
            'input_size': len(input_data)
        }
        self.append_log(log_entry)

    def log_node_execution(self, workflow_id, node_id, input_data, output_data, execution_time):
        """
        记录节点执行
        """
        log_entry = {
            'timestamp': current_time(),
            'event': 'NODE_EXECUTION',
            'workflow_id': workflow_id,
            'node_id': node_id,
            'input_hash': hash(input_data),
            'output_hash': hash(output_data),
            'execution_time': execution_time
        }
        self.append_log(log_entry)

    def log_anomaly(self, workflow_id, anomaly, action_taken):
        """
        记录异常
        """
        log_entry = {
            'timestamp': current_time(),
            'event': 'ANOMALY',
            'workflow_id': workflow_id,
            'anomaly_type': anomaly['type'],
            'severity': anomaly['severity'],
            'description': anomaly['description'],
            'action_taken': action_taken
        }
        self.append_log(log_entry)

    def append_log(self, log_entry):
        """
        追加日志
        """
        WITH open(self.log_file, 'a') AS f:
            f.write(json.dumps(log_entry) + '\n')
```

### 日志查询

```python
def query_audit_logs(workflow_id=None, start_time=None, end_time=None, event_type=None):
    """
    查询审计日志
    """
    logs = load_audit_logs()

    # 过滤条件
    IF workflow_id:
        logs = [log for log in logs IF log['workflow_id'] == workflow_id]

    IF start_time:
        logs = [log for log in logs IF log['timestamp'] >= start_time]

    IF end_time:
        logs = [log for log in logs IF log['timestamp'] <= end_time]

    IF event_type:
        logs = [log for log in logs IF log['event'] == event_type]

    return logs
```

---

## 告警通知

### 告警规则

```python
class AlertRule:
    """
    告警规则
    """
    def __init__(self, name, condition, severity, notification_channels):
        self.name = name
        self.condition = condition  # 告警触发条件
        self.severity = severity    # LOW/MEDIUM/HIGH/CRITICAL
        self.notification_channels = notification_channels  # 通知渠道

# 定义告警规则
alert_rules = [
    AlertRule(
        name='热失控L3预警',
        condition=lambda metrics: metrics.get('fault_level') == 'L3',
        severity='HIGH',
        notification_channels=['email', 'sms', 'webhook']
    ),
    AlertRule(
        name='Workflow执行超时',
        condition=lambda metrics: metrics.get('execution_time', 0) > 5000,
        severity='MEDIUM',
        notification_channels=['email', 'webhook']
    ),
    AlertRule(
        name='CPU占用过高',
        condition=lambda metrics: metrics.get('cpu_usage', 0) > 80,
        severity='LOW',
        notification_channels=['webhook']
    )
]
```

### 告警发送

```python
def send_alert(alert_rule, context):
    """
    发送告警
    """
    alert_message = {
        'rule_name': alert_rule.name,
        'severity': alert_rule.severity,
        'timestamp': current_time(),
        'context': context
    }

    FOR channel IN alert_rule.notification_channels:
        IF channel == 'email':
            send_email_alert(alert_message)
        ELIF channel == 'sms':
            send_sms_alert(alert_message)
        ELIF channel == 'webhook':
            send_webhook_alert(alert_message)
        ELIF channel == 'slack':
            send_slack_alert(alert_message)

    log_info(f"告警已发送：{alert_rule.name}（{alert_rule.severity}）")
```

---

## 监控Dashboard示例

```
┌─────────────────────────────────────────────────────────────────┐
│  Workflow执行状态监控                                              │
├─────────────────────────────────────────────────────────────────┤
│  Workflow名称: 极寒营运车辆充电优化                                 │
│  执行ID: wf-20260207-001                                         │
│  状态: 运行中（已执行3/5节点）                                     │
├─────────────────────────────────────────────────────────────────┤
│  节点执行进度：                                                    │
│  ✓ 气象数据获取 (12ms)                                           │
│  ✓ 环境温度预测 (45ms)                                           │
│  ✓ 充电数据采集 (8ms)                                            │
│  ⟳ B2.5:析锂检测 (执行中...)                                     │
│  ○ B2.1:MCC降流 (等待中)                                         │
│  ○ B2.6:MPC热管理 (等待中)                                       │
├─────────────────────────────────────────────────────────────────┤
│  性能指标：                                                        │
│  - 端到端延迟: 156ms / 目标<200ms ✓                              │
│  - CPU占用: 45% / 阈值80% ✓                                      │
│  - 内存占用: 2.1GB / 可用4GB ✓                                    │
├─────────────────────────────────────────────────────────────────┤
│  告警信息：                                                        │
│  ⚠️ B2.5执行时间较预期长20%（可能原因：低温数据量大）              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 延伸阅读

- [Workflow Planner（规划器）](./01-Planner规划器.md)
- [Workflow Orchestrator（编排器）](./02-Orchestrator编排器.md)
- [Workflow Executor（执行器）](./03-Executor执行器.md)
- [执行模式详解](../execution-modes.md)
