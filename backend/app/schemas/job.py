from typing import List, Optional
from pydantic import BaseModel, Field


class JobAnalysisRequest(BaseModel):
    """Input payload for Job Description parsing"""
    job_description_text: str = Field(..., min_length=10, description="Raw Job Description requirements text")
    job_title: Optional[str] = Field(default=None, description="Optional job title if known")
    company_name: Optional[str] = Field(default=None, description="Optional hiring company name")


class JobRequirements(BaseModel):
    """Structured job requirements extracted by LLM or parser"""
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list, description="Must-have essential skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have or preferred skills")
    education_requirements: List[str] = Field(default_factory=list, description="Degree or academic requirements")
    experience_requirements: List[str] = Field(default_factory=list, description="Years or domain experience criteria")
    certifications: List[str] = Field(default_factory=list, description="Required or preferred certifications")


class JobAnalysisResponse(BaseModel):
    job_id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    parsed_requirements: JobRequirements
    message: str = "Job description analyzed successfully."
