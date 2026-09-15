import React from 'react';
import { AlertTriangle, ShieldCheck, FileCheck, Stethoscope, AlertOctagon } from 'lucide-react';

export default function DisclaimerPage() {
  return (
    <div className="container" style={{ paddingTop: '32px', paddingBottom: '60px' }}>
      <div style={{ maxWidth: '840px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            padding: '6px 14px',
            borderRadius: '9999px',
            color: '#f87171',
            fontSize: '0.82rem',
            fontWeight: 700,
            marginBottom: '16px'
          }}>
            <AlertOctagon size={14} />
            <span>MANDATORY CLINICAL SAFETY NOTICE</span>
          </div>

          <h1 className="section-title">
            Clinical Safety &amp; Legal Disclaimer
          </h1>
          <p className="section-subtitle">
            Ethical, legal, and operational boundaries governing the Drug Interaction Alert System (DIAS).
          </p>
        </div>

        {/* Primary Disclaimer Card */}
        <div className="glass-panel" style={{ padding: '32px', marginBottom: '28px', borderLeft: '4px solid #f59e0b' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertTriangle size={22} color="#f59e0b" />
            Decision-Support Boundaries (Not a Prescribing System)
          </h2>
          <p style={{ color: 'var(--text-primary)', fontSize: '0.95rem', lineHeight: 1.7, marginBottom: '16px' }}>
            <strong>This application is a research and educational clinical decision-support prototype. It is not a substitute 
            for professional medical advice, diagnosis, or prescribing. Predictions and alerts should be independently verified 
            by a qualified healthcare professional.</strong>
          </p>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.6 }}>
            DIAS is engineered to augment clinical vigilance by rapidly cross-referencing chemical structures and machine learning 
            predictions. It does not replace the comprehensive clinical reasoning of licensed physicians, clinical pharmacologists, 
            or registered pharmacists.
          </p>
        </div>

        {/* Core Principles */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '32px' }}>
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(14, 165, 233, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '14px', color: 'var(--primary)' }}>
              <Stethoscope size={20} />
            </div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '8px' }}>
              Qualified Clinician Review
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.5 }}>
              Patient-specific variables including renal clearance (eGFR), hepatic function (Child-Pugh), genetic polymorphisms, 
              age, pregnancy, and polypharmacy must be evaluated by a healthcare professional.
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(245, 158, 11, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '14px', color: '#f59e0b' }}>
              <FileCheck size={20} />
            </div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '8px' }}>
              Alternative Medication Policy
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.5 }}>
              Suggested alternatives are displayed exclusively for clinician consideration when supported by scientific literature. 
              They are not automated substitutions or medical prescriptions.
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '14px', color: '#10b981' }}>
              <ShieldCheck size={20} />
            </div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '8px' }}>
              Regulatory Status
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: 1.5 }}>
              This system is an academic research engineering project. It has not been evaluated or certified as a medical device 
              by the US FDA, EMA, or CDSCO.
            </p>
          </div>
        </div>

        {/* Emergency Medical Guidance */}
        <div style={{
          background: 'rgba(239, 68, 68, 0.08)',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          borderRadius: 'var(--radius-md)',
          padding: '24px',
          color: '#fca5a5',
          fontSize: '0.88rem',
          lineHeight: 1.6
        }}>
          <h4 style={{ color: '#fff', fontSize: '1rem', fontWeight: 700, marginBottom: '8px' }}>
            Emergency Medical Situations
          </h4>
          If you are a patient experiencing adverse symptoms, severe bleeding, chest pain, irregular heartbeat, difficulty breathing, 
          or suspect an acute drug interaction overdose, seek immediate emergency medical care (dial emergency services or go to the nearest hospital emergency room). 
          Do not alter or discontinue any prescribed therapy without consulting your doctor.
        </div>
      </div>
    </div>
  );
}
