import React, { useEffect, useState } from 'react';
import { ShieldCheck, Activity, Pill, History, BarChart2, Info, AlertTriangle, Users, FileText, FileCheck2 } from 'lucide-react';
import { api } from '../services/api';

export default function Navbar({ activePage, setActivePage }) {
  const [isBackendHealthy, setIsBackendHealthy] = useState(false);

  useEffect(() => {
    api.getHealth()
      .then(() => setIsBackendHealthy(true))
      .catch(() => setIsBackendHealthy(false));
  }, []);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart2 },
    { id: 'checker', label: 'Pair Checker', icon: Pill },
    { id: 'patients', label: 'Patient History', icon: Users },
    { id: 'prescriptions', label: 'Prescription OCR', icon: FileText },
    { id: 'safety-report', label: 'Safety Report', icon: FileCheck2 },
    { id: 'history', label: 'Alert History', icon: History },
    { id: 'drugs', label: 'Drug Catalog', icon: Activity },
    { id: 'about', label: 'About', icon: Info },
    { id: 'disclaimer', label: 'Safety', icon: AlertTriangle },
  ];

  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      background: 'rgba(11, 15, 25, 0.85)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '70px'
      }}>
        {/* Brand */}
        <div
          onClick={() => setActivePage('landing')}
          style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
        >
          <div style={{
            background: 'linear-gradient(135deg, #0ea5e9, #14b8a6)',
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 2px 10px rgba(14, 165, 233, 0.4)'
          }}>
            <ShieldCheck size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: 800, fontSize: '1.25rem', letterSpacing: '-0.03em', color: '#fff' }}>
                DIAS
              </span>
              <span style={{
                fontSize: '0.65rem',
                background: 'rgba(14, 165, 233, 0.2)',
                color: '#38bdf8',
                padding: '2px 6px',
                borderRadius: '4px',
                fontWeight: 700,
                border: '1px solid rgba(14, 165, 233, 0.3)'
              }}>
                ML-CDSS
              </span>
            </div>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0 }}>
              Drug Interaction Alert System
            </p>
          </div>
        </div>

        {/* Nav Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-md)',
                  background: isActive ? 'rgba(14, 165, 233, 0.15)' : 'transparent',
                  color: isActive ? '#38bdf8' : 'var(--text-secondary)',
                  border: isActive ? '1px solid rgba(14, 165, 233, 0.3)' : '1px solid transparent',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '0.85rem',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                <Icon size={16} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Status indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.78rem',
            color: isBackendHealthy ? '#4ade80' : '#f87171',
            background: isBackendHealthy ? 'rgba(74, 222, 128, 0.1)' : 'rgba(239, 68, 68, 0.1)',
            padding: '5px 10px',
            borderRadius: '9999px',
            border: isBackendHealthy ? '1px solid rgba(74, 222, 128, 0.25)' : '1px solid rgba(239, 68, 68, 0.25)'
          }}>
            <span style={{
              width: '7px',
              height: '7px',
              borderRadius: '50%',
              backgroundColor: isBackendHealthy ? '#4ade80' : '#f87171',
              boxShadow: isBackendHealthy ? '0 0 8px #4ade80' : 'none'
            }}></span>
            <span>{isBackendHealthy ? 'ML Service Active' : 'Connecting API...'}</span>
          </div>

          <button
            onClick={() => setActivePage('checker')}
            className="btn btn-primary"
            style={{ padding: '8px 16px', fontSize: '0.85rem' }}
          >
            <Pill size={16} />
            Check Pair
          </button>
        </div>
      </div>
    </header>
  );
}
