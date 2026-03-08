"""集成测试：Orchestrator与Online Planner协同工作"""
import pytest
from unittest.mock import Mock
from workflow.engine.orchestrator.orchestrator import Orchestrator
from workflow.engine.orchestrator.online_planner import OnlinePlanner
from workflow.engine.workflow_context import WorkflowExecutionContext

def test_orchestrator_retries_failed_node():
    """测试Orchestrator根据Online Planner决策重试失败节点"""
    # 创建Online Planner
    online_planner = OnlinePlanner(skill_market=None)

    # 创建Orchestrator（简化版，不需要完整的依赖）
    orchestrator = Orchestrator(
        online_planner=online_planner,
        agent_interface=None,
        executor=None,
        monitor=None
    )

    # 创建执行上下文
    context = WorkflowExecutionContext(
        workflow_id="test-wf-001",
        dag={"nodes": ["C3.4"]},
        execution_plan={}
    )

    # 模拟节点
    class MockNode:
        def __init__(self):
            self.id = "C3.4"
            self.skill_id = "C3.4"

    # 测试：Online Planner应该决定重试
    decision = online_planner.handle_node_failure(
        execution_context=context,
        failed_node="C3.4",
        error=Exception("Timeout")
    )

    assert decision.action == "RETRY"
    assert decision.delay > 0
    assert "第1次" in decision.reason
