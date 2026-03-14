# ASGARD Agent 工作流编排示范

本示例展示了 ASGARD v2.0.0 架构下，Agent 如何作为“大脑”进行任务编排，而 Workflow Engine 作为“骨架与肌肉”进行执行。

## 1. 核心流程

1.  **用户定义任务 (NL)**: 用户输入自然语言任务，例如“分析某 Pack 的安全性”。
2.  **Agent 初始规划**: Agent 调用 `AgentInterface.create_workflow`，触发布置在服务端的 **Offline Planner** 生成初始 DAG。
3.  **自主运行时适配**: **Orchestrator** 启动，其内置的 **Online Planner** 负责处理简单故障（如节点重试或轻量级替换），无需 Agent 介入（<50ms 决策）。
4.  **Agent 升级处理**: 当 Online Planner 无法处理（如算法持续不收敛）或任务目标改变时，Agent 通过 `replan` 接口进行深度干预。

## 2. 运行示范

确保环境已安装 Python。

```bash
python d:/ASGARD/workflow/demo_agent_orchestration.py
```

## 3. 代码片段说明

### 发起请求
```python
response = interface.create_workflow(
    workflow_id="WF-001",
    task="分析电芯析锂风险",
    context={"battery": "LFP"}
)
```

### 动态重规划
当 Agent 发现数据噪声过大影响了析锂检测 (C3.13) 的精度时，可以动态插入一个数据清洗节点 (C3.0)：

```python
interface.replan(
    workflow_id="WF-001",
    new_task="增加滤波预处理后重新检测析锂",
    context={"add_node": "C3.0-ButterworthFilter"}
)
```

## 4. 架构优势 (第一性原理)
- **解耦**: Agent 负责“做什么 (What)”，Workflow 负责“怎么做 (How)”。
- **性能**: 80% 的执行异常由 Online Planner 本地闭环处理，极大降低了长链条通信延迟。
- **动态性**: DAG 不再是僵化的配置，而是可在运行时根据电化学边界条件（如 OCV 平台期变化）自主进化的。
