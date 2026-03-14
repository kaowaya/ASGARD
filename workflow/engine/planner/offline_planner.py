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
        生成DAG
        设计原则：编排层主要依据 SKILL.md 中的 ## When to use this skill 章节进行决策。
        """
        task_lower = user_task.lower()
        
        # 模拟：从 SKILL.md 中提取的适用性启发式规则
        # C3.4 (内短路-等效电路): ## When to use this skill -> 适用于快速初步筛查
        # C3.2 (内短路-P2D): ## When to use this skill -> 适用于高精度定量分析
        # C3.13 (析锂): ## When to use this skill -> 适用于快充或低温充电后的弛豫期
        
        nodes = []
        if "热失控" in task_lower or "安全性" in task_lower:
            # 依据: ## When to use this skill - C3.0 (净化数据) 是所有分析的前置条件
            nodes.append("C3.0-净化数据")
            
            if context.get("accuracy") == "high":
                # 依据: ## When to use this skill - C3.2 适用于高精度深度分析
                nodes.append("C3.2-P2D-内短路诊断")
            else:
                # 依据: ## When to use this skill - C3.4 适用于快速初步诊断
                nodes.append("C3.4-内短路诊断")
                
            nodes.append("C3.13-析锂检测")  # 依据: ## When to use this skill - 充电后必查
            
        elif "soh" in task_lower:
            nodes = ["C3.0-净化数据", "C3.8-ICA分析", "C3.9-EIS分析"]
        else:
            nodes = ["C3.0-净化数据"]

        return {
            "nodes": nodes,
            "edges": self._generate_edges(nodes),
            "metadata": {
                "task": user_task,
                "orchestration_logic": "documentation-driven (derived from ## When to use this skill)",
                "battery_type": context.get("battery_type", "LFP")
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
