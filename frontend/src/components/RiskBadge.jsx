import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react';

export default function RiskBadge({ severity, showIcon = true }) {
  const norm = (severity || 'minor').toLowerCase();

  if (norm === 'major') {
    return (
      <span className="badge badge-major">
        {showIcon && <AlertCircle size={13} />}
        Major Risk
      </span>
    );
  }

  if (norm === 'moderate') {
    return (
      <span className="badge badge-moderate">
        {showIcon && <AlertTriangle size={13} />}
        Moderate Risk
      </span>
    );
  }

  return (
    <span className="badge badge-minor">
      {showIcon && <CheckCircle2 size={13} />}
      Minor / Low Risk
    </span>
  );
}
