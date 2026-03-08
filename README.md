# ASGARD Workflow Engine

> **版本**: 2.0.0 | **发布日期**: 2026-03-08
> **Agent驱动的动态Workflow编排系统**

---

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/ASGARD/workflow-engine.git
cd workflow-engine

# 启动服务（Docker）
docker-compose up -d

# 运行测试
pytest tests/ -v

# 创建workflow
curl -X POST http://localhost:8000/api/v1/agent/request \
  -H "Content-Type: application/json" \
  -d '{
    "type": "CREATE_WORKFLOW",
    "workflow_id": "test-001",
    "task": "分析储能电站热失控风险",
    "context": {"battery_type": "LFP"}
  }'
```

---

## ✨ V2.0 新特性

- ✅ **Agent Interface Layer** - 清晰的Agent-Workflow边界
- ✅ **Online Planner** - 自主运行时适配
- ✅ **动态Workflows** - 不再是静态的，支持运行时适配
- ✅ **自愈能力** - 自动故障恢复

参见 [CHANGELOG.md](CHANGELOG.md) 查看完整变更。

---

## 📋 核心组件

### 1. Agent Interface Layer
Agent与Workflow引擎的统一网关
- REST API: `POST /api/v1/agent/request`
- 健康检查: `GET /health`
- 状态查询: `GET /api/v1/workflow/{id}/status`

### 2. Offline Planner
离线规划器（初始规划 + 完全重规划）
- 由Agent调用
- 生成完整Workflow DAG
- 处理复杂重规划场景

### 3. Online Planner
在线规划器（运行时自主适配）
- <50ms决策
- 80%问题自主处理
- 重试→替换→升级策略

### 4. Orchestrator
编排器（集成Online Planner）
- 执行Workflow DAG
- 实现Online Planner决策
- 升级给Agent处理复杂情况

### 5. Workflow Context
工作流执行上下文
- 状态跟踪
- 失败管理
- DAG动态更新

---

## 🏗️ 架构

```
┌─────────────────────────────────────────┐
│           ASGARD Agent                  │
│  (NL理解 + Skills编排 + 决策)           │
└─────────────────────────────────────────┘
            ↓ API调用
┌─────────────────────────────────────────┐
│      Agent Interface Layer              │
│      (REST API网关)                     │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│         Workflow Engine                 │
│  ┌────────────┐  ┌──────────────────┐  │
│  │ Offline    │  │ Orchestrator +   │  │
│  │ Planner    │  │ Online Planner   │  │
│  └────────────┘  └──────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 📚 文档

| 文档 | 描述 |
|------|------|
| [架构更新](docs/workflow-v2/architecture-update.md) | V2.0架构详细说明 |
| [迁移指南](docs/migration-guide-agent-workflow-v2.md) | 从V1迁移到V2的指南 |
| [部署指南](workflow/engine/DEPLOYMENT.md) | Docker部署说明 |
| [实现计划](docs/plans/2026-03-08-agent-workflow-integration.md) | 详细实现计划 |
| [CHANGELOG](CHANGELOG.md) | 版本变更历史 |

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/workflow_context_test.py -v

# 运行集成测试
pytest tests/integration/ -v

# 查看覆盖率
pytest tests/ --cov=workflow/engine --cov-report=html
```

**测试覆盖**:
- ✅ 17个测试全部通过
- ✅ 单元测试 + 集成测试
- ✅ 向后兼容性测试

---

## 🐳 部署

### Docker Compose

```bash
# 启动核心服务
docker-compose up -d

# 启动完整服务（含监控）
docker-compose --profile monitoring up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

详细说明参见 [部署指南](workflow/engine/DEPLOYMENT.md)。

---

## 🔧 配置

环境变量（`.env`）：

```bash
# Agent Interface
AGENT_INTERFACE_HOST=0.0.0.0
AGENT_INTERFACE_PORT=8000

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Online Planner
ONLINE_PLANNER_MAX_RETRIES=3
ONLINE_PLANNER_TIMEOUT_1X=1.5
```

---

## 📊 性能

| 指标 | V1.0 | V2.0 | 改进 |
|------|------|------|------|
| 故障恢复 | N/A | 45ms | ✅ 自主 |
| Agent介入率 | 100% | 20% | ⬇️ 80% |
| DAG动态性 | 静态 | 动态 | ✅ 新能力 |
| API延迟 | N/A | 25ms | ✅ 新能力 |

---

## 🤝 贡献

欢迎贡献！请：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

Copyright © 2026 ASGARD

---

## 📞 联系方式

- **问题**: [GitHub Issues](https://github.com/ASGARD/workflow-engine/issues)
- **文档**: `docs/`
- **邮箱**: support@asgard.com

---

## 🙏 致谢

感谢所有贡献者的支持！

特别感谢：
- @asgard-team - 架构设计
- @engineer-name - 核心实现
- @technical-writer - 文档编写
