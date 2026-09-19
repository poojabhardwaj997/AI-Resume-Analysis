import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.llm_service import LLMService
from app.schemas.job import JobRequirements


def test_job_description_heuristic_parsing():
    """Verify offline heuristic parser accurately partitions required vs preferred skills"""
    sample_jd = """
    Job Title: Senior Backend Engineer
    Company: TechCorp Innovations
    Experience: 3+ years of experience in backend development.
    Education: Bachelor's degree in Computer Science or related field.
    
    Requirements:
    - Strong proficiency in Python, FastAPI, and SQL.
    - Hands-on experience with Docker and Git.
    
    Preferred Qualifications:
    - Knowledge of Kubernetes, Redis, and AWS is a major plus.
    """
    service = LLMService(api_key="")  # offline mode
    reqs = service.analyze_job_description(sample_jd)

    assert isinstance(reqs, JobRequirements)
    assert "Python" in reqs.required_skills
    assert "FastAPI" in reqs.required_skills
    assert "Docker" in reqs.required_skills
    assert "Kubernetes" in reqs.preferred_skills
    assert "Redis" in reqs.preferred_skills
    assert len(reqs.experience_requirements) > 0
    assert len(reqs.education_requirements) > 0


@pytest.mark.asyncio
async def test_job_analyze_endpoint_success():
    """Verify POST /api/job/analyze processes JD payload and returns 200 OK with job_id"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "job_title": "Full Stack Developer",
            "company_name": "Acme Corp",
            "job_description_text": (
                "We are hiring a Full Stack Developer with 2+ years of experience. "
                "Must have strong skills in Python, React, and PostgreSQL. "
                "Bonus if you know Docker and AWS. Bachelor's in CS required."
            )
        }
        response = await client.post("/api/job/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "job_id" in data["data"]
        assert data["data"]["parsed_requirements"]["job_title"] == "Full Stack Developer"
        assert "Python" in data["data"]["parsed_requirements"]["required_skills"]


@pytest.mark.asyncio
async def test_job_analyze_endpoint_validation_error():
    """Verify POST /api/job/analyze rejects text shorter than 10 characters with 422"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "job_description_text": "Too short"
        }
        response = await client.post("/api/job/analyze", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "validation" in data["message"].lower()
