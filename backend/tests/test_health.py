import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_root_endpoint():
    """Verify that GET / returns operational status and docs URL"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["status"] == "operational"
        assert json_data["docs_url"] == "/docs"

@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify that GET /api/health returns healthy envelope and parser statuses"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert json_data["data"]["status"] == "healthy"
        assert "pdf_parser" in json_data["data"]["services"]
        assert "docx_parser" in json_data["data"]["services"]
        assert "scoring_weights" in json_data["data"]
