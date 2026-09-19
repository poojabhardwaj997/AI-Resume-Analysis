import React from 'react';
import { ShieldCheck, GraduationCap, Award } from 'lucide-react';

const Footer = () => {
  return (
    <footer style={{
      borderTop: '1px solid var(--border-subtle)',
      backgroundColor: 'rgba(11, 15, 25, 0.9)',
      padding: '2.5rem 1.5rem',
      marginTop: 'auto',
    }}>
      <div style={{
        maxWidth: '1240px',
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '1.5rem',
      }}>
        {/* Fairness & Human Review Disclaimer Alert */}
        <div style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: '1rem',
          padding: '1rem 1.25rem',
          background: 'rgba(99, 102, 241, 0.07)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          borderRadius: 'var(--radius-md)',
          fontSize: '0.85rem',
          color: 'var(--text-secondary)',
          lineHeight: '1.5',
        }}>
          <ShieldCheck size={24} color="#818cf8" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong style={{ color: '#ffffff' }}>Fairness & Human-in-the-Loop Notice:</strong> This platform calculates an AI-assisted job compatibility indicator using skill taxonomy mapping and semantic reasoning. It is designed to assist career counseling and human recruitment decisions, not to automate employment rejections or replace human judgment. Demographic attributes are excluded from all algorithms.
          </div>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem',
          fontSize: '0.85rem',
          color: 'var(--text-muted)',
          paddingTop: '0.5rem',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <GraduationCap size={18} color="#94a3b8" />
            <span>BSc IT / Data Science Final Year Capstone Project</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Award size={18} color="#94a3b8" />
            <span>FastAPI • React.js • OpenAI • Supabase PostgreSQL</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
