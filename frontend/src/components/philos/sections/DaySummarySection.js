import { useState, useEffect } from 'react';
import { Moon, TrendingUp, Flame, Globe } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionColors = {
  contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b'
};
const directionLabels = {
  recovery: 'התאוששות', order: 'סדר', contribution: 'תרומה', exploration: 'חקירה'
};

export default function DaySummarySection({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [animateBars, setAnimateBars] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    const fetchData = async () => {
      if (!effectiveUserId) { setLoading(false); return; }
      try {
        const res = await fetch(`${API_URL}/api/orientation/day-summary/${effectiveUserId}`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) {
            setData(json);
            setTimeout(() => setAnimateBars(true), 200);
          }
        }
      } catch (e) {
        console.log('Could not fetch day summary:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [effectiveUserId]);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse" dir="rtl">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-20 bg-gray-200 rounded"></div>
      </section>
    );
  }

  if (!data) return null;

  const maxFieldVal = Math.max(...Object.values(data.global_field_effect || {}), 1);

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-5" dir="rtl" data-testid="day-summary-section">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-violet-50 flex items-center justify-center">
            <Moon className="w-5 h-5 text-violet-600" />
          </div>
          <div>
            <span className="text-sm font-semibold text-gray-800">סיכום סוף יום</span>
            <p className="text-[10px] text-gray-400">{data.date}</p>
          </div>
        </div>
      </div>

      {/* Reflection text */}
      <div className="bg-violet-50 rounded-2xl p-3 mb-4 border border-violet-100">
        <p className="text-sm text-violet-800 font-medium" data-testid="day-summary-reflection">{data.reflection_he}</p>
      </div>

      {data.total_actions > 0 && (
        <>
          {/* Stats row */}
          <div className="flex gap-2 mb-4">
            {/* Streak */}
            <div className="flex-1 bg-orange-50 rounded-xl p-2.5 text-center border border-orange-100" data-testid="day-summary-streak">
              <Flame className="w-4 h-4 text-orange-500 mx-auto mb-1" />
              <p className="text-lg font-bold text-orange-700">{data.streak}</p>
              <p className="text-[10px] text-orange-500">רצף ימים</p>
            </div>
            {/* Impact */}
            <div className="flex-1 bg-emerald-50 rounded-xl p-2.5 text-center border border-emerald-100" data-testid="day-summary-impact">
              <TrendingUp className="w-4 h-4 text-emerald-500 mx-auto mb-1" />
              <p className="text-lg font-bold text-emerald-700">{data.impact_on_field}%</p>
              <p className="text-[10px] text-emerald-500">השפעה על השדה</p>
            </div>
            {/* Actions */}
            <div className="flex-1 bg-blue-50 rounded-xl p-2.5 text-center border border-blue-100" data-testid="day-summary-actions">
              <Globe className="w-4 h-4 text-blue-500 mx-auto mb-1" />
              <p className="text-lg font-bold text-blue-700">{data.total_actions}</p>
              <p className="text-[10px] text-blue-500">פעולות היום</p>
            </div>
          </div>

          {/* Direction breakdown pills */}
          <div className="flex gap-1.5 mb-3 flex-wrap">
            {Object.entries(data.direction_counts).map(([d, c]) => c > 0 && (
              <span key={d} className="text-[10px] px-2 py-0.5 rounded-full font-medium"
                style={{ backgroundColor: `${directionColors[d]}15`, color: directionColors[d] }}>
                {directionLabels[d]} ({c})
              </span>
            ))}
          </div>

          {/* Global field effect bars */}
          <div>
            <p className="text-[10px] text-gray-400 mb-2 flex items-center gap-1">
              <Globe className="w-3 h-3" /> השפעה על השדה הגלובלי
            </p>
            <div className="space-y-1.5">
              {Object.entries(data.global_field_effect || {}).map(([dir, pct], i) => (
                <div key={dir} className="flex items-center gap-2">
                  <span className="text-[10px] text-gray-500 w-14">{directionLabels[dir]}</span>
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700 ease-out"
                      style={{
                        width: animateBars ? `${pct}%` : '0%',
                        backgroundColor: directionColors[dir],
                        transitionDelay: `${i * 80}ms`
                      }}
                    />
                  </div>
                  <span className="text-[10px] font-medium text-gray-600 w-8 text-left">{pct}%</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </section>
  );
}
