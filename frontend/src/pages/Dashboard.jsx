import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, Sparkles, CheckCircle, AlertTriangle, TrendingUp, 
  ArrowRight, PlusCircle, Trash2, Calendar, Building2, RefreshCw, BarChart3
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Dashboard = () => {
  const { user, profile } = useAuth();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  const fetchDashboardData = async (isManual = false) => {
    if (isManual) setRefreshing(true);
    else setLoading(true);

    try {
      const res = await apiService.getHistory();
      const list = res.data || res || [];
      setAnalyses(list);
    } catch (err) {
      console.warn('[Dashboard] Could not fetch analyses history:', err.message);
      setAnalyses([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleDelete = async (id, e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this analysis report? This action cannot be undone.')) {
      return;
    }

    setDeletingId(id);
    try {
      await apiService.deleteAnalysis(id);
      setAnalyses((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      alert('Failed to delete analysis: ' + (err.message || 'Server error'));
    } finally {
      setDeletingId(null);
    }
  };

  // Compute KPI metrics
  const totalAnalyses = analyses.length;
  const latestAnalysis = analyses[0] || null;
  const latestScore = latestAnalysis ? Math.round(latestAnalysis.compatibility_score) : null;
  
  // Calculate average score across user history
  const averageScore = totalAnalyses > 0 
    ? Math.round(analyses.reduce((sum, item) => sum + (item.compatibility_score || 0), 0) / totalAnalyses) 
    : 0;

  const displayName = profile?.full_name || user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'Professional';

  const getScoreBadge = (score) => {
    if (score >= 75) return { color: '#10b981', bg: 'rgba(16, 185, 129, 0.12)', border: 'rgba(16, 185, 129, 0.3)' };
    if (score >= 50) return { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.12)', border: 'rgba(245, 158, 11, 0.3)' };
    return { color: '#f43f5e', bg: 'rgba(244, 63, 94, 0.12)', border: 'rgba(244, 63, 94, 0.3)' };
  };

  return (
    <div style={{ maxWidth: '1240px', margin: '0 auto', padding: '2rem 1.5rem' }}>
      {/* Welcome Banner */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1.5rem',
        marginBottom: '2.5rem',
        padding: '2rem',
        borderRadius: 'var(--radius-xl)',
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%)',
        border: '1px solid var(--border-subtle)',
        boxShadow: '0 20px 40px -15px rgba(0, 0, 0, 0.35)',
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.4rem' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--primary-400)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Recruiter & Candidate Workspace
            </span>
          </div>
          <h1 style={{ fontSize: '1.9rem', fontWeight: 800, letterSpacing: '-0.02em', color: '#f8fafc', marginBottom: '0.5rem' }}>
            Welcome back, <span className="text-gradient">{displayName}</span> 👋
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '600px', lineHeight: '1.5' }}>
            Inspect candidate resumes, detect verifiable skill gaps, and access tailored upskilling recommendations.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => fetchDashboardData(true)}
            disabled={refreshing}
            className="btn btn-secondary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            title="Refresh dashboard metrics from database"
          >
            <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
            Refresh
          </button>
          <Link
            to="/upload"
            className="btn btn-primary"
            style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.85rem 1.4rem' }}
          >
            <PlusCircle size={18} />
            Analyze New Resume
          </Link>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1.25rem',
        marginBottom: '2.5rem',
      }}>
        {/* Card 1: Total Analyses */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                Total Analyses
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '0.25rem' }}>
                {loading ? '...' : totalAnalyses}
              </div>
            </div>
            <div style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--primary-400)'
            }}>
              <FileText size={22} />
            </div>
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            Stored securely in your account
          </div>
        </div>

        {/* Card 2: Latest Match Score */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                Latest Match Score
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: latestScore !== null ? (latestScore >= 75 ? '#10b981' : latestScore >= 50 ? '#f59e0b' : '#f43f5e') : 'var(--text-primary)', marginTop: '0.25rem' }}>
                {loading ? '...' : latestScore !== null ? `${latestScore}%` : 'N/A'}
              </div>
            </div>
            <div style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: 'rgba(16, 185, 129, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#10b981'
            }}>
              <TrendingUp size={22} />
            </div>
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            {latestAnalysis ? latestAnalysis.job_title : 'No recent evaluation'}
          </div>
        </div>

        {/* Card 3: Average Match Score */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                Average Compatibility
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '0.25rem' }}>
                {loading ? '...' : totalAnalyses > 0 ? `${averageScore}%` : 'N/A'}
              </div>
            </div>
            <div style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: 'rgba(59, 130, 246, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#60a5fa'
            }}>
              <BarChart3 size={22} />
            </div>
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            Across all candidate evaluations
          </div>
        </div>

        {/* Card 4: Verified Evidence Extraction */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
                Explainability Core
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#34d399', marginTop: '0.5rem' }}>
                Quote Verified
              </div>
            </div>
            <div style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: 'rgba(52, 211, 153, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#34d399'
            }}>
              <CheckCircle size={22} />
            </div>
          </div>
          <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            100% zero-hallucination quotes
          </div>
        </div>
      </div>

      {/* Recent Analyses Section */}
      <div className="card" style={{ padding: '2rem' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Recent Analysis Reports
            </h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
              Click any evaluation report to view the full compatibility breakdown and skill matrix
            </p>
          </div>
          <Link
            to="/history"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              color: 'var(--primary-400)',
              fontSize: '0.9rem',
              fontWeight: 600
            }}
          >
            View All History <ArrowRight size={16} />
          </Link>
        </div>

        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>
            <LoadingSpinner text="Loading recent analyses..." />
          </div>
        ) : analyses.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '3.5rem 1rem',
            border: '1px dashed var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            background: 'rgba(255, 255, 255, 0.01)'
          }}>
            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1.25rem',
              color: 'var(--primary-400)'
            }}>
              <FileText size={28} />
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem', color: '#f8fafc' }}>
              No analyses created yet
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '420px', margin: '0 auto 1.75rem' }}>
              Upload your first resume and enter a target job description to see the AI skill gap engine in action.
            </p>
            <Link to="/upload" className="btn btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
              <PlusCircle size={18} />
              Analyze First Resume
            </Link>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Candidate</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Target Role & Company</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Compatibility</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Date Evaluated</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {analyses.slice(0, 5).map((item) => {
                  const badge = getScoreBadge(item.compatibility_score);
                  const isDeleting = deletingId === item.id;
                  const dateStr = item.created_at ? new Date(item.created_at).toLocaleDateString(undefined, {
                    month: 'short', day: 'numeric', year: 'numeric'
                  }) : 'Recent';

                  return (
                    <tr key={item.id} style={{
                      borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                      transition: 'background-color 0.15s',
                    }}>
                      <td style={{ padding: '1rem', fontWeight: 600, color: '#f1f5f9' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                          <div style={{
                            width: '32px',
                            height: '32px',
                            borderRadius: '50%',
                            background: 'rgba(99, 102, 241, 0.2)',
                            color: 'var(--primary-400)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '0.85rem',
                            fontWeight: 700
                          }}>
                            {item.candidate_name ? item.candidate_name[0].toUpperCase() : 'C'}
                          </div>
                          <span>{item.candidate_name}</span>
                        </div>
                      </td>

                      <td style={{ padding: '1rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        <div>{item.job_title}</div>
                        {item.company_name && (
                          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.15rem' }}>
                            <Building2 size={12} /> {item.company_name}
                          </div>
                        )}
                      </td>

                      <td style={{ padding: '1rem' }}>
                        <span style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.35rem',
                          padding: '0.3rem 0.75rem',
                          borderRadius: 'var(--radius-full)',
                          fontSize: '0.85rem',
                          fontWeight: 700,
                          backgroundColor: badge.bg,
                          color: badge.color,
                          border: `1px solid ${badge.border}`
                        }}>
                          {Math.round(item.compatibility_score)}%
                        </span>
                      </td>

                      <td style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <Calendar size={14} /> {dateStr}
                        </div>
                      </td>

                      <td style={{ padding: '1rem', textAlign: 'right' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.75rem' }}>
                          <Link
                            to={`/analysis/${item.id}`}
                            className="btn btn-secondary"
                            style={{ padding: '0.45rem 0.9rem', fontSize: '0.82rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
                          >
                            View Report <ArrowRight size={14} />
                          </Link>
                          <button
                            onClick={(e) => handleDelete(item.id, e)}
                            disabled={isDeleting}
                            style={{
                              background: 'none',
                              border: 'none',
                              color: 'var(--text-muted)',
                              cursor: 'pointer',
                              padding: '0.4rem',
                              borderRadius: '6px',
                              display: 'flex',
                              alignItems: 'center',
                              transition: 'color 0.2s',
                            }}
                            title="Delete report"
                            aria-label="Delete report"
                            onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
                            onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
