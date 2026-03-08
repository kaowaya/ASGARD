"""Workflow execution context management"""
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class NodeExecutionStatus:
    """Node execution status"""
    node_id: str
    status: str  # PENDING, RUNNING, SUCCESS, FAILED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[Exception] = None

class WorkflowExecutionContext:
    """
    Workflow execution context

    Manages the runtime state of a workflow execution including:
    - Node execution status
    - Intermediate results
    - Failure tracking
    - DAG mutations (for Online Planner)
    """

    def __init__(self, workflow_id: str, dag: Dict, execution_plan: Dict):
        self.workflow_id = workflow_id
        self.dag = dag
        self.execution_plan = execution_plan
        self.status = "PENDING"  # PENDING, RUNNING, PAUSED, COMPLETED, FAILED

        # Node tracking
        self.node_statuses: Dict[str, NodeExecutionStatus] = {}
        self.completed_nodes: Dict[str, Dict] = {}
        self.failed_nodes: Dict[str, List[Exception]] = {}

        # Timing
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        # Metrics
        self.total_nodes = len(dag.get("nodes", []))
        self.agent_controlled = False

    def start(self):
        """Mark workflow as started"""
        self.status = "RUNNING"
        self.start_time = datetime.now()

    def pause(self):
        """Pause workflow execution"""
        self.status = "PAUSED"

    def resume(self):
        """Resume workflow execution"""
        if self.status == "PAUSED":
            self.status = "RUNNING"

    def complete(self):
        """Mark workflow as completed"""
        self.status = "COMPLETED"
        self.end_time = datetime.now()

    def fail(self):
        """Mark workflow as failed"""
        self.status = "FAILED"
        self.end_time = datetime.now()

    def record_success(self, node_id: str, result: Dict):
        """Record successful node execution"""
        self.completed_nodes[node_id] = {
            "status": "SUCCESS",
            "result": result,
            "completed_at": datetime.now().isoformat()
        }
        self.node_statuses[node_id] = NodeExecutionStatus(
            node_id=node_id,
            status="SUCCESS",
            end_time=datetime.now(),
            result=result
        )

    def record_failure(self, node_id: str, error: Exception):
        """Record failed node execution"""
        if node_id not in self.failed_nodes:
            self.failed_nodes[node_id] = []

        self.failed_nodes[node_id].append(error)
        self.node_statuses[node_id] = NodeExecutionStatus(
            node_id=node_id,
            status="FAILED",
            error=error
        )

    def get_failure_count(self, node_id: str) -> int:
        """Get number of failures for a node"""
        return len(self.failed_nodes.get(node_id, []))

    def update_dag(self, new_dag: Dict):
        """Update DAG (for Online Planner replanning)"""
        self.dag = new_dag

    def update_plan(self, new_plan: Dict):
        """Update execution plan"""
        self.execution_plan = new_plan

    def get_snapshot(self) -> Dict:
        """Get execution snapshot for Agent inspection"""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "total_nodes": self.total_nodes,
            "completed_count": len(self.completed_nodes),
            "failed_count": len(self.failed_nodes),
            "completed_nodes": list(self.completed_nodes.keys()),
            "failed_nodes": {k: len(v) for k, v in self.failed_nodes.items()},
            "current_dag": self.dag,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        }

    def get_current_state(self) -> Dict:
        """Get current execution state for replanning"""
        return {
            "dag": self.dag,
            "execution_plan": self.execution_plan,
            "completed_results": self.completed_nodes,
            "failed_nodes": self.failed_nodes,
            "node_statuses": {
                k: {"status": v.status, "error": str(v.error) if v.error else None}
                for k, v in self.node_statuses.items()
            }
        }
