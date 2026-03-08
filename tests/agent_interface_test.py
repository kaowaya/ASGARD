"""Tests for Agent Interface"""
import pytest
from fastapi.testclient import TestClient
from workflow.engine.agent_interface import app

def test_health_check():
    """Test health check endpoint"""
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "agent-interface"
