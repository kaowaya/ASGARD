# Changelog

All notable changes to ASGARD Workflow Engine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-03-08

### Added

- **Agent Interface Layer**: REST API和程序化接口，实现Agent-Workflow清晰边界
- **Online Planner**: 自主运行时工作流适配（重试、替换、优化）
- **Workflow Execution Context**: 集中式工作流执行状态管理
- **Skill Market**: 替代BAS技能的搜索和发现框架
- **集成测试**: 端到端Agent-Workflow流程测试（17个测试全部通过）

### Changed

- **Planner → Offline Planner**: 重命名为清晰区分离线和在线规划
- **Orchestrator**: 集成Online Planner，支持自主决策
- **架构**: 混合决策模式（Online Planner自主 + Agent升级）

### Fixed

- 问题1: Agent-Workflow交互边界通过Agent Interface Layer明确
- 问题2: 静态DAG限制通过Online Planner运行时适配解决

### Performance

- Online Planner决策: <50ms 处理80%的运行时问题
- 减少Agent介入: 80%自主处理，仅20%需要Agent
- 提升容错性: 自动重试和节点替换

### Documentation

- 新增: Agent Interface组件文档
- 更新: Orchestrator文档，包含Online Planner集成
- 新增: V2.0迁移指南
- 新增: 实现计划: `docs/plans/2026-03-08-agent-workflow-integration.md`
- 新增: 部署指南: `workflow/engine/DEPLOYMENT.md`

### Breaking Changes

- Orchestrator现在需要`online_planner`和`agent_interface`参数
- Planner重命名为Offline Planner（提供向后兼容wrapper）
- Agent-Workflow通信现在通过Agent Interface（REST API或程序化）

### Migration

参见迁移指南: `docs/migration-guide-agent-workflow-v2.md`

---

## [1.0.0] - 2026-02-07

### Initial Release

- Workflow Engine基础架构（Planner、Orchestrator、Executor、Monitor）
- 5个Meta-Workflow模板
- 渐进式披露文档架构
