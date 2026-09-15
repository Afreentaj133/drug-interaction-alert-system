import React from 'react';
import { 
  Shield, 
  Pill, 
  Cpu, 
  Activity, 
  CheckCircle2, 
  ArrowRight, 
  FileText, 
  Database, 
  Compass,
  AlertTriangle 
} from 'lucide-react';

export default function LandingPage({ setActivePage }) {
  const steps = [
    { num: '01', title: 'Enter Drug Pair', desc: 'Select or search any two therapeutic medications using autocomplete.' },
    { num: '02', title: 'Molecular Extraction', desc: 'RDKit processes canonical SMILES, generating 1024-bit Morgan fingerprints (ECFP4).' },
    { num: '03', title: 'ML Risk Inference', desc: 'Trained ensemble evaluates Tanimoto similarity and metabolic pathway overlaps.' },
    { num: '04', title: 'Severity Assessment', desc: 'Categorizes risk level into Minor, Moderate, or Major clinical alert thresholds.' },
    { num: '05', title: 'SHAP Explainability', desc: 'TreeExplainer details exact local feature weights that triggered the alert.' },
    { num: '06', title: 'Clinical Review', desc: 'Displays evidence-based risk narratives and clinician-only alternative considerations.' }
  ];

  const features = [
    {
      icon: Cpu,
      title: 'Machine Learning Framework',
      desc: 'Combines structural molecular representations, Tanimoto similarity, and pharmacokinetic enzyme competition to screen drug-drug pairs.'
    },
    {
      icon: Compass,
      title: 'SHAP Explainable AI',
      desc: 'Eliminates black-box opacity by quantifying the positive or negative contribution of each chemical and metabolic attribute.'
    },
    {
      icon: Activity,
      title: 'Severity Triaging',
      desc: 'Stratifies interactions into Major, Moderate, and Minor severity tiers with pharmacological mechanisms and clinical risk descriptions.'
    },
    {
      icon: Database,
      title: 'Validated Chemical Catalog',
      desc: 'Includes verified canonical SMILES, PubChem CIDs, exact molecular weights, LogP, and TPSA from authentic cheminformatics sources.'
    },
    {
      icon: Shield,
      title: 'Evidence-Based Alternatives',
      desc: 'Presents verified potential alternatives strictly for clinician review; avoids automated prescribing substitutions.'
    },
    {
      icon: FileText,
      title: 'Audit Trail & Analytics',
      desc: 'Maintains comprehensive alert histories and real-time database dashboard statistics on interaction prevalence.'
    }
  ];

  return (
    <div className="container" style={{ paddingTop: '40px' }}>
      {/* Hero Section */}
      <section style={{ textAlign: 'center', maxWidth: '840px', margin: '0 auto 60px auto' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(14, 165, 233, 0.12)',
          border: '1px solid rgba(14, 165, 233, 0.3)',
          padding: '6px 14px',
          borderRadius: '9999px',
          color: '#38bdf8',
          fontSize: '0.82rem',
          fontWeight: 700,
          marginBottom: '20px'
        }}>
          <Shield size={14} />
          <span>RESEARCH &amp; CLINICAL DECISION-SUPPORT PROTOTYPE</span>
        </div>

        <h1 style={{
          fontSize: '3.2rem',
          fontWeight: 800,
          lineHeight: 1.15,
          letterSpacing: '-0.03em',
          color: '#ffffff',
          marginBottom: '18px'
        }}>
          Drug Interaction <br />
          <span style={{
            background: 'linear-gradient(135deg, #38bdf8, #14b8a6)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            Alert System
          </span>
        </h1>

        <p style={{
          fontSize: '1.25rem',
          color: 'var(--text-secondary)',
          lineHeight: 1.6,
          marginBottom: '32px'
        }}>
          Machine Learning-Based Clinical Decision Support for Drug-Drug Interaction Review
        </p>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <button
            onClick={() => setActivePage('checker')}
            className="btn btn-primary"
            style={{ padding: '14px 28px', fontSize: '1.05rem' }}
          >
            <Pill size={20} />
            Launch Interaction Checker
            <ArrowRight size={18} />
          </button>

          <button
            onClick={() => setActivePage('about')}
            className="btn btn-secondary"
            style={{ padding: '14px 24px', fontSize: '1rem' }}
          >
            <FileText size={18} />
            System Architecture
          </button>
        </div>

        {/* Disclaimer Banner */}
        <div className="disclaimer-banner" style={{ marginTop: '36px', textAlign: 'left' }}>
          <AlertTriangle size={20} color="#f59e0b" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Educational Decision-Support Prototype:</strong> This software is designed to assist doctors and pharmacists 
            during medication review. It is not an autonomous prescribing system and does not claim medical device certification. 
            All alerts must be independently verified by a qualified healthcare professional.
          </div>
        </div>
      </section>

      {/* How it Works Workflow */}
      <section style={{ marginBottom: '80px' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 className="section-title">How It Works</h2>
          <p className="section-subtitle">
            An explainable 6-stage clinical decision-support pipeline from molecular structure to clinical review
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
          gap: '16px'
        }}>
          {steps.map((s, idx) => (
            <div key={idx} className="glass-panel" style={{ padding: '22px 18px', position: 'relative' }}>
              <div style={{
                color: 'var(--primary)',
                fontFamily: 'var(--font-mono)',
                fontSize: '1.4rem',
                fontWeight: 800,
                marginBottom: '10px'
              }}>
                {s.num}
              </div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '8px' }}>
                {s.title}
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {s.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Key Features Grid */}
      <section style={{ marginBottom: '80px' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 className="section-title">System Capabilities</h2>
          <p className="section-subtitle">
            Built specifically for clinical safety, cheminformatics accuracy, and model explainability
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '24px'
        }}>
          {features.map((f, idx) => {
            const Icon = f.icon;
            return (
              <div key={idx} className="glass-panel" style={{ padding: '28px' }}>
                <div style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '12px',
                  background: 'rgba(14, 165, 233, 0.15)',
                  color: 'var(--primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '18px'
                }}>
                  <Icon size={24} />
                </div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', marginBottom: '10px' }}>
                  {f.title}
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>
                  {f.desc}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Technology Architecture Overview */}
      <section className="glass-panel" style={{ padding: '40px', marginBottom: '60px' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
          <h2 className="section-title">Technology Stack</h2>
          <p className="section-subtitle" style={{ marginBottom: '32px' }}>
            Built on production-proven scientific computing, ML, and web frameworks
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: '16px',
            textAlign: 'left'
          }}>
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700 }}>CHEMINFORMATICS</div>
              <div style={{ color: '#fff', fontWeight: 700, marginTop: '4px' }}>RDKit 2026</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', marginTop: '2px' }}>Morgan ECFP4, SMILES, Lipinski</div>
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700 }}>MACHINE LEARNING</div>
              <div style={{ color: '#fff', fontWeight: 700, marginTop: '4px' }}>Random Forest &amp; XGBoost</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', marginTop: '2px' }}>Scikit-learn, Multi-Model Comparison</div>
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700 }}>EXPLAINABLE AI</div>
              <div style={{ color: '#fff', fontWeight: 700, marginTop: '4px' }}>SHAP TreeExplainer</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', marginTop: '2px' }}>Local Feature Attribution</div>
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', fontWeight: 700 }}>BACKEND API</div>
              <div style={{ color: '#fff', fontWeight: 700, marginTop: '4px' }}>FastAPI + SQLAlchemy</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.78rem', marginTop: '2px' }}>Pydantic v2, RESTful, SQLite/Postgres</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
