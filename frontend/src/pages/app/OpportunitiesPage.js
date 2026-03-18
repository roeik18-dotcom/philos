import { useState, useEffect } from 'react';
import { Loader2, Flame, Lock, CheckCircle, Briefcase, Award, Users, DollarSign } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TYPE_CONFIG = {
  job: { icon: Briefcase, color: '#f59e0b', label: 'Job' },
  grant: { icon: DollarSign, color: '#10b981', label: 'Grant' },
  collaboration: { icon: Users, color: '#00d4ff', label: 'Collaboration' },
  support: { icon: Award, color: '#7c3aed', label: 'Support' },
};

export default function OpportunitiesPage({ user }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('');

  useEffect(() => {
    const fetchOpps = async () => {
      try {
        const url = user?.id
          ? `${API_URL}/api/opportunities?user_id=${user.id}`
          : `${API_URL}/api/opportunities`;
        const res = await fetch(url);
        const d = await res.json();
        if (d.success) setData(d);
      } catch (err) {
        console.error('Opportunities fetch error:', err);
      }
      setLoading(false);
    };
    fetchOpps();
  }, [user]);

  if (loading) {
    return (
      <div className="opp-page" data-testid="opportunities-page">
        <div className="feed-loading"><Loader2 className="w-5 h-5 animate-spin" /><span>Loading opportunities...</span></div>
      </div>
    );
  }

  const opps = data?.opportunities || [];
  const userTrust = data?.user_trust_score || 0;
  const types = ['', 'job', 'grant', 'collaboration', 'support'];
  const filtered = filterType ? opps.filter(o => o.type === filterType) : opps;
  const eligible = filtered.filter(o => o.eligible).length;

  return (
    <div className="opp-page" data-testid="opportunities-page">
      <div className="feed-header">
        <h1 className="feed-title" data-testid="opp-title">Opportunities</h1>
        <p className="feed-subtitle">
          Your Trust Score unlocks real opportunities.
          {user && <span className="opp-trust-inline" data-testid="opp-user-trust"><Flame className="w-3.5 h-3.5" /> {userTrust}</span>}
        </p>
      </div>

      {/* Progress bar */}
      {user && (
        <div className="opp-progress" data-testid="opp-progress">
          <div className="opp-progress-text">
            <span>{eligible} of {filtered.length} unlocked</span>
          </div>
          <div className="opp-progress-bar">
            <div className="opp-progress-fill" style={{ width: `${filtered.length ? (eligible / filtered.length) * 100 : 0}%` }} />
          </div>
        </div>
      )}

      {/* Type filter */}
      <div className="feed-filters" data-testid="opp-filters">
        {types.map(t => (
          <button
            key={t || 'all'}
            className={`feed-filter-btn ${filterType === t ? 'active' : ''}`}
            onClick={() => setFilterType(t)}
            data-testid={`opp-filter-${t || 'all'}`}
          >
            {t ? TYPE_CONFIG[t]?.label || t : 'All'}
          </button>
        ))}
      </div>

      {/* Opportunity cards */}
      <div className="opp-list" data-testid="opp-list">
        {filtered.map(opp => {
          const cfg = TYPE_CONFIG[opp.type] || TYPE_CONFIG.support;
          const Icon = cfg.icon;
          return (
            <div key={opp.id} className={`opp-card ${opp.eligible ? 'eligible' : 'locked'}`} data-testid={`opp-card-${opp.id}`}>
              <div className="opp-card-top">
                <span className="opp-card-type" style={{ color: cfg.color }}>
                  <Icon className="w-3.5 h-3.5" /> {cfg.label}
                </span>
                {opp.eligible ? (
                  <span className="opp-card-status eligible" data-testid={`opp-status-${opp.id}`}>
                    <CheckCircle className="w-3.5 h-3.5" /> Eligible
                  </span>
                ) : (
                  <span className="opp-card-status locked" data-testid={`opp-status-${opp.id}`}>
                    <Lock className="w-3.5 h-3.5" /> Locked
                  </span>
                )}
              </div>
              <h3 className="opp-card-title">{opp.title}</h3>
              <p className="opp-card-desc">{opp.description}</p>
              <div className="opp-card-footer">
                <span className="opp-card-req">
                  <Flame className="w-3 h-3" /> Requires {opp.min_trust_score} Trust
                </span>
                {opp.community !== 'General' && (
                  <span className="opp-card-community">{opp.community}</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
