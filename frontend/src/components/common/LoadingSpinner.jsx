import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ message = 'Processing AI Analysis...', subMessage = 'Extracting resume skills and cross-matching with job requirements...' }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '4rem 2rem',
      textAlign: 'center',
      gap: '1.25rem',
    }}>
      <div style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <div style={{
          position: 'absolute',
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          background: 'rgba(99, 102, 241, 0.2)',
          filter: 'blur(10px)',
          animation: 'pulse 2s infinite ease-in-out',
        }} />
        <Loader2 
          size={44} 
          color="#6366f1" 
          style={{ animation: 'spin 1.2s linear infinite' }} 
        />
      </div>

      <div>
        <h4 style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.35rem' }}>
          {message}
        </h4>
        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', maxWidth: '420px', margin: '0 auto' }}>
          {subMessage}
        </p>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { transform: scale(0.9); opacity: 0.5; }
          50% { transform: scale(1.3); opacity: 0.9; }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
