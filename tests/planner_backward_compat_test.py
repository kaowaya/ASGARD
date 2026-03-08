"""测试Planner重命名为OfflinePlanner后的向后兼容性"""
from workflow.engine.planner.planner import Planner
from workflow.engine.planner.offline_planner import OfflinePlanner

def test_planner_is_offline_planner():
    """验证Planner就是OfflinePlanner"""
    assert Planner == OfflinePlanner

def test_offline_planner_works():
    """验证OfflinePlanner可以正常导入和使用"""
    planner = OfflinePlanner()
    assert planner is not None

    # 测试规划功能
    dag, plan = planner.plan(
        user_task="分析储能电站热失控风险",
        context={"battery_type": "LFP", "application": "energy_storage"}
    )

    assert "nodes" in dag
    assert "C3.4" in dag["nodes"]  # 热失控相关skill
    assert plan["parallel"] is True

def test_backward_compatibility_import():
    """验证旧的导入方式仍然有效"""
    # 这应该继续工作
    from workflow.engine.planner.planner import Planner as OldPlanner

    planner = OldPlanner()
    dag, plan = planner.plan("测试任务", {})

    assert dag is not None
    assert plan is not None
