import React, { useEffect, useState } from 'react';
import { useLocation, useParams, Link } from 'react-router-dom';
import { 
  CheckCircle2, XCircle, AlertTriangle, Sparkles, BookOpen, 
  Briefcase, GraduationCap, ArrowLeft, Download, ShieldCheck,
  Building2, Layers, Check, ExternalLink
} from 'lucide-react';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Analysis = () => {
  const { id } = useParams();
  const location = useLocation();
  
  const [data, setData] = useState(location.state?.analysisData || null);
  const [loading, setLoading] = useState(!data && !!id);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!data && id) {
      setLoading(true);
      apiService.getAnalysis(id)
        .then((res) => {
          setData(res.data || res);
        })
        .catch((err) => {
          setError(err.message || 'Could not load the analysis report from the database.');
        })
        .finally(() => setLoading(false));
    }
  }, [id, data]);

  if (loading) {
    return <LoadingSpinner message="Retrieving Analysis Report" subMessage="Loading candidate profile, skill matrix, and personalized recommendations from Supabase..." />;
  }

  // Fallback demo data if navigated directly without an upload
  const report = data || {
    compatibility_score: 78.5,
    score_breakdown: {
      required_skills_match: 80.0,
      preferred_skills_match: 66.7,
      experience_match: 75.0,
      education_match: 100.0,
    },
    candidate_profile: {
      candidate_name: 'Jane Doe',
      email: 'jane.doe@example.com',
      phone: '+91 98765 43210',
      summary: 'Passionate Full Stack Developer with 2+ years of experience building scalable web applications in Python, React, and PostgreSQL.',
      education: [
        { degree: 'BSc in Information Technology', institution: 'State University', year: '2023' }
      ],
      skills: ['Python', 'FastAPI', 'JavaScript', 'React', 'SQL', 'Git', 'HTML/CSS'],
      experience: [
        { title: 'Junior Software Engineer', company: 'CloudTech Systems', duration: '2023 - Present' }
      ],
      projects: [
        { title: 'Resume Analyzer API', description: 'Built an intelligent resume screener using FastAPI and PostgreSQL.' }
      ]
    },
    job_profile: {
      job_title: 'Full Stack Python & React Engineer',
      company_name: 'NextGen Solutions',
      required_skills: ['Python', 'FastAPI', 'React', 'PostgreSQL', 'Docker', 'Git'],
      preferred_skills: ['Kubernetes', 'Redis', 'OpenAI API'],
      experience_requirements: ['2+ years of full stack web development experience'],
      education_requirements: ['Bachelor degree in Computer Science, IT, or related technical field']
    },
    skill_gaps: [
      { skill: 'Python', status: 'matched', evidence: 'Explicitly highlighted in Candidate Skills and Experience at CloudTech Systems.' },
      { skill: 'FastAPI', status: 'matched', evidence: 'Used in Resume Analyzer API project and listed under Core Technologies.' },
      { skill: 'React', status: 'matched', evidence: 'Mentioned in summary and practical project stack.' },
      { skill: 'PostgreSQL', status: 'matched', evidence: 'Listed in technical competencies and project database layer.' },
      { skill: 'Git', status: 'matched', evidence: 'Demonstrated through version-controlled project experience.' },
      { skill: 'Docker', status: 'missing', explanation: 'Required in job requirements for containerized deployment, but no containerization keywords detected in resume.' },
      { skill: 'Kubernetes', status: 'preferred_gap', explanation: 'Listed as a preferred/nice-to-have skill in the job description.' }
    ],
    recommendations: [
      {
        skill: 'Docker',
        why_it_matters: 'NextGen Solutions requires containerized microservice deployments for all FastAPI backends.',
        learning_objective: 'Understand Dockerfiles, multi-stage builds, and docker-compose for local development.',
        practical_exercise: 'Write a Dockerfile for a FastAPI + PostgreSQL app and test container isolation.',
        suggested_project: 'Containerize an existing React + FastAPI project with a multi-container docker-compose setup.',
        resource_direction: 'Docker Official Documentation (docs.docker.com)'
      },
      {
        skill: 'Kubernetes',
        why_it_matters: 'Preferred skill for enterprise orchestration and automated scaling.',
        learning_objective: 'Learn Pods, Deployments, Services, and ConfigMaps using Minikube or k3s.',
        practical_exercise: 'Deploy a single container to local Minikube and expose it via NodePort Service.',
        suggested_project: 'Build a deployment manifest YAML for your containerized web application.',
        resource_direction: 'Kubernetes Official Tutorials (kubernetes.io/docs/tutorials)'
      }
    ]
  };

  const getScoreColor = (score) => {
    if (score >= 75) return 'var(--color-matched)';
    if (score >= 50) return 'var(--color-transferable)';
    return 'var(--color-missing)';
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Top Controls & Navigation */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <Link to="/upload" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
            <ArrowLeft size={16} /> Back to Upload & Test
          </Link>
          <h1 style={{ fontSize: '2.1rem' }}>
            AI Compatibility & <span className="text-gradient">Skill Gap Report</span>
          </h1>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button 
            onClick={() => window.print()}
            className="btn btn-secondary" 
            style={{ fontSize: '0.85rem', padding: '0.6rem 1.1rem' }}
          >
            <Download size={16} /> Print / Export PDF
          </button>
          <Link to="/upload" className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.6rem 1.1rem' }}>
            Analyze Another Resume
          </Link>
        </div>
      </div>

      {error && (
        <div style={{
          padding: '1rem 1.25rem',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(244, 63, 94, 0.1)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          color: '#fda4af',
        }}>
          {error}
        </div>
      )}

      {/* Primary Row: Compatibility Score & Target Job Overview */}
      <div className="grid-2">
        {/* Compatibility Score Card */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
                  Analytical Indicator
                </span>
                <h3 style={{ fontSize: '1.25rem', marginTop: '0.2rem' }}>AI-Assisted Job Compatibility Score</h3>
              </div>
              <div style={{
                fontSize: '2.5rem',
                fontFamily: 'var(--font-heading)',
                fontWeight: 800,
                color: getScoreColor(report.compatibility_score),
              }}>
                {report.compatibility_score}%
              </div>
            </div>

            {/* Score Progress Bar */}
            <div style={{ width: '100%', height: '12px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '999px', margin: '1rem 0 0.5rem', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${Math.min(100, Math.max(0, report.compatibility_score))}%`,
                background: getScoreColor(report.compatibility_score),
                borderRadius: '999px',
                transition: 'width 1s ease',
              }} />
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Formula: 60% Required Skills + 15% Preferred Skills + 15% Experience Fit + 10% Education Fit.
            </p>
          </div>

          {/* Sub-Score Breakdown Chips */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Required Skills Fit</div>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--color-matched)' }}>
                {report.score_breakdown?.required_skills_match ?? 80}%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Preferred / Bonus Fit</div>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--color-preferred)' }}>
                {report.score_breakdown?.preferred_skills_match ?? 66}%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Experience Fit</div>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                {report.score_breakdown?.experience_match ?? 75}%
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Education Fit</div>
              <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                {report.score_breakdown?.education_match ?? 100}%
              </div>
            </div>
          </div>
        </div>

        {/* Target Job Requirements Card */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
              Target Position Criteria
            </div>
            <h3 style={{ fontSize: '1.35rem', marginTop: '0.2rem' }}>
              {report.job_profile?.job_title || 'Target Job Role'}
            </h3>
            {report.job_profile?.company_name && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                <Building2 size={15} /> {report.job_profile.company_name}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem' }}>
            {report.job_profile?.experience_requirements && report.job_profile.experience_requirements.length > 0 && (
              <div style={{ color: 'var(--text-secondary)' }}>
                <strong style={{ color: 'var(--text-primary)' }}>Experience criteria: </strong> 
                {report.job_profile.experience_requirements.join(' • ')}
              </div>
            )}
            {report.job_profile?.education_requirements && report.job_profile.education_requirements.length > 0 && (
              <div style={{ color: 'var(--text-secondary)' }}>
                <strong style={{ color: 'var(--text-primary)' }}>Education criteria: </strong> 
                {report.job_profile.education_requirements.join(' • ')}
              </div>
            )}
          </div>

          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Mandatory Required Skills:</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {report.job_profile?.required_skills?.map((skill, idx) => (
                <span key={idx} className="skill-badge badge-matched" style={{ fontSize: '0.8rem' }}>
                  {skill}
                </span>
              ))}
            </div>
            {report.job_profile?.preferred_skills && report.job_profile.preferred_skills.length > 0 && (
              <>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, marginTop: '0.25rem' }}>Bonus / Preferred Skills:</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {report.job_profile.preferred_skills.map((skill, idx) => (
                    <span key={idx} className="skill-badge badge-preferred" style={{ fontSize: '0.8rem' }}>
                      {skill}
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Candidate Profile Details */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
              Parsed Candidate Profile
            </div>
            <h3 style={{ fontSize: '1.4rem', marginTop: '0.2rem' }}>
              {report.candidate_profile?.candidate_name || 'Candidate Name Not Explicit'}
            </h3>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', gap: '1.25rem', flexWrap: 'wrap', marginTop: '0.35rem' }}>
              {report.candidate_profile?.email && <span>📧 {report.candidate_profile.email}</span>}
              {report.candidate_profile?.phone && <span>📞 {report.candidate_profile.phone}</span>}
            </div>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
            {report.candidate_profile?.skills?.map((skill, idx) => (
              <span key={idx} className="skill-badge badge-neutral">
                {skill}
              </span>
            ))}
          </div>
        </div>

        {report.candidate_profile?.summary && (
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
            {report.candidate_profile.summary}
          </p>
        )}

        {/* Education and Experience Sub-lists */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem' }}>
          {report.candidate_profile?.education && report.candidate_profile.education.length > 0 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
                <GraduationCap size={16} color="#818cf8" /> Education History
              </div>
              {report.candidate_profile.education.map((edu, idx) => (
                <div key={idx} style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  • {edu.degree} {edu.institution ? `(${edu.institution})` : ''} {edu.year ? `[${edu.year}]` : ''}
                </div>
              ))}
            </div>
          )}

          {report.candidate_profile?.experience && report.candidate_profile.experience.length > 0 && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.4rem' }}>
                <Briefcase size={16} color="#34d399" /> Experience History
              </div>
              {report.candidate_profile.experience.map((exp, idx) => (
                <div key={idx} style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  • {exp.title} at {exp.company} {exp.duration ? `(${exp.duration})` : ''}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Explainable Skill Gap Matrix */}
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem' }}>Explainable Skill Gap Matrix</h2>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            Transparent cross-reference of candidate skills with concrete textual evidence from the uploaded document.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          {report.skill_gaps?.map((gap, idx) => {
            const isMatched = gap.status === 'matched';
            const isMissing = gap.status === 'missing';
            const isTransferable = gap.status === 'transferable';
            const isPreferredGap = gap.status === 'preferred_gap';

            let bg = 'var(--color-preferred-bg)';
            let border = 'var(--color-preferred-border)';
            let statusColor = 'var(--color-preferred)';
            let statusLabel = 'Preferred Gap';
            let StatusIcon = AlertTriangle;

            if (isMatched) {
              bg = 'var(--color-matched-bg)';
              border = 'var(--color-matched-border)';
              statusColor = 'var(--color-matched)';
              statusLabel = 'Matched';
              StatusIcon = CheckCircle2;
            } else if (isMissing) {
              bg = 'var(--color-missing-bg)';
              border = 'var(--color-missing-border)';
              statusColor = 'var(--color-missing)';
              statusLabel = 'Missing Required';
              StatusIcon = XCircle;
            } else if (isTransferable) {
              bg = 'var(--color-transferable-bg)';
              border = 'var(--color-transferable-border)';
              statusColor = 'var(--color-transferable)';
              statusLabel = 'Transferable';
              StatusIcon = Layers;
            }

            return (
              <div 
                key={idx}
                style={{
                  padding: '1.1rem',
                  borderRadius: 'var(--radius-md)',
                  background: bg,
                  border: `1px solid ${border}`,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.6rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: 700, fontSize: '1.05rem', color: '#ffffff' }}>
                    {gap.skill}
                  </span>
                  <span style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.3rem',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: statusColor,
                  }}>
                    <StatusIcon size={14} /> {statusLabel}
                  </span>
                </div>

                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.45' }}>
                  {gap.evidence || gap.explanation}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Actionable Learning Recommendations */}
      {report.recommendations && report.recommendations.length > 0 && (
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '8px',
              background: 'rgba(251, 191, 36, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <BookOpen size={20} color="#fbbf24" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.4rem' }}>Actionable Learning Recommendations</h2>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                Step-by-step learning roadmaps, beginner practice exercises, and portfolio project suggestions to close detected skill gaps.
              </p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
            {report.recommendations.map((rec, idx) => (
              <div 
                key={idx}
                style={{
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1.35rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.85rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span className="skill-badge badge-missing">
                    Target Gap: {rec.skill}
                  </span>
                </div>

                <div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>Why it matters for this job:</div>
                  <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>{rec.why_it_matters}</div>
                </div>

                <div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>Core Learning Objective:</div>
                  <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>{rec.learning_objective}</div>
                </div>

                <div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>Beginner Practice Exercise:</div>
                  <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>{rec.practical_exercise}</div>
                </div>

                <div style={{ padding: '0.75rem 0.95rem', background: 'rgba(99, 102, 241, 0.08)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
                  <div style={{ fontSize: '0.75rem', color: '#a5b4fc', fontWeight: 700, textTransform: 'uppercase', marginBottom: '0.2rem' }}>
                    Suggested Portfolio Project:
                  </div>
                  <div style={{ fontSize: '0.88rem', color: 'var(--text-primary)' }}>
                    {rec.suggested_project}
                  </div>
                </div>

                {rec.resource_direction && (
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <ExternalLink size={13} /> {rec.resource_direction}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Analysis;
