import React, { useState, useEffect } from 'react';
import { 
  History, 
  Search, 
  Filter, 
  Trash2, 
  Eye, 
  AlertCircle, 
  CheckCircle2, 
  Calendar,
  X,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import RiskBadge from '../components/RiskBadge';

export default function HistoryPage() {
  const [alerts, setAlerts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAlert, setSelectedAlert] = useState(null);

  const fetchHistory = () => {
    setLoading(true);
    api.getAlerts(severityFilter, searchTerm)
      .then((data) => {
        setAlerts(data.alerts || []);
        setTotal(data.total || 0);
      })
      .catch((err) => {
        console.error('Failed to load alert history:', err);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHistory();
  }, [severityFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchHistory();
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this alert audit record?')) return;

    try {
      await api.deleteAlert(id);
      fetchHistory();
      if (selectedAlert && selectedAlert.id === id) {
        setSelectedAlert(null);
      }
    } catch (err) {
      alert('Failed to delete alert: ' + err.message);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      const d = new Date(dateStr);
      return d.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="container" style={{ paddingTop: '32px', paddingBottom: '60px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '28px' }}>
        <div>
          <h1 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <History size={28} color="var(--primary)" />
            Alert Audit History
          </h1>
          <p className="section-subtitle" style={{ marginBottom: 0 }}>
            Audit trail of evaluated medication pairs, predictive risk probabilities, and clinical alerts.
          </p>
        </div>

        <button onClick={fetchHistory} className="btn btn-secondary" style={{ fontSize: '0.85rem' }}>
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      {/* Filter and Search Toolbar */}
      <div className="glass-panel" style={{ padding: '18px 24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          {/* Severity Tabs */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600 }}>Severity:</span>
            {['All', 'Major', 'Moderate', 'Minor'].map((sev) => (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                style={{
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: severityFilter === sev ? '1px solid var(--primary)' : '1px solid var(--border-subtle)',
                  background: severityFilter === sev ? 'rgba(14, 165, 233, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                  color: severityFilter === sev ? '#38bdf8' : 'var(--text-secondary)',
                  transition: 'all 0.15s ease'
                }}
              >
                {sev}
              </button>
            ))}
          </div>

          {/* Search Form */}
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: '280px' }}>
            <div style={{ position: 'relative', width: '100%' }}>
              <input
                type="text"
                placeholder="Filter by drug name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field"
                style={{ paddingLeft: '34px', paddingRight: '12px', fontSize: '0.85rem' }}
              />
              <Search size={14} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '14px' }} />
            </div>
            <button type="submit" className="btn btn-secondary" style={{ padding: '10px 16px', fontSize: '0.85rem' }}>
              Filter
            </button>
          </form>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading alert audit records...
          </div>
        ) : alerts.length === 0 ? (
          <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No interaction alerts recorded matching current criteria.
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
            <thead>
              <tr style={{ background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-subtle)' }}>
                <th style={{ padding: '14px 20px', color: 'var(--text-muted)', fontWeight: 700 }}>TIMESTAMP</th>
                <th style={{ padding: '14px 20px', color: 'var(--text-muted)', fontWeight: 700 }}>MEDICATION PAIR</th>
                <th style={{ padding: '14px 20px', color: 'var(--text-muted)', fontWeight: 700 }}>SEVERITY</th>
                <th style={{ padding: '14px 20px', color: 'var(--text-muted)', fontWeight: 700 }}>RISK PROBABILITY</th>
                <th style={{ padding: '14px 20px', color: 'var(--text-muted)', fontWeight: 700 }}>DECISION ORIGIN</th>
                <th style={{ padding: '14px 20px', color: 'var(--text-muted)', fontWeight: 700, textAlign: 'right' }}>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert) => (
                <tr
                  key={alert.id}
                  onClick={() => setSelectedAlert(alert)}
                  style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    cursor: 'pointer',
                    transition: 'background 0.15s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '14px 20px', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', fontSize: '0.78rem' }}>
                    {formatDate(alert.created_at)}
                  </td>
                  <td style={{ padding: '14px 20px', fontWeight: 600, color: '#fff' }}>
                    {alert.drug_a} + {alert.drug_b}
                  </td>
                  <td style={{ padding: '14px 20px' }}>
                    <RiskBadge severity={alert.severity} />
                  </td>
                  <td style={{ padding: '14px 20px', fontFamily: 'var(--font-mono)', color: alert.risk_probability >= 0.7 ? '#f87171' : '#38bdf8' }}>
                    {Math.round(alert.risk_probability * 100)}% ({alert.risk_probability})
                  </td>
                  <td style={{ padding: '14px 20px', color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
                    {alert.source}
                  </td>
                  <td style={{ padding: '14px 20px', textAlign: 'right' }}>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedAlert(alert);
                        }}
                        className="btn btn-secondary"
                        style={{ padding: '6px 10px', fontSize: '0.75rem' }}
                      >
                        <Eye size={13} />
                        View
                      </button>
                      <button
                        onClick={(e) => handleDelete(alert.id, e)}
                        className="btn btn-outline-danger"
                        style={{ padding: '6px 10px', fontSize: '0.75rem' }}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Alert Details Modal */}
      {selectedAlert && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
          padding: '20px'
        }}>
          <div className="glass-panel" style={{
            maxWidth: '680px',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '32px',
            background: '#0f172a',
            border: '1px solid rgba(255, 255, 255, 0.15)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#fff' }}>
                  {selectedAlert.drug_a} + {selectedAlert.drug_b}
                </h3>
                <RiskBadge severity={selectedAlert.severity} />
              </div>
              <button
                onClick={() => setSelectedAlert(null)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
              >
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', fontSize: '0.88rem' }}>
              <div>
                <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Risk Probability: </span>
                <span style={{ color: '#38bdf8', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                  {Math.round(selectedAlert.risk_probability * 100)}% ({selectedAlert.risk_probability})
                </span>
              </div>

              <div>
                <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Pharmacological Mechanism: </span>
                <div style={{ color: 'var(--text-primary)', marginTop: '4px', lineHeight: 1.5 }}>
                  {selectedAlert.mechanism}
                </div>
              </div>

              <div>
                <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Clinical Risk Narrative: </span>
                <div style={{ color: 'var(--text-primary)', marginTop: '4px', lineHeight: 1.5 }}>
                  {selectedAlert.clinical_effect}
                </div>
              </div>

              <div>
                <span style={{ color: 'var(--text-muted)', fontWeight: 600 }}>Recommendation: </span>
                <div style={{ color: 'var(--text-primary)', marginTop: '4px', lineHeight: 1.5 }}>
                  {selectedAlert.recommendation}
                </div>
              </div>

              {selectedAlert.safer_alternative && (
                <div style={{ background: 'rgba(14, 165, 233, 0.08)', padding: '12px 16px', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(14, 165, 233, 0.2)' }}>
                  <span style={{ color: '#38bdf8', fontWeight: 700 }}>Clinician-Only Alternative Options: </span>
                  <div style={{ color: '#fff', marginTop: '4px' }}>
                    {selectedAlert.safer_alternative}
                  </div>
                </div>
              )}

              <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '14px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Recorded: {formatDate(selectedAlert.created_at)} • Source: {selectedAlert.source}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
