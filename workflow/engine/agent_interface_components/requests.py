"""Agent Interface request handlers (mock version for now)"""
from typing import Dict, Any
from datetime import datetime

class AgentRequestHandler:
    """Handles Agent requests"""

    def __init__(self, offline_planner, orchestrator, monitor):
        self.offline_planner = offline_planner
        self.orchestrator = orchestrator
        self.monitor = monitor
        self.active_workflows: Dict[str, Any] = {}
