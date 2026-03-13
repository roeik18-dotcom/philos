import { useState, useEffect } from 'react';
import { Shield, ArrowUpRight } from 'lucide-react';
import { track } from '../../../utils/track';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function TrustChangeCard({ userId }) {
  const [trust, setTrust] = useState(null);

  useEffect(() => {
    if (!userId) return;
    fetch(`${API_URL}/api/user/${userId}/trust`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) { setTrust(d); track('trust_shown', userId, { score: d.trust_score }); } })
      .catch(() => {});
  }, [userId]);

  if (!trust) return null;

  const score = trust.trust_score ?? 0;
  const stateLabel = score > 20 ? 'יציב' : score > 5 ? 'בנייה' : score > 0 ? 'ראשוני' : 'התחלה';
  const stateColor = score > 20 ? '#22c55e' : score > 5 ? '#3b82f6' : score > 0 ? '#f59e0b' : '#94a3b8';

  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-3.5 flex items-center gap-3" dir="rtl" data-testid="trust-change-card">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${stateColor}12` }}>
        <Shield className="w-5 h-5" style={{ color: stateColor }} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-bold" style={{ color: stateColor }}>{score.toFixed(1)}</span>
          <span className="text-[10px] text-gray-400">אמון שדה</span>
          <ArrowUpRight className="w-3 h-3 text-green-500" />
        </div>
        <p className="text-[10px] text-gray-400">מצב: <span className="font-medium" style={{ color: stateColor }}>{stateLabel}</span></p>
      </div>
      <a href={`/profile/${userId}`} className="text-[10px] text-gray-300 hover:text-indigo-500 transition-colors" data-testid="trust-profile-link">
        צפה בפרופיל
      </a>
    </div>
  );
}
