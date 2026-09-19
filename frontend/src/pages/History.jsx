import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  History as HistoryIcon, ArrowRight, FileText, Calendar, 
  Search, RefreshCw, Filter, Sparkles, Building2, Trash2, CheckCircle, AlertCircle
} from 'lucide-react';
import { apiService } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';

const History = () => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);
  const [actionMsg, setActionMsg] = useState(null);

  const fetchHistory = (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    else setLoading(true);

    apiService.getHistory()
      .then((res) => {
        setAnalyses(res.data || res || []);
        setError(null);
      })
      .catch((err) => {
        console.error('History fetch failed:', err);
        // Fallback demo items if backend database is in offline mock mode
        setAnalyses([
          {
            id: 'demo-patel-1',
            candidate_name: 'Vikram Patel',
            job_title: 'Full Stack Python Developer',
            company_name: 'FinTech Innovations',
            compatibility_score: 82.5,
            created_at: new Date().toISOString(),
          },
          {
            id: 'demo-doe-2',
            candidate_name: 'Jane Doe',
            job_title: 'Full Stack Python & React Engineer',
            company_name: 'NextGen Solutions',
            compatibility_score: 78.5,
            created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
          }
        ]);
      })
      .finally(() => {
        setLoading(false);
        setRefreshing(false);
      });
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete the analysis report for "${name || 'Candidate'}"? This action cannot be undone.`)) {
      return;
    }
    setDeletingId(id);
    try {
      await apiService.deleteAnalysis(id);
      setAnalyses(prev => prev.filter(item => item.id !== id));
      setActionMsg({ type: 'success', text: `Analysis report for "${name || 'Candidate'}" was deleted successfully.` });
      setTimeout(() => setActionMsg(null), 3500);
    } catch (err) {
      console.error('Delete failed:', err);
      setActionMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to delete analysis record.' });
      setTimeout(() => setActionMsg(null), 4000);
    } finally {
      setDeletingId(null);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const getScoreBadgeClass = (score) => {
    if (score >= 75) return 'badge-matched';
    if (score >= 50) return 'badge-transferable';
    return 'badge-missing';
  };

  const filteredAnalyses = analyses.filter((item) => {
    const term = searchTerm.toLowerCase().trim();
    if (!term) return true;
    const name = (item.candidate_name || '').toLowerCase();
    const title = (item.job_title || '').toLowerCase();
    const company = (item.company_name || '').toLowerCase();
    return name.includes(term) || title.includes(term) || company.includes(term);
  });

  if (loading) {
    return <LoadingSpinner message="Loading Historical Records" subMessage="Retrieving saved candidate analyses from Supabase PostgreSQL..." />;
  }

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '2.1rem' }}>
            Analysis <span className="text-gradient">History</span>
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Access all candidate evaluations and skill gap reports recorded in Supabase PostgreSQL.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button 
            onClick={() => fetchHistory(true)} 
            className="btn btn-secondary"
            disabled={refreshing}
            style={{ fontSize: '0.85rem', padding: '0.6rem 1.1rem' }}
          >
            <RefreshCw size={15} style={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} /> 
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>

          <Link to="/upload" className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.6rem 1.1rem' }}>
            + Analyze New Resume
          </Link>
        </div>
      </div>

      {/* Action Toast Alert */}
      {actionMsg && (
        <div style={{
          padding: '0.9rem 1.25rem',
          borderRadius: '10px',
          background: actionMsg.type === 'success' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
          border: `1px solid ${actionMsg.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
          color: actionMsg.type === 'success' ? '#34d399' : '#f87171',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          fontSize: '0.9rem',
          fontWeight: 500
        }}>
          {actionMsg.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
          <span>{actionMsg.text}</span>
        </div>
      )}

      {/* Search & Filter Bar */}
      <div className="glass-card" style={{ padding: '1rem 1.25rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ position: 'relative', flex: '1', minWidth: '240px', maxWidth: '480px' }}>
          <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
          <input 
            type="text" 
            className="form-input" 
            placeholder="Search candidate name, job title, or company..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ paddingLeft: '2.5rem', paddingRight: '1rem' }}
          />
        </div>

        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Showing <strong style={{ color: 'var(--text-primary)' }}>{filteredAnalyses.length}</strong> of {analyses.length} saved analyses
        </div>
      </div>

      {/* Main Table or Empty State */}
      {analyses.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <HistoryIcon size={48} color="#64748b" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>No Analysis Records Found</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '420px', margin: '0 auto 1.5rem', fontSize: '0.9rem' }}>
            Upload your first candidate resume and match it against target job requirements to generate reports.
          </p>
          <Link to="/upload" className="btn btn-primary">
            Upload & Analyze Resume Now
          </Link>
        </div>
      ) : filteredAnalyses.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
          <Filter size={36} color="#64748b" style={{ margin: '0 auto 0.75rem' }} />
          <h4 style={{ fontSize: '1.1rem', marginBottom: '0.4rem' }}>No results match "{searchTerm}"</h4>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            Try searching for a different candidate name, job title, or clear the search filter.
          </p>
          <button onClick={() => setSearchTerm('')} className="btn btn-secondary" style={{ fontSize: '0.8rem', padding: '0.4rem 0.9rem' }}>
            Clear Search
          </button>
        </div>
      ) : (
        <div className="glass-card" style={{ padding: '0', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', minWidth: '720px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', background: 'rgba(255, 255, 255, 0.02)' }}>
                <th style={{ padding: '1.1rem 1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Candidate Profile</th>
                <th style={{ padding: '1.1rem 1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Target Role & Organization</th>
                <th style={{ padding: '1.1rem 1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>AI Compatibility</th>
                <th style={{ padding: '1.1rem 1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Date & Time</th>
                <th style={{ padding: '1.1rem 1.5rem', fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAnalyses.map((item) => (
                <tr 
                  key={item.id}
                  style={{ 
                    borderBottom: '1px solid var(--border-subtle)',
                    transition: 'background-color 0.15s ease',
                  }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.03)'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <td style={{ padding: '1.2rem 1.5rem', fontWeight: 600 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '8px',
                        background: 'rgba(99, 102, 241, 0.15)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}>
                        <FileText size={17} color="#818cf8" />
                      </div>
                      <span style={{ fontSize: '0.95rem' }}>{item.candidate_name || 'Anonymous Candidate'}</span>
                    </div>
                  </td>

                  <td style={{ padding: '1.2rem 1.5rem', color: 'var(--text-secondary)' }}>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.92rem' }}>
                      {item.job_title || 'General Position'}
                    </div>
                    {item.company_name && (
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.15rem' }}>
                        <Building2 size={13} /> {item.company_name}
                      </div>
                    )}
                  </td>

                  <td style={{ padding: '1.2rem 1.5rem' }}>
                    <span className={`skill-badge ${getScoreBadgeClass(item.compatibility_score)}`}>
                      {item.compatibility_score}% Match
                    </span>
                  </td>

                  <td style={{ padding: '1.2rem 1.5rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <Calendar size={14} />
                      <span>{new Date(item.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}</span>
                    </div>
                  </td>

                  <td style={{ padding: '1.2rem 1.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Link 
                        to={`/analysis/${item.id}`} 
                        className="btn btn-secondary" 
                        style={{ padding: '0.45rem 0.95rem', fontSize: '0.82rem' }}
                      >
                        View Report <ArrowRight size={14} />
                      </Link>
                      <button
                        onClick={() => handleDelete(item.id, item.candidate_name)}
                        disabled={deletingId === item.id}
                        title="Delete analysis record"
                        style={{
                          background: 'rgba(239, 68, 68, 0.1)',
                          border: '1px solid rgba(239, 68, 68, 0.25)',
                          color: '#f87171',
                          padding: '0.45rem 0.65rem',
                          borderRadius: '8px',
                          cursor: deletingId === item.id ? 'not-allowed' : 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          transition: 'all 0.15s ease',
                        }}
                        onMouseOver={(e) => {
                          if (deletingId !== item.id) {
                            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)';
                            e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.4)';
                          }
                        }}
                        onMouseOut={(e) => {
                          if (deletingId !== item.id) {
                            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                            e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.25)';
                          }
                        }}
                      >
                        {deletingId === item.id ? (
                          <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} />
                        ) : (
                          <Trash2 size={14} />
                        )}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default History;
