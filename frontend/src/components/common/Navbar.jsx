import React, { useState, useEffect } from 'react';
import { NavLink, Link, useNavigate } from 'react-router-dom';
import { Sparkles, FileText, History, Cpu, LayoutDashboard, User, LogOut, LogIn, UserPlus } from 'lucide-react';
import { apiService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const { user, profile, signOut } = useAuth();
  const navigate = useNavigate();
  const [serverStatus, setServerStatus] = useState('checking');

  useEffect(() => {
    let isMounted = true;
    apiService.checkHealth()
      .then(() => {
        if (isMounted) setServerStatus('online');
      })
      .catch(() => {
        if (isMounted) setServerStatus('offline');
      });

    return () => { isMounted = false; };
  }, []);

  const handleSignOut = async () => {
    await signOut();
    navigate('/login');
  };

  const displayName = profile?.full_name || user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'Account';
  const userInitial = displayName[0]?.toUpperCase() || 'U';

  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      backgroundColor: 'rgba(9, 13, 22, 0.85)',
      backdropFilter: 'blur(12px)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{
        maxWidth: '1240px',
        margin: '0 auto',
        padding: '0.85rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        {/* Brand Logo */}
        <Link to={user ? "/dashboard" : "/"} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'var(--primary-gradient)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)'
          }}>
            <Sparkles size={20} color="#ffffff" />
          </div>
          <div>
            <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
              Talent<span className="text-gradient">Lens AI</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Skill Gap Intelligence
            </div>
          </div>
        </Link>

        {/* Dynamic Navigation Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          {user ? (
            <>
              <NavLink 
                to="/dashboard" 
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  color: isActive ? 'var(--primary-400)' : 'var(--text-secondary)',
                  transition: 'color 0.2s',
                })}
              >
                <LayoutDashboard size={16} /> Dashboard
              </NavLink>

              <NavLink 
                to="/upload" 
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  color: isActive ? 'var(--primary-400)' : 'var(--text-secondary)',
                  transition: 'color 0.2s',
                })}
              >
                <FileText size={16} /> Analyze Resume
              </NavLink>

              <NavLink 
                to="/history" 
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  color: isActive ? 'var(--primary-400)' : 'var(--text-secondary)',
                  transition: 'color 0.2s',
                })}
              >
                <History size={16} /> History
              </NavLink>
            </>
          ) : (
            <>
              <NavLink 
                to="/" 
                end
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  color: isActive ? 'var(--primary-400)' : 'var(--text-secondary)',
                  transition: 'color 0.2s',
                })}
              >
                <Cpu size={16} /> Home
              </NavLink>

              <NavLink 
                to="/login" 
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  color: isActive ? 'var(--primary-400)' : 'var(--text-secondary)',
                  transition: 'color 0.2s',
                })}
              >
                <LogIn size={16} /> Sign In
              </NavLink>
            </>
          )}
        </nav>

        {/* Right Controls: Status & User Menu */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Server Status Indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.45rem',
            padding: '0.3rem 0.65rem',
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.74rem',
            fontWeight: 600,
          }}>
            <span style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: serverStatus === 'online' ? '#10b981' : serverStatus === 'checking' ? '#f59e0b' : '#f43f5e',
              boxShadow: serverStatus === 'online' ? '0 0 8px #10b981' : 'none',
            }} />
            <span style={{ color: 'var(--text-muted)' }}>API:</span>
            <span style={{ color: serverStatus === 'online' ? '#10b981' : serverStatus === 'checking' ? '#f59e0b' : '#f43f5e' }}>
              {serverStatus === 'online' ? 'Connected' : serverStatus === 'checking' ? 'Checking' : 'Offline'}
            </span>
          </div>

          {/* User Profile / Auth Action Buttons */}
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Link
                to="/profile"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.3rem 0.6rem',
                  borderRadius: 'var(--radius-full)',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-secondary)',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  transition: 'border-color 0.2s',
                }}
                title="Account & Profile Settings"
              >
                <div style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: 'var(--primary-gradient)',
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                }}>
                  {userInitial}
                </div>
                <span>{displayName.split(' ')[0]}</span>
              </Link>

              <button
                onClick={handleSignOut}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.3rem',
                  fontSize: '0.82rem',
                  padding: '0.4rem',
                  borderRadius: '6px',
                  transition: 'color 0.2s',
                }}
                title="Sign Out"
                onMouseEnter={(e) => e.currentTarget.style.color = '#ef4444'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <Link
              to="/register"
              className="btn btn-primary"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.45rem 0.95rem',
                fontSize: '0.84rem'
              }}
            >
              <UserPlus size={15} /> Get Started
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
