import React, { useState, useEffect } from 'react';
import { 
  FileText, Upload, RefreshCw, CheckCircle2, AlertCircle, 
  ArrowRight, ShieldCheck, Trash2, Edit3, Calendar, Plus, Info
} from 'lucide-react';
import { api } from '../services/api';

export default function PrescriptionPage({ setActivePage, setSelectedPatientId }) {
  const [patients, setPatients] = useState([]);
  const [targetPatientId, setTargetPatientId] = useState('DEMO-PT-1001');

  // Upload & extraction states
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [extractionResult, setExtractionResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  // Review table states (medications to confirm)
  const [reviewMedications, setReviewMedications] = useState([]);
  const [isConfirming, setIsConfirming] = useState(false);
  const [confirmedSuccess, setConfirmedSuccess] = useState(null);

  useEffect(() => {
    api.getPatients()
      .then(pts => {
        setPatients(pts);
        if (pts.length > 0 && !targetPatientId) {
          setTargetPatientId(pts[0].patient_id);
        }
      })
      .catch(err => console.error(err));
  }, []);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Client-side extension check
    const validExts = ['.jpg', '.jpeg', '.png', '.pdf'];
    const name = file.name.toLowerCase();
    const isExtValid = validExts.some(ext => name.endsWith(ext));

    if (!isExtValid) {
      setErrorMessage('Unsupported file format. Please upload a JPG, PNG, or PDF file.');
      setSelectedFile(null);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage('File size exceeds maximum limit of 10 MB.');
      setSelectedFile(null);
      return;
    }

    setErrorMessage(null);
    setSelectedFile(file);
  };

  const handleUploadAndProcess = async () => {
    if (!selectedFile) return;
    setIsProcessing(true);
    setErrorMessage(null);
    setConfirmedSuccess(null);

    try {
      const result = await api.uploadDocument(selectedFile, targetPatientId);
      setExtractionResult(result);
      initializeReviewItems(result.extracted_medications);
    } catch (err) {
      setErrorMessage(err.message || 'Error processing document with OCR engine.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleLoadDemoSample = async () => {
    setIsProcessing(true);
    setErrorMessage(null);
    setConfirmedSuccess(null);

    try {
      const result = await api.loadDemoSamplePrescription(targetPatientId || 'DEMO-PT-1001');
      setExtractionResult(result);
      initializeReviewItems(result.extracted_medications);
    } catch (err) {
      setErrorMessage(err.message || 'Error loading synthetic demonstration prescription.');
    } finally {
      setIsProcessing(false);
    }
  };

  const initializeReviewItems = (extractedList) => {
    const items = extractedList.map(em => ({
      id: em.id,
      selected: em.match_status === 'Matched' || em.match_status === 'Corrected',
      drug_name: em.matched_drug_name || '',
      dose: em.dosage || 'Standard dose',
      frequency: 'Once daily',
      route: 'Oral',
      original_text: em.extracted_text,
      match_status: em.match_status,
      confidence: em.confidence
    }));
    setReviewMedications(items);
  };

  const handleToggleSelect = (index) => {
    setReviewMedications(prev => {
      const copy = [...prev];
      copy[index].selected = !copy[index].selected;
      return copy;
    });
  };

  const handleFieldChange = (index, field, value) => {
    setReviewMedications(prev => {
      const copy = [...prev];
      copy[index][field] = value;
      return copy;
    });
  };

  const handleRemoveRow = (index) => {
    setReviewMedications(prev => prev.filter((_, i) => i !== index));
  };

  const handleConfirmAndTransfer = async () => {
    if (!extractionResult) return;
    const selectedItems = reviewMedications.filter(m => m.selected && m.drug_name.trim());
    if (selectedItems.length === 0) {
      alert('Please select at least one valid medication to confirm.');
      return;
    }

    setIsConfirming(true);
    try {
      const res = await api.confirmMedications(
        extractionResult.document_id,
        targetPatientId,
        selectedItems.map(m => ({
          id: m.id,
          drug_name: m.drug_name,
          dose: m.dose,
          frequency: m.frequency,
          route: m.route,
          status: 'Current'
        }))
      );
      setConfirmedSuccess(res);
      if (setSelectedPatientId) setSelectedPatientId(targetPatientId);
    } catch (err) {
      alert(err.message || 'Error confirming medications to patient record.');
    } finally {
      setIsConfirming(false);
    }
  };

  return (
    <div className="container" style={{ padding: '36px 0 60px' }}>
      {/* Demo Notice */}
      <div style={{
        background: 'rgba(14, 165, 233, 0.1)',
        border: '1px solid rgba(14, 165, 233, 0.25)',
        borderRadius: 'var(--radius-lg)',
        padding: '12px 18px',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        marginBottom: '24px'
      }}>
        <Info size={18} style={{ color: '#38bdf8' }} />
        <span style={{ fontSize: '0.86rem', color: '#e0f2fe' }}>
          <strong>Clinical OCR Intake Workflow:</strong> Uploaded documents are parsed via OCR and mapped to canonical formulary compounds. Clinician verification is required before transfer into the patient's active safety profile.
        </span>
      </div>

      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', margin: '0 0 6px' }}>
          Prescription & Medical Document Intake (OCR)
        </h1>
        <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.92rem' }}>
          Ingest prescriptions, lab reports, and discharge summaries to automatically extract medication entities and screen for potential interactions.
        </p>
      </div>

      {/* Target Patient Selector */}
      <div className="card" style={{ padding: '16px 20px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '0.88rem', fontWeight: 600, color: '#fff' }}>Assign Document to Patient:</span>
          <select
            value={targetPatientId}
            onChange={(e) => setTargetPatientId(e.target.value)}
            style={{
              background: 'rgba(255,255,255,0.05)',
              color: '#fff',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '6px 12px',
              fontSize: '0.88rem'
            }}
          >
            {patients.map(p => (
              <option key={p.patient_id} value={p.patient_id}>
                {p.patient_id} — {p.name}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleLoadDemoSample}
          disabled={isProcessing}
          className="btn btn-outline"
          style={{ fontSize: '0.84rem', padding: '6px 14px', gap: '6px' }}
        >
          <FileText size={16} />
          Load Sample Prescription (1-Click Demo)
        </button>
      </div>

      {/* UPLOAD & PROCESSING CARD */}
      <div className="card" style={{ padding: '28px', marginBottom: '28px' }}>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', margin: '0 0 16px' }}>
          Upload Medical Document (JPG, PNG, PDF)
        </h3>

        <div style={{
          border: '2px dashed var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          padding: '36px 20px',
          textAlign: 'center',
          background: 'rgba(255,255,255,0.01)',
          cursor: 'pointer',
          marginBottom: '18px'
        }}>
          <input
            type="file"
            id="doc-upload-input"
            accept=".jpg,.jpeg,.png,.pdf"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <label htmlFor="doc-upload-input" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '52px',
              height: '52px',
              borderRadius: '50%',
              background: 'rgba(14, 165, 233, 0.15)',
              color: '#38bdf8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Upload size={26} />
            </div>
            <div>
              <span style={{ fontSize: '1rem', fontWeight: 600, color: '#fff' }}>
                {selectedFile ? selectedFile.name : 'Choose a prescription file or drag & drop here'}
              </span>
              <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Supports scanned JPG/PNG images and digital/scanned PDFs up to 10 MB
              </p>
            </div>
          </label>
        </div>

        {errorMessage && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            padding: '10px 14px',
            color: '#fca5a5',
            fontSize: '0.85rem',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <AlertCircle size={16} />
            {errorMessage}
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={handleUploadAndProcess}
            disabled={!selectedFile || isProcessing}
            className="btn btn-primary"
            style={{ padding: '10px 22px', fontSize: '0.9rem', gap: '8px' }}
          >
            {isProcessing ? (
              <>
                <RefreshCw size={16} className="spin" />
                Processing Document (OCR & Entity Match)...
              </>
            ) : (
              <>
                <ShieldCheck size={16} />
                Extract Medications via OCR
              </>
            )}
          </button>
        </div>
      </div>

      {/* OCR EXTRACTION & CLINICIAN REVIEW SCREEN */}
      {extractionResult && (
        <div className="card" style={{ padding: '28px', border: '1px solid rgba(14, 165, 233, 0.3)' }}>
          {/* Header & Document Metadata */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff', margin: '0 0 6px' }}>
                Prescription Review & Medication Verification
              </h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                <span>File: <strong style={{ color: '#e2e8f0' }}>{extractionResult.filename}</strong></span>
                <span>Document Date: <strong style={{ color: '#38bdf8' }}>{extractionResult.document_date}</strong></span>
                <span>Candidate Items: <strong style={{ color: '#fff' }}>{reviewMedications.length}</strong></span>
              </div>
            </div>

            {/* Document Timeline Badge */}
            <div style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '6px 12px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '0.8rem',
              color: '#38bdf8'
            }}>
              <Calendar size={14} />
              <span>Timeline: {extractionResult.document_date}</span>
            </div>
          </div>

          {/* Raw OCR Text Preview (Collapsible) */}
          <details style={{ marginBottom: '20px', background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: 'var(--radius-md)', fontSize: '0.8rem' }}>
            <summary style={{ cursor: 'pointer', color: 'var(--text-muted)', fontWeight: 600 }}>
              View Extracted Raw Text / OCR Transcription
            </summary>
            <pre style={{ margin: '10px 0 0', whiteSpace: 'pre-wrap', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
              {extractionResult.raw_text}
            </pre>
          </details>

          {/* Review Table */}
          <div style={{ overflowX: 'auto', marginBottom: '24px' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-muted)', textAlign: 'left' }}>
                  <th style={{ padding: '10px', width: '40px' }}>Verify</th>
                  <th style={{ padding: '10px' }}>Extracted Line</th>
                  <th style={{ padding: '10px' }}>Matched Drug</th>
                  <th style={{ padding: '10px' }}>Dosage Strength</th>
                  <th style={{ padding: '10px' }}>Status</th>
                  <th style={{ padding: '10px' }}>OCR Confidence</th>
                  <th style={{ padding: '10px', textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {reviewMedications.length === 0 ? (
                  <tr>
                    <td colSpan="7" style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
                      No pharmaceutical entities recognized in this document.
                    </td>
                  </tr>
                ) : (
                  reviewMedications.map((item, idx) => (
                    <tr key={idx} style={{
                      borderBottom: '1px solid rgba(255,255,255,0.03)',
                      background: item.selected ? 'rgba(14, 165, 233, 0.03)' : 'transparent'
                    }}>
                      <td style={{ padding: '12px 10px', textAlign: 'center' }}>
                        <input
                          type="checkbox"
                          checked={item.selected}
                          onChange={() => handleToggleSelect(idx)}
                          style={{ cursor: 'pointer', width: '16px', height: '16px' }}
                        />
                      </td>
                      <td style={{ padding: '12px 10px', color: 'var(--text-secondary)', fontSize: '0.82rem', fontFamily: 'monospace' }}>
                        {item.original_text}
                      </td>
                      <td style={{ padding: '12px 10px' }}>
                        <input
                          type="text"
                          value={item.drug_name}
                          onChange={(e) => handleFieldChange(idx, 'drug_name', e.target.value)}
                          className="input-field"
                          style={{ padding: '4px 8px', fontSize: '0.85rem', width: '140px' }}
                        />
                      </td>
                      <td style={{ padding: '12px 10px' }}>
                        <input
                          type="text"
                          value={item.dose}
                          onChange={(e) => handleFieldChange(idx, 'dose', e.target.value)}
                          className="input-field"
                          style={{ padding: '4px 8px', fontSize: '0.85rem', width: '110px' }}
                        />
                      </td>
                      <td style={{ padding: '12px 10px' }}>
                        <span style={{
                          padding: '3px 8px',
                          borderRadius: '4px',
                          fontSize: '0.74rem',
                          fontWeight: 700,
                          background: item.match_status === 'Matched' ? 'rgba(74, 222, 128, 0.15)' :
                                      item.match_status === 'Corrected' ? 'rgba(56, 189, 248, 0.15)' :
                                      'rgba(245, 158, 11, 0.15)',
                          color: item.match_status === 'Matched' ? '#4ade80' :
                                 item.match_status === 'Corrected' ? '#38bdf8' :
                                 '#fbbf24'
                        }}>
                          {item.match_status === 'Matched' ? '✓ Matched' :
                           item.match_status === 'Corrected' ? '✓ Corrected' :
                           '⚠ Review Required'}
                        </span>
                      </td>
                      <td style={{ padding: '12px 10px', color: 'var(--text-muted)', fontSize: '0.82rem' }}>
                        {(item.confidence * 100).toFixed(0)}%
                      </td>
                      <td style={{ padding: '12px 10px', textAlign: 'right' }}>
                        <button
                          onClick={() => handleRemoveRow(idx)}
                          style={{ background: 'transparent', border: 'none', color: '#f87171', cursor: 'pointer' }}
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

          {/* Action Footer */}
          <div style={{
            borderTop: '1px solid var(--border-subtle)',
            paddingTop: '18px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px'
          }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Selected: <strong style={{ color: '#fff' }}>{reviewMedications.filter(m => m.selected).length}</strong> medication(s) will be added to patient <strong style={{ color: '#38bdf8' }}>{targetPatientId}</strong>.
            </span>

            <button
              onClick={handleConfirmAndTransfer}
              disabled={isConfirming || reviewMedications.filter(m => m.selected).length === 0}
              className="btn btn-primary"
              style={{ padding: '10px 22px', fontSize: '0.9rem', gap: '8px' }}
            >
              {isConfirming ? (
                <>
                  <RefreshCw size={16} className="spin" />
                  Saving to Patient Profile...
                </>
              ) : (
                <>
                  <CheckCircle2 size={16} />
                  Confirm & Transfer to Patient History
                </>
              )}
            </button>
          </div>

          {/* Success Banner */}
          {confirmedSuccess && (
            <div style={{
              marginTop: '20px',
              background: 'rgba(74, 222, 128, 0.1)',
              border: '1px solid rgba(74, 222, 128, 0.3)',
              borderRadius: 'var(--radius-md)',
              padding: '16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '12px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <CheckCircle2 size={20} style={{ color: '#4ade80' }} />
                <div>
                  <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#4ade80', fontWeight: 700 }}>
                    Medications Confirmed Successfully!
                  </h4>
                  <p style={{ margin: '2px 0 0', fontSize: '0.82rem', color: '#e2e8f0' }}>
                    {confirmedSuccess.message}
                  </p>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={() => setActivePage && setActivePage('patients')}
                  className="btn btn-outline"
                  style={{ fontSize: '0.82rem', padding: '6px 12px' }}
                >
                  View Patient History
                </button>
                <button
                  onClick={() => setActivePage && setActivePage('safety-report')}
                  className="btn btn-primary"
                  style={{ fontSize: '0.82rem', padding: '6px 14px' }}
                >
                  Run Full Safety Report
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
