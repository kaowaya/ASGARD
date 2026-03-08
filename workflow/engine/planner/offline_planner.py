"""Offline Planner - 离线规划器"""
from typing import Dict, Any, Tuple, List

class OfflinePlanner:
    """
    离线规划器

    职责：
    - 在初始规划时由Agent调用
    - 生成完整的Workflow DAG
    - 处理Agent请求的完全重规划
    - 不处理运行时调整（由Online Planner负责）
    """

    def __init__(self):
        self.skill_registry = {}  # 技能注册表（简化版）

    def plan(self, user_task: str, context: Dict[str, Any]) -> Tuple[Dict, Dict]:
        """
        规划Workflow

        Args:
            user_task: 用户的自然语言任务描述
            context: 执行上下文（电池类型、应用场景等）

        Returns:
            (dag, execution_plan): DAG和执行计划
        """
        # 简化版：基于任务关键词生成DAG
        # 在生产环境中，这里会调用NLP理解和复杂规划算法

        dag = self._generate_dag(user_task, context)
        execution_plan = self._generate_execution_plan(dag, context)

        return dag, execution_plan

    def _generate_dag(self, user_task: str, context: Dict) -> Dict:
        """
        生成DAG（简化版）

        实际实现应该：
        1. NLP理解任务
        2. 任务分解
        3. BAS匹配
        4. 依赖分析
        5. DAG构建
        """
        # 基于关键词的简单匹配
        task_lower = user_task.lower()

        if "热失控" in task_lower:
            nodes = ["C3.4", "C3.6", "C3.1", "C3.2", "B2.7"]
        elif "析锂" in task_lower or "充电" in task_lower:
            nodes = ["B2.5", "B2.1", "B2.6", "C3.7"]
        elif "soh" in task_lower or "健康" in task_lower:
            nodes = ["C3.8", "C3.9", "C3.10"]
        else:
            nodes = ["C3.0"]  # 默认数据预处理

        return {
            "nodes": nodes,
            "edges": self._generate_edges(nodes),
            "metadata": {
                "task": user_task,
                "battery_type": context.get("battery_type", "LFP"),
                "application": context.get("application", "general")
            }
        }

    def _generate_edges(self, nodes: List[str]) -> List[Tuple[str, str]]:
        """生成节点间的依赖边（简化版）"""
        edges = []
        for i in range(len(nodes) - 1):
            edges.append((nodes[i], nodes[i + 1]))
        return edges

    def _generate_execution_plan(self, dag: Dict, context: Dict) -> Dict:
        """
        生成执行计划

        包括：
        - 并行化策略
        - 资源分配
        - 超时设置
        """
        return {
            "parallel": True,
            "max_parallel_nodes": 4,
            "timeout_per_node": 300,  # 秒
            "retry_policy": {
                "max_retries": 3,
                "backoff": "exponential"
            },
            "resource_allocation": {
                "compute": "auto",
                "memory": "auto"
            }
        }
