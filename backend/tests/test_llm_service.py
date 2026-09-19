import pytest
from app.services.llm_service import LLMService
from app.schemas.resume import CandidateProfile


def test_llm_service_empty_text():
    """Verify empty text returns default empty profile without errors"""
    service = LLMService()
    profile = service.analyze_resume("")
    assert isinstance(profile, CandidateProfile)
    assert profile.skills == []
    assert profile.candidate_name is None


def test_llm_service_heuristic_fallback_extraction():
    """Verify offline heuristic extractor accurately extracts contact, skills, and education"""
    sample_resume = """
    Priya Sharma
    Senior Data Science & Machine Learning Engineer
    Email: priya.sharma@example.com
    Phone: +91 98765 43210
    
    Education:
    BSc in Information Technology from State University (2022)
    
    Technical Skills:
    Python, SQL, Pandas, NumPy, Scikit-Learn, PyTorch, Docker, Git, FastAPI, Power BI
    
    Experience:
    Data Scientist at Analytics Corp (2022 - Present)
    Built predictive machine learning models and automated data pipelines.
    """
    service = LLMService(api_key="")  # Force heuristic mode
    profile = service.analyze_resume(sample_resume)

    assert isinstance(profile, CandidateProfile)
    assert profile.candidate_name == "Priya Sharma"
    assert profile.email == "priya.sharma@example.com"
    assert "98765" in profile.phone
    assert "Python" in profile.skills
    assert "FastAPI" in profile.skills
    assert "Docker" in profile.skills
    assert "Pandas" in profile.skills
    assert len(profile.education) > 0


def test_llm_service_multi_domain_support():
    """Verify extraction works across non-engineering domains (HR, Finance)"""
    hr_resume = """
    Rahul Verma
    HR Executive - Talent Acquisition
    Email: rahul.verma@hrcompany.com
    Phone: 9811223344
    
    Education:
    BBA in Human Resource Management (2023)
    
    Core Competencies:
    Recruitment, Talent Acquisition, Human Resources, Negotiation, Communication, MS Excel
    """
    service = LLMService(api_key="")
    profile = service.analyze_resume(hr_resume)

    assert profile.candidate_name == "Rahul Verma"
    assert "Recruitment" in profile.skills
    assert "Human Resources" in profile.skills
    assert "Excel" in profile.skills
