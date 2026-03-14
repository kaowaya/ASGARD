"""
ASGARD v2.0.0 工作流编排示范脚本
演示内容：Agent 如何通过 AgentInterface 发起任务、监控状态并在运行时进行动态调整。
"""

import time
import json
from datetime import datetime

# 模拟 ASGARD 核心组件
class MockAgentInterface:
    def create_workflow(self, workflow_id, task, context):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [AgentInterface] 收到请求: {task}")
        # 1. 调用 Offline Planner 生成 DAG
        # 决策逻辑：依据 SKILL.md -> ## When to use this skill
        dag = {
            "nodes": ["C3.0-净化数据", "C3.4-内短路诊断", "C3.13-析锂检测"],
            "edges": [("C3.0", "C3.4"), ("C3.0", "C3.13")],
            "heuristic": "derived from ## When to use this skill"
        }
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Offline Planner] 编排逻辑: 依据 ## When to use this skill 章节选择最佳 BAS")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Offline Planner] 生成初始 DAG: {dag['nodes']}")
        return {"status": "CREATED", "workflow_id": workflow_id, "dag": dag}

    def query_status(self, workflow_id):
        # 模拟运行中的状态
        return {
            "workflow_id": workflow_id,
            "status": "RUNNING",
            "completed_nodes": ["C3.0-净化数据"],
            "failed_nodes": {"C3.4-内短路诊断": 2}, # 模拟失败了 2 次
            "message": "Online Planner 正在尝试自愈 (Retry)..."
        }

    def replan(self, workflow_id, new_task, context):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [AgentInterface] Agent 介入重规划: {new_task}")
        new_dag = {
            "nodes": ["C3.0-净化数据", "C3.2-P2D-内短路诊断", "C3.13-析锂检测"],
            "reason": "C3.4 精度不足，升级为 C3.2"
        }
        return {"status": "REPLANED", "dag": new_dag}

def run_orchestration_demo():
    interface = MockAgentInterface()
    
    # 场景 1：Agent 发起诊断任务
    print("=== 场景 1：发起任务 ===")
    response = interface.create_workflow(
        workflow_id="WF-20260314-001",
        task="分析皇岗场站 Pack 08 的安全性",
        context={"battery_type": "LFP", "threshold": "conservative"}
    )
    
    # 场景 2：运行时监控与自愈
    print("\n=== 场景 2：状态监控 (模拟运行 2 秒后) ===")
    time.sleep(1)
    status = interface.query_status(response["workflow_id"])
    print(f"当前进度: {status['completed_nodes']}, 异常节点: {status['failed_nodes']}")
    print(f"系统反馈: {status['message']}")
    
    # 场景 3：Agent 决策重规划 (例如发现 C3.4 持续失败或精度不达标)
    print("\n=== 场景 3：Agent 动态重规划 ===")
    replan_res = interface.replan(
        workflow_id=response["workflow_id"],
        new_task="使用 P2D 模型进行更深度的内短路分析",
        context={"reason": "C3.4 无法收敛"}
    )
    print(f"重规划结果: {replan_res['status']}, 新增节点: {replan_res['dag']['nodes'][1]}")

if __name__ == "__main__":
    run_orchestration_demo()
