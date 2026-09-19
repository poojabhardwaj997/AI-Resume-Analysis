from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EducationItem(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None
    grade: Optional[str] = None


class ExperienceItem(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    """Structured candidate entity extracted from resume text"""
    candidate_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    education: List[EducationItem] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)


class ResumeUploadResponse(BaseModel):
    resume_id: str
    file_name: str
    file_size: int
    file_type: str
    storage_path: Optional[str] = None
    raw_text_preview: Optional[str] = None
    word_count: int = 0
    status: str = "uploaded"
    message: str = "Resume uploaded, validated, and parsed successfully."
