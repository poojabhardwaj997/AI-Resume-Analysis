# AI-Powered Resume Analysis & Skill Gap Detection System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://reactjs.org)
[![Vite](https://img.shields.io/badge/Vite-6.0+-646CFF.svg?style=flat&logo=vite&logoColor=white)](https://vitejs.dev)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg?style=flat&logo=supabase&logoColor=white)](https://supabase.com)
[![Pytest](https://img.shields.io/badge/Tests-53%20Passed-brightgreen.svg?logo=pytest&logoColor=white)](https://pytest.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://docker.com)

A production-grade, AI-assisted recruitment analysis platform engineered with **FastAPI**, **React.js**, **OpenAI Structured JSON Mode**, and **Supabase PostgreSQL**. Built with explainability at its core to replace legacy keyword-stuffing ATS systems with transparent skill gap diagnostics, textual quote verification, and actionable candidate upskilling roadmaps.

---

## 🌟 Key Features

1. **Dual-Format Document Ingestion**:
   - Parses `.pdf` (via C-accelerated PyMuPDF / `fitz`) and `.docx` (via `python-docx`).
   - Automated magic byte verification, MIME validation, and scanned-document detection.
2. **Deterministic & Semantic Skill Normalization**:
   - Cross-domain synonym taxonomy mapping aliases to canonical forms (e.g., `JS` $\to$ `JavaScript`, `Postgres` $\to$ `PostgreSQL`).
   - Identifies adjacent **Transferable Skills** (e.g., Flask $\to$ FastAPI) with 50% partial credit.
3. **Transparent Mathematical Scoring Engine**:
   - Computes weighted compatibility: $60\% \text{ Required} + 15\% \text{ Preferred} + 15\% \text{ Experience} + 10\% \text{ Education}$.
   - Every sub-score is visualized on an interactive glassmorphism meter.
4. **Explainability with Verifiable Textual Evidence**:
   - Every matched competency includes an exact quote extracted directly from the candidate's uploaded document.
5. **Actionable Learning Recommendations**:
   - Automatically generates targeted learning objectives, beginner drill exercises, and portfolio project suggestions for every missing skill.
6. **Enterprise Security & Privacy**:
   - OWASP defensive headers (`nosniff`, `DENY`, XSS protection).
   - In-memory sliding window rate limiting (100 req/min general, 20 req/min analysis).
   - Candidate PII masking (email & phone) preventing server log leakage.
   - React Error Boundary for zero-crash frontend reliability.
7. **53 Automated Unit & Integration Tests**:
   - Complete test coverage across parsers, normalizers, scorers, and security.

---

## 🏗️ System Architecture

```
User Browser / Recruiter
        │
        ▼ (HTTP REST / JSON / Multipart Form)
React Frontend (Vite, Modern CSS) ── Port 5173
        │
        ▼ (Axios Client with Interceptors)
FastAPI Backend ─────────────────── Port 8000
    ├── SecurityHeaders & RateLimit Middleware
    ├── PyMuPDF & python-docx Document Parsers
    ├── Text Sanitizer & PII Masker
    ├── OpenAI LLM Extraction Service (JSON Mode)
    ├── Skill Normalization & Gap Detection Engine
    ├── 60/15/15/10 Weighted Scoring Calculator
    ├── Actionable Learning Recommendation Engine
    └── Supabase Service Layer (Service Role Key, RLS)
        │
        ▼
Supabase Cloud (PostgreSQL with 8 Relational Tables & Storage)
```

---

## 🚀 Quick Start (3 Ways to Run)

### Method 1: Windows 1-Click Launcher (Easiest)
Simply double-click:
```powershell
start_all.bat
```
*(Or in PowerShell: `.\start_all.ps1`)*

This starts the FastAPI backend, starts the Vite React frontend, and opens your default browser at `http://localhost:5173`!

To stop dev servers:
```powershell
stop_all.bat
```

---

### Method 2: Docker Compose
```bash
docker compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`

---

### Method 3: Manual Terminal Setup

#### Backend:
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

#### Frontend:
```powershell
cd frontend
npm install
npm run dev
```

---

## 🧪 Automated Testing

To run the complete automated test suite (53 tests):
```powershell
cd backend
python run_tests.py
```
Or with pytest:
```powershell
pytest tests/ -v
```

---

## 📬 Postman API Collection

A full Postman API collection is included in the project root:
- **Collection**: [`AIResumeAnalysis.postman_collection.json`](file:///c:/AIResumeAnalysis/AIResumeAnalysis.postman_collection.json)
- **Environment**: [`AIResumeAnalysis.postman_environment.json`](file:///c:/AIResumeAnalysis/AIResumeAnalysis.postman_environment.json)

Import both files into Postman or Thunder Client to test all endpoints (`/api/health`, `/api/resumes/upload`, `/api/job/analyze`, `/api/skill-gap/analyze`, `/api/analysis/create`, `/api/analysis/history`).

---

## 📑 Academic Documentation

- **Full Project Report**: [`docs/PROJECT_REPORT.md`](file:///c:/AIResumeAnalysis/docs/PROJECT_REPORT.md) (Abstract, Architecture, DFD Level 0/1/2, ER Diagrams, Scoring Mathematics, Security Analysis).
- **Viva-Voce Q&A Guide**: [`docs/VIVA_PREPARATION_GUIDE.md`](file:///c:/AIResumeAnalysis/docs/VIVA_PREPARATION_GUIDE.md) (25+ examiner questions with model answers).
- **Database Schema DDL**: [`backend/app/database/schema.sql`](file:///c:/AIResumeAnalysis/backend/app/database/schema.sql).

---

## ⚖️ Ethics & Responsible AI Notice

- **Human-in-the-Loop**: This platform serves as an advisory decision-support system for recruiters and an upskilling tool for candidates. It does not perform automated rejections or adverse hiring decisions.
- **Fairness & Bias Minimization**: Demographic attributes (gender, age, ethnicity, religion, marital status) are excluded from all scoring calculations.
- **Candidate Privacy**: Contact details are protected through PII masking and Supabase Row Level Security.
