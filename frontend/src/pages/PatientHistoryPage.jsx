import React, { useState, useEffect } from 'react';
import { 
  Users, Plus, Trash2, AlertTriangle, ShieldAlert, ShieldCheck, 
  Activity, Pill, RefreshCw, FileText, CheckCircle2, ChevronRight, Info
} from 'lucide-react';
import { api } from '../services/api';
import RiskBadge from '../components/RiskBadge';

export default function PatientHistoryPage({ setActivePage, setSelectedPatientId }) {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Add Medication form states
  const [showAddMed, setShowAddMed] = useState(false);
  const [drugSearchQuery, setDrugSearchQuery] = useState('');
  const [drugSearchResults, setDrugSearchResults] = useState([]);
  const [selectedDrugName, setSelectedDrugName] = useState('');
  const [medDose, setMedDose] = useState('5 mg');
  const [medFrequency, setMedFrequency] = useState('Once daily');
  const [medRoute, setMedRoute] = useState('Oral');
  const [medStatus, setMedStatus] = useState('Current');
  const [isSubmittingMed, setIsSubmittingMed] = useState(false);

  // Polypharmacy screening states
  const [isScreening, setIsScreening] = useState(false);
  const [screeningResults, setScreeningResults] = useState(null);

  // Load patients on mount
  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getPatients();
      setPatients(data);
      if (data.length > 0) {
        // Select first demo patient by default
        loadPatientDetails(data[0].patient_id);
      }
    } catch (err) {
      setError(err.message || 'Failed to load patient records.');
    } finally {
      setLoading(false);
    }
  };

  const loadPatientDetails = async (patientId) => {
    try {
      const fullPt = await api.getPatientById(patientId);
      setSelectedPatient(fullPt);
      setScreeningResults(null); // Reset previous screening on patient switch
      if (setSelectedPatientId) setSelectedPatientId(patientId);
    } catch (err) {
      console.error('Failed to load patient details:', err);
    }
  };

  // Autocomplete drug search
  useEffect(() => {
    if (drugSearchQuery.trim().length >= 2) {
      api.searchDrugs(drugSearchQuery.trim())
        .then(res => setDrugSearchResults(res))
        .catch(err => console.error(err));
    } else {
      setDrugSearchResults([]);
    }
  }, [drugSearchQuery]);

  const handleAddMedication = async (e) => {
    e.preventDefault();
    if (!selectedDrugName || !selectedPatient) return;

    setIsSubmittingMed(true);
    try {
      await api.addPatientMedication(selectedPatient.patient_id, {
        drug_name: selectedDrugName,
        dose: medDose,
        frequency: medFrequency,
        route: medRoute,
        status: medStatus,
        source: 'Manual'
      });
      // Refresh patient details
      await loadPatientDetails(selectedPatient.patient_id);
      // Reset form
      setSelectedDrugName('');
      setDrugSearchQuery('');
      setShowAddMed(false);
    } catch (err) {
      alert(err.message || 'Error adding medication');
    } finally {
      setIsSubmittingMed(false);
    }
  };

  const handleDeleteMedication = async (medId) => {
    if (!window.confirm('Remove this medication from patient record?')) return;
    try {
      await api.removePatientMedication(selectedPatient.patient_id, medId);
      await loadPatientDetails(selectedPatient.patient_id);
    } catch (err) {
      alert(err.message || 'Error removing medication');
    }
  };

  const handleRunPolypharmacyScreening = async () => {
    if (!selectedPatient) return;
    setIsScreening(true);
    setScreeningResults(null);
    try {
      const res = await api.screenPatientMedications(selectedPatient.patient_id);
      setScreeningResults(res);
    } catch (err) {
      alert(err.message || 'Error running polypharmacy screening');
    } finally {
      setIsScreening(false);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '60px 0', textAlign: 'center' }}>
        <RefreshCw size={32} className="spin" style={{ color: 'var(--primary-400)', margin: '0 auto 16px' }} />
        <p style={{ color: 'var(--text-secondary)' }}>Loading patient clinical profiles...</p>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '36px 0 60px' }}>
      {/* Demonstration Banner */}
      <div style={{
        background: 'rgba(14, 165, 233, 0.1)',
        border: '1px solid rgba(14, 165, 233, 0.25)',
        borderRadius: 'var(--radius-lg)',
        padding: '12px 18px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Info size={18} style={{ color: '#38bdf8' }} />
          <span style={{ fontSize: '0.86rem', color: '#e0f2fe' }}>
            <strong>Demonstration Mode Active:</strong> Synthetic patient profiles are provided for evaluating multi-drug polypharmacy screening. No real personal identities are collected.
          </span>
        </div>
        <button
          onClick={() => setActivePage && setActivePage('prescriptions')}
          className="btn btn-outline"
          style={{ padding: '5px 12px', fontSize: '0.78rem' }}
        >
          <FileText size={14} />
          Upload Prescription
        </button>
      </div>

      {/* Header & Patient Switcher */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', margin: '0 0 6px' }}>
            Patient Clinical & Medication History
          </h1>
          <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.92rem' }}>
            Review chronic clinical context, track active regimens, and execute multi-drug interaction screening.
          </p>
        </div>

        {/* Patient Selection Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Select Patient:</label>
          <select
            value={selectedPatient ? selectedPatient.patient_id : ''}
            onChange={(e) => loadPatientDetails(e.target.value)}
            style={{
              background: 'var(--surface-card)',
              color: '#fff',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '8px 14px',
              fontSize: '0.9rem',
              cursor: 'pointer'
            }}
          >
            {patients.map(p => (
              <option key={p.patient_id} value={p.patient_id}>
                {p.patient_id} — {p.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedPatient && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px', alignItems: 'start' }}>
          {/* LEFT: Patient Clinical Profile Card */}
          <div className="card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '18px' }}>
              <div style={{
                background: 'rgba(14, 165, 233, 0.15)',
                color: '#38bdf8',
                width: '42px',
                height: '42px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Users size={22} />
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
                  {selectedPatient.name}
                </h3>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  ID: <strong style={{ color: '#38bdf8' }}>{selectedPatient.patient_id}</strong> | {selectedPatient.age} yrs, {selectedPatient.sex}
                </span>
              </div>
            </div>

            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
                  Known Medical Conditions
                </span>
                <p style={{ margin: '4px 0 0', fontSize: '0.88rem', color: '#f1f5f9', fontWeight: 500 }}>
                  {selectedPatient.conditions || 'None documented'}
                </p>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#f87171', fontWeight: 700 }}>
                  Documented Drug Allergies
                </span>
                <p style={{ margin: '4px 0 0', fontSize: '0.88rem', color: '#fca5a5', fontWeight: 500 }}>
                  {selectedPatient.allergies || 'No known allergies'}
                </p>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
                  Clinical Background & History
                </span>
                <p style={{ margin: '4px 0 0', fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {selectedPatient.medical_history || 'No additional history recorded.'}
                </p>
              </div>

              {selectedPatient.surgeries && (
                <div>
                  <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
                    Surgical / Procedural History
                  </span>
                  <p style={{ margin: '4px 0 0', fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
                    {selectedPatient.surgeries}
                  </p>
                </div>
              )}
            </div>

            <div style={{ marginTop: '24px', paddingTop: '18px', borderTop: '1px solid var(--border-subtle)' }}>
              <button
                onClick={() => {
                  if (setActivePage) setActivePage('safety-report');
                }}
                className="btn btn-outline"
                style={{ width: '100%', justifyContent: 'center', fontSize: '0.85rem' }}
              >
                <FileText size={16} />
                View Full Safety Summary
              </button>
            </div>
          </div>

          {/* RIGHT: Active Medications List & Actions */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div className="card" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px' }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff', margin: '0 0 4px' }}>
                    Active Medication Regimen
                  </h2>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0 }}>
                    {selectedPatient.medications.filter(m => m.status === 'Current').length} Current prescription(s) in active profile
                  </p>
                </div>
                <button
                  onClick={() => setShowAddMed(!showAddMed)}
                  className="btn btn-primary"
                  style={{ padding: '8px 14px', fontSize: '0.85rem' }}
                >
                  <Plus size={16} />
                  Add Medication
                </button>
              </div>

              {/* Add Medication Drawer */}
              {showAddMed && (
                <form onSubmit={handleAddMedication} style={{
                  background: 'rgba(255,255,255,0.02)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '16px',
                  marginBottom: '20px'
                }}>
                  <h4 style={{ margin: '0 0 12px', fontSize: '0.95rem', color: '#38bdf8' }}>
                    Add Validated Medication
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                    <div>
                      <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                        Search Drug Name:
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Warfarin, Metformin, Aspirin..."
                        value={drugSearchQuery}
                        onChange={(e) => setDrugSearchQuery(e.target.value)}
                        className="input-field"
                        style={{ width: '100%', padding: '7px 10px', fontSize: '0.85rem' }}
                      />
                      {drugSearchResults.length > 0 && (
                        <div style={{
                          background: 'var(--surface-card)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 'var(--radius-md)',
                          marginTop: '4px',
                          maxHeight: '140px',
                          overflowY: 'auto',
                          zIndex: 20
                        }}>
                          {drugSearchResults.map(d => (
                            <div
                              key={d.name}
                              onClick={() => {
                                setSelectedDrugName(d.name);
                                setDrugSearchQuery(d.name);
                                setDrugSearchResults([]);
                              }}
                              style={{
                                padding: '6px 10px',
                                fontSize: '0.82rem',
                                cursor: 'pointer',
                                borderBottom: '1px solid rgba(255,255,255,0.05)',
                                color: '#fff'
                              }}
                            >
                              <strong>{d.name}</strong> <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>({d.category})</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div>
                      <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                        Dose:
                      </label>
                      <input
                        type="text"
                        value={medDose}
                        onChange={(e) => setMedDose(e.target.value)}
                        className="input-field"
                        style={{ width: '100%', padding: '7px 10px', fontSize: '0.85rem' }}
                      />
                    </div>

                    <div>
                      <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>
                        Frequency:
                      </label>
                      <input
                        type="text"
                        value={medFrequency}
                        onChange={(e) => setMedFrequency(e.target.value)}
                        className="input-field"
                        style={{ width: '100%', padding: '7px 10px', fontSize: '0.85rem' }}
                      />
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                    <button
                      type="button"
                      onClick={() => setShowAddMed(false)}
                      className="btn btn-outline"
                      style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={!selectedDrugName || isSubmittingMed}
                      className="btn btn-primary"
                      style={{ padding: '6px 14px', fontSize: '0.8rem' }}
                    >
                      {isSubmittingMed ? 'Adding...' : 'Confirm & Add'}
                    </button>
                  </div>
                </form>
              )}

              {/* Medications Table */}
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', textAlign: 'left' }}>
                      <th style={{ padding: '10px' }}>Medication</th>
                      <th style={{ padding: '10px' }}>Dosage & Route</th>
                      <th style={{ padding: '10px' }}>Frequency</th>
                      <th style={{ padding: '10px' }}>Status</th>
                      <th style={{ padding: '10px' }}>Source</th>
                      <th style={{ padding: '10px', textAlign: 'right' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedPatient.medications.length === 0 ? (
                      <tr>
                        <td colSpan="6" style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
                          No medications documented. Add a medication or upload a prescription document above.
                        </td>
                      </tr>
                    ) : (
                      selectedPatient.medications.map((m) => (
                        <tr key={m.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                          <td style={{ padding: '12px 10px', fontWeight: 600, color: '#fff' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <Pill size={16} style={{ color: '#38bdf8' }} />
                              <span>{m.drug_name}</span>
                            </div>
                          </td>
                          <td style={{ padding: '12px 10px', color: 'var(--text-secondary)' }}>
                            {m.dose || 'Standard'} ({m.route || 'Oral'})
                          </td>
                          <td style={{ padding: '12px 10px', color: 'var(--text-secondary)' }}>
                            {m.frequency || 'Once daily'}
                          </td>
                          <td style={{ padding: '12px 10px' }}>
                            <span style={{
                              padding: '2px 8px',
                              borderRadius: '4px',
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              background: m.status === 'Current' ? 'rgba(74, 222, 128, 0.15)' : 'rgba(148, 163, 184, 0.15)',
                              color: m.status === 'Current' ? '#4ade80' : '#94a3b8'
                            }}>
                              {m.status}
                            </span>
                          </td>
                          <td style={{ padding: '12px 10px', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                            {m.source}
                          </td>
                          <td style={{ padding: '12px 10px', textAlign: 'right' }}>
                            <button
                              onClick={() => handleDeleteMedication(m.id)}
                              style={{
                                background: 'transparent',
                                border: 'none',
                                color: '#f87171',
                                cursor: 'pointer',
                                padding: '4px'
                              }}
                              title="Delete medication"
                            >
                              <Trash2 size={16} />
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              {/* Polypharmacy Screening Trigger */}
              <div style={{ marginTop: '24px', paddingTop: '18px', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Screens all unique 2-drug combinations across the patient's current active regimen.
                </span>
                <button
                  onClick={handleRunPolypharmacyScreening}
                  disabled={isScreening || selectedPatient.medications.filter(m => m.status === 'Current').length < 2}
                  className="btn btn-primary"
                  style={{ padding: '10px 20px', fontSize: '0.92rem', gap: '8px' }}
                >
                  {isScreening ? (
                    <>
                      <RefreshCw size={16} className="spin" />
                      Evaluating ML Predictions...
                    </>
                  ) : (
                    <>
                      <ShieldAlert size={16} />
                      Screen All Current Medications
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* SCREENING RESULTS PANEL */}
            {screeningResults && (
              <div className="card" style={{ padding: '24px', border: '1px solid rgba(14, 165, 233, 0.3)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <div>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#fff', margin: '0 0 4px' }}>
                      Polypharmacy Screening Report ({screeningResults.total_pairs_screened} Pairs Evaluated)
                    </h3>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0 }}>
                      Evaluated using RDKit 1024-bit Morgan ECFP4 fingerprints and Champion Random Forest model
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <span style={{ padding: '4px 10px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: 700, background: 'rgba(239, 68, 68, 0.2)', color: '#f87171' }}>
                      {screeningResults.major_risk_count} Major
                    </span>
                    <span style={{ padding: '4px 10px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: 700, background: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24' }}>
                      {screeningResults.moderate_risk_count} Moderate
                    </span>
                    <span style={{ padding: '4px 10px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: 700, background: 'rgba(74, 222, 128, 0.2)', color: '#4ade80' }}>
                      {screeningResults.minor_risk_count} Compatible
                    </span>
                  </div>
                </div>

                {/* Cumulative Regimen Warnings */}
                {screeningResults.mechanism_warnings.length > 0 && (
                  <div style={{
                    background: 'rgba(239, 68, 68, 0.08)',
                    border: '1px solid rgba(239, 68, 68, 0.25)',
                    borderRadius: 'var(--radius-md)',
                    padding: '14px',
                    marginBottom: '18px'
                  }}>
                    <h4 style={{ margin: '0 0 8px', fontSize: '0.88rem', color: '#f87171', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <AlertTriangle size={16} />
                      Cumulative Patient-Level Hazard Signals
                    </h4>
                    <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.82rem', color: '#fecaca', lineHeight: 1.5 }}>
                      {screeningResults.mechanism_warnings.map((w, idx) => (
                        <li key={idx}>{w}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* MAJOR RISK PAIRS */}
                {screeningResults.major_pairs.length > 0 && (
                  <div style={{ marginBottom: '18px' }}>
                    <h4 style={{ color: '#f87171', fontSize: '0.92rem', fontWeight: 700, margin: '0 0 10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ef4444' }}></span>
                      High-Priority Major Risks ({screeningResults.major_pairs.length})
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      {screeningResults.major_pairs.map((pair, idx) => (
                        <div key={idx} style={{
                          background: 'rgba(239, 68, 68, 0.05)',
                          border: '1px solid rgba(239, 68, 68, 0.2)',
                          borderRadius: 'var(--radius-md)',
                          padding: '14px'
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                            <span style={{ fontWeight: 700, fontSize: '0.98rem', color: '#fff' }}>
                              {pair.drug_a} + {pair.drug_b}
                            </span>
                            <span style={{ fontSize: '0.8rem', color: '#f87171', fontWeight: 700 }}>
                              Risk: {(pair.risk_probability * 100).toFixed(1)}% (Major)
                            </span>
                          </div>
                          <p style={{ margin: '0 0 6px', fontSize: '0.84rem', color: '#e2e8f0' }}>
                            <strong>Clinical Effect:</strong> {pair.clinical_effect}
                          </p>
                          <p style={{ margin: '0 0 8px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            <strong>Mechanism:</strong> {pair.mechanism}
                          </p>
                          {pair.explanation.length > 0 && (
                            <div style={{ fontSize: '0.78rem', color: '#38bdf8', background: 'rgba(14, 165, 233, 0.1)', padding: '6px 10px', borderRadius: '4px' }}>
                              <strong>XAI Rationale:</strong> {pair.explanation[0]}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* MODERATE RISK PAIRS */}
                {screeningResults.moderate_pairs.length > 0 && (
                  <div style={{ marginBottom: '18px' }}>
                    <h4 style={{ color: '#fbbf24', fontSize: '0.92rem', fontWeight: 700, margin: '0 0 10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }}></span>
                      Moderate Clinical Interactions ({screeningResults.moderate_pairs.length})
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      {screeningResults.moderate_pairs.map((pair, idx) => (
                        <div key={idx} style={{
                          background: 'rgba(245, 158, 11, 0.05)',
                          border: '1px solid rgba(245, 158, 11, 0.2)',
                          borderRadius: 'var(--radius-md)',
                          padding: '12px'
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                            <span style={{ fontWeight: 700, fontSize: '0.92rem', color: '#fff' }}>
                              {pair.drug_a} + {pair.drug_b}
                            </span>
                            <span style={{ fontSize: '0.8rem', color: '#fbbf24', fontWeight: 700 }}>
                              Risk: {(pair.risk_probability * 100).toFixed(1)}%
                            </span>
                          </div>
                          <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                            {pair.clinical_effect}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* MINOR COMPATIBLE PAIRS */}
                {screeningResults.minor_pairs.length > 0 && (
                  <div>
                    <h4 style={{ color: '#4ade80', fontSize: '0.92rem', fontWeight: 700, margin: '0 0 10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></span>
                      No Significant Interaction Detected ({screeningResults.minor_pairs.length})
                    </h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '8px' }}>
                      {screeningResults.minor_pairs.map((pair, idx) => (
                        <div key={idx} style={{
                          background: 'rgba(74, 222, 128, 0.05)',
                          border: '1px solid rgba(74, 222, 128, 0.15)',
                          borderRadius: 'var(--radius-md)',
                          padding: '8px 12px',
                          fontSize: '0.82rem',
                          color: '#e2e8f0'
                        }}>
                          <CheckCircle2 size={14} style={{ color: '#4ade80', display: 'inline', marginRight: '6px' }} />
                          <strong>{pair.drug_a}</strong> + <strong>{pair.drug_b}</strong>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
