import { useState, useEffect } from 'react';
import { Loader2, Tag, Award, Activity, Briefcase, Flame, Sparkles, Lock, CheckCircle, ShieldAlert, TrendingDown } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CATEGORY_COLORS = {
  education: '#7c3aed',
  environment: '#10b981',
  health: '#f43f5e',
  community: '#00d4ff',
  technology: '#f59e0b',
  mentorship: '#ec4899',
  volunteering: '#8b5cf6',
  other: '#6b7280',
};

export default function ProductProfile({ user }) {
  const [profile, setProfile] = useState(null);
  const [trustData, setTrustData] = useState(null);
  const [opps, setOpps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    const fetchAll = async () => {
      try {
        const [profileRes, oppsRes, trustRes] = await Promise.all([
          fetch(`${API_URL}/api/impact/profile/${user.id}`),
          fetch(`${API_URL}/api/opportunities?user_id=${user.id}`),
          fetch(`${API_URL}/api/trust/${user.id}`),
        ]);
        const pd = await profileRes.json();
        const od = await oppsRes.json();
        const td = await trustRes.json();
        if (pd.success) setProfile(pd.profile);
        if (od.success) setOpps(od.opportunities.slice(0, 3));
        if (td.success) setTrustData(td);
      } catch (err) {
        console.error('Profile fetch error:', err);
      }
      setLoading(false);
    };
    fetchAll();
  }, [user]);

  if (loading) {
    return (
      <div className="profile-page" data-testid="product-profile-page">
        <div className="feed-loading">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading profile...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="profile-page" data-testid="product-profile-page">
        <div className="feed-empty"><p>Sign in to view your profile.</p></div>
      </div>
    );
  }

  return (
    <div className="profile-page" data-testid="product-profile-page">
      <div className="profile-header-card" data-testid="profile-header">
        <div className="profile-avatar" data-testid="profile-avatar">
          {(user.name || user.email || '?')[0].toUpperCase()}
        </div>
        <h1 className="profile-name" data-testid="profile-name">{user.name || user.email?.split('@')[0]}</h1>
        <p className="profile-email" data-testid="profile-email">{user.email}</p>
      </div>

      {/* Trust Engine Card */}
      {trustData && (
        <div className="profile-section" data-testid="profile-trust-engine">
          <div className="trust-engine-card">
            <div className="trust-engine-header">
              <Flame className="w-5 h-5" style={{ color: '#f59e0b' }} />
              <span className="trust-engine-title">Trust Score</span>
              {trustData.enforcement_active && (
                <span className="trust-engine-enforcement" data-testid="enforcement-badge">
                  <ShieldAlert className="w-3 h-3" /> Enforcement Active
                </span>
              )}
            </div>
            <div className="trust-engine-score" data-testid="trust-engine-score">
              {trustData.trust_score}
            </div>
            <div className="trust-engine-meta">
              <span className="trust-engine-meta-item" data-testid="trust-decay-rate">
                <TrendingDown className="w-3 h-3" />
                Decay: {trustData.decay_rate * 100}%/month
                {trustData.decay_rate > 0.05 && <span className="trust-accelerated"> (accelerated)</span>}
              </span>
              <span className="trust-engine-meta-item" data-testid="trust-decay-status">
                Status: <span className={`trust-status-${trustData.decay_status}`}>{trustData.decay_status}</span>
              </span>
              <span className="trust-engine-meta-item" data-testid="trust-action-count">
                {trustData.action_count} actions
              </span>
            </div>
            {trustData.risk_signal_count > 0 && (
              <div className="trust-engine-signals" data-testid="trust-risk-signals">
                <span className="trust-signal-header">
                  <ShieldAlert className="w-3 h-3" /> {trustData.risk_signal_count} active signal{trustData.risk_signal_count > 1 ? 's' : ''}
                </span>
                {trustData.active_risk_signals.map((sig, i) => (
                  <div key={i} className={`trust-signal-item trust-signal-${sig.severity}`} data-testid={`risk-signal-${sig.signal_type}`}>
                    <span className="trust-signal-type">{sig.signal_type.replace(/_/g, ' ')}</span>
                    <span className={`trust-signal-severity severity-${sig.severity}`}>{sig.severity}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Stats grid */}
      <div className="profile-stats" data-testid="profile-stats">
        <div className="profile-stat-card">
          <Activity className="w-5 h-5" style={{ color: '#00d4ff' }} />
          <div className="profile-stat-value" data-testid="stat-actions">{profile?.total_actions || 0}</div>
          <div className="profile-stat-label">Actions Posted</div>
        </div>
        <div className="profile-stat-card">
          <Award className="w-5 h-5" style={{ color: '#10b981' }} />
          <div className="profile-stat-value" data-testid="stat-impact">{profile?.impact_score || 0}</div>
          <div className="profile-stat-label">Impact Score</div>
        </div>
        <div className="profile-stat-card">
          <Tag className="w-5 h-5" style={{ color: '#7c3aed' }} />
          <div className="profile-stat-value" data-testid="stat-verified">{profile?.verified_count || 0}</div>
          <div className="profile-stat-label">Verified</div>
        </div>
      </div>

      {/* Categories */}
      {profile?.fields?.length > 0 && (
        <div className="profile-section" data-testid="profile-categories">
          <h2 className="profile-section-title">
            <Briefcase className="w-4 h-4" /> Contribution Categories
          </h2>
          <div className="profile-tags">
            {profile.fields.map(cat => (
              <span
                key={cat}
                className="profile-tag"
                style={{ borderColor: (CATEGORY_COLORS[cat] || '#6b7280') + '44', color: CATEGORY_COLORS[cat] || '#6b7280' }}
                data-testid={`category-tag-${cat}`}
              >
                {cat}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Communities */}
      {profile?.communities?.length > 0 && (
        <div className="profile-section" data-testid="profile-communities">
          <h2 className="profile-section-title">Communities Helped</h2>
          <div className="profile-tags">
            {profile.communities.map(c => (
              <span key={c} className="profile-tag" data-testid={`community-tag-${c}`}>{c}</span>
            ))}
          </div>
        </div>
      )}

      {/* Opportunities preview */}
      {opps.length > 0 && (
        <div className="profile-section" data-testid="profile-opportunities">
          <h2 className="profile-section-title"><Sparkles className="w-4 h-4" /> Opportunities</h2>
          <div className="profile-opps-preview">
            {opps.map(o => (
              <div key={o.id} className={`profile-opp-item ${o.eligible ? 'eligible' : 'locked'}`} data-testid={`profile-opp-${o.id}`}>
                <div className="profile-opp-status">
                  {o.eligible ? <CheckCircle className="w-3.5 h-3.5" style={{ color: '#10b981' }} /> : <Lock className="w-3.5 h-3.5" style={{ color: 'rgba(255,255,255,0.2)' }} />}
                </div>
                <div className="profile-opp-info">
                  <span className="profile-opp-title">{o.title}</span>
                  <span className="profile-opp-req"><Flame className="w-3 h-3" /> {o.min_trust_score} Trust</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
