"""端到端集成测试：Agent-Workflow完整流程"""
import pytest
from workflow.engine.planner.offline_planner import OfflinePlanner
from workflow.engine.orchestrator.orchestrator import Orchestrator
from workflow.engine.orchestrator.online_planner import OnlinePlanner
from workflow.engine.workflow_context import WorkflowExecutionContext
from unittest.mock import Mock

def test_full_workflow_lifecycle():
    """
    测试完整的Workflow生命周期

    流程：
    1. 创建Offline Planner并生成初始DAG
    2. 创建执行上下文
    3. 模拟节点执行（成功和失败）
    4. 验证状态快照
    """

    # 1. 创建Offline Planner并生成DAG
    planner = OfflinePlanner()
    dag, execution_plan = planner.plan(
        user_task="分析储能电站热失控风险",
        context={"battery_type": "LFP"}
    )

    assert "nodes" in dag
    assert "C3.4" in dag["nodes"]  # 热失控相关节点
    assert execution_plan["parallel"] is True

    # 2. 创建执行上下文
    context = WorkflowExecutionContext(
        workflow_id="test-wf-e2e-001",
        dag=dag,
        execution_plan=execution_plan
    )
    context.start()

    assert context.status == "RUNNING"
    assert context.start_time is not None

    # 3. 模拟节点执行
    # 执行C3.4成功
    result_c34 = {"result": "abnormal_cells", "cells": [15, 27]}
    context.record_success("C3.4", result_c34)

    # 执行C3.6成功
    result_c36 = {"center_temp": 48.5, "gradient": 6.2}
    context.record_success("C3.6", result_c36)

    # 4. 验证状态快照
    snapshot = context.get_snapshot()

    assert snapshot["workflow_id"] == "test-wf-e2e-001"
    assert snapshot["status"] == "RUNNING"
    assert snapshot["completed_count"] == 2
    assert "C3.4" in snapshot["completed_nodes"]
    assert "C3.6" in snapshot["completed_nodes"]

    # 5. 完成workflow
    context.complete()
    assert context.status == "COMPLETED"

def test_online_planner_autonomous_recovery():
    """
    测试Online Planner的自主恢复能力

    场景：
    1. 节点失败
    2. Online Planner决策重试
    3. 重试成功
    """

    # 创建组件
    skill_market = None  # 简化版
    online_planner = OnlinePlanner(skill_market)

    # 创建执行上下文
    context = WorkflowExecutionContext(
        workflow_id="test-recovery-001",
        dag={"nodes": ["C3.4"]},
        execution_plan={}
    )

    # 模拟第1次失败
    decision = online_planner.handle_node_failure(
        execution_context=context,
        failed_node="C3.4",
        error=Exception("Timeout")
    )

    # 应该决策RETRY
    assert decision.action == "RETRY"
    assert decision.delay == 1  # 2^0 = 1秒
    assert "第1次" in decision.reason

    # 模拟第2次失败
    context.record_failure("C3.4", Exception("Timeout"))
    decision = online_planner.handle_node_failure(
        execution_context=context,
        failed_node="C3.4",
        error=Exception("Timeout again")
    )

    assert decision.action == "RETRY"
    assert decision.delay == 2  # 2^1 = 2秒

    # 模拟第3次失败（应该仍然RETRY）
    context.record_failure("C3.4", Exception("Timeout"))
    decision = online_planner.handle_node_failure(
        execution_context=context,
        failed_node="C3.4",
        error=Exception("Timeout 3rd time")
    )

    assert decision.action == "RETRY"

    # 模拟第4次失败（应该决策REPLACE）
    context.record_failure("C3.4", Exception("Timeout"))
    decision = online_planner.handle_node_failure(
        execution_context=context,
        failed_node="C3.4",
        error=Exception("Timeout 4th time")
    )

    assert decision.action == "REPLACE_NODE"
    assert "替换" in decision.reason

    # 模拟第5次失败（应该请求Agent）
    context.record_failure("C3.4", Exception("Timeout"))
    decision = online_planner.handle_node_failure(
        execution_context=context,
        failed_node="C3.4",
        error=Exception("Timeout 5th time")
    )

    assert decision.action == "REQUEST_AGENT"
    assert "超出自主处理能力" in decision.reason
    assert decision.current_state is not None

def test_offline_planner_generates_different_dags():
    """
    测试Offline Planner根据不同任务生成不同DAG
    """

    planner = OfflinePlanner()

    # 测试1：热失控任务
    dag1, _ = planner.plan(
        user_task="分析储能电站热失控风险",
        context={"battery_type": "LFP"}
    )

    assert "C3.4" in dag1["nodes"]
    assert "C3.6" in dag1["nodes"]
    assert "B2.7" in dag1["nodes"]

    # 测试2：析锂任务
    dag2, _ = planner.plan(
        user_task="检测析锂并优化充电策略",
        context={"battery_type": "NCM"}
    )

    assert "B2.5" in dag2["nodes"]
    assert "B2.1" in dag2["nodes"]

    # 测试3：SOH任务
    dag3, _ = planner.plan(
        user_task="评估电池健康状态SOH",
        context={"battery_type": "LFP"}
    )

    assert "C3.8" in dag3["nodes"]

def test_orchestrator_integration_with_components():
    """
    测试Orchestrator与各组件的集成
    """

    # 创建组件
    offline_planner = OfflinePlanner()
    online_planner = OnlinePlanner(skill_market=None)

    orchestrator = Orchestrator(
        online_planner=online_planner,
        agent_interface=None,
        executor=None,
        monitor=None
    )

    # 生成DAG
    dag, execution_plan = offline_planner.plan(
        user_task="测试任务",
        context={}
    )

    # 创建上下文
    context = WorkflowExecutionContext(
        workflow_id="test-integration-001",
        dag=dag,
        execution_plan=execution_plan
    )

    # 启动orchestrator
    orchestrator.start("test-integration-001", context)

    assert "test-integration-001" in orchestrator.active_workflows
    assert context.status == "RUNNING"

    # 暂停
    orchestrator.pause("test-integration-001")
    assert context.status == "PAUSED"

    # 恢复
    orchestrator.resume("test-integration-001")
    assert context.status == "RUNNING"

    # 停止
    orchestrator.emergency_stop("test-integration-001")
    assert context.status == "FAILED"
    assert "test-integration-001" not in orchestrator.active_workflows

def test_backward_compatibility():
    """
    测试向后兼容性：旧的Planner导入方式仍然有效
    """

    # 旧的方式（应该仍然工作）
    from workflow.engine.planner.planner import Planner as OldPlanner

    planner = OldPlanner()
    dag, plan = planner.plan("测试", {})

    assert dag is not None
    assert plan is not None

    # 新的方式
    from workflow.engine.planner.offline_planner import OfflinePlanner

    new_planner = OfflinePlanner()
    assert new_planner is not None
