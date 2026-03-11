import { useState, useEffect } from 'react';
import { Sunrise, Compass, ArrowLeft } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionColors = {
  contribution: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200', accent: '#22c55e' },
  recovery: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', accent: '#3b82f6' },
  order: { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200', accent: '#6366f1' },
  exploration: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', accent: '#f59e0b' }
};

export default function DailyOpeningSection({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [animateCompass, setAnimateCompass] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    const fetchData = async () => {
      if (!effectiveUserId) { setLoading(false); return; }
      try {
        const res = await fetch(`${API_URL}/api/orientation/daily-opening/${effectiveUserId}`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) {
            setData(json);
            setTimeout(() => setAnimateCompass(true), 300);
          }
        }
      } catch (e) {
        console.log('Could not fetch daily opening:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [effectiveUserId]);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse" dir="rtl">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-20 bg-gray-200 rounded"></div>
      </section>
    );
  }

  if (!data) return null;

  const suggested = data.suggested_direction;
  const colors = directionColors[suggested] || directionColors.contribution;
  const compassDirs = ['contribution', 'recovery', 'order', 'exploration'];

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-1" dir="rtl" data-testid="daily-opening-section">
      {/* Header with greeting */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-xl bg-orange-50 flex items-center justify-center">
            <Sunrise className="w-5 h-5 text-orange-500" />
          </div>
          <div>
            <span className="text-sm font-semibold text-gray-800">{data.greeting_he}</span>
            <p className="text-[10px] text-gray-400">פתיחת יום</p>
          </div>
        </div>
        {data.total_actions > 0 && (
          <span className="text-xs text-gray-400">{data.total_actions} פעולות</span>
        )}
      </div>

      {/* Compass State - circular visualization */}
      <div className="flex items-center justify-center mb-4">
        <div className="relative w-36 h-36">
          {/* Center circle */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-14 h-14 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center">
              <Compass className="w-6 h-6 text-gray-500" />
            </div>
          </div>
          {/* 4 direction arcs */}
          {compassDirs.map((dir, i) => {
            const pct = data.compass_state[dir] || 0;
            const angle = i * 90 - 45;
            const rad = (angle * Math.PI) / 180;
            const radius = 52;
            const x = 72 + Math.cos(rad) * radius - 16;
            const y = 72 + Math.sin(rad) * radius - 16;
            const dc = directionColors[dir];
            return (
              <div
                key={dir}
                className={`absolute w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold transition-all duration-700 ease-out ${dc.bg} ${dc.text}`}
                style={{
                  left: x, top: y,
                  transform: animateCompass ? 'scale(1)' : 'scale(0)',
                  transitionDelay: `${i * 100}ms`,
                  boxShadow: dir === suggested ? `0 0 12px ${dc.accent}40` : 'none',
                  border: dir === suggested ? `2px solid ${dc.accent}` : '1px solid transparent'
                }}
                data-testid={`compass-dir-${dir}`}
              >
                {pct}%
              </div>
            );
          })}
        </div>
      </div>

      {/* Dominant force */}
      {data.dominant_force_he && (
        <div className="text-center mb-3">
          <span className="text-[10px] text-gray-400">הכוח הדומיננטי שלך</span>
          <p className="text-sm font-semibold text-gray-700">{data.dominant_force_he}</p>
        </div>
      )}

      {/* Suggested direction */}
      <div className={`rounded-2xl p-3 ${colors.bg} ${colors.border} border`} data-testid="daily-opening-suggestion">
        <div className="flex items-center gap-2 mb-1">
          <ArrowLeft className={`w-4 h-4 ${colors.text}`} />
          <span className={`text-sm font-semibold ${colors.text}`}>
            הכיוון המוצע להיום: {data.suggested_direction_he}
          </span>
        </div>
        {data.theory?.explanation_he && (
          <p className="text-xs text-gray-600 leading-relaxed">{data.theory.explanation_he}</p>
        )}
      </div>
    </section>
  );
}
