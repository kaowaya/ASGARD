# Workflow组件详解

> 概述：Workflow引擎的五大核心组件（V2.0更新）

---

## 五大核心组件

Workflow引擎由五个核心组件组成，每个组件负责不同的职责：

### 0. Agent Interface（Agent接口层）⭐ V2.0新增

**详细文档**：[05-Agent-Interface.md](./05-Agent-Interface.md)

**职责**：Agent与Workflow引擎的统一网关

**核心功能**：
- 请求路由（将Agent请求路由到相应组件）
- 权限验证（验证Agent请求的合法性）
- 上下文管理（维护所有活跃Workflow的执行上下文）
- 协议转换（将自然语言请求转换为可执行任务）
- 状态查询（提供Workflow执行状态的实时查询）

**API端点**：
- `POST /api/v1/agent/request` - 创建Workflow、重规划、紧急停止
- `GET /api/v1/workflow/{workflow_id}/status` - 查询Workflow状态
- `GET /health` - 健康检查

---

### 1. Offline Planner（离线规划器）⭐ V2.0重命名

**详细文档**：[01-Planner规划器.md](./01-Planner规划器.md)

**职责**：根据用户任务和上下文，规划最优Workflow

**核心功能**：
- 任务分解（Task Decomposition）
- BAS选择（Skill Selection）
- 依赖分析（Dependency Analysis）
- DAG构建（有向无环图）
- 资源分配（Resource Allocation）

**输入/输出**：
- 输入：用户任务（自然语言）、电池类型、应用场景、约束条件
- 输出：Workflow DAG、BAS列表及配置、执行计划

---

### 2. Workflow Orchestrator（编排器）⭐ V2.0增强

**详细文档**：[02-Orchestrator编排器.md](./02-Orchestrator编排器.md)

**职责**：管理Workflow的执行流程，包括并行、分支、循环

**核心功能**：
- 并行调度（Parallel Execution）
- 条件分支（Conditional Branching）
- 循环迭代（Iterative Loop）
- 异常处理（Error Handling）
- 资源管理（Resource Management）
- **运行时自适应（V2.0新增）**：集成Online Planner实现自主决策

**编排策略**：
- 并行执行：识别可并行节点，提升效率
- 条件分支：根据中间结果动态选择路径
- 循环迭代：重复执行直到收敛
- 混合编排：结合多种策略

---

### 3. Workflow Executor（执行器）

**详细文档**：[03-Executor执行器.md](./03-Executor执行器.md)

**职责**：训练BAS、执行推理、管理数据

**核心功能**：
- BAS训练器（Skill Trainer）
- 模型推理（Model Inference）
- 数据管理（Data Management）
- 结果聚合（Result Aggregation）
- 模型缓存（Model Cache）

**执行流程**：
1. 加载Skill模板
2. 训练个性化模型
3. 模型推理
4. 结果传递给依赖的BAS

---

### 4. Workflow Monitor（监控器）

**详细文档**：[04-Monitor监控器.md](./04-Monitor监控器.md)

**职责**：实时监控Workflow执行，异常检测，性能分析

**核心功能**：
- 实时监控（Real-time Monitoring）
- 异常检测（Anomaly Detection）
- 性能分析（Performance Analytics）
- 日志审计（Log Auditing）
- 告警通知（Alerting）

**监控指标**：
- 性能指标：执行时间、端到端延迟、吞吐量
- 质量指标：BAS推理精度、输出一致性
- 资源指标：CPU/内存/GPU占用
- 业务指标：热失控预警、容量衰减率

---

## 组件协作流程（V2.0架构）

```
用户需求（通过Agent）
   ↓
[Agent Interface] → 请求路由、权限验证、上下文管理
   ↓
[Offline Planner] → 生成Workflow DAG和执行计划
   ↓
[Orchestrator] → 管理执行流程（并行、分支、循环）
   ├─ [Online Planner] → 运行时自主决策（故障恢复、性能优化）
   ↓
[Executor] → 训练BAS、执行推理、管理数据
   ↓
[Monitor] → 实时监控、异常检测、性能分析
   ↓
输出结果 + 持续优化反馈
```

**V2.0关键变化**：
- ✅ Agent Interface成为Agent与Workflow交互的唯一入口
- ✅ Online Planner集成在Orchestrator内，实现80%运行时问题自主处理
- ✅ Offline Planner专注于初始规划和完全重规划

---

## 快速查找指南

| 需求 | 查看文档 |
|-----|---------|
| 了解Agent如何调用Workflow | [05-Agent-Interface.md](./05-Agent-Interface.md) |
| 了解如何规划Workflow | [01-Planner规划器.md](./01-Planner规划器.md) |
| 了解如何编排执行流程 | [02-Orchestrator编排器.md](./02-Orchestrator编排器.md) |
| 了解如何训练和执行BAS | [03-Executor执行器.md](./03-Executor执行器.md) |
| 了解如何监控Workflow | [04-Monitor监控器.md](./04-Monitor监控器.md) |

---

## 延伸阅读

- [Meta-Workflow设计](../meta-workflows/)
- [执行模式详解](../execution-modes.md)
- [Workflow案例与示例](../examples/)
