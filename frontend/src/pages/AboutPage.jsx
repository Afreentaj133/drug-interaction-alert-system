import React, { useState, useEffect } from 'react';
import { Info, Cpu, Database, Shield, BookOpen, Layers, CheckCircle2, Award } from 'lucide-react';
import { api } from '../services/api';

export default function AboutPage() {
  const [modelInfo, setModelInfo] = useState(null);

  useEffect(() => {
    api.getModelInfo()
      .then((data) => setModelInfo(data))
      .catch((err) => console.error('Failed to load model info:', err));
  }, []);

  return (
    <div className="container" style={{ paddingTop: '32px', paddingBottom: '60px' }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '36px' }}>
          <h1 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Info size={28} color="var(--primary)" />
            About the System &amp; Architecture
          </h1>
          <p className="section-subtitle">
            Explainable Multi-Feature Drug Interaction Risk Prediction Framework for Clinical Decision Support.
          </p>
        </div>

        {/* Academic Project Banner */}
        <div className="glass-panel" style={{ padding: '28px', marginBottom: '32px', borderLeft: '4px solid var(--primary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
            <Award size={20} color="var(--primary)" />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#fff' }}>
              Final-Year Engineering Project
            </h3>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: '14px' }}>
            Developed at the <strong>Department of Information Science and Engineering, City Engineering College, Bangalore</strong>.
          </p>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '14px',
            background: 'rgba(255, 255, 255, 0.02)',
            padding: '16px',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.84rem'
          }}>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 700 }}>PROJECT GUIDE / MENTOR</div>
              <div style={{ color: '#fff', fontWeight: 700, marginTop: '2px' }}>Mrs. SWATHI S B</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem' }}>Assistant Professor, Dept. of ISE</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem', fontWeight: 700 }}>STUDENT INVESTIGATORS</div>
              <div style={{ color: '#fff', fontWeight: 600, marginTop: '2px' }}>AFREEN TAJ (1CE23IS006)</div>
              <div style={{ color: '#fff', fontWeight: 600 }}>BHAVANA N (1CE23IS018)</div>
              <div style={{ color: '#fff', fontWeight: 600 }}>BHOOMIKA MH (1CE23IS021)</div>
            </div>
          </div>
        </div>

        {/* Architectural Overview */}
        <section className="glass-panel" style={{ padding: '32px', marginBottom: '32px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={20} color="var(--primary)" />
            System Architecture &amp; Data Pipeline
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: '20px' }}>
            The DIAS architecture is engineered in decoupled tiers to ensure rigorous scientific validation, low-latency inference, and transparent clinical interpretability:
          </p>

          <div style={{
            background: 'rgba(15, 23, 42, 0.9)',
            padding: '24px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.8rem',
            color: '#38bdf8',
            lineHeight: 1.7,
            overflowX: 'auto',
            marginBottom: '20px'
          }}>
            User Input (Drug A + Drug B)<br />
            &nbsp;&nbsp;↓<br />
            Pydantic Schema Validation &amp; SQLite/PostgreSQL Entity Lookup<br />
            &nbsp;&nbsp;↓<br />
            RDKit Chemical Processing (Canonical SMILES → 1024-bit Morgan ECFP4 Fingerprints + Lipinski Descriptors)<br />
            &nbsp;&nbsp;↓<br />
            Symmetric Pair Feature Assembly (Tanimoto Similarity + |ΔMolWt| + |ΔLogP| + |ΔTPSA| + CYP/QT Overlap)<br />
            &nbsp;&nbsp;↓<br />
            Machine Learning Inference ({modelInfo?.active_champion_model || 'Random Forest Ensemble'})<br />
            &nbsp;&nbsp;↓<br />
            Severity Classification (Major: ≥0.70 | Moderate: 0.40–0.70 | Minor: &lt;0.40)<br />
            &nbsp;&nbsp;↓<br />
            SHAP TreeExplainer Local Attribution (Quantifies Positive/Negative Feature Risk Drivers)<br />
            &nbsp;&nbsp;↓<br />
            Decision-Support Alert Dispatch (FastAPI REST API → React Dashboard)
          </div>
        </section>

        {/* Benchmark Results */}
        {modelInfo?.benchmark_report?.models_benchmark && (
          <section className="glass-panel" style={{ padding: '32px', marginBottom: '32px' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Cpu size={20} color="var(--primary)" />
              Multi-Model Benchmark Evaluation (Actual Experimental Data)
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.6, marginBottom: '20px' }}>
              To ensure scientific defensibility without fabricated numbers, candidate algorithms were trained on stratified splits and evaluated on hold-out test sets:
            </p>

            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ background: 'rgba(255, 255, 255, 0.03)', borderBottom: '1px solid var(--border-subtle)' }}>
                  <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>ALGORITHM</th>
                  <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>ACCURACY</th>
                  <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>PRECISION</th>
                  <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>RECALL</th>
                  <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>F1-SCORE</th>
                  <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>ROC-AUC</th>
                  <th style={{ padding: '12px 16px', color: 'var(--text-muted)' }}>PR-AUC</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(modelInfo.benchmark_report.models_benchmark).map(([name, m]) => (
                  <tr key={name} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '12px 16px', fontWeight: 600, color: '#fff' }}>{name}</td>
                    <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)' }}>{m.accuracy.toFixed(4)}</td>
                    <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)' }}>{m.precision.toFixed(4)}</td>
                    <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)' }}>{m.recall.toFixed(4)}</td>
                    <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)' }}>{m.f1_score.toFixed(4)}</td>
                    <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', color: 'var(--primary)' }}>{m.roc_auc.toFixed(4)}</td>
                    <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>{m.pr_auc.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </div>
    </div>
  );
}
