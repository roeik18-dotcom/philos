import { useState, useEffect } from 'react';
import { FileText, Flame, Target, TrendingUp } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionColors = {
  recovery: { color: '#3b82f6', label: 'Recovery' },
  order: { color: '#6366f1', label: 'Order' },
  contribution: { color: '#22c55e', label: 'Contribution' },
  exploration: { color: '#f59e0b', label: 'Exploration' }
};

export default function WeeklyReportSection({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [animateBars, setAnimateBars] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    const fetchReport = async () => {
      if (!effectiveUserId) return;
      try {
        const res = await fetch(`${API_URL}/api/orientation/weekly-report/${effectiveUserId}`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) {
            setData(json);
            setTimeout(() => setAnimateBars(true), 300);
          }
        }
      } catch (e) {
        console.log('Could not fetch weekly report:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [effectiveUserId]);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-3"></div>
        <div className="h-20 bg-gray-200 rounded mb-3"></div>
        <div className="h-4 bg-gray-200 rounded w-2/3"></div>
      </section>
    );
  }

  if (!data) return null;

  const maxPct = Math.max(...Object.values(data.distribution || {}), 1);

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-3" data-testid="weekly-report-section">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-emerald-50 flex items-center justify-center">
            <FileText className="w-5 h-5 text-emerald-600" />
          </div>
          <span className="text-sm font-medium text-emerald-700">Weekly Report</span>
        </div>
        <span className="text-xs text-gray-400">{data.days_active} days active</span>
      </div>

      {/* Distribution bars */}
      {data.total_actions > 0 ? (
        <div className="space-y-2 mb-4">
          {Object.entries(directionColors).map(([key, meta], index) => {
            const pct = data.distribution?.[key] || 0;
            const isDominant = key === data.dominant_direction;
            return (
              <div key={key} className="flex items-center gap-3" data-testid={`report-bar-${key}`}>
                <span className="text-xs text-gray-600 w-16 text-right">{meta.label}</span>
                <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-700 ease-out"
                    style={{
                      width: animateBars ? `${(pct / maxPct) * 100}%` : '0%',
                      backgroundColor: meta.color,
                      opacity: isDominant ? 1 : 0.6,
                      minWidth: pct > 0 ? '6px' : '0',
                      transitionDelay: `${index * 100}ms`
                    }}
                  />
                </div>
                <span className="text-xs font-medium w-8 text-left" dir="ltr" style={{ color: meta.color }}>{pct}%</span>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-4 text-gray-400 text-sm mb-4">No data This week</div>
      )}

      {/* Insight */}
      {data.insight_he && (
        <div className="bg-emerald-50 rounded-2xl p-3 mb-4">
          <p className="text-sm text-emerald-800 font-medium" data-testid="report-insight">{data.insight_he}</p>
        </div>
      )}

      {/* Stats row */}
      <div className="flex items-center justify-around text-center border-t border-gray-100 pt-3">
        <div className="flex flex-col items-center gap-1" data-testid="report-streak">
          <Flame className="w-4 h-4 text-orange-500" />
          <span className="text-lg font-bold text-gray-800">{data.streak}</span>
          <span className="text-[10px] text-gray-500">Streak</span>
        </div>
        <div className="flex flex-col items-center gap-1" data-testid="report-mission">
          <Target className="w-4 h-4 text-amber-500" />
          <span className="text-lg font-bold text-gray-800">{data.mission_participation}%</span>
          <span className="text-[10px] text-gray-500">Missions</span>
        </div>
        <div className="flex flex-col items-center gap-1" data-testid="report-actions">
          <TrendingUp className="w-4 h-4 text-blue-500" />
          <span className="text-lg font-bold text-gray-800">{data.total_actions}</span>
          <span className="text-[10px] text-gray-500">actions</span>
        </div>
      </div>
    </section>
  );
}
