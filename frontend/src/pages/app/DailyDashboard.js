import { useState, useEffect } from 'react';
import { Loader2, Activity, Zap, Target, TrendingUp } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function DailyDashboard({ user }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    const fetchDashboard = async () => {
      try {
        const res = await fetch(`${API_URL}/api/impact/dashboard/${user.id}`);
        const d = await res.json();
        if (d.success) setData(d);
      } catch (err) {
        console.error('Dashboard fetch error:', err);
      }
      setLoading(false);
    };
    fetchDashboard();
  }, [user]);

  if (loading) {
    return (
      <div className="dashboard-page" data-testid="daily-dashboard-page">
        <div className="feed-loading">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading dashboard...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="dashboard-page" data-testid="daily-dashboard-page">
        <div className="feed-empty"><p>Sign in to view your dashboard.</p></div>
      </div>
    );
  }

  const summary = data?.profile_summary || {};
  const network = data?.network_activity || [];
  const suggestions = data?.suggested_actions || [];

  return (
    <div className="dashboard-page" data-testid="daily-dashboard-page">
      <div className="dash-header">
        <h1 className="feed-title" data-testid="dashboard-title">Daily Dashboard</h1>
        <p className="feed-subtitle">Your impact at a glance</p>
      </div>

      {/* Summary cards */}
      <div className="dash-summary" data-testid="dashboard-summary">
        <div className="dash-stat-card">
          <div className="dash-stat-icon" style={{ background: 'rgba(0,212,255,0.1)' }}>
            <Activity className="w-5 h-5" style={{ color: '#00d4ff' }} />
          </div>
          <div>
            <div className="dash-stat-value" data-testid="dash-total-actions">{summary.total_actions || 0}</div>
            <div className="dash-stat-label">Total Actions</div>
          </div>
        </div>
        <div className="dash-stat-card">
          <div className="dash-stat-icon" style={{ background: 'rgba(245,158,11,0.1)' }}>
            <TrendingUp className="w-5 h-5" style={{ color: '#f59e0b' }} />
          </div>
          <div>
            <div className="dash-stat-value" data-testid="dash-impact-score">{summary.impact_score || 0}</div>
            <div className="dash-stat-label">Impact Score</div>
          </div>
        </div>
        <div className="dash-stat-card">
          <div className="dash-stat-icon" style={{ background: 'rgba(16,185,129,0.1)' }}>
            <Target className="w-5 h-5" style={{ color: '#10b981' }} />
          </div>
          <div>
            <div className="dash-stat-value" data-testid="dash-verified">{summary.verified_count || 0}</div>
            <div className="dash-stat-label">Verified</div>
          </div>
        </div>
      </div>

      {/* Network activity */}
      <div className="dash-section" data-testid="network-activity">
        <h2 className="dash-section-title">
          <Zap className="w-4 h-4" style={{ color: '#00d4ff' }} /> Network Activity
        </h2>
        {network.length === 0 ? (
          <p className="dash-empty">No recent network activity.</p>
        ) : (
          <div className="dash-activity-list">
            {network.map((item, i) => (
              <div key={i} className="dash-activity-item" data-testid={`network-item-${i}`}>
                <span className="dash-activity-user">{item.user}</span>
                <span className="dash-activity-action">{item.action}</span>
                <span className="dash-activity-cat">{item.category}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="dash-section" data-testid="suggested-actions">
          <h2 className="dash-section-title">
            <Target className="w-4 h-4" style={{ color: '#10b981' }} /> Suggested Actions
          </h2>
          <div className="dash-suggestions">
            {suggestions.map((s, i) => (
              <div key={i} className="dash-suggestion-card" data-testid={`suggestion-${i}`}>
                <span className="dash-suggestion-cat">{s.category}</span>
                <span className="dash-suggestion-text">{s.prompt}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
