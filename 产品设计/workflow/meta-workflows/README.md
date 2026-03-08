# Meta-Workflow（预制元工作流）

> 概述：ASGARD预定义的、覆盖最常见场景的Workflow模板

---

## 什么是Meta-Workflow？

**Meta-Workflow** = 由ASGARD团队预定义的Workflow模板，覆盖80%常见需求。

**特点**：
- ✅ 经过实战验证，可靠性高
- ✅ 可作为Custom Workflow的基础
- ✅ 持续优化，社区贡献

---

## 5大Meta-Workflow

### 1. 热失控预防Workflow

**详细文档**：[01-热失控预防Workflow.md](./01-热失控预防Workflow.md)

**核心目标**：提前2个月预警热失控，实现零事故

**应用场景**：
- 储能电站
- 大型电池包
- 数据中心UPS

**关键BAS**：C3.4、C3.6、C3.1、C3.2、B2.7

---

### 2. 析锂延寿Workflow

**详细文档**：[02-析锂延寿Workflow.md](./02-析锂延寿Workflow.md)

**核心目标**：检测并抑制析锂，降低衰减率30%

**应用场景**：
- 电动营运车辆
- 快充站
- 低温充电

**关键BAS**：B2.5、B2.1、B2.6、C3.7

---

### 3. 储能电站健康管理Workflow

**详细文档**：[03-储能电站健康管理Workflow.md](./03-储能电站健康管理Workflow.md)

**核心目标**：全生命周期健康管理，最大化电站收益

**应用场景**：
- 工商业储能
- 电网侧储能
- 户用储能

**关键BAS**：C3.5、C3.3、C3.1、I5.5

---

### 4. 电池银行评估Workflow

**详细文档**：[04-电池银行评估Workflow.md](./04-电池银行评估Workflow.md)

**核心目标**：快速准确评估退役电池健康状态，降低误判率

**应用场景**：
- 动力电池退役评估
- 梯次利用筛选
- 电池回收决策

**关键BAS**：C3.7、C3.8、C3.3、I5.6

---

### 5. 生产质量控制Workflow

**详细文档**：[05-生产质量控制Workflow.md](./05-生产质量控制Workflow.md)

**核心目标**：拦截质量问题，降低返修率80%

**应用场景**：
- 电池制造商
- 模组Pack组装厂
- 第三方质检机构

**关键BAS**：M1.1、M1.2、M1.3、M1.5

---

## 如何使用Meta-Workflow？

### Step 1: 选择合适的Meta-Workflow

参考[Workflow案例与示例](../examples/README.md#q1-如何选择合适的meta-workflow)中的决策树。

### Step 2: 阅读详细文档

点击上方的文档链接，了解Workflow的详细设计、BAS配置、执行逻辑等。

### Step 3: 微调生成Custom Workflow

基于Meta-Workflow，根据客户的具体需求进行微调：
- 添加/删除BAS
- 调整参数
- 优化执行策略

参考[Custom Workflow示例](../examples/custom-workflow-极寒地区营运车辆充电优化.md)。

---

## 贡献新的Meta-Workflow

欢迎社区贡献新的Meta-Workflow模板！

**提交要求**：
1. 经过至少3个客户的实战验证
2. 包含完整的DAG图和BAS配置
3. 提供执行效果数据
4. 编写详细文档

**提交路径**：提交PR到 `workflow/meta-workflows/` 目录

---

## 延伸阅读

- [Workflow案例与示例](../examples/)
- [Workflow组件详解](../components/)
- [执行模式详解](../execution-modes.md)
