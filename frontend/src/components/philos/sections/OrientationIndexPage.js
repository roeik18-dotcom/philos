import { useState, useEffect } from 'react';
import { Globe, Users, Activity, ArrowLeftRight, TrendingUp } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionMeta = {
  recovery: { color: '#3b82f6', label: 'התאוששות' },
  order: { color: '#6366f1', label: 'סדר' },
  contribution: { color: '#22c55e', label: 'תרומה' },
  exploration: { color: '#f59e0b', label: 'חקירה' }
};

export default function OrientationIndexPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [animateBars, setAnimateBars] = useState(false);

  useEffect(() => {
    const fetchIndex = async () => {
      try {
        const res = await fetch(`${API_URL}/api/orientation/index`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) {
            setData(json);
            setTimeout(() => setAnimateBars(true), 200);
          }
        }
      } catch (e) {
        console.log('Could not fetch orientation index:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchIndex();
    const interval = setInterval(fetchIndex, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse" dir="rtl">
        <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
        <div className="h-40 bg-gray-200 rounded mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/3"></div>
      </section>
    );
  }

  if (!data) return null;

  const directions = Object.entries(directionMeta);
  const maxPct = Math.max(...Object.values(data.distribution || {}), 1);

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-1" dir="rtl" data-testid="orientation-index-page">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-teal-50 flex items-center justify-center">
            <Globe className="w-5 h-5 text-teal-600" />
          </div>
          <span className="text-sm font-medium text-teal-700">מדד התמצאות גלובלי</span>
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-400">
          <Activity className="w-3 h-3 animate-pulse" />
          <span>חי</span>
        </div>
      </div>

      {/* Headline */}
      {data.headline_he && (
        <div className="bg-gradient-to-l from-teal-50 to-white rounded-2xl p-3 mb-4 border border-teal-100">
          <p className="text-sm font-bold text-teal-800" data-testid="index-headline">{data.headline_he}</p>
        </div>
      )}

      {/* Distribution - Animated vertical bars */}
      <div className="flex items-end justify-around gap-2 h-40 mb-4 px-2" data-testid="index-distribution">
        {directions.map(([key, meta], index) => {
          const pct = data.distribution?.[key] || 0;
          const heightPct = maxPct > 0 ? (pct / maxPct) * 100 : 0;
          const isDominant = key === data.dominant_direction;
          return (
            <div key={key} className="flex flex-col items-center flex-1 h-full justify-end">
              <span
                className="text-xs font-bold mb-1 transition-opacity duration-500"
                style={{ color: meta.color, opacity: animateBars ? 1 : 0 }}
              >
                {pct}%
              </span>
              <div
                className="w-full max-w-[48px] relative rounded-t-xl transition-all ease-out"
                style={{
                  height: animateBars ? `${Math.max(heightPct, 4)}%` : '4%',
                  backgroundColor: meta.color,
                  opacity: isDominant ? 1 : 0.6,
                  transitionDuration: '800ms',
                  transitionDelay: `${index * 120}ms`
                }}
              >
                {isDominant && animateBars && (
                  <div className="absolute -top-5 left-1/2 -translate-x-1/2 animate-glow-in">
                    <TrendingUp className="w-3.5 h-3.5" style={{ color: meta.color }} />
                  </div>
                )}
              </div>
              <span className="text-[10px] text-gray-500 mt-2 text-center leading-tight">{meta.label}</span>
            </div>
          );
        })}
      </div>

      {/* Stats row */}
      <div className="flex items-center justify-between text-xs text-gray-500 border-t border-gray-100 pt-3">
        <div className="flex items-center gap-1">
          <Users className="w-3.5 h-3.5" />
          <span>{data.total_users} משתמשים פעילים</span>
        </div>
        <span>{data.total_actions_today} פעולות היום</span>
      </div>

      {/* Direction change indicator */}
      {data.direction_change && data.direction_change !== 'same' && data.yesterday_dominant && (
        <div className="flex items-center justify-center gap-2 mt-3 text-xs text-gray-500 bg-gray-50 rounded-xl py-2" data-testid="direction-change">
          <ArrowLeftRight className="w-3.5 h-3.5" />
          <span>שינוי מאתמול: {directionMeta[data.yesterday_dominant]?.label || data.yesterday_dominant}</span>
        </div>
      )}
    </section>
  );
}
