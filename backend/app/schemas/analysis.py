from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.resume import CandidateProfile
from app.schemas.job import JobRequirements
from app.services.skill_gap import SkillMatchItem
from app.services.scoring import ScoreBreakdown
from app.services.recommendation import RecommendationItem


class FullAnalysisReport(BaseModel):
    """Complete consolidated analysis report payload"""
    analysis_id: str
    resume_id: str
    job_id: str
    compatibility_score: float = Field(..., description="Overall AI-Assisted Compatibility Score (0-100)")
    score_breakdown: ScoreBreakdown
    applied_weights: Dict[str, float]
    candidate_profile: CandidateProfile
    job_profile: JobRequirements
    skill_gaps: List[SkillMatchItem] = Field(default_factory=list)
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    summary_notes: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    indicator_label: str = "AI-Assisted Job Compatibility Score"
    fairness_disclaimer: str = (
        "Notice: This score is an analytical indicator based on skill taxonomy matching and semantic criteria. "
        "It does NOT represent a guaranteed hiring decision, employment probability, or automatic screening rejection."
    )


class AnalysisHistoryItem(BaseModel):
    """Compact history record for dashboard table"""
    id: str
    candidate_name: str
    job_title: str
    company_name: Optional[str] = None
    compatibility_score: float
    created_at: str
