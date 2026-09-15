import React, { useState } from 'react';
import { 
  AlertCircle, 
  AlertTriangle, 
  CheckCircle2, 
  ShieldCheck, 
  Copy, 
  Check, 
  ArrowRightLeft, 
  Sparkles, 
  Info,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import RiskBadge from '../components/RiskBadge';

export default function ResultsPanel({ result, onReset }) {
  const [copied, setCopied] = useState(false);

  if (!result) return null;

  const severityNorm = (result.severity || 'Minor').toLowerCase();
  const isMajor = severityNorm === 'major';
  const isModerate = severityNorm === 'moderate';

  const probPercent = Math.round(result.risk_probability * 100);

  const getGaugeColor = () => {
    if (isMajor) return '#ef4444';
    if (isModerate) return '#f59e0b';
    return '#10b981';
  };

  const handleCopy = () => {
    const summary = `DIAS Drug Interaction Alert:
Pair: ${result.drug_a} + ${result.drug_b}
Severity: ${result.severity.toUpperCase()}
Risk Probability: ${probPercent}%
Mechanism: ${result.mechanism}
Clinical Risk: ${result.clinical_effect}
Alternative Guidance: ${result.safer_alternative || 'None'}
Disclaimer: Clinical decision-support only. Must be independently verified by a licensed clinician.`;

    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-panel" style={{
      padding: '32px',
      marginTop: '28px',
      borderColor: isMajor ? 'rgba(239, 68, 68, 0.4)' : isModerate ? 'rgba(245, 158, 11, 0.4)' : 'rgba(16, 185, 129, 0.3)'
    }}>
      {/* Top Banner */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
        paddingBottom: '20px',
        borderBottom: '1px solid var(--border-subtle)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            fontSize: '1.6rem',
            fontWeight: 800,
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span>{result.drug_a}</span>
            <span style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }}>+</span>
            <span>{result.drug_b}</span>
          </div>
          <RiskBadge severity={result.severity} />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={handleCopy}
            className="btn btn-secondary"
            style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          >
            {copied ? <Check size={14} color="#4ade80" /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy Summary'}
          </button>
        </div>
      </div>

      {/* Main Stats Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '20px',
        margin: '24px 0'
      }}>
        {/* Probability Gauge Card */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.7)',
          borderRadius: 'var(--radius-md)',
          padding: '20px',
          border: '1px solid var(--border-subtle)'
        }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Interaction Risk Probability
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', margin: '8px 0' }}>
            <span style={{ fontSize: '2.5rem', fontWeight: 800, color: getGaugeColor(), fontFamily: 'var(--font-mono)' }}>
              {probPercent}%
            </span>
            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              ({result.risk_probability})
            </span>
          </div>
          {/* Progress Bar */}
          <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{
              width: `${probPercent}%`,
              height: '100%',
              background: getGaugeColor(),
              transition: 'width 0.6s ease'
            }}></div>
          </div>
        </div>

        {/* Severity Classification */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.7)',
          borderRadius: 'var(--radius-md)',
          padding: '20px',
          border: '1px solid var(--border-subtle)'
        }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Triaged Clinical Severity
          </div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#fff', margin: '10px 0' }}>
            {result.severity.toUpperCase()}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Status: {result.interaction_detected ? 'Adverse Interaction Flagged' : 'Low Interaction Liability'}
          </div>
        </div>

        {/* Evidence Source */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.7)',
          borderRadius: 'var(--radius-md)',
          padding: '20px',
          border: '1px solid var(--border-subtle)'
        }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
            Prediction Origin
          </div>
          <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--primary)', margin: '12px 0 6px 0' }}>
            {result.source}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            ECFP4 Fingerprints &amp; Lipinski Descriptors
          </div>
        </div>
      </div>

      {/* Clinical Mechanism & Adverse Effect */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '20px',
        marginBottom: '24px'
      }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '20px'
        }}>
          <h4 style={{ color: '#fff', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Info size={16} color="var(--primary)" />
            Pharmacological Mechanism
          </h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.6 }}>
            {result.mechanism}
          </p>
        </div>

        <div style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '20px'
        }}>
          <h4 style={{ color: '#fff', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <AlertTriangle size={16} color={isMajor ? '#ef4444' : '#f59e0b'} />
            Documented Clinical Risk
          </h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.6 }}>
            {result.clinical_effect}
          </p>
        </div>
      </div>

      {/* XAI: Why this alert was generated (SHAP Explanations) */}
      <div style={{
        background: 'rgba(15, 23, 42, 0.8)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
          <Sparkles size={18} color="#38bdf8" />
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff' }}>
            Why Did the Model Produce This Result? (Explainable AI)
          </h3>
        </div>

        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '18px' }}>
          SHAP (Shapley Additive Explanations) TreeExplainer analyzes the contribution of each chemical fingerprint similarity, 
          molecular descriptor, and metabolic attribute toward elevating or dampening interaction probability.
        </p>

        {/* Feature Contribution Bars */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {result.shap_contributions && result.shap_contributions.map((item, idx) => {
            const isRiskInc = item.shap_value > 0;
            return (
              <div key={idx} style={{
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '12px 16px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '12px'
              }}>
                <div style={{ flex: 1, minWidth: '220px' }}>
                  <div style={{ color: '#fff', fontSize: '0.88rem', fontWeight: 600 }}>
                    {item.feature_label}
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
                    Feature value: {item.value}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    padding: '3px 8px',
                    borderRadius: '4px',
                    background: isRiskInc ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                    color: isRiskInc ? '#f87171' : '#4ade80',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    {isRiskInc ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                    {item.impact} ({item.shap_value > 0 ? `+${item.shap_value}` : item.shap_value})
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Plain Language Clinical Summary Reasons */}
        {result.explanation && result.explanation.length > 0 && (
          <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
              Active Clinical Factor Indicators:
            </div>
            <ul style={{ paddingLeft: '20px', color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.6 }}>
              {result.explanation.map((reason, i) => (
                <li key={i}>{reason}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Suggested Lower-Risk Options (Strictly for clinician review) */}
      <div style={{
        background: 'rgba(14, 165, 233, 0.05)',
        border: '1px solid rgba(14, 165, 233, 0.2)',
        borderRadius: 'var(--radius-md)',
        padding: '20px',
        marginBottom: '24px'
      }}>
        <h4 style={{ color: '#38bdf8', fontSize: '0.95rem', fontWeight: 700, marginBottom: '6px' }}>
          Suggested Lower-Risk Options (Clinician Review Only)
        </h4>
        <p style={{ color: 'var(--text-primary)', fontSize: '0.88rem', lineHeight: 1.6 }}>
          {result.safer_alternative || 'No verified alternative information is available in the current formulary.'}
        </p>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '8px' }}>
          Disclaimer: Alternative options are NOT autonomous prescriptions. A qualified physician or pharmacist must evaluate patient-specific 
          indication, organ function, comorbidities, allergies, and lab results.
        </p>
      </div>

      {/* Mandatory Clinical Verification Banner */}
      <div style={{
        background: 'rgba(245, 158, 11, 0.08)',
        border: '1px solid rgba(245, 158, 11, 0.25)',
        borderRadius: 'var(--radius-md)',
        padding: '14px 18px',
        fontSize: '0.82rem',
        color: '#fef3c7',
        lineHeight: 1.5,
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <ShieldCheck size={20} color="#f59e0b" style={{ flexShrink: 0 }} />
        <div>
          <strong>Clinical Verification Required:</strong> {result.clinical_disclaimer}
        </div>
      </div>
    </div>
  );
}
