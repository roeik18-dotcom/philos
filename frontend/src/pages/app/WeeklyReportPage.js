import { useState, useEffect } from 'react';
import { Loader2, Flame, Activity, TrendingUp, Users, Calendar, Award, BarChart3 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function WeeklyReportPage({ user }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    const fetchReport = async () => {
      try {
        const res = await fetch(`${API_URL}/api/weekly-report/${user.id}`);
        const d = await res.json();
        if (d.success) setReport(d.report);
      } catch (err) {
        console.error('Report fetch error:', err);
      }
      setLoading(false);
    };
    fetchReport();
  }, [user]);

  if (loading) {
    return (
      <div className="report-page" data-testid="weekly-report-page">
        <div className="feed-loading"><Loader2 className="w-5 h-5 animate-spin" /><span>Loading report...</span></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="report-page" data-testid="weekly-report-page">
        <div className="feed-empty"><p>Sign in to view your weekly report.</p></div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="report-page" data-testid="weekly-report-page">
        <div className="feed-empty"><p>No report data available yet.</p></div>
      </div>
    );
  }

  return (
    <div className="report-page" data-testid="weekly-report-page">
      <div className="report-header" data-testid="report-header">
        <Calendar className="w-5 h-5" style={{ color: '#00d4ff' }} />
        <div>
          <h1 className="feed-title" data-testid="report-title">Weekly Impact Report</h1>
          <p className="feed-subtitle">{report.period}</p>
        </div>
      </div>

      {/* Your week */}
      <div className="report-section" data-testid="report-your-week">
        <h2 className="report-section-title">Your Week</h2>
        <div className="report-stats-grid">
          <div className="report-stat">
            <Activity className="w-5 h-5" style={{ color: '#00d4ff' }} />
            <div className="report-stat-value" data-testid="report-week-actions">{report.week_actions}</div>
            <div className="report-stat-label">Actions This Week</div>
          </div>
          <div className="report-stat">
            <Flame className="w-5 h-5" style={{ color: '#f59e0b' }} />
            <div className="report-stat-value" data-testid="report-week-trust">{report.week_trust_earned}</div>
            <div className="report-stat-label">Trust Earned</div>
          </div>
          <div className="report-stat">
            <Award className="w-5 h-5" style={{ color: '#10b981' }} />
            <div className="report-stat-value" data-testid="report-total-trust">{report.total_trust_score}</div>
            <div className="report-stat-label">Total Trust Score</div>
          </div>
          <div className="report-stat">
            <BarChart3 className="w-5 h-5" style={{ color: '#7c3aed' }} />
            <div className="report-stat-value" data-testid="report-rank">#{report.rank || '—'}</div>
            <div className="report-stat-label">Your Rank</div>
          </div>
        </div>
      </div>

      {/* Categories & Communities */}
      {(report.week_categories?.length > 0 || report.week_communities?.length > 0) && (
        <div className="report-section" data-testid="report-categories">
          <h2 className="report-section-title">Contributions</h2>
          {report.week_categories?.length > 0 && (
            <div className="report-tags">
              <span className="report-tag-label">Categories:</span>
              {report.week_categories.map(c => (
                <span key={c} className="profile-tag">{c}</span>
              ))}
            </div>
          )}
          {report.week_communities?.length > 0 && (
            <div className="report-tags" style={{ marginTop: '10px' }}>
              <span className="report-tag-label">Communities:</span>
              {report.week_communities.map(c => (
                <span key={c} className="profile-tag">{c}</span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Network */}
      <div className="report-section" data-testid="report-network">
        <h2 className="report-section-title"><Users className="w-4 h-4" /> Network This Week</h2>
        <div className="report-network-grid">
          <div className="report-network-stat">
            <span className="report-network-value">{report.network_active_users}</span>
            <span className="report-network-label">Active Users</span>
          </div>
          <div className="report-network-stat">
            <span className="report-network-value">{report.network_actions_this_week}</span>
            <span className="report-network-label">Total Actions</span>
          </div>
          <div className="report-network-stat">
            <span className="report-network-value">{report.network_trust_this_week}</span>
            <span className="report-network-label">Trust Generated</span>
          </div>
        </div>
      </div>

      {/* All-time */}
      <div className="report-section" data-testid="report-alltime">
        <h2 className="report-section-title"><TrendingUp className="w-4 h-4" /> All-Time</h2>
        <div className="report-alltime-row">
          <span>{report.total_actions} total actions</span>
          <span className="report-alltime-trust"><Flame className="w-3.5 h-3.5" /> {report.total_trust_score} Trust Score</span>
          <span>Rank #{report.rank} of {report.total_users}</span>
        </div>
      </div>
    </div>
  );
}
