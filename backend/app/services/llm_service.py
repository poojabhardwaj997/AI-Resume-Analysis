import json
import re
from typing import Dict, Any, Optional
from openai import OpenAI
from pydantic import ValidationError

from app.config import get_settings
from app.schemas.resume import CandidateProfile
from app.schemas.job import JobRequirements
from app.utils.logger import logger

RESUME_EXTRACTION_SYSTEM_PROMPT = """
You are an expert HR Data Scientist and Resume Intelligence System.
Your job is to parse unstructured resume text into a strict, structured JSON object.

STRICT EXTRACTION RULES:
1. NEVER hallucinate or invent qualifications, companies, degrees, or skills not explicitly stated in the resume text.
2. If any field is not explicitly mentioned, output null for strings or an empty array [] for lists.
3. Separate technical skills, frameworks, tools, and domain concepts into individual string items in the "skills" list.
4. Distinguish candidate projects from work experience companies.
5. Extract contact details (email, phone, candidate_name) accurately without formatting distortion.

Output MUST be a valid JSON object matching this schema:
{
  "candidate_name": string or null,
  "email": string or null,
  "phone": string or null,
  "summary": string or null,
  "education": [
    { "degree": string, "institution": string, "year": string or null, "grade": string or null }
  ],
  "skills": [string],
  "experience": [
    { "title": string, "company": string, "duration": string or null, "responsibilities": [string] }
  ],
  "projects": [
    { "title": string, "description": string, "technologies": [string] }
  ],
  "certifications": [string],
  "languages": [string]
}
"""

JOB_DESCRIPTION_SYSTEM_PROMPT = """
You are an expert Technical Recruiter and Job Requirements Analyst.
Your job is to parse unstructured Job Description (JD) text into a structured JSON requirements specification.

EXTRACTION RULES:
1. Distinguish between REQUIRED skills (mandatory, must-have) and PREFERRED skills (nice-to-have, bonus, optional, advantageous).
2. Do NOT invent skills or requirements that cannot be reasonably inferred from the JD text.
3. Extract education requirements (e.g., "Bachelor's in CS or equivalent").
4. Extract experience requirements (e.g., "3+ years in backend engineering").
5. Extract relevant certifications if mentioned.

Output MUST be a valid JSON object matching this schema:
{
  "job_title": string or null,
  "company_name": string or null,
  "required_skills": [string],
  "preferred_skills": [string],
  "education_requirements": [string],
  "experience_requirements": [string],
  "certifications": [string]
}
"""


class LLMService:
    """
    Orchestrates OpenAI LLM calls with JSON schema mode and deterministic heuristic fallbacks.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.OPENAI_API_KEY
        self.model = model or self.settings.OPENAI_MODEL
        self.client: Optional[OpenAI] = None

        if self.settings.is_openai_configured and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI LLM service initialized with model '{self.model}'")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None

    def analyze_resume(self, clean_text: str) -> CandidateProfile:
        """
        Parses resume text into CandidateProfile.
        Uses OpenAI structured JSON mode if configured; otherwise uses deterministic fallback.
        """
        if not clean_text or not clean_text.strip():
            return CandidateProfile()

        if self.client:
            try:
                return self._call_openai_resume_extraction(clean_text)
            except Exception as e:
                logger.warning(f"OpenAI API call failed ({str(e)}). Switching to intelligent fallback parser.")
                return self._heuristic_fallback_resume_parser(clean_text)
        else:
            logger.info("OpenAI API key not configured. Using deterministic heuristic resume parser.")
            return self._heuristic_fallback_resume_parser(clean_text)

    def analyze_job_description(self, jd_text: str, job_title: Optional[str] = None, company_name: Optional[str] = None) -> JobRequirements:
        """
        Parses Job Description text into structured JobRequirements.
        Uses OpenAI JSON mode when configured; falls back to deterministic heuristic rules.
        """
        if not jd_text or not jd_text.strip():
            return JobRequirements(job_title=job_title, company_name=company_name)

        if self.client:
            try:
                return self._call_openai_job_extraction(jd_text, job_title, company_name)
            except Exception as e:
                logger.warning(f"OpenAI JD analysis failed ({str(e)}). Switching to fallback parser.")
                return self._heuristic_fallback_job_parser(jd_text, job_title, company_name)
        else:
            logger.info("OpenAI API key not configured. Using deterministic heuristic JD parser.")
            return self._heuristic_fallback_job_parser(jd_text, job_title, company_name)

    def _call_openai_resume_extraction(self, text: str) -> CandidateProfile:
        truncated_text = " ".join(text.split()[:4000])
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": RESUME_EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Parse the following resume text:\n\n{truncated_text}"}
            ]
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI returned an empty response")
        parsed_dict = json.loads(content)
        return CandidateProfile.model_validate(parsed_dict)

    def _call_openai_job_extraction(self, text: str, job_title: Optional[str], company_name: Optional[str]) -> JobRequirements:
        truncated_text = " ".join(text.split()[:3000])
        user_prompt = f"Parse the following Job Description text into required vs preferred skills, education, and experience."
        if job_title:
            user_prompt += f"\nSpecified Job Title: {job_title}"
        if company_name:
            user_prompt += f"\nSpecified Company: {company_name}"
        user_prompt += f"\n\n{truncated_text}"

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": JOB_DESCRIPTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI returned an empty response for JD parsing")
        parsed_dict = json.loads(content)
        if job_title and not parsed_dict.get("job_title"):
            parsed_dict["job_title"] = job_title
        if company_name and not parsed_dict.get("company_name"):
            parsed_dict["company_name"] = company_name
        return JobRequirements.model_validate(parsed_dict)

    def _heuristic_fallback_resume_parser(self, text: str) -> CandidateProfile:
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        candidate_name = lines[0] if lines and len(lines[0].split()) <= 4 else None

        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        email = email_match.group(0) if email_match else None

        phone_match = re.search(r'(?:Phone|Mobile|Contact|Tel)?[:\s]*(\+?\d[\d\s\-\(\)\.]{8,18}\d)', text, re.IGNORECASE)
        phone = phone_match.group(1).strip() if phone_match else None

        found_skills = self._extract_skills_by_vocabulary(text)

        education = []
        edu_degrees = ["BSc", "B.Sc", "Bachelor", "B.Tech", "BTech", "BBA", "B.Com", "MSc", "M.Tech", "MBA", "Master", "PhD", "Diploma"]
        for line in lines:
            if any(deg.lower() in line.lower() for deg in edu_degrees):
                education.append({"degree": line, "institution": "Extracted from Resume", "year": None, "grade": None})
                if len(education) >= 2:
                    break

        summary = lines[1] if len(lines) > 2 and len(lines[1]) > 30 else "Candidate profile extracted from document."

        profile_data = {
            "candidate_name": candidate_name,
            "email": email,
            "phone": phone,
            "summary": summary,
            "education": education,
            "skills": found_skills,
            "experience": [],
            "projects": [],
            "certifications": [],
            "languages": ["English"]
        }
        return CandidateProfile.model_validate(profile_data)

    def _heuristic_fallback_job_parser(self, text: str, job_title: Optional[str], company_name: Optional[str]) -> JobRequirements:
        """
        Deterministic offline JD parser separating required vs preferred skills
        and extracting experience and degree criteria.
        """
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        # Infer title if not explicitly supplied
        inferred_title = job_title
        if not inferred_title:
            for line in lines[:3]:
                if any(k in line.lower() for k in ["title:", "role:", "engineer", "developer", "analyst", "manager", "specialist", "executive"]):
                    inferred_title = re.sub(r'(?i)^(job\s+title|role|position)[:\s]*', '', line).strip()
                    break
        if not inferred_title and lines:
            inferred_title = lines[0]

        # Partition text into Preferred sections vs General/Required sections
        preferred_indicators = ["preferred", "nice to have", "plus", "bonus", "advantageous", "desirable", "good to have"]
        required_lines = []
        preferred_lines = []
        is_preferred_block = False

        for line in lines:
            lower_line = line.lower()
            if any(ind in lower_line for ind in preferred_indicators):
                is_preferred_block = True
            elif any(req in lower_line for req in ["requirements:", "must have:", "responsibilities:", "qualifications:"]):
                is_preferred_block = False

            if is_preferred_block:
                preferred_lines.append(line)
            else:
                required_lines.append(line)

        all_skills = self._extract_skills_by_vocabulary(text)
        preferred_skills_found = self._extract_skills_by_vocabulary("\n".join(preferred_lines))

        # Separate required from preferred
        required_skills_found = [s for s in all_skills if s not in preferred_skills_found]
        if not required_skills_found and all_skills:
            required_skills_found = all_skills
            preferred_skills_found = []

        # Extract experience requirements
        experience_requirements = []
        for line in lines:
            if re.search(r'\b\d+\+?\s*(?:-\s*\d+)?\s*(?:years?|yrs?)\b', line, re.IGNORECASE):
                experience_requirements.append(line.lstrip("-*• "))

        # Extract education requirements
        education_requirements = []
        edu_keywords = ["degree", "bachelor", "master", "bsc", "btech", "bba", "msc", "mba", "diploma", "graduate"]
        for line in lines:
            if any(k in line.lower() for k in edu_keywords):
                education_requirements.append(line.lstrip("-*• "))

        return JobRequirements(
            job_title=inferred_title or "General Position",
            company_name=company_name or "Hiring Organization",
            required_skills=required_skills_found,
            preferred_skills=preferred_skills_found,
            education_requirements=education_requirements[:2],
            experience_requirements=experience_requirements[:2],
            certifications=[]
        )

    def _extract_skills_by_vocabulary(self, text: str) -> list[str]:
        """Scans text against multi-domain skills taxonomy"""
        common_skills_vocabulary = [
            "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "HTML", "CSS", "SQL", "Git",
            "FastAPI", "Django", "Flask", "React", "Node.js", "Express", "Next.js", "Angular", "Vue",
            "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis", "Docker", "Kubernetes", "AWS", "Azure",
            "Linux", "CI/CD", "REST API", "GraphQL", "PyTorch", "TensorFlow", "Pandas", "NumPy", "Scikit-Learn",
            "Power BI", "Tableau", "Excel", "Data Analysis", "Machine Learning", "Deep Learning",
            "Statistics", "R Programming", "Big Data", "Spark", "Hadoop", "Data Modeling", "ETL",
            "Recruitment", "Talent Acquisition", "Human Resources", "Employee Engagement", "Payroll",
            "Negotiation", "Project Management", "Agile", "Scrum", "Jira", "Leadership", "Communication",
            "Financial Modeling", "Accounting", "Auditing", "Taxation", "Tally", "QuickBooks", "Budgeting"
        ]
        found = []
        lower_text = text.lower()
        for skill in common_skills_vocabulary:
            pattern = r'(?i)\b' + re.escape(skill) + r'\b'
            if re.search(pattern, lower_text):
                found.append(skill)
        return found
