"""Orchestrator - Workflow执行编排（集成Online Planner）"""
from typing import Dict, Any, Optional
from workflow.engine.orchestrator.online_planner import OnlinePlanner, ReplanDecision
from workflow.engine.workflow_context import WorkflowExecutionContext

class AgentInterventionException(Exception):
    """需要Agent介入时抛出"""
    pass

class Orchestrator:
    """
    增强的Orchestrator，集成Online Planner

    职责：
    - 执行Workflow DAG
    - 委托运行时决策给Online Planner
    - 实现Online Planner的决策（重试、替换、优化）
    - 无法处理时升级给Agent
    """

    def __init__(self, online_planner: OnlinePlanner,
                 agent_interface=None,
                 executor=None,
                 monitor=None):
        self.online_planner = online_planner
        self.agent_interface = agent_interface
        self.executor = executor or MockExecutor()
        self.monitor = monitor or MockMonitor()
        self.active_workflows: Dict[str, WorkflowExecutionContext] = {}

    def start(self, workflow_id: str, execution_context: WorkflowExecutionContext):
        """启动workflow执行"""
        self.active_workflows[workflow_id] = execution_context
        execution_context.start()
        # TODO: 启动异步执行循环

    def pause(self, workflow_id: str):
        """暂停workflow执行"""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id].pause()

    def resume(self, workflow_id: str):
        """恢复workflow执行"""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id].resume()

    def emergency_stop(self, workflow_id: str):
        """紧急停止workflow"""
        if workflow_id in self.active_workflows:
            context = self.active_workflows[workflow_id]
            context.fail()
            del self.active_workflows[workflow_id]

    def execute_node(self, execution_context: WorkflowExecutionContext,
                    node: Any) -> Dict:
        """
        执行节点（集成Online Planner）

        处理失败和性能问题，通过咨询Online Planner
        """
        # 检查节点是否已完成
        if node.id in execution_context.completed_nodes:
            return execution_context.completed_nodes[node.id]["result"]

        # 尝试执行节点
        try:
            result = self._execute_with_online_planning(execution_context, node)
            execution_context.record_success(node.id, result)
            return result

        except Exception as e:
            # 通过Online Planner处理失败
            decision = self.online_planner.handle_node_failure(
                execution_context=execution_context,
                failed_node=node.id,
                error=e
            )

            return self._implement_online_decision(
                execution_context, node, decision, e
            )

    def _execute_with_online_planning(self, context: WorkflowExecutionContext,
                                     node: Any) -> Dict:
        """正常执行节点"""
        return self.executor.execute(node, context)

    def _implement_online_decision(self, context: WorkflowExecutionContext,
                                  node: Any, decision: ReplanDecision,
                                  original_error: Exception) -> Dict:
        """实现Online Planner的决策"""

        if decision.action == "RETRY":
            # 重试（递归调用）
            import time
            time.sleep(decision.delay)
            return self.execute_node(context, node)

        elif decision.action == "REPLACE_NODE":
            # 替换节点并执行
            if decision.new_skill:
                new_node = self._create_replacement_node(node, decision.new_skill)
                log_warning(f"替换节点 {node.id} → {decision.new_skill}: {decision.reason}")
                return self.execute_node(context, new_node)
            else:
                # 没有可替换的skill，重试
                log_warning(f"无法替换节点 {node.id}，重试")
                import time
                time.sleep(1)
                return self.execute_node(context, node)

        elif decision.action == "OPTIMIZE_PARAMS":
            # 优化参数并重试
            if hasattr(node, 'update_params'):
                node.update_params(decision.new_params)
            log_info(f"优化节点 {node.id} 参数: {decision.new_params}")
            return self.execute_node(context, node)

        elif decision.action == "REQUEST_AGENT":
            # 升级给Agent
            if self.agent_interface:
                self.agent_interface.trigger_agent_replan(
                    workflow_id=context.workflow_id,
                    reason=decision.reason,
                    current_state=decision.current_state
                )
            raise AgentInterventionException(
                f"请求Agent介入: {decision.reason}"
            )

        else:  # CONTINUE
            raise original_error

    def _create_replacement_node(self, old_node: Any, new_skill_id: str) -> Any:
        """创建替换节点"""
        class ReplacementNode:
            def __init__(self, skill_id, original_node):
                self.id = f"{original_node.id}_replaced_{skill_id}"
                self.skill_id = skill_id
                self.original_node = original_node

            def update_params(self, params):
                pass  # TODO: 实现

        return ReplacementNode(new_skill_id, old_node)


# Mock类（用于测试）
class MockExecutor:
    def execute(self, node, context):
        return {"result": "ok"}

class MockMonitor:
    def get_node_metrics(self, node_id):
        class MockMetrics:
            execution_time = 100
            memory_usage = 512
        return MockMetrics()


# 辅助函数
def log_warning(msg):
    """记录警告"""
    print(f"[WARNING] {msg}")

def log_info(msg):
    """记录信息"""
    print(f"[INFO] {msg}")
