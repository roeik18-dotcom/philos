import { useState, useEffect } from 'react';
import { BarChart3, Users, CheckCircle, UserPlus, Flame, Target, Lock } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const metrics = [
  { key: 'active_users_today', label: 'משתמשים פעילים', Icon: Users, color: '#0d9488', format: v => v.toLocaleString('he-IL') },
  { key: 'daily_question_completion_rate', label: 'השלמת שאלה יומית', Icon: CheckCircle, color: '#22c55e', format: v => `${v}%` },
  { key: 'day2_retention', label: 'שימור יום 2', Icon: UserPlus, color: '#6366f1', format: v => `${v}%` },
  { key: 'mission_participation_rate', label: 'השתתפות במשימה', Icon: Target, color: '#f59e0b', format: v => `${v}%` },
  { key: 'avg_streak', label: 'רצף ממוצע', Icon: Flame, color: '#ef4444', format: v => v.toFixed(1) }
];

export default function MetricsDashboardSection() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await fetch(`${API_URL}/api/orientation/metrics-today`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) {
            setData(json);
            setTimeout(() => setVisible(true), 100);
          }
        }
      } catch (e) {
        console.log('Could not fetch metrics:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse" dir="rtl">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="grid grid-cols-2 gap-3">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-20 bg-gray-100 rounded-2xl"></div>)}
        </div>
      </section>
    );
  }

  if (!data) return null;

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-2" dir="rtl" data-testid="metrics-dashboard-section">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-xl bg-gray-100 flex items-center justify-center">
          <BarChart3 className="w-5 h-5 text-gray-600" />
        </div>
        <span className="text-sm font-medium text-gray-700">מדדי מערכת</span>
        <Lock className="w-3 h-3 text-gray-400 mr-auto" />
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {metrics.map(({ key, label, Icon, color, format }, index) => (
          <div
            key={key}
            className="bg-gray-50 rounded-2xl p-3 flex flex-col items-center gap-1.5 transition-all duration-300 hover:shadow-sm"
            style={{
              opacity: visible ? 1 : 0,
              transform: visible ? 'translateY(0)' : 'translateY(8px)',
              transition: `opacity 0.4s ease ${index * 80}ms, transform 0.4s ease ${index * 80}ms`
            }}
            data-testid={`metric-${key}`}
          >
            <Icon className="w-5 h-5" style={{ color }} />
            <span className="text-xl font-black" style={{ color }} data-testid={`metric-value-${key}`}>
              {format(data[key] || 0)}
            </span>
            <span className="text-[10px] text-gray-500 text-center leading-tight">{label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
