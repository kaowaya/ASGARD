"""Online Planner data models"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class ReplanDecision:
    """Decision made by Online Planner"""
    action: str  # RETRY, REPLACE_NODE, OPTIMIZE_PARAMS, REQUEST_AGENT, CONTINUE
    delay: Optional[float] = None  # For RETRY
    new_skill: Optional[str] = None  # For REPLACE_NODE
    new_params: Optional[Dict] = None  # For OPTIMIZE_PARAMS
    reason: Optional[str] = None
    current_state: Optional[Dict] = None  # For REQUEST_AGENT
