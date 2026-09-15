import React, { useState, useEffect, useRef } from 'react';
import { 
  Pill, 
  ArrowRightLeft, 
  Trash2, 
  Search, 
  AlertCircle, 
  Loader2, 
  Sparkles,
  Info,
  CheckCircle2
} from 'lucide-react';
import { api } from '../services/api';
import ResultsPanel from './ResultsPanel';

export default function CheckerPage() {
  const [drugA, setDrugA] = useState('');
  const [drugB, setDrugB] = useState('');

  const [suggestionsA, setSuggestionsA] = useState([]);
  const [suggestionsB, setSuggestionsB] = useState([]);

  const [selectedDrugA, setSelectedDrugA] = useState(null);
  const [selectedDrugB, setSelectedDrugB] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  // Example Preset Clinical Pairs
  const presetPairs = [
    { a: 'Warfarin', b: 'Aspirin', label: 'Warfarin + Aspirin (Major Bleeding Risk)' },
    { a: 'Simvastatin', b: 'Clarithromycin', label: 'Simvastatin + Clarithromycin (Major Rhabdomyolysis)' },
    { a: 'Fluoxetine', b: 'Tramadol', label: 'Fluoxetine + Tramadol (Serotonin Syndrome)' },
    { a: 'Lisinopril', b: 'Spironolactone', label: 'Lisinopril + Spironolactone (Hyperkalemia)' },
    { a: 'Digoxin', b: 'Verapamil', label: 'Digoxin + Verapamil (Moderate AV Block)' },
    { a: 'Paracetamol', b: 'Amoxicillin', label: 'Paracetamol + Amoxicillin (Low Risk Standard Care)' },
  ];

  // Autocomplete fetch for Drug A
  useEffect(() => {
    if (drugA.trim().length >= 1 && (!selectedDrugA || selectedDrugA.name !== drugA)) {
      const timer = setTimeout(() => {
        api.searchDrugs(drugA, 6)
          .then(data => setSuggestionsA(data))
          .catch(() => setSuggestionsA([]));
      }, 150);
      return () => clearTimeout(timer);
    } else {
      setSuggestionsA([]);
    }
  }, [drugA, selectedDrugA]);

  // Autocomplete fetch for Drug B
  useEffect(() => {
    if (drugB.trim().length >= 1 && (!selectedDrugB || selectedDrugB.name !== drugB)) {
      const timer = setTimeout(() => {
        api.searchDrugs(drugB, 6)
          .then(data => setSuggestionsB(data))
          .catch(() => setSuggestionsB([]));
      }, 150);
      return () => clearTimeout(timer);
    } else {
      setSuggestionsB([]);
    }
  }, [drugB, selectedDrugB]);

  const handleSwap = () => {
    const tempName = drugA;
    const tempSelected = selectedDrugA;
    setDrugA(drugB);
    setSelectedDrugA(selectedDrugB);
    setDrugB(tempName);
    setSelectedDrugB(tempSelected);
    setError(null);
  };

  const handleClear = () => {
    setDrugA('');
    setDrugB('');
    setSelectedDrugA(null);
    setSelectedDrugB(null);
    setError(null);
    setResult(null);
  };

  const handleCheck = async (overrideA = null, overrideB = null) => {
    const nameA = (overrideA || drugA).trim();
    const nameB = (overrideB || drugB).trim();

    setError(null);

    // Front-end Validation
    if (!nameA || !nameB) {
      setError('Please provide both Drug A and Drug B.');
      return;
    }

    if (nameA.toLowerCase() === nameB.toLowerCase()) {
      setError(`Cannot evaluate interaction: Drug A and Drug B are identical ('${nameA}'). Please select two distinct medications.`);
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await api.checkInteraction(nameA, nameB);
      setResult(response);
    } catch (err) {
      setError(err.message || 'Failed to complete drug interaction evaluation.');
    } finally {
      setLoading(false);
    }
  };

  const loadPreset = (preset) => {
    setDrugA(preset.a);
    setDrugB(preset.b);
    setSelectedDrugA({ name: preset.a });
    setSelectedDrugB({ name: preset.b });
    handleCheck(preset.a, preset.b);
  };

  return (
    <div className="container" style={{ paddingTop: '32px', paddingBottom: '60px' }}>
      <div style={{ maxWidth: '860px', margin: '0 auto' }}>
        {/* Page Header */}
        <div style={{ marginBottom: '28px' }}>
          <h1 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Pill size={28} color="var(--primary)" />
            Drug-Drug Interaction Checker
          </h1>
          <p className="section-subtitle">
            Enter two medications to run RDKit molecular feature extraction and ML severity classification with SHAP explainability.
          </p>
        </div>

        {/* Clinical Presets Bar */}
        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '12px 16px',
          marginBottom: '24px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          flexWrap: 'wrap'
        }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
            Clinical Presets:
          </span>
          {presetPairs.map((p, idx) => (
            <button
              key={idx}
              onClick={() => loadPreset(p)}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-secondary)',
                fontSize: '0.78rem',
                padding: '4px 10px',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(14, 165, 233, 0.15)';
                e.target.style.color = '#38bdf8';
                e.target.style.borderColor = 'rgba(14, 165, 233, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.05)';
                e.target.style.color = 'var(--text-secondary)';
                e.target.style.borderColor = 'var(--border-subtle)';
              }}
            >
              {p.a} + {p.b}
            </button>
          ))}
        </div>

        {/* Main Checker Box */}
        <div className="glass-panel" style={{ padding: '32px' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr auto 1fr',
            gap: '16px',
            alignItems: 'center'
          }}>
            {/* Drug A Input */}
            <div style={{ position: 'relative' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Primary Medication (Drug A)
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  placeholder="e.g. Warfarin, Simvastatin..."
                  value={drugA}
                  onChange={(e) => {
                    setDrugA(e.target.value);
                    setSelectedDrugA(null);
                    setError(null);
                  }}
                  className="input-field"
                  style={{ paddingLeft: '38px' }}
                />
                <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '15px' }} />
              </div>

              {/* Autocomplete Dropdown Drug A */}
              {suggestionsA.length > 0 && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  right: 0,
                  background: '#0f172a',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  marginTop: '4px',
                  zIndex: 20,
                  boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
                  overflow: 'hidden'
                }}>
                  {suggestionsA.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => {
                        setDrugA(item.name);
                        setSelectedDrugA(item);
                        setSuggestionsA([]);
                      }}
                      style={{
                        padding: '10px 14px',
                        cursor: 'pointer',
                        borderBottom: '1px solid rgba(255,255,255,0.04)',
                        transition: 'background 0.15s ease'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(14, 165, 233, 0.15)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.9rem' }}>{item.name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {item.category} • MW: {item.molecular_weight}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Selected Chemical Badge */}
              {selectedDrugA && selectedDrugA.smiles && (
                <div style={{ marginTop: '8px', fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  SMILES: {selectedDrugA.smiles.slice(0, 30)}...
                </div>
              )}
            </div>

            {/* Swap Button */}
            <div style={{ paddingTop: '24px' }}>
              <button
                onClick={handleSwap}
                title="Swap Medication Order"
                className="btn btn-secondary"
                style={{ width: '42px', height: '42px', padding: 0, borderRadius: '50%' }}
              >
                <ArrowRightLeft size={16} />
              </button>
            </div>

            {/* Drug B Input */}
            <div style={{ position: 'relative' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                Secondary Medication (Drug B)
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  placeholder="e.g. Aspirin, Clarithromycin..."
                  value={drugB}
                  onChange={(e) => {
                    setDrugB(e.target.value);
                    setSelectedDrugB(null);
                    setError(null);
                  }}
                  className="input-field"
                  style={{ paddingLeft: '38px' }}
                />
                <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '15px' }} />
              </div>

              {/* Autocomplete Dropdown Drug B */}
              {suggestionsB.length > 0 && (
                <div style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  right: 0,
                  background: '#0f172a',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  marginTop: '4px',
                  zIndex: 20,
                  boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
                  overflow: 'hidden'
                }}>
                  {suggestionsB.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => {
                        setDrugB(item.name);
                        setSelectedDrugB(item);
                        setSuggestionsB([]);
                      }}
                      style={{
                        padding: '10px 14px',
                        cursor: 'pointer',
                        borderBottom: '1px solid rgba(255,255,255,0.04)',
                        transition: 'background 0.15s ease'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(14, 165, 233, 0.15)'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                    >
                      <div style={{ fontWeight: 600, color: '#fff', fontSize: '0.9rem' }}>{item.name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {item.category} • MW: {item.molecular_weight}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Selected Chemical Badge */}
              {selectedDrugB && selectedDrugB.smiles && (
                <div style={{ marginTop: '8px', fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  SMILES: {selectedDrugB.smiles.slice(0, 30)}...
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginTop: '28px',
            paddingTop: '20px',
            borderTop: '1px solid var(--border-subtle)'
          }}>
            <button
              onClick={handleClear}
              className="btn btn-secondary"
              style={{ fontSize: '0.85rem' }}
            >
              <Trash2 size={16} />
              Clear Selection
            </button>

            <button
              onClick={() => handleCheck()}
              disabled={loading || !drugA.trim() || !drugB.trim()}
              className="btn btn-primary"
              style={{ padding: '12px 28px', fontSize: '1rem' }}
            >
              {loading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Running ML Inference...
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  Evaluate Interaction Risk
                </>
              )}
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div style={{
              marginTop: '20px',
              padding: '14px 16px',
              background: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid rgba(239, 68, 68, 0.35)',
              borderRadius: 'var(--radius-md)',
              color: '#fca5a5',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '0.88rem'
            }}>
              <AlertCircle size={18} color="#ef4444" style={{ flexShrink: 0 }} />
              <div>{error}</div>
            </div>
          )}
        </div>

        {/* Results Panel */}
        {result && (
          <ResultsPanel result={result} onReset={handleClear} />
        )}
      </div>
    </div>
  );
}
