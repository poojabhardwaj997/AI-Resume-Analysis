-- ===================================================================
-- DATABASE MIGRATION V2: SUPABASE AUTH INTEGRATION, USER OWNERSHIP & RLS
-- Target: Supabase PostgreSQL
-- Non-destructive migration preserving existing application data.
-- ===================================================================

-- 1. Ensure UUID extension is active
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -------------------------------------------------------------------
-- 2. Create Application-Level `profiles` Table
-- -------------------------------------------------------------------
-- References Supabase managed `auth.users(id)`
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    email TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- Automated trigger function to create a profile row upon Supabase Auth sign-up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, email, created_at, updated_at)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
        NEW.email,
        NOW(),
        NOW()
    )
    ON CONFLICT (id) DO UPDATE
    SET 
        full_name = EXCLUDED.full_name,
        email = EXCLUDED.email,
        updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop trigger if it already exists to allow idempotent re-runs
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Bind trigger to auth.users
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- -------------------------------------------------------------------
-- 3. Add `user_id` Columns to Existing Application Tables
-- -------------------------------------------------------------------

-- 3.1 resumes table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'resumes' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE public.resumes ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 3.2 job_descriptions table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'job_descriptions' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE public.job_descriptions ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 3.3 analyses table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'analyses' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE public.analyses ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- -------------------------------------------------------------------
-- 4. Create `audit_logs` Table for Forensic Security Tracking
-- -------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc', NOW())
);

-- -------------------------------------------------------------------
-- 5. Create Performance Indexes on User Ownership Columns
-- -------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON public.resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_user_id ON public.job_descriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);

-- -------------------------------------------------------------------
-- 6. Configure Row Level Security (RLS) Policies
-- -------------------------------------------------------------------

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.candidate_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.job_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.skill_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Clean up old overly-permissive policies if they exist
DROP POLICY IF EXISTS "Allow public read on analyses" ON public.analyses;
DROP POLICY IF EXISTS "Allow public insert on analyses" ON public.analyses;
DROP POLICY IF EXISTS "Allow public read on resumes" ON public.resumes;
DROP POLICY IF EXISTS "Allow public insert on resumes" ON public.resumes;
DROP POLICY IF EXISTS "Allow public read on job_descriptions" ON public.job_descriptions;
DROP POLICY IF EXISTS "Allow public insert on job_descriptions" ON public.job_descriptions;
DROP POLICY IF EXISTS "Allow public read on candidate_skills" ON public.candidate_skills;
DROP POLICY IF EXISTS "Allow public insert on candidate_skills" ON public.candidate_skills;
DROP POLICY IF EXISTS "Allow public read on job_skills" ON public.job_skills;
DROP POLICY IF EXISTS "Allow public insert on job_skills" ON public.job_skills;
DROP POLICY IF EXISTS "Allow public read on skill_gaps" ON public.skill_gaps;
DROP POLICY IF EXISTS "Allow public insert on skill_gaps" ON public.skill_gaps;
DROP POLICY IF EXISTS "Allow public read on recommendations" ON public.recommendations;
DROP POLICY IF EXISTS "Allow public insert on recommendations" ON public.recommendations;

-- 6.1 `profiles` Policies
CREATE POLICY "Users can read their own profile"
ON public.profiles FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
ON public.profiles FOR UPDATE
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);

-- 6.2 `resumes` Policies (User-scoped data isolation)
CREATE POLICY "Users can read own resumes"
ON public.resumes FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own resumes"
ON public.resumes FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own resumes"
ON public.resumes FOR DELETE
USING (auth.uid() = user_id);

-- 6.3 `job_descriptions` Policies
CREATE POLICY "Users can read own job descriptions"
ON public.job_descriptions FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own job descriptions"
ON public.job_descriptions FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own job descriptions"
ON public.job_descriptions FOR DELETE
USING (auth.uid() = user_id);

-- 6.4 `analyses` Policies (Strict BOLA / IDOR protection)
CREATE POLICY "Users can read own analyses"
ON public.analyses FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analyses"
ON public.analyses FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own analyses"
ON public.analyses FOR DELETE
USING (auth.uid() = user_id);

-- 6.5 Child Table Policies (Inherited ownership via foreign key lookups)

-- candidate_skills
CREATE POLICY "Users can read own candidate skills"
ON public.candidate_skills FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.resumes 
        WHERE resumes.id = candidate_skills.resume_id 
        AND resumes.user_id = auth.uid()
    )
);

CREATE POLICY "Users can insert own candidate skills"
ON public.candidate_skills FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.resumes 
        WHERE resumes.id = candidate_skills.resume_id 
        AND resumes.user_id = auth.uid()
    )
);

-- job_skills
CREATE POLICY "Users can read own job skills"
ON public.job_skills FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.job_descriptions 
        WHERE job_descriptions.id = job_skills.job_id 
        AND job_descriptions.user_id = auth.uid()
    )
);

CREATE POLICY "Users can insert own job skills"
ON public.job_skills FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.job_descriptions 
        WHERE job_descriptions.id = job_skills.job_id 
        AND job_descriptions.user_id = auth.uid()
    )
);

-- skill_gaps
CREATE POLICY "Users can read own skill gaps"
ON public.skill_gaps FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.analyses 
        WHERE analyses.id = skill_gaps.analysis_id 
        AND analyses.user_id = auth.uid()
    )
);

CREATE POLICY "Users can insert own skill gaps"
ON public.skill_gaps FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.analyses 
        WHERE analyses.id = skill_gaps.analysis_id 
        AND analyses.user_id = auth.uid()
    )
);

-- recommendations
CREATE POLICY "Users can read own recommendations"
ON public.recommendations FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.analyses 
        WHERE analyses.id = recommendations.analysis_id 
        AND analyses.user_id = auth.uid()
    )
);

CREATE POLICY "Users can insert own recommendations"
ON public.recommendations FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM public.analyses 
        WHERE analyses.id = recommendations.analysis_id 
        AND analyses.user_id = auth.uid()
    )
);

-- 6.6 `audit_logs` Policies (Forensic Integrity)
-- Normal users can view their own audit logs, but CANNOT modify or delete them.
CREATE POLICY "Users can read own audit logs"
ON public.audit_logs FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Allow authenticated insert on audit logs"
ON public.audit_logs FOR INSERT
WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- Explicitly DO NOT create UPDATE or DELETE policies on audit_logs!
-- This guarantees audit immutability for ordinary users.

-- ===================================================================
-- End of Migration V2
-- ===================================================================
