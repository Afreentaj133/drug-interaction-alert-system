import React from 'react';
import { ShieldAlert, BookOpen, ExternalLink, Heart } from 'lucide-react';

export default function Footer({ setActivePage }) {
  return (
    <footer style={{
      borderTop: '1px solid var(--border-subtle)',
      background: 'rgba(7, 10, 19, 0.95)',
      padding: '48px 0 24px 0',
      marginTop: '60px'
    }}>
      <div className="container">
        {/* Critical Safety Notice Box */}
        <div style={{
          background: 'rgba(239, 68, 68, 0.06)',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          borderRadius: 'var(--radius-md)',
          padding: '16px 20px',
          marginBottom: '36px',
          display: 'flex',
          alignItems: 'center',
          gap: '16px'
        }}>
          <ShieldAlert size={28} color="#ef4444" style={{ flexShrink: 0 }} />
          <div style={{ fontSize: '0.84rem', color: '#fca5a5', lineHeight: 1.5 }}>
            <strong>CLINICAL DECISION-SUPPORT NOTICE:</strong> This application is an educational and research prototype. 
            It is <em>not</em> an autonomous prescribing or diagnostic system, does not guarantee medication safety, 
            and must never replace qualified clinical judgement by licensed physicians and clinical pharmacists.
          </div>
        </div>

        {/* Footer Columns */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '32px',
          marginBottom: '36px'
        }}>
          <div>
            <h4 style={{ color: '#fff', fontSize: '1rem', fontWeight: 700, marginBottom: '12px' }}>
              DIAS System
            </h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.6 }}>
              Explainable Multi-Feature Drug Interaction Risk Prediction Framework combining RDKit cheminformatics,
              Random Forest ensemble modeling, and SHAP explainability.
            </p>
          </div>

          <div>
            <h4 style={{ color: '#fff', fontSize: '1rem', fontWeight: 700, marginBottom: '12px' }}>
              Navigation
            </h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
              <li>
                <button onClick={() => setActivePage('checker')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', textAlign: 'left' }}>
                  Interaction Checker
                </button>
              </li>
              <li>
                <button onClick={() => setActivePage('dashboard')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', textAlign: 'left' }}>
                  Analytics Dashboard
                </button>
              </li>
              <li>
                <button onClick={() => setActivePage('history')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', textAlign: 'left' }}>
                  Alert History Audit
                </button>
              </li>
              <li>
                <button onClick={() => setActivePage('drugs')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', textAlign: 'left' }}>
                  Drug Catalog & SMILES
                </button>
              </li>
            </ul>
          </div>

          <div>
            <h4 style={{ color: '#fff', fontSize: '1rem', fontWeight: 700, marginBottom: '12px' }}>
              Academic Project
            </h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.6 }}>
              Final-Year Engineering Project<br />
              Department of Information Science and Engineering<br />
              <strong>City Engineering College, Bangalore</strong>
            </p>
            <div style={{ marginTop: '10px' }}>
              <button 
                onClick={() => setActivePage('about')}
                style={{ 
                  display: 'inline-flex', 
                  alignItems: 'center', 
                  gap: '4px', 
                  background: 'none', 
                  border: 'none', 
                  color: 'var(--primary)', 
                  fontSize: '0.82rem', 
                  cursor: 'pointer', 
                  fontWeight: 600 
                }}
              >
                View System Architecture &amp; Methodology <ExternalLink size={12} />
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div style={{
          borderTop: '1px solid var(--border-subtle)',
          paddingTop: '20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.78rem',
          color: 'var(--text-muted)'
        }}>
          <div>
            © {new Date().getFullYear()} DIAS — Clinical Decision-Support Prototype. All rights reserved.
          </div>
          <div>
            Complies with IEEE Guidelines for CDSS Prototype Evaluation
          </div>
        </div>
      </div>
    </footer>
  );
}
