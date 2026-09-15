import React, { useState, useEffect } from 'react';
import { 
  BarChart2, 
  Activity, 
  AlertCircle, 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw,
  Clock,
  Pill,
  Users,
  FileText
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  BarChart, 
  Bar 
} from 'recharts';
import { api } from '../services/api';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = () => {
    setLoading(true);
    api.getDashboardStats()
      .then((data) => setStats(data))
      .catch((err) => console.error('Dashboard fetch error:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading && !stats) {
    return (
      <div className="container" style={{ paddingTop: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading live clinical analytics from database...
      </div>
    );
  }

  const severityData = [
    { name: 'Major', value: stats?.major_alerts || 0, color: '#ef4444' },
    { name: 'Moderate', value: stats?.moderate_alerts || 0, color: '#f59e0b' },
    { name: 'Minor', value: stats?.minor_alerts || 0, color: '#10b981' },
  ].filter(d => d.value > 0);

  const totalChecks = stats?.total_checks || 0;
  const interactionsDetected = stats?.interactions_detected || 0;
  const interactionRate = totalChecks > 0 ? Math.round((interactionsDetected / totalChecks) * 100) : 0;

  return (
    <div className="container" style={{ paddingTop: '32px', paddingBottom: '60px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '28px' }}>
        <div>
          <h1 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <BarChart2 size={28} color="var(--primary)" />
            Clinical Decision-Support Analytics
          </h1>
          <p className="section-subtitle" style={{ marginBottom: 0 }}>
            Live clinical database aggregates, severity distribution, and screening trends.
          </p>
        </div>

        <button onClick={fetchStats} className="btn btn-secondary" style={{ fontSize: '0.85rem' }}>
          <RefreshCw size={14} />
          Refresh Stats
        </button>
      </div>

      {/* KPI Cards Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px',
        marginBottom: '32px'
      }}>
        {/* Total Inquiries */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
              Total Interactions Screened
            </span>
            <Activity size={18} color="var(--primary)" />
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#fff', fontFamily: 'var(--font-mono)' }}>
            {totalChecks}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Cumulative database checks
          </div>
        </div>

        {/* Flagged Interactions */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
              Interactions Flagged
            </span>
            <AlertCircle size={18} color="#ef4444" />
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#f87171', fontFamily: 'var(--font-mono)' }}>
            {interactionsDetected}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            {interactionRate}% overall interaction rate
          </div>
        </div>

        {/* Major Severity */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
              Major Alerts
            </span>
            <span className="badge badge-major" style={{ padding: '2px 8px' }}>Severe</span>
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#fca5a5', fontFamily: 'var(--font-mono)' }}>
            {stats?.major_alerts || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Immediate clinician review required
          </div>
        </div>

        {/* Moderate Severity */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
              Moderate Alerts
            </span>
            <span className="badge badge-moderate" style={{ padding: '2px 8px' }}>Warning</span>
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#fcd34d', fontFamily: 'var(--font-mono)' }}>
            {stats?.moderate_alerts || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Monitoring and dosage adjustment
          </div>
        </div>

        {/* Patients Registered */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
              Patients Enrolled
            </span>
            <Users size={18} color="#38bdf8" />
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
            {stats?.total_patients || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Clinical history profiles
          </div>
        </div>

        {/* Active Meds Screened */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
              Medications Screened
            </span>
            <Pill size={18} color="#4ade80" />
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#4ade80', fontFamily: 'var(--font-mono)' }}>
            {stats?.total_medications_screened || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Prescriptions in active regimens
          </div>
        </div>

        {/* Documents Ingested */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
              Documents Processed
            </span>
            <FileText size={18} color="#c084fc" />
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#c084fc', fontFamily: 'var(--font-mono)' }}>
            {stats?.total_documents_processed || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Prescriptions parsed via OCR
          </div>
        </div>

        {/* Minor Severity */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>
              Minor / Low Risk
            </span>
            <span className="badge badge-minor" style={{ padding: '2px 8px' }}>Mild</span>
          </div>
          <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#6ee7b7', fontFamily: 'var(--font-mono)' }}>
            {stats?.minor_alerts || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Standard clinical care
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
        gap: '24px',
        marginBottom: '32px'
      }}>
        {/* Severity Distribution Donut */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', marginBottom: '4px' }}>
            Severity Tier Distribution
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
            Proportion of Major, Moderate, and Minor risk alerts recorded
          </p>

          {severityData.length === 0 ? (
            <div style={{ height: '260px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No alerts logged yet. Run interaction checks to populate charts.
            </div>
          ) : (
            <div style={{ height: '260px', position: 'relative' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={95}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: '#0f172a', borderColor: 'var(--border-subtle)', borderRadius: '8px', color: '#fff' }}
                  />
                </PieChart>
              </ResponsiveContainer>

              {/* Legend */}
              <div style={{ display: 'flex', justifyContent: 'center', gap: '18px', marginTop: '8px', fontSize: '0.82rem' }}>
                {severityData.map((d, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '10px', height: '10px', borderRadius: '50%', backgroundColor: d.color }}></span>
                    <span style={{ color: 'var(--text-secondary)' }}>{d.name}: <strong>{d.value}</strong></span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Screening Activity Timeline */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', marginBottom: '4px' }}>
            Recent Screening Activity
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
            Interaction checks executed over the last 7 days
          </p>

          <div style={{ height: '260px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats?.recent_activity || []}>
                <defs>
                  <linearGradient id="activityGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ background: '#0f172a', borderColor: 'var(--border-subtle)', borderRadius: '8px', color: '#fff' }}
                />
                <Area type="monotone" dataKey="checks" stroke="#0ea5e9" strokeWidth={2} fillOpacity={1} fill="url(#activityGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top Flagged Drugs Bar Chart */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#fff', marginBottom: '4px' }}>
          Most Frequently Flagged Medications
        </h3>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Active pharmaceutical agents most commonly appearing in moderate and severe interaction pairs
        </p>

        {(!stats?.top_flagged_drugs || stats.top_flagged_drugs.length === 0) ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            No flagged medications yet. Screen pairs in the Interaction Checker to record trends.
          </div>
        ) : (
          <div style={{ height: '220px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.top_flagged_drugs}>
                <XAxis dataKey="drug_name" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ background: '#0f172a', borderColor: 'var(--border-subtle)', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="count" fill="#38bdf8" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
