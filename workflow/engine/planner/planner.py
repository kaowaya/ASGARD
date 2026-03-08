"""向后兼容wrapper - Planner现在指向OfflinePlanner"""
from workflow.engine.planner.offline_planner import OfflinePlanner

# 向后兼容：Planner实际上是OfflinePlanner
Planner = OfflinePlanner

__all__ = ['Planner', 'OfflinePlanner']
