import { useState, useEffect } from 'react';
import { UserPlus } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };

export default function HighlightedRecords() {
  const [records, setRecords] = useState([]);

  useEffect(() => {
    fetch(`${API_URL}/api/orientation/highlighted-records`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setRecords(d.records || []); })
      .catch(() => {});
  }, []);

  if (!records.length) return null;

  return (
    <section className="mb-2" data-testid="highlighted-records">
      <p className="text-[10px] text-gray-400 mb-2.5">People in the field</p>

      <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1 scrollbar-hide">
        {records.map((r) => {
          const dc = dirColors[r.dominant_direction] || '#6366f1';
          return (
            <button
              key={r.user_id}
              onClick={() => { window.location.href = `/profile/${r.user_id}`; }}
              className="flex-shrink-0 w-[130px] rounded-2xl bg-[#0a0a1a] border border-white/[0.04] p-3 text-right transition-all hover:border-white/[0.08] active:scale-[0.97]"
              data-testid={`record-card-${r.user_id}`}
            >
              <div className="flex items-center gap-2 mb-2.5">
                <span className="relative flex-shrink-0">
                  {r.present && (
                    <span className="absolute inset-0 rounded-lg animate-[pulse_4s_ease-in-out_infinite] opacity-[0.15]" style={{ backgroundColor: dc }} />
                  )}
                  <span
                    className="relative w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold"
                    style={{ backgroundColor: `${dc}15`, color: dc, border: `1px solid ${dc}25` }}
                  >
                    {r.alias?.charAt(0)}
                  </span>
                </span>
                <span className="text-xs text-white font-medium truncate">{r.alias}</span>
              </div>

              <div className="mb-2">
                <span
                  className="text-[9px] px-1.5 py-0.5 rounded-full font-medium"
                  style={{ backgroundColor: `${dc}12`, color: dc }}
                >
                  {r.dominant_direction_he}
                </span>
              </div>

              <div className="flex items-center gap-2.5">
                <div>
                  <p className="text-xs font-bold text-white tabular-nums">{r.impact_score}</p>
                  <p className="text-[8px] text-gray-600">Impact</p>
                </div>
                {r.invite_count > 0 && (
                  <div className="flex items-center gap-0.5">
                    <UserPlus className="w-2.5 h-2.5 text-gray-600" />
                    <span className="text-[9px] text-gray-500">{r.invite_count}</span>
                  </div>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
