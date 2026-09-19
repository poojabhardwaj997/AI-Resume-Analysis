import pytest
from app.services.skill_normalizer import (
    normalize_skill,
    normalize_skills_list,
    get_skill_category,
    get_related_skills
)


def test_programming_languages_normalization():
    """Verify JS, ES6, Python3, and C++ normalize to canonical terms"""
    assert normalize_skill("JS") == "JavaScript"
    assert normalize_skill("javascript") == "JavaScript"
    assert normalize_skill("ES6") == "JavaScript"
    assert normalize_skill("Python 3") == "Python"
    assert normalize_skill("python programming") == "Python"
    assert normalize_skill("cpp") == "C++"
    assert normalize_skill("golang") == "Go"


def test_frameworks_and_databases_normalization():
    """Verify web frameworks and databases normalize accurately"""
    assert normalize_skill("fast api") == "FastAPI"
    assert normalize_skill("react.js") == "React"
    assert normalize_skill("reactjs") == "React"
    assert normalize_skill("postgres") == "PostgreSQL"
    assert normalize_skill("k8s") == "Kubernetes"
    assert normalize_skill("docker containers") == "Docker"
    assert normalize_skill("aws") == "AWS"


def test_business_and_data_science_normalization():
    """Verify Excel, Power BI, and ML aliases normalize properly"""
    assert normalize_skill("MS Excel") == "Microsoft Excel"
    assert normalize_skill("advanced excel") == "Microsoft Excel"
    assert normalize_skill("powerbi") == "Power BI"
    assert normalize_skill("ml") == "Machine Learning"
    assert normalize_skill("deep learning") == "Deep Learning"


def test_hr_and_management_normalization():
    """Verify non-tech domain aliases normalize"""
    assert normalize_skill("hr") == "Human Resources"
    assert normalize_skill("talent sourcing") == "Recruitment & Talent Acquisition"
    assert normalize_skill("agile") == "Agile / Scrum"


def test_normalize_skills_list_deduplication():
    """Verify aliases collapse into single canonical items without duplicates"""
    raw_list = ["JavaScript", "js", "ES6", "Python", "Python3", "Docker", "docker containers"]
    normalized = normalize_skills_list(raw_list)
    assert normalized == ["JavaScript", "Python", "Docker"]


def test_related_skills_lookup():
    """Verify related/transferable skill cluster lookup"""
    related_fastapi = get_related_skills("FastAPI")
    assert "Flask" in related_fastapi or "Django" in related_fastapi
    
    related_react = get_related_skills("React")
    assert "Vue.js" in related_react or "Angular" in related_react


def test_skill_category_lookup():
    """Verify category classification for resume badges"""
    assert get_skill_category("Python") == "Programming Language"
    assert get_skill_category("Docker") == "DevOps & Containers"
    assert get_skill_category("Power BI") == "Business Intelligence"
    assert get_skill_category("Human Resources") == "Human Resources"
