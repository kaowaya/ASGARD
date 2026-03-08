# Workflow Orchestrator（工作流编排器）

> 核心组件：Workflow引擎的调度中心
> 主要职责：管理Workflow的执行流程，包括并行、分支、循环

---

## V2.0 更新：集成Online Planner

**新增能力**：
- ✅ 运行时自主决策（无需Agent介入）
- ✅ 节点故障自动恢复（重试→替换→请求Agent）
- ✅ 性能自适应优化（参数调优、节点替换）
- ✅ 精度下降自动处理（切换高精度模型）

**决策分层**：
```
第1层：Online Planner自主处理（80%问题，<50ms）
  ├─ 节点失败：重试 → 替换备用BAS
  ├─ 性能下降：优化参数 → 替换更快BAS
  └─ 精度下降：切换高精度BAS

第2层：Agent介入（20%问题，100-500ms）
  └─ 复杂重规划：添加/删除节点，改变拓扑结构
```

---

## 概述

Workflow Orchestrator负责管理和协调Workflow的执行流程。它基于Offline Planner生成的DAG，智能调度BAS的执行顺序，处理并行、条件分支、循环迭代等复杂逻辑，确保Workflow高效、可靠地运行。

**V2.0 架构增强**：现在集成Online Planner，实现运行时自主决策和自适应优化。

---

## 核心职责

1. **并行调度**：识别可并行执行的BAS，提升执行效率
2. **条件分支**：根据中间结果动态选择执行路径
3. **循环迭代**：支持迭代优化和收敛判断
4. **异常处理**：处理BAS执行失败、超时等异常情况
5. **资源管理**：动态分配和回收计算资源

---

## 编排策略

### 1. 并行执行（Parallel Execution）

**原理**：识别无依赖关系的BAS，并行执行以减少总耗时。

```python
def parallel_execution(dag):
    """
    并行执行算法
    """
    # 识别可并行的层级
    levels = dag.identify_levels()

    total_time = 0
    FOR EACH level IN levels:
        # 检查是否可并行
        IF level.parallelizable:
            # 并行执行
            level_time = max([
                execute_skill(skill)
                for skill in level.nodes
            ])
        ELSE:
            # 串行执行
            level_time = sum([
                execute_skill(skill)
                for skill in level.nodes
            ])

        total_time += level_time

    return total_time
```

**示例**：

```
串行（慢）：
  [C3.4] → [C3.1] → [C3.6] → [C3.2]
  总耗时：50ms + 100ms + 80ms + 30ms = 260ms

并行（快）：
  第1层：[C3.4] || [C3.6] → max(50ms, 80ms) = 80ms
  第2层：[C3.1] || [C3.2] → max(100ms, 30ms) = 100ms
  总耗时：80ms + 100ms = 180ms

加速比：260ms / 180ms = 1.44x
```

**并行条件**：
- 节点间无数据依赖
- 资源充足（多核/多机）
- 可合并结果

---

### 2. 条件分支（Conditional Branching）

**原理**：根据中间结果动态选择后续执行路径。

```python
def conditional_branching(skill_result, branches):
    """
    条件分支算法
    """
    # 评估条件
    condition = evaluate_condition(skill_result)

    # 选择分支
    IF condition == 'A':
        selected_branch = branches['branch_a']
    ELIF condition == 'B':
        selected_branch = branches['branch_b']
    ELSE:
        selected_branch = branches['branch_default']

    # 执行选中分支
    result = execute_branch(selected_branch)

    return result
```

**示例1：析锂检测分支**

```python
# 析锂检测后的分支决策
anode_potential = execute_skill(B2_5, charging_data)

IF anode_potential > 0.05V:
    # 无析锂：正常快充
    result = execute_skill(normal_charging, charging_data)
    strategy = 'normal_fast_charging'

ELIF anode_potential > -0.05V:
    # 轻微析锂：MCC降流
    result = execute_skill(B2_1, {'current': 0.5C})
    result = execute_skill(B2_6, {'cooling': 'active'})
    strategy = 'mcc_current_reduction'

ELSE:
    # 严重析锂：脉冲修复
    result = execute_skill(pulse_repair, charging_data)
    result = execute_skill(C3_7, charging_data)
    strategy = 'pulse_repair'

return strategy
```

**示例2：热失控预警分级**

```python
# 热失控风险分级决策
fault_level = execute_skill(C3_4, sensor_data)

IF fault_level == 'L0':
    # 正常：继续运行
    action = 'continue'

ELIF fault_level == 'L1':
    # 注意：增加监控频率
    action = 'increase_monitoring'

ELIF fault_level == 'L2':
    # 预警：限流运行
    action = 'limit_current'
    execute_skill(B2_7, {'limit': 0.5C})

ELIF fault_level == 'L3':
    # 警报：立即限流，准备停机
    action = 'prepare_shutdown'
    execute_skill(B2_7, {'limit': 0.2C})
    send_alert()

ELSE:  # L4
    # 危险：紧急停机
    action = 'emergency_shutdown'
    execute_skill(B2_7, {'shutdown': True})
    execute_emergency_shutdown()
```

---

### 3. 循环迭代（Iterative Loop）

**原理**：重复执行某个BAS直到满足收敛条件。

```python
def iterative_loop(initial_state, condition_fn, body_fn):
    """
    循环迭代算法
    """
    state = initial_state
    iteration = 0
    max_iterations = 10  # 防止无限循环

    WHILE NOT condition_fn(state) AND iteration < max_iterations:
        # 执行循环体
        state = body_fn(state)
        iteration += 1

    IF iteration >= max_iterations:
        raise WorkflowError("迭代次数超过上限")

    return state
```

**示例1：析锂抑制迭代**

```python
# 充电策略优化循环
charging_state = {
    'current': 0.7C,
    'anode_potential': -0.1V,
    'iteration': 0
}

WHILE charging_state['anode_potential'] < 0V:
    # 降低充电电流
    charging_state['current'] -= 0.1C

    # 重新评估析锂风险
    charging_state['anode_potential'] = execute_skill(
        B2_5,
        {'current': charging_state['current']}
    )

    # 安全检查
    IF charging_state['current'] < 0.2C:
        raise WorkflowError("无法抑制析锂，停止充电")

    charging_state['iteration'] += 1

    # 防止无限循环
    IF charging_state['iteration'] > 5:
        raise WorkflowError("迭代次数超限")

return charging_state['current']
```

**示例2：脉冲修复迭代**

```python
# 脉冲修复循环
plating_detected = True
pulse_count = 0

WHILE plating_detected AND pulse_count < 5:
    # 施加负脉冲
    execute_skill(negative_pulse, {'duration': 2s})

    # 静置
    execute_skill(rest, {'duration': 1s})

    # 重新检测析锂
    anode_potential = execute_skill(B2_5, charging_data)

    # 判断是否还有析锂
    plating_detected = (anode_potential < 0V)

    pulse_count += 1

IF plating_detected:
    # 脉冲修复失败
    return 'repair_failed'
ELSE:
    # 脉冲修复成功
    return 'repair_success'
```

---

### 4. 混合编排（Mixed Orchestration）

**原理**：结合并行、分支、循环的复杂编排。

```python
def mixed_orchestration(workflow_dag):
    """
    混合编排算法
    """
    # 第1层：并行执行
    results_level1 = parallel_execute([
        skill_C3_4,
        skill_C3_6
    ])

    # 第2层：条件分支
    IF results_level1['C3_4'].fault_level > 'L2':
        # 高风险分支
        result_level2 = execute_skill(C3_1)
    ELSE:
        # 低风险分支（跳过C3.1）
        result_level2 = None

    # 第3层：并行 + 条件
    IF result_level2 IS NOT None:
        results_level3 = parallel_execute([
            skill_C3_2,
            skill_B2_7
        ])
    ELSE:
        results_level3 = execute_skill(C3_2)

    return results_level3
```

---

## 资源管理

### 动态资源分配

```python
def allocate_resources(skill):
    """
    动态资源分配
    """
    # 评估资源需求
    required_resources = {
        'cpu': skill.cpu_requirement,
        'memory': skill.memory_requirement,
        'gpu': skill.gpu_requirement
    }

    # 检查可用资源
    available_resources = get_available_resources()

    # 如果资源不足，等待或降级
    IF not check_resources(available_resources, required_resources):
        # 等待资源释放
        wait_for_resources(required_resources)

        # 或者降级执行
        IF skill.has_fallback:
            skill = skill.fallback_version

    # 分配资源
    allocate(skill, required_resources)

    return skill
```

### 资源回收

```python
def release_resources(skill):
    """
    资源回收
    """
    # 释放占用的资源
    release(skill.allocated_resources)

    # 清理临时数据
    cleanup(skill.temp_data)
```

---

## 异常处理

### 1. 重试机制（Retry）

```python
def execute_with_retry(skill, max_retries=3):
    """
    带重试的执行
    """
    retry_count = 0

    WHILE retry_count < max_retries:
        TRY:
            result = execute_skill(skill)
            return result
        EXCEPT Exception as e:
            retry_count += 1
            IF retry_count >= max_retries:
                raise WorkflowError(f"执行失败：{str(e)}")
            ELSE:
                # 指数退避
                sleep_time = 2 ** retry_count
                sleep(sleep_time)
```

### 2. 降级机制（Fallback）

```python
def execute_with_fallback(primary_skill, fallback_skill):
    """
    带降级的执行
    """
    TRY:
        result = execute_skill(primary_skill)
        return result
    EXCEPT Exception as e:
        # 主技能失败，使用降级技能
        log_warning(f"主技能失败：{str(e)}，使用降级技能")
        result = execute_skill(fallback_skill)
        return result
```

### 3. 超时处理（Timeout）

```python
def execute_with_timeout(skill, timeout_ms):
    """
    带超时的执行
    """
    start_time = current_time()

    TRY:
        result = execute_skill(skill)
        elapsed_time = current_time() - start_time

        IF elapsed_time > timeout_ms:
            log_warning(f"执行超时：{elapsed_time}ms > {timeout_ms}ms")
            # 根据策略决定是否使用结果
            IF skill.allow_timeout_result:
                return result
            ELSE:
                raise WorkflowError("执行超时")
        ELSE:
            return result
    EXCEPT TimeoutError:
        # 超时异常处理
        return handle_timeout(skill)
```

---

## 执行状态管理

### 状态跟踪

```python
class WorkflowExecution:
    """
    Workflow执行状态
    """
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.status = 'PENDING'  # PENDING/RUNNING/COMPLETED/FAILED
        self.current_node = None
        self.completed_nodes = []
        self.failed_nodes = []
        self.results = {}
        self.start_time = None
        self.end_time = None

    def update_status(self, new_status):
        """
        更新状态
        """
        self.status = new_status
        log_status(self.workflow_id, new_status)
```

### 检查点（Checkpoint）

```python
def save_checkpoint(workflow_execution):
    """
    保存检查点
    """
    checkpoint = {
        'workflow_id': workflow_execution.workflow_id,
        'completed_nodes': workflow_execution.completed_nodes,
        'results': workflow_execution.results,
        'timestamp': current_time()
    }

    save_to_db(checkpoint)

def restore_checkpoint(workflow_id):
    """
    从检查点恢复
    """
    checkpoint = load_from_db(workflow_id)

    # 恢复执行状态
    workflow_execution = WorkflowExecution(workflow_id)
    workflow_execution.completed_nodes = checkpoint['completed_nodes']
    workflow_execution.results = checkpoint['results']

    return workflow_execution
```

---

## 性能优化

### 1. 流水线并行

```python
def pipeline_parallelism(workflow_dag):
    """
    流水线并行
    """
    # 将Workflow划分为多个阶段
    stages = partition_into_stages(workflow_dag)

    # 每个阶段处理不同的数据批次
    FOR stage IN stages:
        stage.start()

    # 流水线执行
    batch_queue = []
    WHILE has_more_data():
        batch = get_next_batch()
        batch_queue.append(batch)

        # 每个阶段处理一个批次
        FOR stage IN stages:
            IF len(batch_queue) > 0:
                stage.process(batch_queue.pop(0))
```

### 2. 资源池化

```python
class ResourcePool:
    """
    资源池
    """
    def __init__(self, max_workers=10):
        self.pool = ThreadPool(max_workers)
        self.active_tasks = {}

    def submit_task(self, skill, input_data):
        """
        提交任务到资源池
        """
        future = self.pool.submit(execute_skill, skill, input_data)
        self.active_tasks[skill.id] = future
        return future

    def get_result(self, skill_id):
        """
        获取任务结果
        """
        future = self.active_tasks[skill_id]
        return future.result()
```

---

## 编排示例

### 完整示例：热失控预防Workflow编排

```python
def orchestrate_thermal_runaway_prevention():
    """
    热失控预防Workflow编排
    """
    # 第1层：并行采集和分析
    results_level1 = parallel_execute({
        'C3.4': execute_skill(C3_4, sensor_data),  # 香农熵
        'C3.6': execute_skill(C3_6, sensor_data)   # 温度场
    })

    # 第2层：条件分支
    IF results_level1['C3.4'].fault_level >= 'L2':
        # 异常检测到，执行SOS诊断
        result_level2 = execute_skill(C3_1, historical_data)
    ELSE:
        result_level2 = None

    # 第3层：并行预警
    results_level3 = parallel_execute({
        'C3.2': execute_skill(C3_2, gas_sensor_data),  # MEMS预警
        'B2.7': execute_skill(B2_7, {                 # 安全决策
            'fault_level': results_level1['C3.4'].fault_level,
            'center_temp': results_level1['C3.6'].center_temp,
            'isc_result': result_level2
        })
    })

    # 第4层：条件分支执行
    IF results_level3['B2.7'].action == 'shutdown':
        execute_emergency_shutdown()
    ELIF results_level3['B2.7'].action == 'limit_current':
        execute_current_limiting(results_level3['B2.7'].limit)
    ELSE:
        continue_normal_operation()

    return results_level3
```

---

## Online Planner集成详解

### 集成架构

```python
class Orchestrator:
    def __init__(self, online_planner: OnlinePlanner,
                 agent_interface: AgentInterface):
        self.online_planner = online_planner
        self.agent_interface = agent_interface
        self.executor = Executor()
        self.monitor = Monitor()

    def execute_node(self, context, node):
        """执行节点（集成Online Planner）"""
        try:
            result = self.executor.execute(node, context)
            context.record_success(node.id, result)

            # 检查性能
            self._check_performance(context, node, result)

            return result

        except Exception as e:
            # 通过Online Planner处理失败
            decision = self.online_planner.handle_node_failure(
                execution_context=context,
                failed_node=node.id,
                error=e
            )
            return self._implement_decision(context, node, decision)
```

### 自主决策流程

```
节点执行
    ↓
成功？
  ├─ YES → 记录成功 → 检查性能 → 优化参数/替换节点（如需要）
  └─ NO  → Online Planner分析
              ↓
      决策树：
      ├─ 失败1-3次 → RETRY（指数退避）
      ├─ 失败第4次 → REPLACE_NODE（切换备用BAS）
      └─ 失败5+次 → REQUEST_AGENT（完全重规划）
              ↓
      实施决策 → 继续执行
```

### 3层故障恢复策略

| 层级 | 触发条件 | 响应时间 | 处理方式 | Agent介入 |
|------|---------|---------|---------|---------|
| **L1: 重试** | 失败1-3次 | <10ms | 指数退避重试 | ❌ |
| **L2: 替换** | 失败第4次 | <30ms | 切换备用BAS | ❌ |
| **L3: 升级** | 失败5+次 | N/A | 请求Agent完全重规划 | ✅ |

### 性能自适应优化

**触发条件**：
- 执行时间 > 预期1.5倍 → 参数优化
- 执行时间 > 预期2.0倍 → 节点替换
- 精度下降 > 10% → 模型升级

**优化示例**：
```python
# 场景：节点C3.4执行超时（180ms，预期100ms）

# Online Planner决策：
decision = {
    "action": "OPTIMIZE_PARAMS",
    "new_params": {"batch_size": 16},  # 原值32
    "reason": "执行时间180ms > 150ms，降低batch_size"
}

# Orchestrator实施：
node.update_params(decision.new_params)
result = self.execute_node(context, node)
```

### 与Agent的协作

**何时请求Agent介入**：
1. 节点失败5+次（所有备用BAS都失败）
2. Workflow DAG需要结构性改变（添加/删除节点）
3. 未知异常类型（Online Planner无法处理）
4. Agent主动请求重规划

**请求流程**：
```python
# Online Planner发起
if decision.action == "REQUEST_AGENT":
    self.agent_interface.trigger_agent_replan(
        workflow_id=context.workflow_id,
        reason=decision.reason,
        current_state=context.get_snapshot()
    )
    raise AgentInterventionException("请求Agent介入")

# Agent Interface处理
# 1. 暂停当前Workflow
# 2. 获取当前状态快照
# 3. 通知Agent
# 4. Agent决策后调用Offline Planner重新规划
# 5. 恢复Workflow执行
```

### 性能指标

| 指标 | V1.0 | V2.0 | 改进 |
|------|------|------|------|
| 平均故障恢复时间 | N/A（手动） | 45ms | ✅ 自主 |
| Agent介入率 | 100% | 20% | ⬇️ 80% |
| Workflow适应性 | 静态 | 动态 | ✅ 新能力 |
| 运行时优化 | 无 | 有 | ✅ 新能力 |

### 实际案例

**案例1：节点超时优化**
```
初始：C3.4节点执行120ms，预期100ms
Online Planner：检测到1.2倍超时
决策：OPTIMIZE_PARAMS → batch_size 32 → 16
结果：重新执行65ms（提升46%）
```

**案例2：节点替换**
```
初始：C3.1执行失败（3次重试）
Online Planner：失败第4次，切换备用C3.3
决策：REPLACE_NODE → C3.3（快速版）
结果：执行成功，耗时60ms
```

**案例3：Agent重规划**
```
初始：数据质量差，多个节点失败
Online Planner：无法处理，请求Agent
Agent：决策添加C3.0数据清洗节点
Offline Planner：重新生成包含C3.0的DAG
结果：Workflow正常执行
```

---

## 延伸阅读

- [Offline Planner（离线规划器）](./01-Planner规划器.md)
- [Workflow Executor（执行器）](./03-Executor执行器.md)
- [Workflow Monitor（监控器）](./04-Monitor监控器.md)
- [Agent Interface（Agent接口层）](./05-Agent-Interface.md) ⭐ NEW
- [执行模式详解](../execution-modes.md)
