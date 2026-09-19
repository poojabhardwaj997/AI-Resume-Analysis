import io
import fitz
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_end_to_end_analysis_creation():
    """Verify complete end-to-end pipeline: PDF upload -> extraction -> LLM -> scoring -> recommendations -> response"""
    # 1. Generate in-memory PDF
    doc = fitz.open()
    page = doc.new_page()
    resume_content = (
        "Vikram Patel\n"
        "Full Stack Python & React Developer\n"
        "Email: vikram.patel@example.com\n"
        "Phone: +91 98765 12345\n\n"
        "Technical Skills: Python, FastAPI, React, SQL, PostgreSQL, Git\n"
        "Experience: 2 years building microservices at CloudScale Corp.\n"
        "Education: Bachelor of Science in Information Technology (BSc IT)"
    )
    page.insert_text((50, 72), resume_content)
    pdf_bytes = doc.tobytes()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "file": ("vikram_patel_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")
        }
        data = {
            "job_description_text": (
                "Job Title: Full Stack Python Developer\n"
                "Company: FinTech Innovations\n"
                "Experience required: 2+ years\n"
                "Requirements: Python, FastAPI, React, Docker, Git.\n"
                "Bonus: Kubernetes, AWS."
            ),
            "job_title": "Full Stack Python Developer",
            "company_name": "FinTech Innovations"
        }

        response = await client.post("/api/analysis/create", files=files, data=data)
        assert response.status_code == 201
        res = response.json()
        assert res["success"] is True

        analysis = res["data"]
        assert "analysis_id" in analysis
        assert "compatibility_score" in analysis
        assert analysis["compatibility_score"] > 0
        assert "score_breakdown" in analysis
        assert analysis["candidate_profile"]["candidate_name"] == "Vikram Patel"

        # Check skill gaps
        skills_matched = [g["skill"] for g in analysis["skill_gaps"] if g["status"] == "matched"]
        skills_missing = [g["skill"] for g in analysis["skill_gaps"] if g["status"] == "missing"]
        assert "Python" in skills_matched
        assert "FastAPI" in skills_matched
        assert "Docker" in skills_missing

        # Check recommendations
        assert len(analysis["recommendations"]) > 0
        docker_rec = next((r for r in analysis["recommendations"] if r["skill"] == "Docker"), None)
        assert docker_rec is not None
        assert "container" in docker_rec["why_it_matters"].lower()


@pytest.mark.asyncio
async def test_analysis_history_endpoint():
    """Verify GET /api/analysis/history returns 200 OK list"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/analysis/history")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)


@pytest.mark.asyncio
async def test_analysis_create_missing_inputs():
    """Verify validation error when no file and no resume_id is sent"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/analysis/create", data={"job_description_text": "Requirements: Python, React"})
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "either a resume file or an existing resume_id" in data["message"].lower()
