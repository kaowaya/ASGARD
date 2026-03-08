# ASGARD Workflow架构设计

> 版本：V2.0 | 日期：2026-03-08 | 核心理念：Agent驱动的动态Workflow编排系统
> **V2.0更新**：新增Agent Interface层和Online Planner，实现动态自适应Workflow

---

## 渐进式披露原则

本文档采用**渐进式披露**的设计原则：
- **主文档**（本文件）：提供核心概念、快速查找指南、文件夹结构
- **详细子文档**：按需加载，深入了解特定主题

**目标**：降低主文档token数量，提升阅读体验，支持快速查找和深入学习。

---

## Workflow核心概念

### 什么是Workflow？

**Workflow（工作流）** = 由多个训练好的BAS（Battery Algorithm Skills）按照任务逻辑编排而成的有向无环图（DAG），是ASGARD交付给客户的核心价值载体。

**形式化定义**：
```
Workflow = (Nodes, Edges, Context, Constraints)

其中：
  Nodes: BAS节点的集合 [BAS₁, BAS₂, ..., BASₙ]
  Edges: 节点间的依赖关系（数据流、控制流）
  Context: 执行上下文（电池类型、工况、历史数据）
  Constraints: 约束条件（时效性、精度、算力）
```

---

### Workflow vs 单一BAS

| 维度 | 单一BAS | Workflow |
|-----|--------|---------|
| **功能** | 单一算法功能 | 复杂任务全流程解决 |
| **输入** | 原始数据 | 多源数据（V-I-T-历史-工况） |
| **输出** | 单一结果 | 决策报告 + 处置建议 + 持续监控 |
| **智能** | 算法模板 | Agent编排 + 自适应调整 |
| **价值** | 工具 | 解决方案 |

---

## Workflow的类型

### 1. Meta-Workflow（预制元工作流）

由ASGARD团队预定义的、覆盖最常见场景的Workflow模板。

**5大Meta-Workflow**（详见 [meta-workflows/](./meta-workflows/)）：
1. 热失控预防Workflow
2. 析锂延寿Workflow
3. 储能电站健康管理Workflow
4. 电池银行评估Workflow
5. 生产质量控制Workflow

**特点**：
- ✅ 经过实战验证，可靠性高
- ✅ 覆盖80%常见需求
- ✅ 可作为Custom Workflow的基础

---

### 2. Custom Workflow（个性化工作流）

客户基于Meta-Workflow，在Agent辅助下微调得到的个性化Workflow。

**微调维度**：
- BAS选择：添加/替换/删除Skills
- 参数调整：阈值、权重、优先级
- 执行策略：串行/并行、条件分支、循环迭代
- 输出定制：报告格式、通知方式、集成接口

**示例**：
```
Meta-Workflow: 析锂延寿Workflow
    ↓ 客户：东北地区出租营运车辆
    ↓
Custom Workflow: 极寒地区营运车辆充电优化Workflow
  - 添加：气象数据接口 → 环境感知
  - 调整：B2.5析锂阈值 → 低温环境优化
  - 强化：C3.7 ICA分析 → 极寒特征提取
```

**详细案例**：[examples/custom-workflow-极寒地区营运车辆充电优化.md](./examples/custom-workflow-极寒地区营运车辆充电优化.md)

---

### 3. Dynamic Workflow（动态自适应工作流）

在执行过程中，Agent根据实时数据和反馈动态调整执行路径的Workflow。

**自适应机制**：
```
正常路径：
  Step 1 → Step 2 → Step 3 → Step 4 → 完成

异常触发：
  Step 1 → Step 2 → [异常] → Agent重规划
                    ↓
              替代路径：Step 2.1 → Step 2.2 → Step 3
```

---

## Workflow引擎架构（V2.0）

```
┌─────────────────────────────────────────────────────────────────┐
│                        ASGARD Agent                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ NL理解引擎  │  │ Skills编排器│  │ 决策引擎    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                            ↓ API调用
┌�─────────────────────────────────────────────────────────────────┐
│              ⭐ Agent Interface Layer（V2.0新增）                  │
│  - REST API网关  - 请求路由  - 上下文管理  - 权限验证             │
└─────────────────────────────────────────────────────────────────┘
                            ↓ 调用
┌─────────────────────────────────────────────────────────────────┐
│                    Workflow引擎核心                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ⭐ Offline Planner（V2.0重命名）                         │  │
│  │  - 任务分解  - BAS选择  - 依赖分析  - 资源分配            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ⭐ Orchestrator（V2.0增强）                            │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │ ⭐ Online Planner（V2.0新增）                      │  │  │
│  │  │  - 运行时自主决策  - 故障恢复  - 性能优化      │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  │  - DAG构建  - 并行调度  - 条件分支  - 异常处理            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Workflow Executor（工作流执行器）                       │  │
│  │  - BAS训练器  - 模型推理  - 数据管理  - 结果聚合          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Workflow Monitor（工作流监控器）                        │  │
│  │  - 实时监控  - 性能分析  - 异常检测  - 日志审计            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**组件详解**：[components/](./components/)

---

## 快速查找指南

### 按主题查找

| 主题 | 文档路径 |
|-----|---------|
| **Meta-Workflow模板** | [meta-workflows/README.md](./meta-workflows/README.md) |
| - 热失控预防Workflow | [meta-workflows/01-热失控预防Workflow.md](./meta-workflows/01-热失控预防Workflow.md) |
| - 析锂延寿Workflow | [meta-workflows/02-析锂延寿Workflow.md](./meta-workflows/02-析锂延寿Workflow.md) |
| - 储能电站健康管理Workflow | [meta-workflows/03-储能电站健康管理Workflow.md](./meta-workflows/03-储能电站健康管理Workflow.md) |
| - 电池银行评估Workflow | [meta-workflows/04-电池银行评估Workflow.md](./meta-workflows/04-电池银行评估Workflow.md) |
| - 生产质量控制Workflow | [meta-workflows/05-生产质量控制Workflow.md](./meta-workflows/05-生产质量控制Workflow.md) |
| **Workflow组件** | [components/README.md](./components/README.md) |
| - Agent Interface（接口层） | [components/05-Agent-Interface.md](./components/05-Agent-Interface.md) |
| - Offline Planner（离线规划器） | [components/01-Planner规划器.md](./components/01-Planner规划器.md) |
| - Orchestrator（编排器） | [components/02-Orchestrator编排器.md](./components/02-Orchestrator编排器.md) |
| - Executor（执行器） | [components/03-Executor执行器.md](./components/03-Executor执行器.md) |
| - Monitor（监控器） | [components/04-Monitor监控器.md](./components/04-Monitor监控器.md) |
| **执行模式** | [execution-modes.md](./execution-modes.md) |
| **案例与示例** | [examples/README.md](./examples/README.md) |

---

### 按角色查找

| 角色 | 推荐阅读 |
|-----|---------|
| **产品经理** | 本文档（核心概念）+ [meta-workflows/](./meta-workflows/)（了解5大模板） |
| **算法工程师** | [components/](./components/)（深入了解四大组件）+ [execution-modes.md](./execution-modes.md) |
| **解决方案架构师** | 本文档 + [examples/](./examples/)（了解真实案例） |
| **客户** | 本文档 + [meta-workflows/](./meta-workflows/)（了解能解决什么问题） |

---

## 文件夹结构树

```
workflow/
├── README.md                           # 本文档（主入口）
├── meta-workflows/                    # Meta-Workflow模板
│   ├── README.md                      # Meta-Workflow概览
│   ├── 01-热失控预防Workflow.md
│   ├── 02-析锂延寿Workflow.md
│   ├── 03-储能电站健康管理Workflow.md
│   ├── 04-电池银行评估Workflow.md
│   └── 05-生产质量控制Workflow.md
├── components/                        # Workflow组件详解
│   ├── README.md                      # 组件概览
│   ├── 01-Planner规划器.md            # Offline Planner（V2.0重命名）
│   ├── 02-Orchestrator编排器.md       # V2.0集成Online Planner
│   ├── 03-Executor执行器.md
│   ├── 04-Monitor监控器.md
│   └── 05-Agent-Interface.md          # Agent接口层（V2.0新增）
├── execution-modes.md                 # 执行模式详解
└── examples/                          # 案例与示例
    ├── README.md                      # 案例概览
    └── custom-workflow-极寒地区营运车辆充电优化.md
```

---

## Workflow的核心价值

### 对客户

| 痛点 | 传统方案 | ASGARD Workflow |
|-----|---------|----------------|
| "我需要解决X问题" | 采购固定产品，功能不匹配 | Agent生成Custom Workflow，精准匹配 |
| "我有特殊工况" | 无法适配，需定制开发（周期长） | 基于Meta-Workflow微调，小时级 |
| "我要快速上线" | 集成开发、调试、部署（数月） | Agent编排+训练+部署，数周 |
| "我要持续优化" | 人工调参，版本升级（慢） | Agent持续学习，自动迭代 |

### 对ASGARD

| 优势 | 说明 |
|-----|------|
| **复用性** | BAS可跨Workflow复用，降低开发成本 |
| **可扩展** | 社区贡献新Skills → Workflow自动增强 |
| **数据飞轮** | 执行数据 → BAS优化 → Workflow更精准 |
| **技术壁垒** | Workflow编排know-how，竞品难以复制 |

---

## 技术创新点

| 创新点 | 说明 | 竞争优势 |
|-------|------|---------|
| **Agentic编排** | Agent自主生成Workflow | 零代码，低门槛 |
| **BAS模板化** | 算法模板 + 客户数据训练 | 快速适配，个性化 |
| **跨体系复用** | 第一性原理层100%通用 | 新电池3-6个月适配 |
| **混合执行** | 边缘实时 + 云端深度 | 低延迟 + 高精度 |
| **持续优化** | Agent自动学习迭代 | Workflow越用越好 |

---

## V2.0 完成情况

### ✅ 已完成（V2.0）
- [x] Agent Interface Layer 实现
- [x] Online Planner 运行时自主决策
- [x] Offline Planner 与 Online Planner 职责分离
- [x] Workflow Execution Context 状态管理
- [x] Orchestrator 集成 Online Planner
- [x] 向后兼容性保证
- [x] 完整的集成测试（17个测试全部通过）

### 下一步行动（V2.1 规划中）
- [ ] 构建5大Meta-Workflow模板
- [ ] 设计Skills市场API
- [ ] 开发Workflow监控Dashboard
- [ ] 建立Workflow版本管理规范
- [ ] 通过ISO 26262功能安全认证

---

## 联系方式

- **文档作者**：Claude Sonnet 4.5
- **更新日期**：2026-03-08
- **下次评审**：2026-04-15

---

**文档版本**：V2.0（Agent驱动动态Workflow架构）
**主文档token**：~3.5K
**详细内容**：按需加载子文档
