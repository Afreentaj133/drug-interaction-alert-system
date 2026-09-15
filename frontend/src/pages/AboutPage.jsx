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

        {/* Architectural Overview */}
        <section className="glass-panel" style={{ padding: '32px', marginBottom: '32px', border: '1px solid rgba(0, 210, 255, 0.3)' }}>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#fff', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={22} color="var(--primary)" />
            Clinical Decision-Support Architecture
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.6, marginBottom: '24px' }}>
            The DIAS architecture is engineered in decoupled clinical tiers to ensure rigorous scientific validation, low-latency ML inference, and transparent physician interpretability:
          </p>

          <div style={{
            background: 'rgba(5, 12, 28, 0.95)',
            padding: '28px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(0, 210, 255, 0.35)',
            boxShadow: '0 0 25px rgba(0, 210, 255, 0.12)',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.88rem',
            color: '#00f0ff',
            lineHeight: 1.45,
            overflowX: 'auto',
            whiteSpace: 'pre',
            textAlign: 'center',
            marginBottom: '10px'
          }}>
{`               PATIENT
                 ↓
       ┌───────────────────┐
       │ Patient History   │
       │ + Medication List │
       └─────────┬─────────┘
                 ↓
       ┌───────────────────┐
       │ Prescription /    │
       │ Medical Document  │
       └─────────┬─────────┘
                 ↓
              OCR / NLP
                 ↓
       Extract medication names
                 ↓
       ┌─────────────────────┐
       │ Drug Interaction    │
       │ Detection Engine    │
       └──────────┬──────────┘
                  ↓
          RDKit + ML Model
                  ↓
       ┌─────────────────────┐
       │ Risk + Severity     │
       │ + Explanation       │
       └──────────┬──────────┘
                  ↓
          Clinical Summary
                  ↓
       👨‍⚕️ Physician Review`}
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
