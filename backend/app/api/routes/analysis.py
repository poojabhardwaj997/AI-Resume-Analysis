from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Request, Depends

from app.schemas.common import APIResponse
from app.schemas.resume import CandidateProfile
from app.schemas.job import JobRequirements
from app.schemas.analysis import FullAnalysisReport, AnalysisHistoryItem
from app.utils.file_validation import read_and_validate_upload
from app.services.resume_parser import parse_resume_document
from app.services.llm_service import LLMService
from app.services.skill_gap import detect_skill_gaps
from app.services.scoring import calculate_compatibility_score
from app.services.recommendation import RecommendationEngine
from app.database.supabase import SupabaseService
from app.api.deps import get_current_user, AuthenticatedUser
from app.services.audit_service import audit_service
from app.utils.logger import logger

router = APIRouter(prefix="/api/analysis", tags=["Analysis & Pipeline"])


@router.post("/create", response_model=APIResponse[FullAnalysisReport], status_code=status.HTTP_201_CREATED)
async def create_analysis(
    request: Request,
    file: Optional[UploadFile] = File(None),
    job_description_text: str = Form(..., min_length=10),
    job_title: Optional[str] = Form(""),
    company_name: Optional[str] = Form(""),
    resume_id: Optional[str] = Form(None),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    End-to-End Recruitment Analysis Pipeline:
    1. Ingests & validates Resume file (.pdf/.docx) or links existing resume_id.
    2. Extracts clean text via PyMuPDF or python-docx.
    3. Analyzes Resume entity structure via LLM (Zero-hallucination).
    4. Analyzes Job Description criteria via LLM.
    5. Normalizes skills across domains.
    6. Computes Skill Gap Matrix (Matched, Missing, Transferable, Preferred).
    7. Computes Transparent Weighted Compatibility Score.
    8. Synthesizes Actionable Learning Recommendations for missing competencies.
    9. Persists relational records to Supabase PostgreSQL & Storage scoped to user.
    """
    audit_service.log_event(
        action="ANALYSIS_STARTED",
        user_id=user.id,
        resource_type="analysis",
        request=request
    )

    db_service = SupabaseService(user_token=user.token)
    llm_service = LLMService()

    raw_text = ""
    candidate_profile = CandidateProfile()
    final_resume_id = resume_id

    # Step 1: Process Resume File or Retrieve Existing
    if file and file.filename:
        safe_filename, file_type, file_bytes = await read_and_validate_upload(file)
        raw_text = parse_resume_document(file_bytes=file_bytes, filename=safe_filename)

        # Upload file to Supabase Storage if configured
        storage_path = db_service.upload_file_to_storage(
            file_bytes=file_bytes,
            original_filename=safe_filename,
            content_type=file_type,
            user_id=user.id
        )

        # Extract structured candidate entities
        candidate_profile = llm_service.analyze_resume(raw_text)

        # Save resume record to Supabase
        final_resume_id = db_service.insert_resume(
            file_name=safe_filename,
            file_type=file_type,
            file_size=len(file_bytes),
            raw_text=raw_text,
            parsed_profile=candidate_profile.model_dump(),
            storage_path=storage_path,
            user_id=user.id
        )

        # Save individual candidate skills
        candidate_skills_rows = [
            {"skill_name": s, "normalized_name": s, "category": "General"}
            for s in candidate_profile.skills
        ]
        db_service.insert_candidate_skills(final_resume_id, candidate_skills_rows)

    elif final_resume_id:
        # Fetch existing resume from DB
        resume_record = db_service.get_resume(final_resume_id, user_id=user.id)
        if resume_record:
            raw_text = resume_record.get("raw_text", "")
            candidate_profile = CandidateProfile.model_validate(resume_record.get("parsed_profile", {}))
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID '{final_resume_id}' not found or unauthorized."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either a resume file or an existing resume_id must be provided."
        )

    # Step 2: Analyze Job Description
    job_reqs: JobRequirements = llm_service.analyze_job_description(
        jd_text=job_description_text,
        job_title=job_title,
        company_name=company_name
    )

    final_job_id = db_service.insert_job_description(
        job_title=job_reqs.job_title or job_title or "General Position",
        company_name=job_reqs.company_name or company_name or "Hiring Organization",
        raw_text=job_description_text,
        parsed_requirements=job_reqs.model_dump(),
        user_id=user.id
    )

    # Save job skills to DB
    job_skills_rows = []
    for s in job_reqs.required_skills:
        job_skills_rows.append({"skill_name": s, "normalized_name": s, "requirement_type": "required", "importance_weight": 1.0})
    for s in job_reqs.preferred_skills:
        job_skills_rows.append({"skill_name": s, "normalized_name": s, "requirement_type": "preferred", "importance_weight": 0.5})
    db_service.insert_job_skills(final_job_id, job_skills_rows)

    # Step 3: Skill Gap Detection
    gap_result = detect_skill_gaps(
        candidate_skills=candidate_profile.skills,
        required_job_skills=job_reqs.required_skills,
        preferred_job_skills=job_reqs.preferred_skills,
        resume_raw_text=raw_text
    )

    # Step 4: Calculate Compatibility Score
    score_result = calculate_compatibility_score(
        gap_result=gap_result,
        candidate_profile=candidate_profile,
        jd_experience_reqs=job_reqs.experience_requirements,
        jd_education_reqs=job_reqs.education_requirements
    )

    # Step 5: Generate Actionable Learning Recommendations
    all_unmatched_gaps = gap_result.missing_skills + gap_result.preferred_skill_gaps
    rec_engine = RecommendationEngine()
    recommendations = rec_engine.generate_recommendations_for_gaps(
        missing_skills=all_unmatched_gaps,
        job_title=job_reqs.job_title or "Target Position",
        company_name=job_reqs.company_name or "Hiring Organization"
    )

    # Step 6: Persist Full Analysis Report in Supabase
    all_gaps_combined = gap_result.matched_skills + gap_result.missing_skills + gap_result.related_skills + gap_result.preferred_skill_gaps

    analysis_id = db_service.insert_analysis(
        resume_id=final_resume_id or "mock-resume-id",
        job_id=final_job_id or "mock-job-id",
        compatibility_score=score_result.compatibility_score,
        required_score=score_result.score_breakdown.required_skills_match,
        preferred_score=score_result.score_breakdown.preferred_skills_match,
        experience_score=score_result.score_breakdown.experience_match,
        education_score=score_result.score_breakdown.education_match,
        summary_notes={"status": "completed", "candidate_name": candidate_profile.candidate_name},
        user_id=user.id
    )

    db_service.insert_skill_gaps(
        analysis_id=analysis_id,
        gaps=[g.model_dump() for g in all_gaps_combined]
    )

    db_service.insert_recommendations(
        analysis_id=analysis_id,
        recommendations=[r.model_dump() for r in recommendations]
    )

    audit_service.log_event(
        action="ANALYSIS_COMPLETED",
        user_id=user.id,
        resource_type="analysis",
        resource_id=analysis_id,
        request=request
    )

    logger.info(f"Analysis completed successfully: AnalysisID={analysis_id}, Score={score_result.compatibility_score}%, User={user.id}")

    report_payload = FullAnalysisReport(
        analysis_id=analysis_id,
        resume_id=final_resume_id or "mock-resume-id",
        job_id=final_job_id or "mock-job-id",
        compatibility_score=score_result.compatibility_score,
        score_breakdown=score_result.score_breakdown,
        applied_weights=score_result.applied_weights,
        candidate_profile=candidate_profile,
        job_profile=job_reqs,
        skill_gaps=all_gaps_combined,
        recommendations=recommendations,
        created_at=datetime.now(timezone.utc).isoformat()
    )

    return APIResponse(
        success=True,
        message="Resume analyzed and compatibility evaluation completed successfully",
        data=report_payload
    )


@router.get("/history", response_model=APIResponse[List[AnalysisHistoryItem]], status_code=status.HTTP_200_OK)
async def get_history(
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Fetches list of historical resume analyses strictly scoped to requesting user"""
    db_service = SupabaseService(user_token=user.token)
    history = db_service.get_history(user_id=user.id)

    history_items = [
        AnalysisHistoryItem(
            id=item["id"],
            candidate_name=item.get("candidate_name", "Anonymous Candidate"),
            job_title=item.get("job_title", "General Position"),
            company_name=item.get("company_name"),
            compatibility_score=item.get("compatibility_score", 0.0),
            created_at=item.get("created_at", datetime.now(timezone.utc).isoformat())
        )
        for item in history
    ]

    audit_service.log_event(
        action="HISTORY_VIEWED",
        user_id=user.id,
        resource_type="history",
        request=request
    )

    return APIResponse(
        success=True,
        message=f"Retrieved {len(history_items)} analysis records",
        data=history_items
    )


@router.get("/{analysis_id}", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
async def get_analysis_by_id(
    analysis_id: str,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Retrieves an existing full analysis report from Supabase by analysis UUID ensuring user ownership"""
    db_service = SupabaseService(user_token=user.token)
    report = db_service.get_analysis_by_id(analysis_id, user_id=user.id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report with ID '{analysis_id}' was not found or you do not have permission to view it."
        )

    audit_service.log_event(
        action="ANALYSIS_VIEWED",
        user_id=user.id,
        resource_type="analysis",
        resource_id=analysis_id,
        request=request
    )

    return APIResponse(
        success=True,
        message="Analysis report retrieved successfully",
        data=report
    )


@router.delete("/{analysis_id}", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
async def delete_analysis(
    analysis_id: str,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Deletes an analysis report and associated skill gaps/recommendations.
    Guarantees strict ownership check: users can only delete their own analyses.
    """
    db_service = SupabaseService(user_token=user.token)
    
    # Verify report exists and belongs to user
    existing_report = db_service.get_analysis_by_id(analysis_id, user_id=user.id)
    if not existing_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report '{analysis_id}' not found or you do not have permission to delete it."
        )

    deleted = db_service.delete_analysis(analysis_id, user_id=user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete analysis record from database."
        )

    audit_service.log_event(
        action="ANALYSIS_DELETED",
        user_id=user.id,
        resource_type="analysis",
        resource_id=analysis_id,
        request=request
    )

    return APIResponse(
        success=True,
        message="Analysis report successfully deleted.",
        data={"analysis_id": analysis_id}
    )
