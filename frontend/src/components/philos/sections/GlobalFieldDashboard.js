import { useState, useEffect, useCallback } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };

export default function GlobalFieldDashboard() {
  const [data, setData] = useState(null);

  const fetchField = useCallback(() => {
    fetch(`${API_URL}/api/orientation/field-dashboard`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setData(d); })
      .catch(() => {});
  }, []);

  useEffect(() => { fetchField(); const i = setInterval(fetchField, 30000); return () => clearInterval(i); }, [fetchField]);

  if (!data) return null;
  const domColor = dirColors[data.dominant_direction] || '#6366f1';
  const narrative = data.field_narrative_he || '';
  const aiField = data.ai_field_interpretation || '';

  return (
    <div className="relative overflow-hidden rounded-2xl bg-[#0a0a1a] border border-gray-800/60 px-4 py-3" data-testid="global-field-dashboard">
      {/* Subtle ambient glow */}
      <div className="absolute inset-0 pointer-events-none" style={{ background: `radial-gradient(ellipse at 30% 50%, ${domColor}08 0%, transparent 70%)` }} />

      <div className="relative">
        <div className="flex items-center gap-2.5">
          {/* Living pulse dot */}
          <span className="relative flex-shrink-0">
            <span className="absolute inset-0 rounded-full animate-ping opacity-30" style={{ backgroundColor: domColor }} />
            <span className="relative block w-2 h-2 rounded-full" style={{ backgroundColor: domColor }} />
          </span>

          {/* Narrative sentence */}
          <p className="text-sm text-gray-300 font-medium leading-snug" data-testid="field-narrative">
            {narrative}
          </p>
        </div>

        {/* AI field interpretation */}
        {aiField && (
          <p className="text-[10px] text-gray-500 italic leading-relaxed mt-1.5 mr-[18px]" data-testid="ai-field-interpretation">
            {aiField}
          </p>
        )}
      </div>
    </div>
  );
}
