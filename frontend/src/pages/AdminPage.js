import { useState, useEffect } from 'react';
import { BarChart3, Users, Zap, RotateCcw, MessageSquare, ArrowRight } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function AdminPage() {
  const [data, setData] = useState(null);
  const [feedback, setFeedback] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/api/admin/analytics`).then(r => r.ok ? r.json() : null),
      fetch(`${API_URL}/api/admin/feedback`).then(r => r.ok ? r.json() : null)
    ]).then(([analytics, fb]) => {
      if (analytics?.success) setData(analytics);
      if (fb?.success) setFeedback(fb.feedback || []);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">
        Failed to load analytics
      </div>
    );
  }

  const todayDau = data.dau[0] || {};

  return (
    <div className="min-h-screen bg-gray-50 p-6" data-testid="admin-page">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Philos Admin Analytics</h1>
            <p className="text-xs text-gray-400 mt-0.5">
              Generated: {new Date(data.generated_at).toLocaleString()}
            </p>
          </div>
          <a href="/" className="flex items-center gap-1 text-xs text-indigo-500 hover:text-indigo-700" data-testid="admin-back-to-app">
            <ArrowRight className="w-3.5 h-3.5" /> Back to App
          </a>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="admin-kpi-cards">
          <KpiCard icon={Users} label="Total Users" value={data.totals.users} color="indigo" />
          <KpiCard icon={Zap} label="Total Actions" value={data.totals.actions} color="green" />
          <KpiCard icon={Users} label="DAU Today" value={todayDau.active_users || 0} color="blue" />
          <KpiCard icon={BarChart3} label="Actions/User" value={todayDau.actions_per_user || 0} color="amber" />
        </div>

        {/* Retention */}
        <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm" data-testid="admin-retention">
          <div className="flex items-center gap-2 mb-4">
            <RotateCcw className="w-4 h-4 text-purple-500" />
            <h2 className="text-sm font-bold text-gray-800">Retention</h2>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <RetentionCard label="Day 1" data={data.retention.d1} />
            <RetentionCard label="Day 7" data={data.retention.d7} />
          </div>
        </div>

        {/* DAU Chart (last 7 days) */}
        <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm" data-testid="admin-dau-chart">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-4 h-4 text-blue-500" />
            <h2 className="text-sm font-bold text-gray-800">Daily Active Users (7 days)</h2>
          </div>
          <div className="space-y-2">
            {data.dau.map((day, i) => {
              const maxUsers = Math.max(...data.dau.map(d => d.active_users), 1);
              const pct = (day.active_users / maxUsers) * 100;
              return (
                <div key={i} className="flex items-center gap-3" data-testid={`dau-row-${i}`}>
                  <span className="text-[10px] text-gray-400 w-20 text-right">{day.date}</span>
                  <div className="flex-1 h-5 bg-gray-50 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-400 rounded-full transition-all" style={{ width: `${Math.max(pct, 2)}%` }} />
                  </div>
                  <span className="text-xs font-semibold text-gray-700 w-8 text-right">{day.active_users}</span>
                  <span className="text-[10px] text-gray-400 w-16">{day.total_actions} acts</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Feedback */}
        <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm" data-testid="admin-feedback">
          <div className="flex items-center gap-2 mb-4">
            <MessageSquare className="w-4 h-4 text-orange-500" />
            <h2 className="text-sm font-bold text-gray-800">User Feedback ({data.totals.feedback})</h2>
          </div>
          {feedback.length === 0 ? (
            <p className="text-xs text-gray-400 text-center py-4">No feedback yet</p>
          ) : (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {feedback.map((f, i) => (
                <div key={i} className="p-3 bg-gray-50 rounded-xl text-xs" data-testid={`feedback-item-${i}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-medium bg-orange-100 text-orange-600">{f.type}</span>
                    <span className="text-gray-400">{f.page || 'general'}</span>
                    <span className="text-gray-300 mr-auto">{new Date(f.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-gray-700">{f.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function KpiCard({ icon: Icon, label, value, color }) {
  const colors = {
    indigo: 'bg-indigo-50 text-indigo-600',
    green: 'bg-green-50 text-green-600',
    blue: 'bg-blue-50 text-blue-600',
    amber: 'bg-amber-50 text-amber-600'
  };
  return (
    <div className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center mb-2 ${colors[color]}`}>
        <Icon className="w-4 h-4" />
      </div>
      <p className="text-2xl font-bold text-gray-900">{typeof value === 'number' ? value.toLocaleString() : value}</p>
      <p className="text-[10px] text-gray-400 mt-0.5">{label}</p>
    </div>
  );
}

function RetentionCard({ label, data }) {
  return (
    <div className="rounded-xl p-4 bg-purple-50 border border-purple-100">
      <p className="text-xs font-semibold text-purple-700 mb-2">{label} Retention</p>
      <p className="text-2xl font-bold text-purple-900">{data.rate}%</p>
      <p className="text-[10px] text-purple-400 mt-1">
        {data.returned}/{data.cohort_size} users returned
      </p>
    </div>
  );
}
