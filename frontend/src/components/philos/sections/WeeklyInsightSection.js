import { useState, useEffect } from 'react';
import { CalendarDays, TrendingUp, TrendingDown, Minus, BarChart3 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionColors = {
  recovery: { color: '#3b82f6', label: 'Recovery' },
  order: { color: '#6366f1', label: 'Order' },
  contribution: { color: '#22c55e', label: 'Contribution' },
  exploration: { color: '#f59e0b', label: 'Exploration' }
};

const trendIcons = {
  improving: <TrendingUp className="w-4 h-4 text-green-500" />,
  declining: <TrendingDown className="w-4 h-4 text-red-500" />,
  stable: <Minus className="w-4 h-4 text-gray-400" />
};

export default function WeeklyInsightSection({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [animateBars, setAnimateBars] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    const fetchInsight = async () => {
      if (!effectiveUserId) return;
      try {
        const res = await fetch(`${API_URL}/api/orientation/weekly-insight/${effectiveUserId}`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) {
            setData(json);
            setTimeout(() => setAnimateBars(true), 300);
          }
        }
      } catch (e) {
        console.log('Could not fetch weekly insight:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchInsight();
  }, [effectiveUserId]);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-3"></div>
        <div className="h-16 bg-gray-200 rounded mb-3"></div>
        <div className="h-4 bg-gray-200 rounded w-2/3"></div>
      </section>
    );
  }

  if (!data) return null;

  const maxPercent = Math.max(...Object.values(data.distribution_percent || {}), 1);

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-1" data-testid="weekly-insight-section">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-violet-50 flex items-center justify-center">
            <CalendarDays className="w-5 h-5 text-violet-600" />
          </div>
          <span className="text-sm font-medium text-violet-700">Weekly Insight</span>
        </div>
        <div className="flex items-center gap-1">
          {trendIcons[data.trend] || trendIcons.stable}
          <span className="text-xs text-gray-500">
            {data.trend === 'improving' ? 'Improving trend' : data.trend === 'declining' ? 'Declining trend' : 'Stable'}
          </span>
        </div>
      </div>

      {/* Distribution bars */}
      {data.total_actions > 0 ? (
        <div className="space-y-2.5 mb-4">
          {Object.entries(directionColors).map(([key, meta], index) => {
            const pct = data.distribution_percent?.[key] || 0;
            const count = data.distribution?.[key] || 0;
            const targetWidth = maxPercent > 0 ? (pct / maxPercent) * 100 : 0;
            return (
              <div key={key} className="flex items-center gap-3" data-testid={`weekly-bar-${key}`}>
                <span className="text-xs text-gray-600 w-16 text-right">{meta.label}</span>
                <div className="flex-1 h-5 bg-gray-100 rounded-full overflow-hidden relative">
                  <div
                    className="h-full rounded-full transition-all duration-700 ease-out"
                    style={{
                      width: animateBars ? `${targetWidth}%` : '0%',
                      backgroundColor: meta.color,
                      minWidth: count > 0 ? '8px' : '0',
                      transitionDelay: `${index * 100}ms`
                    }}
                  />
                </div>
                <span className="text-xs font-medium text-gray-500 w-10 text-left" dir="ltr">{pct}%</span>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="flex items-center justify-center py-6 text-gray-400">
          <BarChart3 className="w-8 h-8 opacity-30" />
        </div>
      )}

      {/* Insight text */}
      {data.insight_he && (
        <div className="bg-violet-50 rounded-2xl p-3">
          <p className="text-sm text-violet-800 font-medium" data-testid="weekly-insight-text">{data.insight_he}</p>
        </div>
      )}

      {/* Meta */}
      <div className="flex items-center justify-between mt-3 text-xs text-gray-400">
        <span>{data.total_actions} actions in 7 days</span>
        {data.dominant_direction && (
          <span>Leading: {directionColors[data.dominant_direction]?.label || data.dominant_direction}</span>
        )}
      </div>
    </section>
  );
}
