# Offline Planner（离线规划器）

> **V2.0 更新说明**：
> - 原"Planner"重命名为"Offline Planner"以区别于Online Planner
> - 现在仅在初始规划和完全重规划时由Agent调用
> - 不再负责运行时调整（由Online Planner负责）
> - 提供向后兼容wrapper：`from workflow.engine.planner.planner import Planner`

---

## 概述

Offline Planner是ASGARD Workflow引擎的核心组件，负责将用户的自然语言需求转化为可执行的Workflow DAG（有向无环图）。它通过任务分解、BAS匹配、依赖分析和资源分配，生成最优的执行计划。

---

## 输入与输出

### 输入

| 输入项 | 说明 | 示例 |
|-------|------|------|
| **用户任务** | 自然语言描述的需求 | "分析储能电站热失控风险" |
| **电池类型** | 目标电池化学体系 | LFP/NCM/Na-ion/固态 |
| **应用场景** | 应用领域 | 储能/电动车/生产 |
| **约束条件** | 算力、时效、精度要求 | 响应时间<200ms，精度>95% |
| **历史数据** | 客户的历史运行数据 | 充放电曲线、温度记录 |

### 输出

| 输出项 | 说明 | 格式 |
|-------|------|------|
| **Workflow DAG** | 有向无环图 | JSON/DOT格式 |
| **BAS列表** | 选中的BAS及配置 | [{"skill": "C3.4", "params": {...}}] |
| **执行计划** | 资源、时间、依赖关系 | 调度计划表 |
| **预估指标** | 预计的执行时间、精度 | {"latency": "150ms", "accuracy": "96%"} |

---

## 规划算法

### 完整规划流程

```python
def plan_workflow(user_task, context):
    """
    Workflow规划主函数
    """
    # Step 1: 任务分解
    subtasks = decompose_task(user_task)

    # Step 2: BAS匹配（从Skills市场检索）
    candidate_skills = search_skills_market(subtasks)

    # Step 3: BAS筛选（基于约束条件）
    selected_skills = filter_skills(candidate_skills, context)

    # Step 4: 依赖分析
    dependencies = analyze_dependencies(selected_skills)

    # Step 5: DAG构建
    workflow_dag = build_dag(selected_skills, dependencies)

    # Step 6: 资源分配
    execution_plan = allocate_resources(workflow_dag, context)

    return workflow_dag, execution_plan
```

---

### Step 1: 任务分解（Task Decomposition）

将复杂任务分解为可执行的子任务。

```python
def decompose_task(user_task):
    """
    任务分解算法
    """
    # 使用NLP理解用户意图
    intent = understand_intent(user_task)

    # 识别关键实体
    entities = extract_entities(user_task)

    # 分解为子任务
    subtasks = []

    IF intent == 'SAFETY_ANALYSIS':
        subtasks = [
            'identify_abnormal_cells',      # 识别异常电芯
            'diagnose_internal_short',      # 诊断内短路
            'predict_thermal_runaway',      # 预测热失控
            'generate_safety_strategy'      # 生成安全策略
        ]

    ELIF intent == 'LIFETIME_OPTIMIZATION':
        subtasks = [
            'detect_lithium_plating',       # 检测析锂
            'optimize_charging_strategy',   # 优化充电策略
            'manage_thermal',               # 热管理
            'validate_effect'               # 效果验证
        ]

    # 为每个子任务提取关键参数
    FOR subtask IN subtasks:
        subtask.params = extract_params(subtask, entities)

    return subtasks
```

**示例**：
```
用户任务："分析储能电站热失控风险"
↓
子任务分解：
  1. identify_abnormal_cells（识别异常电芯）
  2. diagnose_internal_short（诊断内短路）
  3. predict_thermal_runaway（预测热失控）
  4. generate_safety_strategy（生成安全策略）
```

---

### Step 2: BAS匹配（Skill Matching）

从Skills市场检索匹配的BAS。

```python
def search_skills_market(subtasks):
    """
    BAS匹配算法
    """
    candidates = []

    FOR EACH subtask IN subtasks:
        # 向量检索（基于语义相似度）
        relevant_skills = vector_search(
            query=subtask.description,
            collection=skills_market,
            top_k=10
        )

        # 关键词匹配（精确匹配）
        keyword_matches = keyword_search(
            keywords=subtask.keywords,
            collection=skills_market
        )

        # 合并结果并去重
        matched_skills = merge_and_dedup(
            relevant_skills,
            keyword_matches
        )

        candidates.extend(matched_skills)

    return candidates
```

**检索策略**：

| 策略 | 适用场景 | 示例 |
|-----|---------|------|
| **向量检索** | 语义理解 | "检测异常" → ["异常检测", "故障诊断"] |
| **关键词匹配** | 精确匹配 | "SOH" → ["SOH估计", "SOH集成"] |
| **层级过滤** | 按层级筛选 | Tier筛选（L1/L2/L3/L4） |
| **电池类型** | 化学体系兼容 | LFP专用/通用算法 |

---

### Step 3: BAS筛选（Skill Filtering）

基于约束条件筛选最优BAS。

```python
def filter_skills(candidate_skills, context):
    """
    BAS筛选算法
    """
    selected_skills = []

    FOR EACH subtask IN context.subtasks:
        # 获取该子任务的候选BAS
        candidates = [s for s in candidate_skills
                     if s.subtask == subtask]

        # 评分排序
        scored_skills = []
        FOR EACH skill IN candidates:
            score = calculate_skill_score(skill, context)
            scored_skills.append((skill, score))

        # 选择Top-K（默认Top-3）
        top_k_skills = sorted(
            scored_skills,
            key=lambda x: x[1],
            reverse=True
        )[:context.top_k]

        selected_skills.extend(top_k_skills)

    return selected_skills

def calculate_skill_score(skill, context):
    """
    BAS评分函数
    """
    score = 0

    # 维度1: 功能匹配度（40%权重）
    score += skill.functionality_match * 0.4

    # 维度2: 电池类型兼容性（30%权重）
    IF skill.supports(context.battery_type):
        score += 0.3
    ELIF skill.is_universal:
        score += 0.15

    # 维度3: 算力需求适配（20%权重）
    IF skill.compute_requirement <= context.available_compute:
        score += 0.2
    ELIF skill.compute_requirement <= context.available_compute * 1.5:
        score += 0.1

    # 维度4: 社区评分（10%权重）
    score += skill.community_rating * 0.1

    return score
```

**评分维度**：

| 维度 | 权重 | 评分标准 |
|-----|------|---------|
| **功能匹配度** | 40% | 语义相似度、关键词匹配度 |
| **电池类型兼容** | 30% | 完全兼容0.3，通用0.15，不兼容0 |
| **算力需求** | 20% | 满足0.2，略超0.1，不满足0 |
| **社区评分** | 10% | 0-1之间的归一化评分 |

---

### Step 4: 依赖分析（Dependency Analysis）

分析BAS间的数据依赖关系。

```python
def analyze_dependencies(skills):
    """
    依赖分析算法
    """
    # Step 1: 提取输入输出
    FOR EACH skill IN skills:
        skill.inputs = extract_inputs(skill.signature)
        skill.outputs = extract_outputs(skill.signature)

    # Step 2: 构建依赖图
    dependency_graph = {}
    FOR EACH skill_a IN skills:
        dependency_graph[skill_a] = []
        FOR EACH skill_b IN skills:
            IF skill_a != skill_b:
                # 检查是否存在数据依赖
                IF has_dependency(skill_a.outputs, skill_b.inputs):
                    dependency_graph[skill_a].append(skill_b)

    # Step 3: 检测循环依赖
    IF has_cycle(dependency_graph):
        raise WorkflowError("检测到循环依赖，无法构建DAG")

    # Step 4: 拓扑排序
    execution_order = topological_sort(dependency_graph)

    return execution_order

def has_dependency(outputs_a, inputs_b):
    """
    判断两个BAS是否存在依赖关系
    """
    # 简单版本：输出名称匹配输入名称
    FOR output IN outputs_a:
        IF output IN inputs_b:
            return True
    return False
```

**依赖类型**：

| 类型 | 说明 | 示例 |
|-----|------|------|
| **数据依赖** | B需要A的输出作为输入 | C3.1 → C3.2（诊断结果 → 预警） |
| **控制依赖** | B的执行条件依赖于A的结果 | 异常检测 → 安全策略（IF异常 THEN执行） |
| **顺序依赖** | B必须在A之后执行（无数据传递） | 充电 → 放电（时间顺序） |

---

### Step 5: DAG构建（Build DAG）

构建有向无环图。

```python
def build_dag(skills, dependencies):
    """
    DAG构建算法
    """
    # 初始化DAG
    dag = DAG()

    # 添加节点
    FOR EACH skill IN skills:
        dag.add_node(skill.id, skill)

    # 添加边（基于依赖关系）
    FOR EACH skill_a, dependents IN dependencies.items():
        FOR EACH skill_b IN dependents:
            dag.add_edge(skill_a.id, skill_b.id)

    # 优化DAG（识别可并行节点）
    dag = optimize_dag_structure(dag)

    return dag

def optimize_dag_structure(dag):
    """
    优化DAG结构，识别并行机会
    """
    # 识别可并行执行的层级
    levels = dag.identify_levels()

    # 每个层级内的节点可并行
    FOR level IN levels:
        parallelizable = True
        FOR node IN level:
            IF node.sequential_required:
                parallelizable = False
                BREAK

        level.parallelizable = parallelizable

    return dag
```

---

### Step 6: 资源分配（Resource Allocation）

为每个BAS分配计算资源。

```python
def allocate_resources(dag, context):
    """
    资源分配算法
    """
    execution_plan = {}

    # 遍历DAG的每一层
    FOR level IN dag.levels:
        # 计算该层总资源需求
        total_compute = sum([
            skill.compute_requirement
            for skill in level.nodes
        ])

        # 检查资源是否充足
        IF total_compute <= context.available_compute:
            # 资源充足，并行执行
            FOR skill IN level.nodes:
                execution_plan[skill] = {
                    'compute': skill.compute_requirement,
                    'parallel': True,
                    'estimated_time': skill.estimated_time
                }
        ELSE:
            # 资源不足，串行化
            FOR skill IN level.nodes:
                execution_plan[skill] = {
                    'compute': skill.compute_requirement,
                    'parallel': False,
                    'estimated_time': skill.estimated_time
                }

    return execution_plan
```

---

## 规划示例

### 示例：储能电站热失控风险分析

```
用户任务："分析储能电站热失控风险"

Step 1: 任务分解
  ├─ identify_abnormal_cells（识别异常电芯）
  ├─ diagnose_internal_short（诊断内短路）
  ├─ predict_thermal_runaway（预测热失控）
  └─ generate_safety_strategy（生成安全策略）

Step 2: BAS匹配
  ├─ identify_abnormal_cells → [C3.4, C3.6]
  ├─ diagnose_internal_short → [C3.1]
  ├─ predict_thermal_runaway → [C3.2]
  └─ generate_safety_strategy → [B2.7]

Step 3: BAS筛选
  ├─ C3.4（香农熵异常检测）- 评分：0.92
  ├─ C3.6（温度场重构）- 评分：0.88
  ├─ C3.1（SOS内短路诊断）- 评分：0.95
  ├─ C3.2（MEMS热失控预警）- 评分：0.90
  └─ B2.7（主动安全控制）- 评分：0.93

Step 4: 依赖分析
  ├─ C3.4 → C3.1（先识别异常，再诊断原因）
  ├─ C3.6 → C3.2（温度预测 → 热失控预警）
  └─ C3.1 + C3.2 → B2.7（诊断结果 → 安全策略）

Step 5: DAG构建
  [C3.4] ──┐
           ├─→ [C3.1] ──┐
  [C3.6] ──┘            ├─→ [B2.7]
                       [C3.2] ──┘

Step 6: 资源分配
  ├─ 第1层：C3.4 || C3.6（并行）
  ├─ 第2层：C3.1 || C3.2（并行）
  └─ 第3层：B2.7（串行）

预估执行时间：
  ├─ 第1层：max(50ms, 80ms) = 80ms
  ├─ 第2层：max(100ms, 30ms) = 100ms
  └─ 第3层：20ms
  └─ 总计：200ms（满足<200ms要求）
```

---

## Meta-Workflow匹配

Planner还负责匹配最合适的Meta-Workflow作为基础。

```python
def match_meta_workflow(user_task, context):
    """
    Meta-Workflow匹配算法
    """
    # 计算与每个Meta-Workflow的相似度
    similarities = {}
    FOR EACH meta_workflow IN meta_workflow_library:
        similarity = calculate_similarity(
            user_task,
            meta_workflow.description
        )
        similarities[meta_workflow] = similarity

    # 选择相似度最高的
    best_match = max(similarities, key=similarities.get)

    # 如果相似度 > 阈值，使用该Meta-Workflow
    IF similarities[best_match] > 0.7:
        return best_match
    ELSE:
        # 相似度不足，从头规划
        return None
```

**5大Meta-Workflow匹配特征**：

| Meta-Workflow | 关键词特征 | 应用场景 |
|--------------|-----------|---------|
| 热失控预防 | 安全、预警、内短路、储能 | 储能电站、UPS |
| 析锂延寿 | 析锂、充电、寿命、营运车辆 | 出租车、快充 |
| 储能健康管理 | SOH、RUL、资产、收益 | 工商业储能 |
| 电池银行评估 | 梯次、退役、回收、分级 | 电池回收厂 |
| 生产质量控制 | 生产、质检、缺陷、化成 | 电池制造商 |

---

## 性能优化

### 1. 缓存机制

```python
# 缓存常见任务的规划结果
IF cache.exists(user_task_hash):
    return cache.get(user_task_hash)
ELSE:
    plan = plan_workflow(user_task, context)
    cache.set(user_task_hash, plan)
    return plan
```

### 2. 增量规划

```python
# 对于微调任务，基于现有Workflow增量修改
IF is_fine_tuning_task(user_task):
    base_workflow = load_workflow(base_workflow_id)
    new_workflow = incremental_plan(base_workflow, changes)
    return new_workflow
```

### 3. 并行规划

```python
# 并行执行多个子任务的BAS匹配
subtasks = decompose_task(user_task)
candidate_skills = Parallel.map(
    search_skills_market,
    subtasks
)
```

---

## Offline vs Online Planner

**V2.0 架构引入双Planner设计**：

| 维度 | Offline Planner | Online Planner |
|------|----------------|---------------|
| **调用时机** | 初始规划、Agent重规划 | 运行时自主决策 |
| **规划范围** | 完整Workflow DAG | 局部调整（单节点/参数） |
| **响应时间** | 100-500ms | <50ms |
| **决策者** | Agent主导 | Orchestrator自主 |
| **适用场景** | 创建Workflow、复杂重规划 | 性能优化、故障恢复 |
| **调用方式** | 通过Agent Interface | 由Orchestrator集成 |

**职责划分**：

```
Offline Planner（离线规划）：
├─ 任务分解（复杂 → 子任务）
├─ BAS匹配（从Skills市场检索）
├─ 依赖分析（构建完整DAG）
├─ 资源分配（全局优化）
└─ 生成执行计划

Online Planner（在线规划）：
├─ 节点失败处理（重试/替换/升级）
├─ 性能优化（参数调优）
├─ 精度维护（模型切换）
└─ 资源动态调整
```

**协作模式**：

```
场景1：正常执行
  Agent → Offline Planner → 初始DAG → Orchestrator → Online Planner（运行时优化）

场景2：运行时故障
  Online Planner → 自主处理（80%问题）
    ↓ 无法处理
  Online Planner → Agent → Offline Planner → 完全重规划

场景3：Agent主动重规划
  Agent → Agent Interface → Offline Planner → 新DAG → Orchestrator
```

---

## V2.0 架构定位

**在Workflow引擎中的位置**：

```
Agent
  ↓ (通过Agent Interface)
Agent Interface Layer
  ↓ 调用
┌─────────────────────────────────────┐
│  Offline Planner（离线规划器）     │
│  - 初始规划                           │
│  - 完全重规划                         │
│  - Meta-Workflow匹配                │
└─────────────────────────────────────┘
          ↓ 生成DAG
┌─────────────────────────────────────┐
│  Orchestrator（编排器）              │
│  └─ Online Planner（在线规划器）    │
│     - 运行时自主决策                  │
└─────────────────────────────────────┘
```

**关键设计决策**：

1. **职责分离**：Offline Planner负责"宏观规划"，Online Planner负责"微调适配"
2. **性能优化**：80%的运行时问题由Online Planner<50ms内处理，无需Agent介入
3. **渐进增强**：Workflow可以从静态（仅Offline Planner）演进到动态（双Planner）
4. **向后兼容**：保留旧的`Planner`导入方式，平滑迁移路径

---

## 延伸阅读

- [Workflow Orchestrator（编排器）](./02-Orchestrator编排器.md)
- [Workflow Executor（执行器）](./03-Executor执行器.md)
- [Workflow Monitor（监控器）](./04-Monitor监控器.md)
- [Agent Interface（Agent接口层）](./05-Agent-Interface.md) ⭐ NEW
- [执行模式详解](../execution-modes.md)
