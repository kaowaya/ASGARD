# Agent Interface（Agent接口层）

> 核心组件：Agent与Workflow引擎的统一网关
> 主要职责：接收Agent请求、路由到相应组件、返回响应

> **V2.0 新增组件**

---

## 概述

Agent Interface是ASGARD Workflow引擎的新增核心组件（V2.0），作为Agent与Workflow引擎交互的**唯一入口**。它提供REST API和程序化接口两种调用方式，确保Agent-Workflow交互的清晰边界。

**核心价值**：解决Agent-Workflow交互边界模糊的问题，提供统一、清晰、可观测的接口。

---

## 核心职责

1. **请求路由**：将Agent请求路由到相应组件（Offline Planner、Orchestrator、Monitor）
2. **权限验证**：验证Agent请求的合法性和权限
3. **上下文管理**：维护所有活跃Workflow的执行上下文
4. **协议转换**：将Agent的自然语言请求转换为Workflow引擎可执行的任务
5. **状态查询**：提供Workflow执行状态的实时查询

---

## API端点

### 1. 创建Workflow

**端点**: `POST /api/v1/agent/request`

**请求体**:
```json
{
  "type": "CREATE_WORKFLOW",
  "workflow_id": "wf-20260308-001",
  "task": "分析储能电站热失控风险",
  "context": {
    "battery_type": "LFP",
    "application": "energy_storage",
    "constraints": {
      "max_latency": "200ms",
      "min_accuracy": "0.95"
    }
  }
}
```

**响应**:
```json
{
  "status": "CREATED",
  "workflow_id": "wf-20260308-001",
  "dag": {
    "nodes": ["C3.4", "C3.6", "C3.1", "C3.2", "B2.7"],
    "edges": [
      ["C3.4", "C3.1"],
      ["C3.6", "C3.2"],
      ["C3.1", "B2.7"],
      ["C3.2", "B2.7"]
    ]
  },
  "execution_plan": {
    "parallel": true,
    "max_parallel_nodes": 4,
    "estimated_time": "180ms"
  },
  "timestamp": "2026-03-08T10:30:00Z"
}
```

---

### 2. 查询Workflow状态

**端点**: `GET /api/v1/workflow/{workflow_id}/status`

**URL参数**:
- `workflow_id` (path): Workflow ID

**响应**:
```json
{
  "workflow_id": "wf-20260308-001",
  "status": "RUNNING",
  "total_nodes": 5,
  "completed_count": 2,
  "failed_count": 0,
  "completed_nodes": ["C3.4", "C3.6"],
  "failed_nodes": {},
  "uptime_seconds": 15.3,
  "current_dag": {
    "nodes": ["C3.4", "C3.6", "C3.1", "C3.2", "B2.7"]
  },
  "progress_percentage": 40
}
```

**状态说明**：
- `PENDING`: 待执行
- `RUNNING`: 执行中
- `PAUSED`: 已暂停（Agent重规划中）
- `COMPLETED`: 已完成
- `FAILED`: 已失败

---

### 3. 请求重规划

**端点**: `POST /api/v1/agent/request`

**请求体**:
```json
{
  "type": "REPLAN",
  "workflow_id": "wf-20260308-001",
  "new_task": "分析储能电站热失控风险（增加数据清洗）",
  "context": {
    "reason": "数据质量差，需要增加C3.0数据清洗节点",
    "current_snapshot": {...}
  }
}
```

**响应**:
```json
{
  "status": "REPLANED",
  "workflow_id": "wf-20260308-001",
  "old_dag": {
    "nodes": ["C3.4", "C3.6", "C3.1", "C3.2", "B2.7"]
  },
  "new_dag": {
    "nodes": ["C3.0", "C3.4", "C3.6", "C3.1", "C3.2", "B2.7"],
    "edges": [...]
  },
  "changes": {
    "added": ["C3.0"],
    "removed": [],
    "modified": []
  },
  "timestamp": "2026-03-08T10:35:00Z"
}
```

---

### 4. 紧急停止

**端点**: `POST /api/v1/agent/request`

**请求体**:
```json
{
  "type": "EMERGENCY_STOP",
  "workflow_id": "wf-20260308-001",
  "context": {
    "reason": "检测到严重安全风险"
  }
}
```

**响应**:
```json
{
  "status": "STOPPED",
  "workflow_id": "wf-20260308-001",
  "stop_time": "2026-03-08T10:40:00Z",
  "final_state": {
    "completed_nodes": ["C3.4", "C3.6"],
    "failed_nodes": {"C3.1": "Timeout"},
    "status": "EMERGENCY_STOPPED"
  }
}
```

---

### 5. 健康检查

**端点**: `GET /health`

**响应**:
```json
{
  "status": "healthy",
  "service": "agent-interface",
  "version": "2.0.0",
  "dependencies": {
    "offline_planner": "ok",
    "orchestrator": "ok",
    "redis": "ok"
  },
  "timestamp": "2026-03-08T10:45:00Z"
}
```

---

## Agent-Workflow交互流程

### 流程1：正常执行（初始规划）

```
1. Agent发送创建Workflow请求
   ↓
2. Agent Interface验证请求
   ↓
3. Agent Interface调用Offline Planner
   ├─ 任务分解
   ├─ BAS匹配
   ├─ 依赖分析
   └─ DAG构建
   ↓
4. Offline Planner返回DAG和执行计划
   ↓
5. Agent Interface创建WorkflowContext
   ↓
6. Agent Interface启动Orchestrator
   ├─ 初始化Online Planner
   └─ 开始执行
   ↓
7. 返回创建成功响应给Agent
```

### 流程2：运行时故障处理（Online Planner自主）

```
1. Orchestrator执行节点
   ↓
2. 节点执行失败
   ↓
3. Orchestrator调用Online Planner
   ├─ 分析失败类型
   ├─ 决策：RETRY（失败1-3次）
   ├─ 实施：指数退避重试
   └─ 节点最终执行成功
   ↓
4. Workflow继续执行
   ↓
（Agent始终不知道故障发生）
```

### 流程3：Agent介入重规划

```
1. Orchestrator执行节点
   ↓
2. 节点失败第5次
   ↓
3. Online Planner决策：REQUEST_AGENT
   ↓
4. Orchestrator通过Agent Interface通知Agent
   ↓
5. Agent Interface
   ├─ 暂停Workflow执行
   ├─ 获取当前状态快照
   └─ 返回给Agent（包含失败详情）
   ↓
6. Agent分析并决策：
   "添加C3.0数据清洗节点"
   ↓
7. Agent发送重规划请求
   ↓
8. Agent Interface
   ├─ 调用Offline Planner重新规划
   ├─ 生成新DAG（包含C3.0）
   └─ 更新WorkflowContext
   ↓
9. 恢复Orchestrator执行
   ↓
10. Workflow继续执行（使用新DAG）
```

---

## 数据模型

### AgentRequest（Agent请求）

```python
class AgentRequest(BaseModel):
    type: RequestType  # CREATE_WORKFLOW, QUERY_STATUS, REPLAN, EMERGENCY_STOP
    workflow_id: str
    task: Optional[str] = None  # CREATE_WORKFLOW, REPLAN
    new_task: Optional[str] = None  # REPLAN
    context: Dict[str, Any]  # 请求上下文
```

### AgentResponse（Agent响应）

```python
class AgentResponse(BaseModel):
    status: str  # CREATED, RUNNING, COMPLETED, FAILED, REPLANED, STOPPED
    workflow_id: str
    dag: Optional[Dict] = None
    execution_plan: Optional[Dict] = None
    message: Optional[str] = None
    timestamp: str
```

### WorkflowStatus（Workflow状态）

```python
class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str  # PENDING, RUNNING, PAUSED, COMPLETED, FAILED
    total_nodes: int
    completed_count: int
    failed_count: int
    completed_nodes: List[str]
    failed_nodes: Dict[str, int]
    uptime_seconds: float
```

---

## 架构设计

### 在Workflow引擎中的位置

```
┌─────────────────────────────────────────┐
│            ASGARD Agent                 │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │ NL理解引擎  │  │ Skills编排器│  │ 决策引擎  │  │
│  └─────────────┘  └─────────────┘  └───────────┘  │
└─────────────────────────────────────────┘
            ↓ API调用
┌─────────────────────────────────────────┐
│       Agent Interface Layer              │
│  ┌──────────────────────────────────┐  │
│  │  请求路由  - 权限验证  - 上下文管理  │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
            ↓ 调用
┌─────────────────────────────────────────┐
│         Workflow Engine核心             │
│  ┌──────────────┐  ┌──────────────┐  │
│  │ Offline      │  │ Orchestrator  │  │
│  │ Planner      │  │  +Online     │  │
│  └──────────────┘  │  │ Planner     │  │
│  ┌──────────────┐  └──────────────┘  │
│  │ Executor    │                     │
│  └──────────────┘                     │
│  ┌──────────────┐                      │
│  │ Monitor      │                     │
│  └──────────────┘                     │
└─────────────────────────────────────────┘
```

### 组件交互

**Agent Interface → Offline Planner**:
- 调用时机：创建Workflow、Agent重规划
- 传递内容：用户任务、电池类型、约束条件
- 返回内容：DAG、执行计划

**Agent Interface → Orchestrator**:
- 调用时机：启动Workflow、恢复执行、紧急停止
- 传递内容：WorkflowContext、执行参数
- 返回内容：执行结果、状态更新

**Agent Interface ← Orchestrator**:
- 调用时机：Online Planner无法处理、请求Agent介入
- 传递内容：失败详情、当前状态快照
- 返回内容：重规划结果

---

## 性能特性

### 1. 异步处理

所有耗时操作异步处理，避免阻塞：

```python
@app.post("/api/v1/agent/request")
async def handle_request(request: AgentRequest):
    # 异步调用Offline Planner
    dag, plan = await offline_planner.plan_async(request.task, request.context)

    # 异步创建上下文
    context = await create_context_async(dag, plan)

    # 立即返回（不等待执行完成）
    return AgentResponse(status="CREATED", workflow_id=request.workflow_id, dag=dag)
```

### 2. 流量控制

```python
# 限制并发Workflow数量
max_concurrent_workflows = 100

# 请求队列
request_queue = asyncio.Queue(maxsize=1000)

# 限流：单Agent每秒最多10个请求
rate_limiter = RateLimiter(max_requests=10, window=1.0)
```

### 3. 缓存机制

```python
# 缓存常见任务的规划结果
@lru_cache(maxsize=1000)
async def get_cached_plan(task_hash: str):
    return await redis.get(f"plan:{task_hash}")
```

---

## 安全特性

### 1. 权限验证

```python
async def verify_agent_permission(agent_id: str, action: str):
    # 验证Agent是否有权限执行操作
    permission = await agent_service.get_permission(agent_id, action)
    if not permission.granted:
        raise HTTPException(status_code=403, detail="权限不足")
```

### 2. 输入验证

```python
# 使用Pydantic进行自动验证
class AgentRequest(BaseModel):
    type: RequestType
    workflow_id: str = Field(min_length=1, max_length=100)
    task: Optional[str] = Field(max_length=1000)
    context: Dict[str, Any] = Field(default_factory=dict)
```

### 3. 速率限制

```python
# 限制单Agent请求频率
@rate_limit(max_calls=100, time_window=60)
async def rate_limit_agent(agent_id: str):
    pass
```

---

## 监控和可观测性

### 1. 请求日志

```python
# 记录所有Agent请求
logger.info(f"Agent请求: {request.type} - {request.workflow_id}")
logger.info(f"Agent决策: {decision.action} - {decision.reason}")
```

### 2. 性能指标

```python
# 记录API延迟
api_latency_histogram.observe(latency_ms)

# 记录请求成功率
agent_request_success_counter.labels(status="success").inc()
```

### 3. 错误追踪

```python
# 记录错误详情
logger.error(f"请求失败: {error}", exc_info=True,
               extra={"workflow_id": workflow_id, "agent_id": agent_id})
```

---

## 使用示例

### Python SDK（程序化接口）

```python
from workflow.engine.agent_interface import AgentInterface
from workflow.engine.planner.offline_planner import OfflinePlanner
from workflow.engine.orchestrator.orchestrator import Orchestrator
from workflow.engine.monitor import Monitor

# 初始化Agent Interface
agent_interface = AgentInterface(
    offline_planner=OfflinePlanner(),
    orchestrator=Orchestrator(...),
    monitor=Monitor()
)

# 创建Workflow
result = agent_interface.create_workflow(
    workflow_id="wf-001",
    task="分析储能电站热失控风险",
    context={"battery_type": "LFP"}
)

print(f"创建成功: {result.status}")
print(f"DAG节点: {result.dag['nodes']}")
```

### REST API（curl）

```bash
# 创建Workflow
curl -X POST http://localhost:8000/api/v1/agent/request \
  -H "Content-Type: application/json" \
  -d '{
    "type": "CREATE_WORKFLOW",
    "workflow_id": "wf-001",
    "task": "分析储能电站热失控风险",
    "context": {"battery_type": "LFP"}
  }'

# 查询状态
curl http://localhost:8000/api/v1/workflow/wf-001/status
```

---

## 错误处理

### 常见错误

| 错误码 | 说明 | 解决方案 |
|-------|------|---------|
| 400 | 请求格式错误 | 检查JSON格式 |
| 403 | 权限不足 | 联系管理员 |
| 404 | Workflow不存在 | 检查workflow_id |
| 409 | Workflow已完成 | 无法修改已完成的Workflow |
| 500 | 内部错误 | 查看日志并联系支持 |

### 错误响应格式

```json
{
  "error": {
    "code": "WORKFLOW_NOT_FOUND",
    "message": "Workflow wf-001 不存在",
    "details": {...},
    "timestamp": "2026-03-08T10:50:00Z"
  }
}
```

---

## 设计优势

| 优势 | 说明 |
|------|------|
| **清晰边界** | Agent通过统一接口访问Workflow，无需了解内部实现 |
| **灵活调用** | 支持REST API和程序化接口两种调用方式 |
| **异步解耦** | Agent和Workflow引擎可以独立部署和扩展 |
| **可观测性** | 所有Agent请求都有日志，便于调试和审计 |
| **安全控制** | 可以在接口层实现权限验证、限流等安全措施 |

---

## 延伸阅读

- [Offline Planner（离线规划器）](./01-Planner规划器.md)
- [Orchestrator（编排器）](./02-Orchestrator编排器.md)
- [Workflow Monitor（监控器）](./04-Monitor监控器.md)
- [架构更新文档](../../docs/workflow-v2/architecture-update.md)
- [迁移指南](../../docs/migration-guide-agent-workflow-v2.md)
