import { useState, useEffect, useCallback } from 'react';
import { MapPin, Tag, Users, Clock, Loader2, Heart, ThumbsUp, ShieldCheck, Flame } from 'lucide-react';

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

const REACTION_CONFIG = [
  { type: 'support', icon: Heart, label: 'Support', color: '#f43f5e', weight: 1 },
  { type: 'useful', icon: ThumbsUp, label: 'Useful', color: '#00d4ff', weight: 2 },
  { type: 'verified', icon: ShieldCheck, label: 'Verified', color: '#10b981', weight: 5 },
];

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function ActionFeed({ user }) {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('');
  const [reactingId, setReactingId] = useState(null);

  const fetchFeed = useCallback(async () => {
    setLoading(true);
    try {
      let url = `${API_URL}/api/actions/feed?`;
      if (category) url += `category=${category}&`;
      if (user?.id) url += `viewer_id=${user.id}`;
      const res = await fetch(url);
      const data = await res.json();
      if (data.success) setActions(data.actions);
    } catch (err) {
      console.error('Feed fetch error:', err);
    }
    setLoading(false);
  }, [category, user]);

  useEffect(() => { fetchFeed(); }, [fetchFeed]);

  const handleReact = async (actionId, reactionType) => {
    if (!user) return;
    setReactingId(`${actionId}-${reactionType}`);

    // Optimistic update
    setActions(prev => prev.map(a => {
      if (a.id !== actionId) return a;
      const wasReacted = a.user_reacted[reactionType];
      const weight = REACTION_CONFIG.find(r => r.type === reactionType)?.weight || 0;
      return {
        ...a,
        user_reacted: { ...a.user_reacted, [reactionType]: !wasReacted },
        reactions: {
          ...a.reactions,
          [reactionType]: a.reactions[reactionType] + (wasReacted ? -1 : 1),
        },
        trust_signal: a.trust_signal + (wasReacted ? -weight : weight),
      };
    }));

    try {
      const token = localStorage.getItem('philos_auth_token');
      const res = await fetch(`${API_URL}/api/actions/${actionId}/react`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ reaction_type: reactionType }),
      });
      const data = await res.json();
      if (data.success) {
        // Update trust_signal with server value
        setActions(prev => prev.map(a =>
          a.id === actionId ? { ...a, trust_signal: data.trust_signal } : a
        ));
      }
    } catch (err) {
      console.error('React error:', err);
      fetchFeed(); // Revert on error
    }
    setReactingId(null);
  };

  const categories = ['', 'education', 'environment', 'health', 'community', 'technology', 'mentorship', 'volunteering'];

  return (
    <div className="feed-page" data-testid="action-feed-page">
      <div className="feed-header">
        <h1 className="feed-title" data-testid="feed-title">Action Feed</h1>
        <p className="feed-subtitle">Real actions. Real impact. Real people.</p>
      </div>

      <div className="feed-filters" data-testid="feed-filters">
        {categories.map(cat => (
          <button
            key={cat || 'all'}
            className={`feed-filter-btn ${category === cat ? 'active' : ''}`}
            onClick={() => setCategory(cat)}
            data-testid={`filter-${cat || 'all'}`}
          >
            {cat || 'All'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="feed-loading" data-testid="feed-loading">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading actions...</span>
        </div>
      ) : actions.length === 0 ? (
        <div className="feed-empty" data-testid="feed-empty">
          <p>No actions yet. Be the first to contribute.</p>
        </div>
      ) : (
        <div className="feed-list" data-testid="feed-list">
          {actions.map(action => (
            <article key={action.id} className="feed-card" data-testid={`action-card-${action.id}`}>
              <div className="feed-card-top">
                <span
                  className="feed-card-category"
                  style={{ color: CATEGORY_COLORS[action.category] || '#6b7280' }}
                  data-testid="action-category"
                >
                  <Tag className="w-3 h-3" />
                  {action.category}
                </span>
                <span className="feed-card-time" data-testid="action-time">
                  <Clock className="w-3 h-3" />
                  {timeAgo(action.created_at)}
                </span>
              </div>

              <h3 className="feed-card-title" data-testid="action-title">{action.title}</h3>
              <p className="feed-card-desc" data-testid="action-description">{action.description}</p>

              <div className="feed-card-meta">
                <span className="feed-card-contributor" data-testid="action-contributor">
                  <Users className="w-3 h-3" />
                  {action.user_name || 'Anonymous'}
                </span>
                {action.community && (
                  <span className="feed-card-community" data-testid="action-community">
                    <Users className="w-3 h-3" />
                    {action.community}
                  </span>
                )}
                {action.location?.name && (
                  <span className="feed-card-location" data-testid="action-location">
                    <MapPin className="w-3 h-3" />
                    {action.location.name}
                  </span>
                )}
              </div>

              {/* Reactions + Trust Score */}
              <div className="feed-card-reactions" data-testid={`reactions-${action.id}`}>
                <div className="reaction-buttons">
                  {REACTION_CONFIG.map(r => {
                    const Icon = r.icon;
                    const active = action.user_reacted?.[r.type];
                    const count = action.reactions[r.type] || 0;
                    return (
                      <button
                        key={r.type}
                        className={`reaction-btn ${active ? 'active' : ''}`}
                        style={{ '--reaction-color': r.color }}
                        onClick={() => handleReact(action.id, r.type)}
                        disabled={!user || reactingId === `${action.id}-${r.type}`}
                        data-testid={`react-${r.type}-${action.id}`}
                        title={user ? r.label : 'Sign in to react'}
                      >
                        <Icon className="w-3.5 h-3.5" />
                        {count > 0 && <span className="reaction-count">{count}</span>}
                      </button>
                    );
                  })}
                </div>
                {action.trust_signal > 0 && (
                  <div className="feed-trust-score" data-testid={`trust-score-${action.id}`}>
                    <Flame className="w-3.5 h-3.5" />
                    <span>{Math.round(action.trust_signal)}</span>
                  </div>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
