import { useState, useEffect, useCallback } from 'react';
import { MapPin, Tag, Users, Clock, Loader2, Heart, ThumbsUp, ShieldCheck, Flame, Share2, Copy, Check, X, BadgeCheck, Building2 } from 'lucide-react';

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

const VERIFICATION_BADGES = {
  self_reported: null,
  community_verified: { icon: BadgeCheck, label: 'Community Verified', color: '#10b981' },
  org_verified: { icon: Building2, label: 'Organization Verified', color: '#f59e0b' },
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

const BASE_URL = typeof window !== 'undefined' ? window.location.origin : '';

function ShareModal({ action, onClose, user }) {
  const [copied, setCopied] = useState(false);
  const refParam = user ? `?ref=${user.id}` : '';
  const shareUrl = `${BASE_URL}/api/share/action/${action.id}${refParam}`;
  const directUrl = `${BASE_URL}/app/action/${action.id}${refParam}`;
  const trustScore = Math.round(action.trust_signal || 0);
  const shareText = `${action.user_name || 'Someone'} made an impact: "${action.title}"${action.community ? ` for ${action.community}` : ''}${trustScore > 0 ? ` — Trust Score: ${trustScore}` : ''} #Philos`;

  const copyLink = async () => {
    try { await navigator.clipboard.writeText(directUrl); } catch { /* fallback */ }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const shareWhatsApp = () => window.open(`https://wa.me/?text=${encodeURIComponent(shareText + '\n' + shareUrl)}`, '_blank');
  const shareLinkedIn = () => window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`, '_blank');
  const shareTwitter = () => window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`, '_blank');

  return (
    <div className="share-overlay" onClick={onClose} data-testid="share-modal-overlay">
      <div className="share-modal" onClick={e => e.stopPropagation()} data-testid="share-modal">
        <div className="share-modal-header">
          <span>Share this action</span>
          <button className="share-modal-close" onClick={onClose} data-testid="share-modal-close"><X className="w-4 h-4" /></button>
        </div>

        {/* Mini preview */}
        <div className="share-modal-preview" data-testid="share-modal-preview">
          <div className="share-modal-preview-avatar">{(action.user_name || '?')[0].toUpperCase()}</div>
          <div>
            <div className="share-modal-preview-name">{action.user_name || 'Anonymous'}</div>
            <div className="share-modal-preview-title">{action.title}</div>
            {action.community && <div className="share-modal-preview-community">{action.community}</div>}
          </div>
          {trustScore > 0 && (
            <div className="share-modal-trust"><Flame className="w-3.5 h-3.5" />{trustScore}</div>
          )}
        </div>

        {/* Share buttons */}
        <div className="share-modal-actions">
          <button className="share-option-btn" onClick={copyLink} data-testid="share-copy-link">
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            <span>{copied ? 'Copied!' : 'Copy link'}</span>
          </button>
          <button className="share-option-btn share-whatsapp" onClick={shareWhatsApp} data-testid="share-whatsapp">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
            <span>WhatsApp</span>
          </button>
          <button className="share-option-btn share-linkedin" onClick={shareLinkedIn} data-testid="share-linkedin">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
            <span>LinkedIn</span>
          </button>
          <button className="share-option-btn share-twitter" onClick={shareTwitter} data-testid="share-twitter">
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
            <span>Twitter / X</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default function ActionFeed({ user }) {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('');
  const [reactingId, setReactingId] = useState(null);
  const [sharingAction, setSharingAction] = useState(null);

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
        setActions(prev => prev.map(a =>
          a.id === actionId ? { ...a, trust_signal: data.trust_signal } : a
        ));
      } else {
        fetchFeed(); // Revert optimistic update
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

              <h3 className="feed-card-title" data-testid="action-title">
                {action.title}
                {(() => {
                  const vb = VERIFICATION_BADGES[action.verification_level];
                  if (!vb) return null;
                  const VIcon = vb.icon;
                  return (
                    <span className="feed-verification-badge" style={{ color: vb.color }} data-testid={`verification-${action.id}`} title={vb.label}>
                      <VIcon className="w-3.5 h-3.5" />
                    </span>
                  );
                })()}
              </h3>
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
                    const isOwnAction = user && action.user_id === user.id;
                    return (
                      <button
                        key={r.type}
                        className={`reaction-btn ${active ? 'active' : ''}`}
                        style={{ '--reaction-color': r.color }}
                        onClick={() => handleReact(action.id, r.type)}
                        disabled={!user || isOwnAction || reactingId === `${action.id}-${r.type}`}
                        data-testid={`react-${r.type}-${action.id}`}
                        title={!user ? 'Sign in to react' : isOwnAction ? 'Cannot react to own action' : `${r.label} (+${r.weight})`}
                      >
                        <Icon className="w-3.5 h-3.5" />
                        {count > 0 && <span className="reaction-count">{count}</span>}
                        <span className="reaction-weight" data-testid={`weight-${r.type}-${action.id}`}>+{r.weight}</span>
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
                <button
                  className="share-btn"
                  onClick={() => setSharingAction(action)}
                  data-testid={`share-btn-${action.id}`}
                  title="Share this action"
                >
                  <Share2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {sharingAction && (
        <ShareModal action={sharingAction} onClose={() => setSharingAction(null)} user={user} />
      )}
    </div>
  );
}
