"""Tests for WorkflowExecutionContext"""
import pytest
from workflow.engine.workflow_context import WorkflowExecutionContext, NodeExecutionStatus

def test_create_execution_context():
    """Test creating a new execution context"""
    context = WorkflowExecutionContext(
        workflow_id="test-wf-001",
        dag={"nodes": ["C3.4", "C3.1"]},
        execution_plan={"parallel": True}
    )

    assert context.workflow_id == "test-wf-001"
    assert context.status == "PENDING"
    assert len(context.completed_nodes) == 0
    assert context.get_failure_count("C3.4") == 0

def test_record_node_success():
    """Test recording successful node execution"""
    context = WorkflowExecutionContext(
        workflow_id="test-wf-001",
        dag={"nodes": ["C3.4"]},
        execution_plan={}
    )

    context.record_success("C3.4", {"result": "ok"})

    assert "C3.4" in context.completed_nodes
    assert context.completed_nodes["C3.4"]["status"] == "SUCCESS"
    assert context.get_failure_count("C3.4") == 0

def test_record_node_failure():
    """Test recording failed node execution"""
    context = WorkflowExecutionContext(
        workflow_id="test-wf-001",
        dag={"nodes": ["C3.4"]},
        execution_plan={}
    )

    context.record_failure("C3.4", Exception("Timeout"))

    assert context.get_failure_count("C3.4") == 1

    context.record_failure("C3.4", Exception("Timeout again"))
    assert context.get_failure_count("C3.4") == 2

def test_get_snapshot():
    """Test getting execution snapshot for Agent"""
    context = WorkflowExecutionContext(
        workflow_id="test-wf-001",
        dag={"nodes": ["C3.4", "C3.1"]},
        execution_plan={}
    )

    context.record_success("C3.4", {"result": "ok"})
    context.record_failure("C3.1", Exception("Failed"))

    snapshot = context.get_snapshot()

    assert snapshot["workflow_id"] == "test-wf-001"
    assert snapshot["completed_count"] == 1
    assert snapshot["failed_count"] == 1
    assert "C3.4" in snapshot["completed_nodes"]
