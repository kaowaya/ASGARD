"""Agent Interface data models"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Literal
from enum import Enum

class RequestType(str, Enum):
    """Agent request types"""
    CREATE_WORKFLOW = "CREATE_WORKFLOW"
    QUERY_STATUS = "QUERY_STATUS"
    REPLAN = "REPLAN"
    EMERGENCY_STOP = "EMERGENCY_STOP"

class AgentRequest(BaseModel):
    """Request from Agent"""
    type: RequestType
    workflow_id: str
    task: Optional[str] = None  # For CREATE_WORKFLOW, REPLAN
    new_task: Optional[str] = None  # For REPLAN
    context: Dict[str, Any] = Field(default_factory=dict)

class AgentResponse(BaseModel):
    """Response to Agent"""
    status: str  # CREATED, RUNNING, COMPLETED, FAILED, REPLANED
    workflow_id: str
    dag: Optional[Dict] = None
    execution_state: Optional[Dict] = None
    message: Optional[str] = None
    timestamp: str

class WorkflowStatus(BaseModel):
    """Workflow status response"""
    workflow_id: str
    status: str
    total_nodes: int
    completed_count: int
    failed_count: int
    completed_nodes: list[str]
    failed_nodes: Dict[str, int]
    uptime_seconds: float
