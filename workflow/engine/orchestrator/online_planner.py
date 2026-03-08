"""Online Planner - Runtime workflow adaptation"""
import math
from typing import Optional, Dict, Any
from workflow.engine.orchestrator.online_planner_models import ReplanDecision
from workflow.engine.workflow_context import WorkflowExecutionContext

class OnlinePlanner:
    """
    Online Planner for autonomous runtime workflow adaptation

    Responsibilities:
    - Handle node failures (retry, replace, escalate)
    - Optimize performance (parameter tuning, node replacement)
    - Maintain accuracy (switch to higher-accuracy models)
    - Escalate to Agent when unable to handle

    Design goal: 80% of issues handled autonomously in <50ms
    """

    def __init__(self, skill_market=None):
        self.skill_market = skill_market
        self.replan_thresholds = {
            'node_failure_retry': 3,        # Retry 3 times before replacing
            'timeout_1x': 1.5,              # 1.5x timeout = optimize params
            'timeout_2x': 2.0,              # 2x timeout = replace node
            'accuracy_drop': 0.1,           # 10% drop = switch model
            'memory_pressure': 0.9          # 90% memory = reduce batch size
        }

    def handle_node_failure(self, execution_context: WorkflowExecutionContext,
                           failed_node: str, error: Exception) -> ReplanDecision:
        """
        Handle node failure

        Strategy:
        - Failures 1-3: Retry with exponential backoff
        - Failure 4: Replace with alternative skill
        - Failures 5+: Request Agent intervention
        """
        failure_count = execution_context.get_failure_count(failed_node)

        # Strategy 1: Retry (first 3 failures)
        if failure_count < self.replan_thresholds['node_failure_retry']:
            delay = self._calculate_backoff(failure_count)
            return ReplanDecision(
                action="RETRY",
                delay=delay,
                reason=f"节点失败第{failure_count + 1}次，重试"
            )

        # Strategy 2: Replace with alternative skill (4th failure)
        elif failure_count == self.replan_thresholds['node_failure_retry']:
            # For now, return REPLACE_NODE without actual skill (mock)
            return ReplanDecision(
                action="REPLACE_NODE",
                new_skill=None,  # Would be set by skill_market in production
                reason=f"节点失败{failure_count + 1}次，替换为备用BAS"
            )

        # Strategy 3: Request Agent intervention (5+ failures)
        return ReplanDecision(
            action="REQUEST_AGENT",
            reason=f"节点失败{failure_count + 1}次，超出自主处理能力",
            current_state=execution_context.get_snapshot()
        )

    def handle_performance_degradation(self, execution_context: WorkflowExecutionContext,
                                      node: Any, metrics: Any) -> ReplanDecision:
        """
        Handle performance degradation (slow execution)

        Strategy:
        - 1.5x timeout: Optimize parameters (reduce batch size)
        - 2x timeout: Replace with faster skill
        """
        if not hasattr(node, 'expected_time'):
            return ReplanDecision(action="CONTINUE")

        timeout_ratio = metrics.execution_time / node.expected_time

        # Strategy 1: Optimize parameters (1.5x timeout)
        if timeout_ratio >= self.replan_thresholds['timeout_1x']:
            optimized = self._optimize_parameters(node, metrics)
            if optimized:
                return ReplanDecision(
                    action="OPTIMIZE_PARAMS",
                    new_params=optimized,
                    reason=f"执行时间{metrics.execution_time}ms，优化参数"
                )

        # Strategy 2: Replace with faster skill (2x timeout)
        if timeout_ratio >= self.replan_thresholds['timeout_2x']:
            return ReplanDecision(
                action="REPLACE_NODE",
                new_skill=None,  # Would be set by skill_market
                reason=f"执行时间{metrics.execution_time}ms，替换为更快BAS"
            )

        return ReplanDecision(action="CONTINUE")

    def handle_accuracy_drop(self, execution_context: WorkflowExecutionContext,
                           node: Any, accuracy: float) -> ReplanDecision:
        """
        Handle accuracy drop

        Strategy:
        - Switch to higher-accuracy model
        """
        if not hasattr(node, 'expected_accuracy'):
            return ReplanDecision(action="CONTINUE")

        accuracy_drop = node.expected_accuracy - accuracy

        if accuracy_drop >= self.replan_thresholds['accuracy_drop']:
            return ReplanDecision(
                action="REPLACE_NODE",
                new_skill=None,  # Would be set by skill_market
                reason=f"精度下降至{accuracy:.2%}，切换高精度模型"
            )

        return ReplanDecision(action="CONTINUE")

    def _calculate_backoff(self, failure_count: int) -> float:
        """Calculate exponential backoff delay (seconds)"""
        return min(2 ** failure_count, 60)  # Max 60 seconds

    def _optimize_parameters(self, node: Any, metrics: Any) -> Optional[Dict]:
        """Optimize node parameters based on metrics"""
        optimized = {}

        # Reduce batch size if memory pressure
        if hasattr(metrics, 'memory_usage') and hasattr(node, 'max_memory'):
            if metrics.memory_usage > node.max_memory * self.replan_thresholds['memory_pressure']:
                if hasattr(node, 'batch_size'):
                    optimized['batch_size'] = max(node.batch_size // 2, 1)

        # Reduce batch size if timeout (trade accuracy for speed)
        if hasattr(metrics, 'execution_time') and hasattr(node, 'expected_time'):
            if metrics.execution_time > node.expected_time * 1.5:
                if hasattr(node, 'batch_size') and node.batch_size > 1:
                    optimized['batch_size'] = max(node.batch_size // 2, 1)

        return optimized if optimized else None
