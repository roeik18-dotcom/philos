import { useState, useEffect } from 'react';
import { MapPin, Tag, Users, Clock, Loader2 } from 'lucide-react';

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

export default function ActionFeed() {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('');

  useEffect(() => {
    const fetchFeed = async () => {
      setLoading(true);
      try {
        const url = category
          ? `${API_URL}/api/actions/feed?category=${category}`
          : `${API_URL}/api/actions/feed`;
        const res = await fetch(url);
        const data = await res.json();
        if (data.success) setActions(data.actions);
      } catch (err) {
        console.error('Feed fetch error:', err);
      }
      setLoading(false);
    };
    fetchFeed();
  }, [category]);

  const categories = ['', 'education', 'environment', 'health', 'community', 'technology', 'mentorship', 'volunteering'];

  return (
    <div className="feed-page" data-testid="action-feed-page">
      <div className="feed-header">
        <h1 className="feed-title" data-testid="feed-title">Action Feed</h1>
        <p className="feed-subtitle">Real actions. Real impact. Real people.</p>
      </div>

      {/* Category filter */}
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

      {/* Feed */}
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
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
