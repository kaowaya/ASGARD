"""Agent Interface Layer - Gateway between Agent and Workflow Engine"""
from fastapi import FastAPI, HTTPException
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="ASGARD Workflow Engine - Agent Interface",
    description="REST API gateway for Agent-Workflow communication",
    version="2.0.0"
)

# Global handler (initialized in main())
agent_handler = None

@app.on_event("startup")
async def startup_event():
    """Initialize Agent Interface with dependencies"""
    global agent_handler
    # For now, use a mock handler
    from workflow.engine.agent_interface.requests import AgentRequestHandler
    agent_handler = AgentRequestHandler(
        offline_planner=None,  # Will be implemented in Task 5
        orchestrator=None,     # Will be implemented in Task 4
        monitor=None           # Will be implemented later
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "agent-interface"}
