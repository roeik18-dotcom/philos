import { useState, useEffect } from 'react';
import { Compass, ArrowLeft, Lightbulb, Flame } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };
const dirLabels = { contribution: 'תרומה', recovery: 'התאוששות', order: 'סדר', exploration: 'חקירה' };

export default function CompassAISection({ userId }) {
  const [data, setData] = useState(null);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    if (!effectiveUserId) return;
    fetch(`${API_URL}/api/orientation/compass-ai/${effectiveUserId}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setData(d); })
      .catch(() => {});
  }, [effectiveUserId]);

  if (!data) return null;

  const domColor = dirColors[data.dominant_direction] || '#6366f1';
  const weakColor = dirColors[data.weak_direction] || '#9ca3af';

  return (
    <section className="philos-section bg-white border-border" dir="rtl" data-testid="compass-ai-section">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-xl bg-cyan-50 flex items-center justify-center">
          <Compass className="w-5 h-5 text-cyan-600" />
        </div>
        <div>
          <span className="text-sm font-semibold text-gray-800">המצפן שלך</span>
          {data.niche_he && <p className="text-[10px] text-gray-400">{data.niche_he}</p>}
        </div>
        {data.streak > 0 && (
          <div className="mr-auto flex items-center gap-1 text-[10px] text-orange-500">
            <Flame className="w-3 h-3" />
            <span>{data.streak}</span>
          </div>
        )}
      </div>

      {data.dominant_direction ? (
        <>
          {/* Direction compass visual */}
          <div className="flex gap-3 mb-4">
            <div className="flex-1 rounded-xl p-3 text-center" style={{ backgroundColor: `${domColor}08`, border: `1px solid ${domColor}20` }}>
              <ArrowLeft className="w-4 h-4 mx-auto mb-1" style={{ color: domColor }} />
              <p className="text-xs font-bold" style={{ color: domColor }}>{data.dominant_direction_he}</p>
              <p className="text-[9px] text-gray-400">כיוון דומיננטי</p>
            </div>
            <div className="flex-1 rounded-xl p-3 text-center" style={{ backgroundColor: `${weakColor}08`, border: `1px solid ${weakColor}20` }}>
              <ArrowLeft className="w-4 h-4 mx-auto mb-1 rotate-180" style={{ color: weakColor }} />
              <p className="text-xs font-bold" style={{ color: weakColor }}>{data.weak_direction_he}</p>
              <p className="text-[9px] text-gray-400">כיוון חלש</p>
            </div>
          </div>

          {/* Balance */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] text-gray-400">איזון כיוונים</span>
              <span className="text-[10px] font-medium text-gray-600">{data.balance_score}%</span>
            </div>
            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden flex">
              {Object.entries(data.dir_percentages || {}).map(([d, pct]) => (
                <div key={d} className="h-full" style={{ width: `${pct}%`, backgroundColor: dirColors[d] }} />
              ))}
            </div>
          </div>

          {/* Suggestion */}
          <div className="bg-cyan-50 rounded-xl p-3 border border-cyan-100" data-testid="compass-ai-suggestion">
            <div className="flex items-center gap-1.5 mb-1">
              <Lightbulb className="w-3.5 h-3.5 text-cyan-600" />
              <span className="text-[10px] font-semibold text-cyan-700">פעולה מוצעת</span>
            </div>
            <p className="text-xs text-cyan-800 leading-relaxed">{data.suggestion_he}</p>
          </div>
        </>
      ) : (
        <div className="text-center py-4">
          <p className="text-sm text-gray-500">{data.suggestion_he}</p>
        </div>
      )}
    </section>
  );
}
