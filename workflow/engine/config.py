"""Workflow Engine Configuration"""
from pydantic_settings import BaseSettings

class WorkflowEngineConfig(BaseSettings):
    """Workflow引擎配置"""

    # Agent Interface
    agent_interface_host: str = "0.0.0.0"
    agent_interface_port: int = 8000
    agent_interface_workers: int = 4

    # Redis（workflow状态存储）
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # Online Planner阈值
    online_planner_max_retries: int = 3
    online_planner_timeout_1x: float = 1.5
    online_planner_timeout_2x: float = 2.0
    online_planner_accuracy_drop: float = 0.1

    # Orchestrator
    orchestrator_max_parallel_workflows: int = 100
    orchestrator_node_timeout: int = 300  # 秒

    # Monitor
    monitor_metrics_retention_days: int = 30
    monitor_alert_webhook_url: str | None = None

    class Config:
        env_file = ".env"

# 全局配置实例
config = WorkflowEngineConfig()
