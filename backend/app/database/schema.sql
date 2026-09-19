-- ===================================================================
-- AI-Powered Resume Analysis & Skill Gap Detection Database Schema
-- Database: Supabase PostgreSQL
-- ===================================================================

-- 0. Enable UUID generation extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -------------------------------------------------------------------
-- 1. Users Table (System or Candidate Profile Identity)
-- -------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- -------------------------------------------------------------------
-- 2. Resumes Table (Uploaded documents & extracted candidate profile)
-- -------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    file_name VARCHAR(255) NOT NULL,
    storage_path TEXT,
    file_type VARCHAR(50) NOT NULL,            -- e.g. 'application/pdf', 'docx'
    file_size INTEGER NOT NULL,                -- bytes
    raw_text TEXT,                             -- Sanitized raw text extracted from file
    parsed_profile JSONB DEFAULT '{}'::jsonb,  -- Full structured JSON extracted by LLM
    uploaded_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- -------------------------------------------------------------------
-- 3. Job Descriptions Table (Target job requirements & criteria)
-- -------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.job_descriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_title VARCHAR(255),
    company_name VARCHAR(255),
    raw_text TEXT NOT NULL,
    parsed_requirements JSONB DEFAULT '{}'::jsonb, -- Structured requirements extracted by LLM
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- -------------------------------------------------------------------
-- 4. Candidate Skills Table (Normalized candidate skill entities)
-- -------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.candidate_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL REFERENCES public.resumes(id) ON DELETE CASCADE,
    skill_name VARCHAR(150) NOT NULL,          -- Raw string as appeared in resume
    normalized_name VARCHAR(150) NOT NULL,     -- Standardized taxonomy term (e.g. 'JavaScript')
    category VARCHAR(100),                     -- e.g. 'Programming Language', 'Cloud', 'Soft Skill'
    proficiency VARCHAR(50),                   -- e.g. 'Beginner', 'Intermediate', 'Advanced'
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- -------------------------------------------------------------------
-- 5. Job Skills Table (Normalized required & preferred job skills)
-- -------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.job_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES public.job_descriptions(id) ON DELETE CASCADE,
    skill_name VARCHAR(150) NOT NULL,          -- Raw string from JD
    normalized_name VARCHAR(150) NOT NULL,     -- Standardized taxonomy term
    requirement_type VARCHAR(50) DEFAULT 'required', -- 'required' OR 'preferred'
    importance_weight NUMERIC(3,2) DEFAULT 1.00,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- -------------------------------------------------------------------
-- 6. Analyses Table (Master compatibility analysis report)
-- -------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resume_id UUID NOT NULL REFERENCES public.resumes(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES public.job_descriptions(id) ON DELETE CASCADE,
    compatibility_score NUMERIC(5,2) NOT NULL, -- Overall weighted score: 0.00 to 100.00
    required_score NUMERIC(5,2) DEFAULT 0.00,  -- Required skills sub-score
    preferred_score NUMERIC(5,2) DEFAULT 0.00, -- Preferred skills sub-score
    experience_score NUMERIC(5,2) DEFAULT 0.00,
    education_score NUMERIC(5,2) DEFAULT 0.00,
    summary_notes JSONB DEFAULT '{}'::jsonb,   -- Additional LLM qualitative evaluation
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- -------------------------------------------------------------------
-- 7. Skill Gaps Table (Skill comparison matrix & evidence)
-- -------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.skill_gaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES public.analyses(id) ON DELETE CASCADE,
    skill_name VARCHAR(150) NOT NULL,
    status VARCHAR(50) NOT NULL,               -- 'matched', 'missing', 'transferable', 'preferred_gap'
    evidence TEXT,                             -- Direct quote from candidate's resume
    explanation TEXT,                          -- Reason why this skill is marked missing or needed
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- -------------------------------------------------------------------
-- 8. Recommendations Table (Actionable learning roadmap per gap)
-- -------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID NOT NULL REFERENCES public.analyses(id) ON DELETE CASCADE,
    skill_name VARCHAR(150) NOT NULL,
    learning_objective TEXT NOT NULL,          -- What to learn
    why_it_matters TEXT NOT NULL,              -- Contextual relevance to target job
    practical_exercise TEXT,                   -- Hands-on beginner practice drill
    suggested_project TEXT,                    -- Portfolio-ready project idea
    resource_direction TEXT,                   -- Suggested documentation or framework link
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- ===================================================================
-- PERFORMANCE INDEXES
-- ===================================================================
CREATE INDEX IF NOT EXISTS idx_resumes_uploaded_at ON public.resumes(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON public.resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_candidate_skills_resume ON public.candidate_skills(resume_id);
CREATE INDEX IF NOT EXISTS idx_candidate_skills_normalized ON public.candidate_skills(normalized_name);
CREATE INDEX IF NOT EXISTS idx_job_skills_job ON public.job_skills(job_id);
CREATE INDEX IF NOT EXISTS idx_job_skills_normalized ON public.job_skills(normalized_name);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON public.analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_resume_job ON public.analyses(resume_id, job_id);
CREATE INDEX IF NOT EXISTS idx_skill_gaps_analysis ON public.skill_gaps(analysis_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_analysis ON public.recommendations(analysis_id);

-- ===================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ===================================================================
-- Enable RLS on all 8 tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.candidate_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.skill_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;

-- Note on Backend Service Role:
-- FastAPI connects using `SUPABASE_SERVICE_ROLE_KEY`. In Supabase PostgreSQL,
-- requests authenticated via the service_role key automatically bypass RLS policies.
-- This allows our backend to safely write records, perform cross-table transactions,
-- and manage storage while preventing external users from tampering with data.

-- Public Read Policies (Allows reading reports on the React dashboard / history):
CREATE POLICY "Allow public read on analyses" 
ON public.analyses FOR SELECT USING (true);

CREATE POLICY "Allow public read on skill_gaps" 
ON public.skill_gaps FOR SELECT USING (true);

CREATE POLICY "Allow public read on recommendations" 
ON public.recommendations FOR SELECT USING (true);

CREATE POLICY "Allow public read on resumes" 
ON public.resumes FOR SELECT USING (true);

CREATE POLICY "Allow public read on job_descriptions" 
ON public.job_descriptions FOR SELECT USING (true);

CREATE POLICY "Allow public read on candidate_skills" 
ON public.candidate_skills FOR SELECT USING (true);

CREATE POLICY "Allow public read on job_skills" 
ON public.job_skills FOR SELECT USING (true);

-- Public Insert Policies (Ensures backend operations succeed even if using anon / publishable key):
CREATE POLICY "Allow public insert on resumes" 
ON public.resumes FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public insert on job_descriptions" 
ON public.job_descriptions FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public insert on candidate_skills" 
ON public.candidate_skills FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public insert on job_skills" 
ON public.job_skills FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public insert on analyses" 
ON public.analyses FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public insert on skill_gaps" 
ON public.skill_gaps FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public insert on recommendations" 
ON public.recommendations FOR INSERT WITH CHECK (true);

-- End of schema
