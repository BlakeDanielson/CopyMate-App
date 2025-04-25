"""Tests for the main API application."""
import pytest
from fastapi.testclient import TestClient

from backend.config import settings
from backend.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Tests for the health check endpoints."""
    
    def test_health_check(self):
        """Test that the basic health endpoint returns status 'ok'."""
        endpoint = f"{settings.api_prefix}/health"
        response = client.get(endpoint)
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_detailed_health_check(self):
        """Test the detailed health check endpoint."""
        endpoint = f"{settings.api_prefix}/health/detailed"
        response = client.get(endpoint)
        
        assert response.status_code == 200
        assert "status" in response.json()
        assert "services" in response.json()
        assert "api" in response.json()["services"]
        assert "database" in response.json()["services"]
        assert "info" in response.json()
        assert "version" in response.json()["info"]


class TestApiDocs:
    """Tests for API documentation endpoints."""
    
    def test_docs_available(self):
        """Test that the Swagger UI is available."""
        response = client.get("/api/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()
    
    def test_openapi_schema(self):
        """Test that the OpenAPI schema is available."""
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        
        # Verify basic structure of OpenAPI schema
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        assert settings.app_name in schema["info"]["title"]