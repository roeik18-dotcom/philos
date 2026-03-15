import { useState, useEffect } from 'react';
import { Loader2, Tag, Users, MapPin, Flame, Heart, ThumbsUp, ShieldCheck, ArrowLeft } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CATEGORY_COLORS = {
  education: '#7c3aed', environment: '#10b981', health: '#f43f5e',
  community: '#00d4ff', technology: '#f59e0b', mentorship: '#ec4899',
  volunteering: '#8b5cf6', other: '#6b7280',
};

const REACTION_ICONS = { support: Heart, useful: ThumbsUp, verified: ShieldCheck };
const REACTION_COLORS = { support: '#f43f5e', useful: '#00d4ff', verified: '#10b981' };

export default function ActionSharePage() {
  const [action, setAction] = useState(null);
  const [loading, setLoading] = useState(true);

  const actionId = window.location.pathname.split('/app/action/')[1];

  useEffect(() => {
    if (!actionId) { setLoading(false); return; }
    const fetchAction = async () => {
      try {
        const res = await fetch(`${API_URL}/api/actions/${actionId}`);
        const data = await res.json();
        if (data.success) setAction(data.action);
      } catch (err) {
        console.error('Action fetch error:', err);
      }
      setLoading(false);
    };
    fetchAction();
  }, [actionId]);

  if (loading) {
    return (
      <div className="share-page" data-testid="action-share-page">
        <div className="feed-loading"><Loader2 className="w-5 h-5 animate-spin" /><span>Loading...</span></div>
      </div>
    );
  }

  if (!action) {
    return (
      <div className="share-page" data-testid="action-share-page">
        <div className="feed-empty"><p>Action not found.</p></div>
      </div>
    );
  }

  const trustScore = Math.round(action.trust_signal || 0);
  const catColor = CATEGORY_COLORS[action.category] || '#6b7280';

  return (
    <div className="share-page" data-testid="action-share-page">
      <button className="share-back-btn" onClick={() => { window.location.href = '/app/feed'; }} data-testid="share-back-btn">
        <ArrowLeft className="w-4 h-4" /> Back to feed
      </button>

      {/* Preview card */}
      <div className="share-preview-card" data-testid="share-preview-card">
        <div className="share-preview-badge">Philos Impact Action</div>

        <div className="share-preview-contributor" data-testid="share-contributor">
          <div className="share-preview-avatar">{(action.user_name || '?')[0].toUpperCase()}</div>
          <span>{action.user_name || 'Anonymous'}</span>
        </div>

        <h1 className="share-preview-title" data-testid="share-action-title">{action.title}</h1>

        {action.description && (
          <p className="share-preview-desc" data-testid="share-description">{action.description}</p>
        )}

        <div className="share-preview-details">
          <span className="share-preview-cat" style={{ color: catColor }}>
            <Tag className="w-3 h-3" /> {action.category}
          </span>
          {action.community && (
            <span className="share-preview-community" data-testid="share-community">
              <Users className="w-3 h-3" /> {action.community}
            </span>
          )}
          {action.location?.name && (
            <span className="share-preview-loc">
              <MapPin className="w-3 h-3" /> {action.location.name}
            </span>
          )}
        </div>

        {/* Reactions summary */}
        <div className="share-preview-reactions">
          {['support', 'useful', 'verified'].map(type => {
            const Icon = REACTION_ICONS[type];
            const count = action.reactions?.[type] || 0;
            if (count === 0) return null;
            return (
              <span key={type} className="share-reaction-badge" style={{ color: REACTION_COLORS[type] }}>
                <Icon className="w-3.5 h-3.5" /> {count}
              </span>
            );
          })}
        </div>

        {trustScore > 0 && (
          <div className="share-preview-trust" data-testid="share-trust-score">
            <Flame className="w-5 h-5" />
            <span className="share-trust-value">{trustScore}</span>
            <span className="share-trust-label">Trust Score</span>
          </div>
        )}

        <div className="share-preview-footer">philos-mvp.preview.emergentagent.com</div>
      </div>

      {/* CTA */}
      <div className="share-cta">
        <a href="/app/feed" className="share-cta-btn" data-testid="share-view-feed-btn">
          View more actions
        </a>
      </div>
    </div>
  );
}
