import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, Check, AlertCircle, Sparkles, Building2, Briefcase } from 'lucide-react';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

const sampleJobs = [
  {
    title: 'Full Stack Python & React Engineer',
    company: 'NextGen Solutions',
    text: `Job Title: Full Stack Python & React Engineer
Company: NextGen Solutions
Experience: 2+ years
Requirements:
- Strong proficiency in Python, FastAPI, and asynchronous backend services.
- Hands-on experience with modern React.js, React Hooks, and REST API integration.
- Database expertise with PostgreSQL or Supabase, schema design, and SQL optimization.
- Familiarity with Git version control, Docker containers, and CI/CD pipelines.
- Preferred: Experience with OpenAI API / LLM integrations, Redis caching, and Tailwind CSS.
- Education: Bachelor's degree in Computer Science, IT, or related technical field.`
  },
  {
    title: 'Junior Data Analyst / BI Specialist',
    company: 'FinMetrics Analytics',
    text: `Job Title: Junior Data Analyst
Company: FinMetrics Analytics
Experience: 0-2 years
Requirements:
- Proven experience with SQL queries, data extraction, joins, and database reporting.
- Proficiency in Python for data cleaning using Pandas, NumPy, and Matplotlib.
- Strong knowledge of Microsoft Excel (VLOOKUP, Pivot Tables, Advanced formulas).
- Experience building dashboards using Power BI or Tableau.
- Good communication and analytical problem-solving skills.
- Education: Degree in Data Science, Information Technology, Statistics, or Mathematics.`
  },
  {
    title: 'HR Executive / Talent Acquisition',
    company: 'Global Talent Partners',
    text: `Job Title: HR Executive - Talent Acquisition
Company: Global Talent Partners
Requirements:
- End-to-end recruitment lifecycle management and candidate sourcing via LinkedIn.
- Experience conducting initial HR interviews, screening resumes, and coordinating technical rounds.
- Proficient with Applicant Tracking Systems (ATS) and MS Office suite.
- Excellent English verbal and written communication.
- Education: Bachelor of Business Administration (BBA) or Master of Human Resources.`
  }
];

const Upload = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [jobTitle, setJobTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    setErrorMessage(null);
    const validExtensions = ['.pdf', '.docx'];
    const fileName = selectedFile.name.toLowerCase();
    const isValid = validExtensions.some(ext => fileName.endsWith(ext));

    if (!isValid) {
      setErrorMessage('Unsupported file type. Please upload a PDF (.pdf) or Word document (.docx).');
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      setErrorMessage('File exceeds the 10 MB limit. Please upload a smaller resume.');
      return;
    }

    setFile(selectedFile);
  };

  const loadSampleJob = (sample) => {
    setJobTitle(sample.title);
    setCompanyName(sample.company);
    setJobDescription(sample.text);
    setErrorMessage(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setErrorMessage('Please upload a resume file (PDF or DOCX).');
      return;
    }
    if (!jobDescription.trim()) {
      setErrorMessage('Please paste or select a Job Description.');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await apiService.createAnalysis(file, jobDescription, jobTitle, companyName);
      if (response && response.data && response.data.analysis_id) {
        navigate(`/analysis/${response.data.analysis_id}`, { state: { analysisData: response.data } });
      } else {
        // In initial phase or testing when backend route is being plugged
        navigate('/analysis', { state: { mockMode: true, raw: response } });
      }
    } catch (err) {
      setErrorMessage(err.message || 'Failed to analyze resume. Please verify your backend server is active.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingSpinner message="Analyzing Resume & Job Description" subMessage="Running LLM parsing, normalizing skills, and computing compatibility matrix..." />;
  }

  return (
    <div className="animate-fade-in" style={{ maxWidth: '960px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h1 style={{ fontSize: '2.2rem', marginBottom: '0.5rem' }}>
          Upload Resume & <span className="text-gradient">Job Description</span>
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
          Provide the candidate's resume (PDF or DOCX) alongside the target job requirements to calculate skill gaps and personalized learning roadmaps.
        </p>
      </div>

      {errorMessage && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '1rem 1.25rem',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(244, 63, 94, 0.1)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          color: '#fda4af',
          fontSize: '0.9rem',
        }}>
          <AlertCircle size={20} color="#f43f5e" style={{ flexShrink: 0 }} />
          <span>{errorMessage}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {/* Step 1: Resume Upload Box */}
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <span style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              background: 'var(--primary-gradient)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.85rem',
              fontWeight: 700,
            }}>1</span>
            <h2 style={{ fontSize: '1.25rem' }}>Upload Candidate Resume</h2>
          </div>

          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${dragActive ? 'var(--primary-500)' : file ? 'var(--color-matched)' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-md)',
              padding: '2.5rem 1.5rem',
              textAlign: 'center',
              backgroundColor: dragActive ? 'rgba(99, 102, 241, 0.08)' : file ? 'rgba(16, 185, 129, 0.05)' : 'rgba(15, 23, 42, 0.6)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              position: 'relative',
            }}
          >
            <input 
              type="file" 
              id="resume-upload" 
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={handleFileInput}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                opacity: 0,
                cursor: 'pointer',
              }}
            />

            {file ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{
                  width: '50px',
                  height: '50px',
                  borderRadius: '50%',
                  background: 'rgba(16, 185, 129, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <Check size={28} color="#10b981" />
                </div>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 600 }}>{file.name}</h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {(file.size / (1024 * 1024)).toFixed(2)} MB • Ready to analyze
                </p>
                <span style={{ fontSize: '0.8rem', color: 'var(--primary-500)', textDecoration: 'underline' }}>
                  Click to replace file
                </span>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{
                  width: '56px',
                  height: '56px',
                  borderRadius: '50%',
                  background: 'rgba(99, 102, 241, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <UploadCloud size={28} color="#818cf8" />
                </div>
                <div>
                  <h4 style={{ fontSize: '1.05rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                    Drag & Drop your resume here, or <span style={{ color: 'var(--primary-500)' }}>browse</span>
                  </h4>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Supported formats: PDF (.pdf) and Microsoft Word (.docx) • Max size: 10 MB
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Step 2: Job Description Box */}
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{
                width: '28px',
                height: '28px',
                borderRadius: '50%',
                background: 'var(--primary-gradient)',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.85rem',
                fontWeight: 700,
              }}>2</span>
              <h2 style={{ fontSize: '1.25rem' }}>Target Job Description</h2>
            </div>

            {/* Quick 1-Click Sample Pre-loaders */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <Sparkles size={14} color="#818cf8" /> Quick Test Samples:
              </span>
              {sampleJobs.map((sample, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => loadSampleJob(sample)}
                  style={{
                    padding: '0.25rem 0.6rem',
                    fontSize: '0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    background: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-secondary)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                  onMouseOver={(e) => e.target.style.borderColor = 'var(--primary-500)'}
                  onMouseOut={(e) => e.target.style.borderColor = 'var(--border-subtle)'}
                >
                  {sample.title.split(' ')[0]}
                </button>
              ))}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '1rem' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Briefcase size={15} /> Job Title (Optional)
              </label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="e.g. Full Stack Developer" 
                value={jobTitle} 
                onChange={(e) => setJobTitle(e.target.value)} 
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Building2 size={15} /> Company Name (Optional)
              </label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="e.g. Acme Corp" 
                value={companyName} 
                onChange={(e) => setCompanyName(e.target.value)} 
              />
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Job Description Requirements Text *</label>
            <textarea
              className="form-textarea"
              rows={8}
              placeholder="Paste the full job description text here, including required skills, qualifications, experience, and responsibilities..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              required
            />
          </div>
        </div>

        {/* Action Button */}
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={!file || !jobDescription.trim()}
            style={{ padding: '0.95rem 2.5rem', fontSize: '1.05rem' }}
          >
            Run AI Resume Analysis <Sparkles size={18} />
          </button>
        </div>
      </form>
    </div>
  );
};

export default Upload;
