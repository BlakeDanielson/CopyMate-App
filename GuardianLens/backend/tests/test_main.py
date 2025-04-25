"""Tests for the main FastAPI application."""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test that the health endpoint returns a 200 status code and the correct response body."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}