# College Viva-Voce Preparation Guide: AI Resume Analysis System

This guide prepares you for questions commonly asked by internal professors, external university examiners, and technical evaluators during project defense / viva-voce presentations.

---

## Category 1: Project Overview & Motivation

### Q1: What is the main problem your project solves?
**Answer**:
Traditional Applicant Tracking Systems (ATS) rely on simple keyword matching. This leads to two major flaws:
1. **False Rejections**: Qualified candidates who use synonyms (e.g. "PostgreSQL" vs "Postgres", or "Flask" instead of "FastAPI") get filtered out.
2. **Zero Actionability**: Candidates receive generic rejection emails with no guidance.

Our system introduces **semantic skill normalization**, **verifiable evidence quotes** extracted directly from the resume text, a **transparent 60/15/15/10 scoring algorithm**, and **actionable learning recommendations** (practice exercises & project ideas) for missing competencies.

---

### Q2: Why did you choose FastAPI over Django or Flask?
**Answer**:
1. **Asynchronous Performance (ASGI)**: FastAPI is built on Starlette and Uvicorn, making it natively async. Handling multiple concurrent document uploads and external LLM API calls is significantly faster without blocking threads.
2. **Automatic Data Validation**: FastAPI uses Pydantic v2 for request/response serialization and type validation.
3. **Interactive Documentation**: It automatically generates OpenAPI (`/docs` Swagger UI and `/redoc`) schemas without extra code.

---

### Q3: What is the tech stack used in your project?
**Answer**:
* **Backend**: Python 3.11+, FastAPI, Uvicorn, PyMuPDF (`fitz`), `python-docx`, OpenAI API (JSON Mode), Pydantic v2.
* **Frontend**: React 18 (Vite), Modern Vanilla CSS with design tokens (glassmorphism & responsive layouts), Lucide Icons, Axios.
* **Database & Cloud**: Supabase (PostgreSQL with Row Level Security & Indexes), Supabase Storage.
* **Testing & Security**: Pytest (53 automated tests), OWASP defensive headers middleware, sliding window rate limiter, PII sanitization.
* **DevOps**: Docker, Docker Compose, Nginx Alpine.

---

## Category 2: AI, Parsing & LLM Implementation

### Q4: How do you parse PDF and Word documents without OCR?
**Answer**:
* For **PDFs**: We use **PyMuPDF (`fitz`)**, which is a high-performance C-based binding that extracts digital text streams, font bounding blocks, and paragraph layouts.
* For **Word (.docx)**: We use **`python-docx`**, traversing document paragraph and table XML trees.
* **Scanned PDF Handling**: We implemented an automated character threshold check: if a PDF yields fewer than 40 characters, the system flags it as an image/scanned document and prompts the user for a digital text document.

---

### Q5: How do you prevent LLM hallucinations and get structured data?
**Answer**:
1. **JSON Object Mode**: We pass `response_format={"type": "json_object"}` in OpenAI API calls.
2. **Pydantic Validation**: The LLM's raw JSON response is parsed into strict Pydantic schemas (`CandidateProfileSchema`, `JobRequirementsSchema`). If any required field is missing or invalid, our validation layer catches it.
3. **Deterministic Fallback Engine**: If the OpenAI API key is unconfigured or rate-limited, our system falls back to a deterministic heuristic extraction engine so the application never crashes during offline demonstrations.

---

### Q6: How does the Skill Normalization Engine work?
**Answer**:
Raw skills in resumes vary wildly (e.g., "JS", "Javascript", "ECMAScript", "Vanilla JS").
Our normalization engine:
1. Normalizes case and punctuation (e.g., "Node.JS" $\to$ "nodejs").
2. Resolves aliases against a curated synonym taxonomy dictionary (mapping "JS" $\to$ "JavaScript", "Python 3" $\to$ "Python", "Postgres" $\to$ "PostgreSQL").
3. Groups skills into functional categories (Frontend, Backend, Database, Cloud, Machine Learning, HR, Management).
4. Associates related/transferable skills (e.g., Flask is mapped as transferable to FastAPI; Vue is mapped as transferable to React).

---

## Category 3: Scoring & Explainability Algorithm

### Q7: Explain your scoring formula. Why are weights divided 60/15/15/10?
**Answer**:
The overall compatibility score is calculated using a transparent weighted sum:
$$\text{Score} = (0.60 \times S_{\text{required}}) + (0.15 \times S_{\text{preferred}}) + (0.15 \times S_{\text{experience}}) + (0.10 \times S_{\text{education}})$$

**Justification**:
* **60% Required Skills**: Mandatory skills are the primary filter for job performance.
* **15% Preferred Skills**: Bonus competencies give competitive advantage but aren't strictly disqualifying.
* **15% Experience Alignment**: Assesses years and seniority level in the target domain.
* **10% Education**: Relevant degree or equivalent accreditation.
* *Note: All weights are fully configurable via `.env` without modifying business logic.*

---

### Q8: What are "Transferable Skills" and how are they scored?
**Answer**:
If a job requires **FastAPI** and the candidate lists **Flask** or **Django**, rejecting the candidate would be inaccurate because their Python backend foundations directly transfer.
Our engine awards **0.5 (50% partial credit)** for transferable skills and highlights them with an amber badge, explaining why the skill is transferable.

---

### Q9: How do you ensure Explainability in skill matches?
**Answer**:
Rather than simply returning `"Python: Matched"`, our system searches the sanitized resume text and extracts an **exact textual quote** showing the candidate's actual usage (e.g. *"Developed microservices using Python and FastAPI handling 10k requests/min"*). This allows recruiters to verify evidence with zero guesswork.

---

## Category 4: Database, Security & Testing

### Q10: Why Supabase and what is Row Level Security (RLS)?
**Answer**:
Supabase provides enterprise-grade PostgreSQL with instant REST/GraphQL APIs and Storage buckets.
**Row Level Security (RLS)** ensures that database rows are protected at the database engine level. We enabled RLS across all 8 tables and configured backend operations to communicate securely using the `SUPABASE_SERVICE_ROLE_KEY`.

---

### Q11: How does your Rate Limiter work?
**Answer**:
We implemented an **in-memory sliding window rate limiter middleware** in Starlette/FastAPI. It tracks request timestamps per client IP. If a client exceeds 20 requests per minute on heavy AI analysis endpoints, the server rejects subsequent requests with **`HTTP 429 Too Many Requests`** and includes a standard **`Retry-After`** header indicating how many seconds to wait.

---

### Q12: How do you protect candidate Privacy and PII?
**Answer**:
Under GDPR and privacy best practices, sensitive personally identifiable information (PII) like personal emails and phone numbers must not be dumped into server console logs.
We built a `pii_sanitizer` module that masks emails (e.g., `j***e@example.com`) and phone numbers (e.g., `***-***-8765`) before passing profiles to loggers.

---

### Q13: How many automated tests exist in your project?
**Answer**:
We have **53 automated unit and integration tests** in Pytest covering all 12 system domains (parsers, normalizers, file validation, security headers, rate limiting, LLM fallbacks, scoring math, and Supabase integration). All 53 tests execute in under 8 seconds with 100% pass rate via `python backend/run_tests.py`.

---

## Quick Viva Tips
1. **Be confident about the Math**: Remember the formula: $60\% \text{ Required} + 15\% \text{ Preferred} + 15\% \text{ Experience} + 10\% \text{ Education}$.
2. **Emphasize Explainability**: Mention that recruiters love the textual evidence quotes and candidates love the learning roadmaps.
3. **Highlight Zero-Crash Resilience**: Mention that both frontend (React Error Boundary) and backend (deterministic fallback parser) are designed never to crash, even if offline or without third-party API keys.
