import React from 'react';
import { Activity, ShieldCheck, Sparkles, Database, FileText, CheckCircle2 } from 'lucide-react';

export default function Footer({ setActivePage }) {
  return (
    <footer style={{
      borderTop: '1px solid var(--border-subtle)',
      background: 'rgba(5, 10, 24, 0.96)',
      padding: '36px 0 20px 0',
      marginTop: '60px'
    }}>
      <div className="container">
        {/* Footer Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '32px',
          marginBottom: '28px'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <div style={{
                width: '28px',
                height: '28px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #00d2ff, #0072ff)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 12px rgba(0, 210, 255, 0.4)'
              }}>
                <Activity size={16} color="#ffffff" />
              </div>
              <span style={{ color: '#fff', fontSize: '1.1rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
                DIAS <span style={{ color: 'var(--primary)', fontWeight: 600, fontSize: '0.85rem' }}>Core</span>
              </span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.84rem', lineHeight: 1.6, margin: 0 }}>
              AI-driven Drug-Drug Interaction risk detection, chemical fingerprint similarity, and clinical medication history analysis powered by machine learning.
            </p>
          </div>

          <div>
            <h4 style={{ color: '#f8fafc', fontSize: '0.9rem', fontWeight: 700, marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Quick Navigation
            </h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
              <li>
                <button onClick={() => setActivePage('checker')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', textAlign: 'left', padding: 0, transition: 'color 0.2s' }}>
                  ⚡ Interaction Checker
                </button>
              </li>
              <li>
                <button onClick={() => setActivePage('patient-history')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', textAlign: 'left', padding: 0, transition: 'color 0.2s' }}>
                  📋 Patient Medication Records
                </button>
              </li>
              <li>
                <button onClick={() => setActivePage('prescription-ocr')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', textAlign: 'left', padding: 0, transition: 'color 0.2s' }}>
                  📄 Prescription Intake &amp; OCR
                </button>
              </li>
              <li>
                <button onClick={() => setActivePage('drugs')} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', textAlign: 'left', padding: 0, transition: 'color 0.2s' }}>
                  🧪 Drug Catalog &amp; SMILES
                </button>
              </li>
            </ul>
          </div>

          <div>
            <h4 style={{ color: '#f8fafc', fontSize: '0.9rem', fontWeight: 700, marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Clinical Intelligence
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={14} color="#10b981" />
                <span>RDKit Morgan Fingerprint (2048-bit) Similarity</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={14} color="#00d2ff" />
                <span>Random Forest Multi-Class Interaction Classifier</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={14} color="#a855f7" />
                <span>Contextual Medication Extraction Guardrails</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div style={{
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          paddingTop: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          fontSize: '0.8rem',
          color: 'var(--text-muted)'
        }}>
          <div>
            © {new Date().getFullYear()} DIAS Platform. Intelligent Clinical Decision Support.
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10b981', fontWeight: 600 }}>
            <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 8px #10b981' }}></span>
            Decision Support Engine Active
          </div>
        </div>
      </div>
    </footer>
  );
}
