"""Agent Interface Layer - Gateway between Agent and Workflow Engine"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from datetime import datetime

# Global handler (initialized in main())
agent_handler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    global agent_handler
    # Startup: Initialize Agent Interface with dependencies
    from workflow.engine.agent_interface.requests import AgentRequestHandler
    agent_handler = AgentRequestHandler(
        offline_planner=None,  # Will be implemented in Task 5
        orchestrator=None,     # Will be implemented in Task 4
        monitor=None           # Will be implemented later
    )
    yield
    # Shutdown: Cleanup resources (if needed)
    pass

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="ASGARD Workflow Engine - Agent Interface",
    description="REST API gateway for Agent-Workflow communication",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "agent-interface"}
