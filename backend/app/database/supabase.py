from typing import Optional, Dict, Any, List
import uuid
from supabase import create_client, Client
from app.config import get_settings
from app.utils.logger import logger

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
    """
    Returns a singleton instance of the Supabase Client authenticated
    using the backend's configured API key (service_role or publishable).
    """
    global _supabase_client
    settings = get_settings()

    if _supabase_client is not None:
        return _supabase_client

    if not settings.is_supabase_configured:
        logger.warning("Supabase credentials not configured in backend/.env. Database features will operate in mock/offline mode.")
        return None

    try:
        _supabase_client = create_client(settings.supabase_url, settings.supabase_api_key)
        logger.info(f"Supabase client initialized for project: {settings.supabase_url}")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {str(e)}")
        return None


_SENTINEL = object()


class SupabaseService:
    """
    Service layer abstracting Supabase PostgreSQL tables and Storage bucket operations.
    Enforces user ownership and multi-tenant data isolation.
    """

    def __init__(self, client: Any = _SENTINEL, user_token: Optional[str] = None):
        if client is not _SENTINEL:
            self.client = client
        else:
            self.client = get_supabase_client()
        self.settings = get_settings()

        if self.client and user_token:
            try:
                self.client.postgrest.auth(user_token)
            except Exception as e:
                logger.warning(f"Could not apply user token to PostgREST client: {str(e)}")

    def check_connection(self) -> Dict[str, Any]:
        """
        Pings Supabase by performing a lightweight query on the resumes table.
        """
        if not self.client:
            return {"status": "unconfigured", "detail": "Missing SUPABASE_URL or API key"}
        
        try:
            res = self.client.table("resumes").select("id").limit(1).execute()
            return {"status": "connected", "detail": "Successfully queried Supabase PostgreSQL database"}
        except Exception as e:
            logger.error(f"Supabase connection check failed: {str(e)}")
            return {"status": "error", "detail": str(e)}

    def upload_file_to_storage(self, file_bytes: bytes, original_filename: str, content_type: str, user_id: Optional[str] = None) -> Optional[str]:
        """
        Uploads a resume file to Supabase Storage bucket ('resumes').
        Stores files under a user-scoped path (e.g., 'user_id/safe_filename') for clean isolation.
        """
        if not self.client:
            return None

        try:
            safe_id = uuid.uuid4().hex[:8]
            clean_name = original_filename.replace(" ", "_").replace("/", "_")
            user_prefix = f"{user_id}/" if user_id else ""
            storage_path = f"{user_prefix}{safe_id}_{clean_name}"
            
            bucket_name = self.settings.SUPABASE_STORAGE_BUCKET
            self.client.storage.from_(bucket_name).upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": content_type}
            )
            logger.info(f"Uploaded resume file to Supabase Storage: {bucket_name}/{storage_path}")
            return storage_path
        except Exception as e:
            logger.warning(f"Failed to upload file to Supabase Storage: {str(e)}")
            return None

    def insert_resume(
        self,
        file_name: str,
        file_type: str,
        file_size: int,
        raw_text: str,
        parsed_profile: dict,
        storage_path: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Inserts a parsed resume record into the 'resumes' table with user ownership.
        """
        if not self.client:
            mock_id = str(uuid.uuid4())
            logger.info(f"[Mock DB] Generated resume ID: {mock_id}")
            return mock_id

        data = {
            "file_name": file_name,
            "storage_path": storage_path,
            "file_type": file_type,
            "file_size": file_size,
            "raw_text": raw_text,
            "parsed_profile": parsed_profile,
        }
        if user_id:
            data["user_id"] = user_id

        try:
            res = self.client.table("resumes").insert(data).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]["id"]
            return str(uuid.uuid4())
        except Exception as e:
            logger.error(f"Failed to insert resume into Supabase: {str(e)}")
            return str(uuid.uuid4())

    def insert_job_description(
        self,
        job_title: str,
        company_name: str,
        raw_text: str,
        parsed_requirements: dict,
        user_id: Optional[str] = None
    ) -> str:
        """
        Inserts a job description record into 'job_descriptions' with user ownership.
        """
        if not self.client:
            mock_id = str(uuid.uuid4())
            logger.info(f"[Mock DB] Generated job ID: {mock_id}")
            return mock_id

        data = {
            "job_title": job_title,
            "company_name": company_name,
            "raw_text": raw_text,
            "parsed_requirements": parsed_requirements
        }
        if user_id:
            data["user_id"] = user_id

        try:
            res = self.client.table("job_descriptions").insert(data).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]["id"]
            return str(uuid.uuid4())
        except Exception as e:
            logger.error(f"Failed to insert job description into Supabase: {str(e)}")
            return str(uuid.uuid4())

    def insert_candidate_skills(self, resume_id: str, skills: List[Dict[str, Any]]):
        """
        Bulk inserts normalized candidate skills.
        """
        if not self.client or not skills:
            return
        
        rows = [
            {
                "resume_id": resume_id,
                "skill_name": s.get("skill_name", ""),
                "normalized_name": s.get("normalized_name", s.get("skill_name", "")),
                "category": s.get("category", "General"),
                "proficiency": s.get("proficiency", "Intermediate")
            }
            for s in skills
        ]
        try:
            self.client.table("candidate_skills").insert(rows).execute()
        except Exception as e:
            logger.warning(f"Could not persist candidate skills: {str(e)}")

    def insert_job_skills(self, job_id: str, skills: List[Dict[str, Any]]):
        """
        Bulk inserts required and preferred job skills.
        """
        if not self.client or not skills:
            return

        rows = [
            {
                "job_id": job_id,
                "skill_name": s.get("skill_name", ""),
                "normalized_name": s.get("normalized_name", s.get("skill_name", "")),
                "requirement_type": s.get("requirement_type", "required"),
                "importance_weight": s.get("importance_weight", 1.0)
            }
            for s in skills
        ]
        try:
            self.client.table("job_skills").insert(rows).execute()
        except Exception as e:
            logger.warning(f"Could not persist job skills: {str(e)}")

    def insert_analysis(
        self,
        resume_id: str,
        job_id: str,
        compatibility_score: float,
        required_score: float = 0.0,
        preferred_score: float = 0.0,
        experience_score: float = 0.0,
        education_score: float = 0.0,
        summary_notes: Optional[dict] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Inserts master analysis report into 'analyses' with user ownership.
        """
        if not self.client:
            mock_id = str(uuid.uuid4())
            logger.info(f"[Mock DB] Generated analysis ID: {mock_id}")
            return mock_id

        data = {
            "resume_id": resume_id,
            "job_id": job_id,
            "compatibility_score": round(compatibility_score, 2),
            "required_score": round(required_score, 2),
            "preferred_score": round(preferred_score, 2),
            "experience_score": round(experience_score, 2),
            "education_score": round(education_score, 2),
            "summary_notes": summary_notes or {}
        }
        if user_id:
            data["user_id"] = user_id

        try:
            res = self.client.table("analyses").insert(data).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]["id"]
            return str(uuid.uuid4())
        except Exception as e:
            logger.error(f"Failed to insert analysis into Supabase: {str(e)}")
            return str(uuid.uuid4())

    def insert_skill_gaps(self, analysis_id: str, gaps: List[Dict[str, Any]]):
        """
        Bulk inserts individual skill gap status and evidence.
        """
        if not self.client or not gaps:
            return

        rows = [
            {
                "analysis_id": analysis_id,
                "skill_name": g.get("skill", g.get("skill_name", "")),
                "status": g.get("status", "missing"),
                "evidence": g.get("evidence"),
                "explanation": g.get("explanation")
            }
            for g in gaps
        ]
        try:
            self.client.table("skill_gaps").insert(rows).execute()
        except Exception as e:
            logger.warning(f"Could not persist skill gaps: {str(e)}")

    def insert_recommendations(self, analysis_id: str, recommendations: List[Dict[str, Any]]):
        """
        Bulk inserts learning recommendations.
        """
        if not self.client or not recommendations:
            return

        rows = [
            {
                "analysis_id": analysis_id,
                "skill_name": r.get("skill", r.get("skill_name", "")),
                "learning_objective": r.get("learning_objective", ""),
                "why_it_matters": r.get("why_it_matters", ""),
                "practical_exercise": r.get("practical_exercise", ""),
                "suggested_project": r.get("suggested_project", ""),
                "resource_direction": r.get("resource_direction", "")
            }
            for r in recommendations
        ]
        try:
            self.client.table("recommendations").insert(rows).execute()
        except Exception as e:
            logger.warning(f"Could not persist recommendations: {str(e)}")

    def get_analysis_by_id(self, analysis_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetches an analysis report joined with resume, job, skill gaps, and recommendations.
        Enforces user ownership: if user_id is provided, returns None if owned by another user.
        """
        if not self.client:
            return None

        try:
            query = self.client.table("analyses").select("*").eq("id", analysis_id)
            if user_id:
                query = query.eq("user_id", user_id)
                
            analysis_res = query.single().execute()
            if not analysis_res.data:
                return None
            analysis = analysis_res.data

            # Fetch related records
            resume_res = self.client.table("resumes").select("*").eq("id", analysis["resume_id"]).single().execute()
            job_res = self.client.table("job_descriptions").select("*").eq("id", analysis["job_id"]).single().execute()
            gaps_res = self.client.table("skill_gaps").select("*").eq("analysis_id", analysis_id).execute()
            recs_res = self.client.table("recommendations").select("*").eq("analysis_id", analysis_id).execute()

            return {
                "analysis_id": analysis["id"],
                "user_id": analysis.get("user_id"),
                "compatibility_score": float(analysis["compatibility_score"]),
                "score_breakdown": {
                    "required_skills_match": float(analysis.get("required_score", 0)),
                    "preferred_skills_match": float(analysis.get("preferred_score", 0)),
                    "experience_match": float(analysis.get("experience_score", 0)),
                    "education_match": float(analysis.get("education_score", 0)),
                },
                "candidate_profile": resume_res.data.get("parsed_profile", {}) if resume_res.data else {},
                "job_profile": {
                    "job_title": job_res.data.get("job_title") if job_res.data else "",
                    "company_name": job_res.data.get("company_name") if job_res.data else "",
                    **(job_res.data.get("parsed_requirements", {}) if job_res.data else {})
                },
                "skill_gaps": [
                    {
                        "skill": g["skill_name"],
                        "status": g["status"],
                        "evidence": g.get("evidence"),
                        "explanation": g.get("explanation")
                    }
                    for g in (gaps_res.data or [])
                ],
                "recommendations": recs_res.data or [],
                "created_at": analysis["created_at"]
            }
        except Exception as e:
            logger.error(f"Error fetching analysis {analysis_id}: {str(e)}")
            return None

    def get_history(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetches history summaries of analyses scoped strictly to the requesting user.
        """
        if not self.client:
            return []

        try:
            query = self.client.table("analyses").select(
                "id, user_id, compatibility_score, created_at, resumes(parsed_profile), job_descriptions(job_title, company_name)"
            )
            
            # Strict user isolation filter
            if user_id:
                query = query.eq("user_id", user_id)

            res = query.order("created_at", desc=True).limit(50).execute()

            history = []
            for row in (res.data or []):
                cand_name = "Anonymous Candidate"
                if row.get("resumes") and row["resumes"].get("parsed_profile"):
                    cand_name = row["resumes"]["parsed_profile"].get("candidate_name") or "Candidate"

                job_title = "General Role"
                company = ""
                if row.get("job_descriptions"):
                    job_title = row["job_descriptions"].get("job_title") or "General Role"
                    company = row["job_descriptions"].get("company_name") or ""

                history.append({
                    "id": row["id"],
                    "candidate_name": cand_name,
                    "job_title": job_title,
                    "company_name": company,
                    "compatibility_score": float(row["compatibility_score"]),
                    "created_at": row["created_at"]
                })
            return history
        except Exception as e:
            logger.error(f"Error fetching analysis history: {str(e)}")
            return []

    def delete_analysis(self, analysis_id: str, user_id: Optional[str] = None) -> bool:
        """
        Deletes an analysis report and cascades associated child records (skill_gaps, recommendations).
        Verifies ownership: user can only delete their own analyses.
        """
        if not self.client:
            return True

        try:
            query = self.client.table("analyses").delete().eq("id", analysis_id)
            if user_id:
                query = query.eq("user_id", user_id)
            
            res = query.execute()
            # If at least 1 record deleted
            return bool(res.data and len(res.data) > 0)
        except Exception as e:
            logger.error(f"Error deleting analysis {analysis_id}: {str(e)}")
            return False

    def get_resume(self, resume_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetches a resume metadata record ensuring user ownership.
        """
        if not self.client:
            return {"id": resume_id, "file_name": "sample_resume.pdf"}

        try:
            query = self.client.table("resumes").select("*").eq("id", resume_id)
            if user_id:
                query = query.eq("user_id", user_id)
            res = query.single().execute()
            return res.data
        except Exception as e:
            logger.warning(f"Resume {resume_id} not found: {str(e)}")
            return None

    def get_job(self, job_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetches a job description record ensuring user ownership.
        """
        if not self.client:
            return {"id": job_id, "job_title": "Software Engineer"}

        try:
            query = self.client.table("job_descriptions").select("*").eq("id", job_id)
            if user_id:
                query = query.eq("user_id", user_id)
            res = query.single().execute()
            return res.data
        except Exception as e:
            logger.warning(f"Job {job_id} not found: {str(e)}")
            return None
