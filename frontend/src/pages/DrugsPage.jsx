import React, { useState, useEffect } from 'react';
import { Activity, Search, ExternalLink, Copy, Check, Filter } from 'lucide-react';
import { api } from '../services/api';

export default function DrugsPage() {
  const [drugs, setDrugs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDrug, setSelectedDrug] = useState(null);
  const [copiedSmiles, setCopiedSmiles] = useState(null);

  useEffect(() => {
    setLoading(true);
    api.getAllDrugs(0, 100)
      .then((data) => setDrugs(data))
      .catch((err) => console.error('Failed to load drug catalog:', err))
      .finally(() => setLoading(false));
  }, []);

  const filteredDrugs = drugs.filter((d) => {
    const q = searchTerm.toLowerCase();
    return (
      d.name.toLowerCase().includes(q) ||
      (d.brand_names && d.brand_names.toLowerCase().includes(q)) ||
      (d.category && d.category.toLowerCase().includes(q)) ||
      (d.atc_code && d.atc_code.toLowerCase().includes(q))
    );
  });

  const handleCopySmiles = (smiles, id, e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(smiles);
    setCopiedSmiles(id);
    setTimeout(() => setCopiedSmiles(null), 2000);
  };

  return (
    <div className="container" style={{ paddingTop: '32px', paddingBottom: '60px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '28px' }}>
        <div>
          <h1 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Activity size={28} color="var(--primary)" />
            Pharmaceutical Chemical Catalog
          </h1>
          <p className="section-subtitle" style={{ marginBottom: 0 }}>
            Curated catalog of {drugs.length} clinically essential drugs with authentic canonical SMILES and RDKit descriptors.
          </p>
        </div>

        {/* Search Bar */}
        <div style={{ position: 'relative', minWidth: '300px' }}>
          <input
            type="text"
            placeholder="Search by drug name, brand, or class..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field"
            style={{ paddingLeft: '38px', fontSize: '0.88rem' }}
          />
          <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '14px' }} />
        </div>
      </div>

      {/* Grid of Drugs */}
      {loading ? (
        <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading chemical catalog and molecular properties...
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
          gap: '20px'
        }}>
          {filteredDrugs.map((drug) => (
            <div
              key={drug.id}
              className="glass-panel"
              style={{
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                cursor: 'pointer'
              }}
              onClick={() => setSelectedDrug(drug)}
            >
              <div>
                {/* Header Row */}
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <div>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>
                      {drug.name}
                    </h3>
                    <div style={{ fontSize: '0.78rem', color: 'var(--primary)', fontWeight: 600, marginTop: '2px' }}>
                      {drug.category}
                    </div>
                  </div>
                  {drug.atc_code && (
                    <span className="badge badge-neutral" style={{ fontFamily: 'var(--font-mono)' }}>
                      {drug.atc_code}
                    </span>
                  )}
                </div>

                {drug.brand_names && (
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
                    Brands: {drug.brand_names}
                  </div>
                )}

                {/* Chemical Descriptors Pills */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: '8px',
                  background: 'rgba(255, 255, 255, 0.02)',
                  padding: '12px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-subtle)',
                  marginBottom: '14px',
                  textAlign: 'center',
                  fontSize: '0.78rem'
                }}>
                  <div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>MOL WT</div>
                    <div style={{ color: '#fff', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{drug.molecular_weight}</div>
                  </div>
                  <div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>LogP</div>
                    <div style={{ color: '#fff', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{drug.logp}</div>
                  </div>
                  <div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>TPSA</div>
                    <div style={{ color: '#fff', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{drug.tpsa} Å²</div>
                  </div>
                </div>

                {/* Canonical SMILES Display */}
                <div style={{
                  background: 'rgba(15, 23, 42, 0.8)',
                  padding: '10px 12px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '8px',
                  fontSize: '0.72rem',
                  fontFamily: 'var(--font-mono)',
                  color: 'var(--text-secondary)'
                }}>
                  <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {drug.smiles}
                  </div>
                  <button
                    onClick={(e) => handleCopySmiles(drug.smiles, drug.id, e)}
                    title="Copy SMILES"
                    style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', flexShrink: 0 }}
                  >
                    {copiedSmiles === drug.id ? <Check size={14} color="#4ade80" /> : <Copy size={14} />}
                  </button>
                </div>
              </div>

              {/* Risk Flags Indicator */}
              <div style={{
                display: 'flex',
                gap: '6px',
                flexWrap: 'wrap',
                marginTop: '16px',
                paddingTop: '12px',
                borderTop: '1px solid var(--border-subtle)',
                fontSize: '0.72rem'
              }}>
                {drug.cyp_inhibitor === 1 && <span className="badge badge-major" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>CYP Inh</span>}
                {drug.cyp_substrate === 1 && <span className="badge badge-moderate" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>CYP Sub</span>}
                {drug.qt_prolonging === 1 && <span className="badge badge-major" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>QT Risk</span>}
                {drug.bleeding_risk === 1 && <span className="badge badge-major" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>Bleed Risk</span>}
                {drug.serotonergic === 1 && <span className="badge badge-moderate" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>5-HT</span>}
                {drug.renal_risk === 1 && <span className="badge badge-neutral" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>Renal</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
