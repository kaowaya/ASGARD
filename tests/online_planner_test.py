"""Tests for Online Planner"""
import pytest
from workflow.engine.orchestrator.online_planner import OnlinePlanner, ReplanDecision
from workflow.engine.workflow_context import WorkflowExecutionContext

def test_handle_node_failure_retry():
    """Test that Online Planner decides to retry on first failure"""
    planner = OnlinePlanner(skill_market=None)
    context = WorkflowExecutionContext(
        workflow_id="test-wf-001",
        dag={"nodes": ["C3.4"]},
        execution_plan={}
    )

    decision = planner.handle_node_failure(
        execution_context=context,
        failed_node="C3.4",
        error=Exception("Timeout")
    )

    assert decision.action == "RETRY"
    assert decision.delay > 0

def test_handle_node_failure_replace():
    """Test that Online Planner decides to replace after 3 failures"""
    planner = OnlinePlanner(skill_market=None)
    context = WorkflowExecutionContext(
        workflow_id="test-wf-001",
        dag={"nodes": ["C3.4"]},
        execution_plan={}
    )

    # Simulate 3 failures
    context.record_failure("C3.4", Exception("Timeout"))
    context.record_failure("C3.4", Exception("Timeout"))
    context.record_failure("C3.4", Exception("Timeout"))

    decision = planner.handle_node_failure(
        execution_context=context,
        failed_node="C3.4",
        error=Exception("Timeout")
    )

    assert decision.action == "REPLACE_NODE"

def test_handle_node_failure_request_agent():
    """Test that Online Planner requests Agent after 4+ failures"""
    planner = OnlinePlanner(skill_market=None)
    context = WorkflowExecutionContext(
        workflow_id="test-wf-001",
        dag={"nodes": ["C3.4"]},
        execution_plan={}
    )

    # Simulate 4 failures
    for _ in range(4):
        context.record_failure("C3.4", Exception("Timeout"))

    decision = planner.handle_node_failure(
        execution_context=context,
        failed_node="C3.4",
        error=Exception("Timeout")
    )

    assert decision.action == "REQUEST_AGENT"
