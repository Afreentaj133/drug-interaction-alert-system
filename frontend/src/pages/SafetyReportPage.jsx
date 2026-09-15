import React, { useState, useEffect } from 'react';
import { 
  FileCheck2, Printer, AlertTriangle, ShieldCheck, 
  Users, Pill, Calendar, RefreshCw, ChevronDown, Info
} from 'lucide-react';
import { api } from '../services/api';

export default function SafetyReportPage({ selectedPatientId = 'DEMO-PT-1001', setActivePage }) {
  const [patients, setPatients] = useState([]);
  const [currentPatientId, setCurrentPatientId] = useState(selectedPatientId);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getPatients()
      .then(pts => {
        setPatients(pts);
        if (pts.length > 0 && !currentPatientId) {
          setCurrentPatientId(pts[0].patient_id);
        }
      })
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    if (currentPatientId) {
      loadReport(currentPatientId);
    }
  }, [currentPatientId]);

  const loadReport = async (ptId) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getPatientSafetySummary(ptId);
      setReport(data);
    } catch (err) {
      setError(err.message || 'Error generating medication safety report.');
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="container" style={{ padding: '36px 0 60px' }}>
      {/* Top Action Bar */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', margin: '0 0 6px' }}>
            Clinical Medication Safety Summary
          </h1>
          <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.92rem' }}>
            Comprehensive AI-assisted review combining patient clinical history, active medications, and SHAP explainability.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <select
            value={currentPatientId}
            onChange={(e) => setCurrentPatientId(e.target.value)}
            style={{
              background: 'var(--surface-card)',
              color: '#fff',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '8px 14px',
              fontSize: '0.88rem'
            }}
          >
            {patients.map(p => (
              <option key={p.patient_id} value={p.patient_id}>
                {p.patient_id} — {p.name}
              </option>
            ))}
          </select>

          <button
            onClick={handlePrint}
            className="btn btn-outline"
            style={{ padding: '8px 16px', fontSize: '0.85rem', gap: '6px' }}
          >
            <Printer size={16} />
            Print / Save PDF Report
          </button>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ padding: '60px 20px', textAlign: 'center' }}>
          <RefreshCw size={32} className="spin" style={{ color: 'var(--primary-400)', margin: '0 auto 16px' }} />
          <p style={{ color: 'var(--text-secondary)' }}>Compiling clinical safety summary & running polypharmacy model...</p>
        </div>
      ) : error ? (
        <div className="card" style={{ padding: '30px', textAlign: 'center', color: '#f87171' }}>
          <AlertTriangle size={32} style={{ margin: '0 auto 12px' }} />
          <p>{error}</p>
        </div>
      ) : report ? (
        <div className="printable-report" style={{
          background: 'var(--surface-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          padding: '36px',
          boxShadow: 'var(--shadow-lg)'
        }}>
          {/* REPORT HEADER */}
          <div style={{
            borderBottom: '2px solid var(--border-subtle)',
            paddingBottom: '20px',
            marginBottom: '24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            flexWrap: 'wrap',
            gap: '16px'
          }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <span style={{
                  background: 'rgba(14, 165, 233, 0.2)',
                  color: '#38bdf8',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: 700
                }}>
                  DIAS CDSS PROTOTYPE
                </span>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  Generated: {report.generated_at}
                </span>
              </div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff', margin: 0 }}>
                Patient Medication Safety Assessment Report
              </h2>
            </div>

            <div style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '8px 16px',
              textAlign: 'right'
            }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Patient ID Code</span>
              <strong style={{ fontSize: '1.1rem', color: '#38bdf8' }}>{report.patient_id}</strong>
            </div>
          </div>

          {/* SECTION 1: CLINICAL PROFILE */}
          <div style={{ marginBottom: '28px' }}>
            <h3 style={{ fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '14px' }}>
              1. Patient Demographics & Documented Clinical Context
            </h3>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '16px',
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '18px'
            }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Patient Name:</span>
                <p style={{ margin: '2px 0 0', fontWeight: 600, color: '#fff' }}>{report.patient_name}</p>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Age & Sex:</span>
                <p style={{ margin: '2px 0 0', fontWeight: 600, color: '#fff' }}>{report.age} years | {report.sex}</p>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Documented Conditions:</span>
                <p style={{ margin: '2px 0 0', fontWeight: 600, color: '#e2e8f0' }}>
                  {report.known_conditions.join(', ') || 'None documented'}
                </p>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#f87171' }}>Known Drug Allergies:</span>
                <p style={{ margin: '2px 0 0', fontWeight: 600, color: '#fca5a5' }}>
                  {report.known_allergies.join(', ') || 'No known drug allergies'}
                </p>
              </div>
            </div>
          </div>

          {/* SECTION 2: ACTIVE MEDICATIONS */}
          <div style={{ marginBottom: '28px' }}>
            <h3 style={{ fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '14px' }}>
              2. Active Prescribed Regimen ({report.active_medications.length} Medications)
            </h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', textAlign: 'left' }}>
                    <th style={{ padding: '8px 10px' }}>Medication</th>
                    <th style={{ padding: '8px 10px' }}>Dosage & Route</th>
                    <th style={{ padding: '8px 10px' }}>Frequency</th>
                    <th style={{ padding: '8px 10px' }}>Source</th>
                    <th style={{ padding: '8px 10px' }}>Clinical Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {report.active_medications.map((m, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                      <td style={{ padding: '10px', fontWeight: 700, color: '#fff' }}>
                        {m.drug_name}
                      </td>
                      <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>
                        {m.dose} ({m.route})
                      </td>
                      <td style={{ padding: '10px', color: 'var(--text-secondary)' }}>
                        {m.frequency}
                      </td>
                      <td style={{ padding: '10px', color: 'var(--text-muted)' }}>
                        {m.source}
                      </td>
                      <td style={{ padding: '10px', color: 'var(--text-muted)' }}>
                        {m.notes || '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* SECTION 3: DETECTED INTERACTIONS */}
          <div style={{ marginBottom: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', margin: 0 }}>
                3. Polypharmacy Drug-Drug Interaction Matrix ({report.total_screened_pairs} Pairs Screened)
              </h3>
              <div style={{ display: 'flex', gap: '8px' }}>
                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, background: 'rgba(239, 68, 68, 0.2)', color: '#f87171' }}>
                  {report.risk_breakdown.Major} Major
                </span>
                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24' }}>
                  {report.risk_breakdown.Moderate} Moderate
                </span>
                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, background: 'rgba(74, 222, 128, 0.2)', color: '#4ade80' }}>
                  {report.risk_breakdown.Minor} Compatible
                </span>
              </div>
            </div>

            {/* High Priority Major Alerts */}
            {report.high_priority_alerts.length > 0 && (
              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ color: '#f87171', fontSize: '0.9rem', fontWeight: 700, margin: '0 0 8px' }}>
                  Critical Priority Alerts (Major Severity)
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {report.high_priority_alerts.map((pair, idx) => (
                    <div key={idx} style={{
                      background: 'rgba(239, 68, 68, 0.05)',
                      border: '1px solid rgba(239, 68, 68, 0.25)',
                      borderRadius: 'var(--radius-md)',
                      padding: '14px'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                        <span style={{ fontWeight: 800, fontSize: '1rem', color: '#fff' }}>
                          {pair.drug_a} + {pair.drug_b}
                        </span>
                        <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#f87171' }}>
                          Probability: {(pair.risk_probability * 100).toFixed(1)}% (Major)
                        </span>
                      </div>
                      <p style={{ margin: '0 0 6px', fontSize: '0.85rem', color: '#f1f5f9' }}>
                        <strong>Clinical Risk:</strong> {pair.clinical_effect}
                      </p>
                      <p style={{ margin: '0 0 8px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                        <strong>Mechanism:</strong> {pair.mechanism}
                      </p>
                      {pair.explanation.length > 0 && (
                        <div style={{ fontSize: '0.8rem', color: '#38bdf8', background: 'rgba(14, 165, 233, 0.1)', padding: '6px 10px', borderRadius: '4px' }}>
                          <strong>SHAP Explainable Feature:</strong> {pair.explanation[0]}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Moderate Alerts */}
            {report.moderate_alerts.length > 0 && (
              <div style={{ marginBottom: '16px' }}>
                <h4 style={{ color: '#fbbf24', fontSize: '0.9rem', fontWeight: 700, margin: '0 0 8px' }}>
                  Moderate Severity Interactions
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {report.moderate_alerts.map((pair, idx) => (
                    <div key={idx} style={{
                      background: 'rgba(245, 158, 11, 0.05)',
                      border: '1px solid rgba(245, 158, 11, 0.2)',
                      borderRadius: 'var(--radius-md)',
                      padding: '10px 14px'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 700, color: '#fff', fontSize: '0.92rem' }}>
                          {pair.drug_a} + {pair.drug_b}
                        </span>
                        <span style={{ fontSize: '0.8rem', color: '#fbbf24', fontWeight: 600 }}>
                          Probability: {(pair.risk_probability * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p style={{ margin: '4px 0 0', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                        {pair.clinical_effect}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Compatible Pairs */}
            {report.minor_interactions.length > 0 && (
              <div>
                <h4 style={{ color: '#4ade80', fontSize: '0.88rem', fontWeight: 700, margin: '0 0 8px' }}>
                  No Significant Interactions Detected ({report.minor_interactions.length} Pairs)
                </h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {report.minor_interactions.map((pair, idx) => (
                    <span key={idx} style={{
                      background: 'rgba(74, 222, 128, 0.08)',
                      border: '1px solid rgba(74, 222, 128, 0.2)',
                      padding: '4px 10px',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      color: '#4ade80'
                    }}>
                      {pair.drug_a} + {pair.drug_b}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* SECTION 4: CLINICIAN ACTION ITEMS */}
          <div style={{ marginBottom: '28px' }}>
            <h3 style={{ fontSize: '1rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '12px' }}>
              4. Recommended Pharmacotherapy Actions & Monitoring
            </h3>
            <div style={{
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '16px'
            }}>
              <ul style={{ margin: 0, paddingLeft: '20px', color: '#e2e8f0', fontSize: '0.88rem', lineHeight: 1.6 }}>
                {report.clinician_action_items.map((action, idx) => (
                  <li key={idx} style={{ marginBottom: '6px' }}>{action}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* SECTION 5: CLINICAL SAFETY NOTICE */}
          <div style={{
            background: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            fontSize: '0.8rem',
            color: '#fef3c7',
            lineHeight: 1.5
          }}>
            <strong>MANDATORY CLINICAL SAFETY NOTICE:</strong> {report.clinical_disclaimer}
          </div>
        </div>
      ) : null}
    </div>
  );
}
