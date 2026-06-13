"""Smoke tests for Dungeon Master app setup.

These tests verify that the scaffold is correct and the app
starts and responds as expected.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_returns_welcome_message():
    """GET / should return a welcome message."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to Dungeon Master"
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_health_returns_ok():
    """GET /health should return status ok."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_api_status_returns_version():
    """GET /api/v1/status should return API version info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["api"] == "v1"
    assert data["status"] == "active"
