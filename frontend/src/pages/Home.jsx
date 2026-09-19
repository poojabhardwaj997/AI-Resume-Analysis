import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, FileSearch, Target, Compass, Database, ArrowRight, CheckCircle2, Shield } from 'lucide-react';

const Home = () => {
  const steps = [
    {
      num: '01',
      title: 'Upload Resume',
      desc: 'Native PyMuPDF & python-docx extraction supports digital PDF and DOCX files without formatting loss.',
      icon: <FileSearch size={22} color="#818cf8" />,
    },
    {
      num: '02',
      title: 'LLM Extraction',
      desc: 'OpenAI GPT extracts candidate skills, experience, education, and projects strictly without hallucination.',
      icon: <Sparkles size={22} color="#c084fc" />,
    },
    {
      num: '03',
      title: 'Skill Normalization',
      desc: 'Synonym and taxonomy rules unify aliases (e.g. JS, ES6 → JavaScript; Excel, MS-Excel → Excel).',
      icon: <Target size={22} color="#38bdf8" />,
    },
    {
      num: '04',
      title: 'Gap & Compatibility Score',
      desc: 'Computes a transparent weighted compatibility score and surfaces explicit resume evidence for matches.',
      icon: <CheckCircle2 size={22} color="#34d399" />,
    },
    {
      num: '05',
      title: 'Learning Recommendations',
      desc: 'Generates targeted roadmaps, practical hands-on exercises, and project ideas for missing competencies.',
      icon: <Compass size={22} color="#fbbf24" />,
    },
  ];

  const features = [
    {
      title: 'Multi-Domain Support',
      desc: 'Optimized not only for Software Developers, but also Data Analysts, HR Executives, Financial Analysts, and Marketers.',
      badge: 'BSc IT / Data Science',
    },
    {
      title: 'Explainable Matching Evidence',
      desc: 'Every matched or missing skill cites concrete quotes directly from the parsed resume text to eliminate black-box AI doubt.',
      badge: 'Zero Hallucination',
    },
    {
      title: 'Production Cloud Persistence',
      desc: 'Relational data modeled in Supabase PostgreSQL with protected Row Level Security (RLS) policies.',
      badge: 'Enterprise Architecture',
    },
  ];

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '3.5rem' }}>
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '3rem 1rem 1.5rem', maxWidth: '840px', margin: '0 auto' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.4rem 1rem',
          borderRadius: 'var(--radius-full)',
          background: 'rgba(99, 102, 241, 0.1)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          color: '#818cf8',
          fontSize: '0.85rem',
          fontWeight: 600,
          marginBottom: '1.5rem',
        }}>
          <Sparkles size={16} /> Powered by FastAPI, OpenAI, & Supabase PostgreSQL
        </div>

        <h1 style={{
          fontSize: 'clamp(2.2rem, 5vw, 3.4rem)',
          letterSpacing: '-0.03em',
          marginBottom: '1.25rem',
          fontWeight: 800,
        }}>
          AI-Powered Resume Analysis with <span className="text-gradient">Skill Gap Intelligence</span>
        </h1>

        <p style={{
          fontSize: '1.15rem',
          color: 'var(--text-secondary)',
          lineHeight: '1.7',
          marginBottom: '2.5rem',
        }}>
          Bridge the gap between candidate qualifications and job market demands. Upload any resume, compare it against a target job description, detect missing competencies, and generate actionable learning roadmaps.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <Link to="/upload" className="btn btn-primary" style={{ padding: '0.9rem 2rem', fontSize: '1.05rem' }}>
            Get Started — Analyze Resume <ArrowRight size={18} />
          </Link>
          <Link to="/history" className="btn btn-secondary" style={{ padding: '0.9rem 1.75rem' }}>
            View Saved Analyses
          </Link>
        </div>
      </section>

      {/* 5-Step Pipeline Flow */}
      <section>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.85rem', marginBottom: '0.5rem' }}>System Architecture & Pipeline</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            From raw binary file extraction to structured semantic intelligence.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
          gap: '1.25rem',
        }}>
          {steps.map((step) => (
            <div key={step.num} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', position: 'relative' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{
                  fontFamily: 'var(--font-heading)',
                  fontSize: '1.75rem',
                  fontWeight: 800,
                  color: 'rgba(255, 255, 255, 0.1)',
                }}>
                  {step.num}
                </span>
                <div style={{
                  padding: '0.5rem',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(255, 255, 255, 0.04)',
                }}>
                  {step.icon}
                </div>
              </div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>{step.title}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="grid-3">
        {features.map((f, idx) => (
          <div key={idx} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <span style={{
              alignSelf: 'flex-start',
              fontSize: '0.75rem',
              fontWeight: 700,
              padding: '0.25rem 0.65rem',
              borderRadius: 'var(--radius-full)',
              background: 'rgba(99, 102, 241, 0.15)',
              color: '#a5b4fc',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}>
              {f.badge}
            </span>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{f.title}</h3>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
              {f.desc}
            </p>
          </div>
        ))}
      </section>
    </div>
  );
};

export default Home;
