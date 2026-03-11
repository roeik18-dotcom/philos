import { useState, useEffect } from 'react';
import { Sun, FileText } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionColors = {
  recovery: '#3b82f6', order: '#6366f1', contribution: '#22c55e', exploration: '#f59e0b'
};
const directionLabels = {
  recovery: 'התאוששות', order: 'סדר', contribution: 'תרומה', exploration: 'חקירה'
};
const forceLabels = {
  cognitive: 'קוגניטיבי', emotional: 'רגשי', physical: 'פיזי',
  personal: 'אישי', social: 'חברתי', drives: 'דחפים'
};
const vectorLabels = {
  internal: 'פנימי', external: 'חיצוני', collective: 'קולקטיבי'
};

export default function DailySummarySection({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [animateBars, setAnimateBars] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    const fetch_ = async () => {
      if (!effectiveUserId) return;
      try {
        const res = await fetch(`${API_URL}/api/orientation/daily-summary/${effectiveUserId}`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) {
            setData(json);
            setTimeout(() => setAnimateBars(true), 200);
          }
        }
      } catch (e) {
        console.log('Could not fetch daily summary:', e);
      } finally {
        setLoading(false);
      }
    };
    fetch_();
  }, [effectiveUserId]);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse" dir="rtl">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-16 bg-gray-200 rounded"></div>
      </section>
    );
  }

  if (!data) return null;

  const maxForce = Math.max(...Object.values(data.forces), 0.01);
  const maxVec = Math.max(...Object.values(data.vectors), 0.01);

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-2" dir="rtl" data-testid="daily-summary-section">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-amber-50 flex items-center justify-center">
            <Sun className="w-5 h-5 text-amber-600" />
          </div>
          <span className="text-sm font-medium text-amber-700">סיכום יומי</span>
        </div>
        <span className="text-xs text-gray-400">{data.date}</span>
      </div>

      {/* Summary text */}
      <div className="bg-amber-50 rounded-2xl p-3 mb-4">
        <p className="text-sm text-amber-800 font-medium" data-testid="daily-summary-text">{data.summary_he}</p>
      </div>

      {data.total_actions > 0 && (
        <>
          {/* Direction breakdown */}
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            {Object.entries(data.direction_counts).map(([d, c]) => c > 0 && (
              <span key={d} className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: `${directionColors[d]}15`, color: directionColors[d] }}>
                {directionLabels[d]} ({c})
              </span>
            ))}
          </div>

          {/* Forces mini-bars */}
          <div className="mb-3">
            <p className="text-[10px] text-gray-500 mb-1.5">פרופיל כוחות</p>
            <div className="grid grid-cols-3 gap-x-3 gap-y-1">
              {Object.entries(data.forces).map(([f, v], i) => (
                <div key={f} className="flex items-center gap-1.5">
                  <span className="text-[10px] text-gray-500 w-12">{forceLabels[f]}</span>
                  <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-indigo-400 transition-all duration-700 ease-out"
                      style={{ width: animateBars ? `${(v / maxForce) * 100}%` : '0%', transitionDelay: `${i * 60}ms` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Value vectors */}
          <div className="mb-3">
            <p className="text-[10px] text-gray-500 mb-1.5">וקטורי ערך</p>
            <div className="flex gap-3">
              {Object.entries(data.vectors).map(([v, val]) => (
                <div key={v} className="flex-1 text-center bg-gray-50 rounded-xl py-2">
                  <span className="text-sm font-bold text-gray-800">{val}</span>
                  <p className="text-[10px] text-gray-500">{vectorLabels[v]}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Field impact */}
          {data.field_impact > 0 && (
            <div className="flex items-center gap-1.5 text-xs text-gray-500">
              <FileText className="w-3 h-3" />
              <span>השפעת שדה: {data.field_impact}%</span>
            </div>
          )}
        </>
      )}
    </section>
  );
}
