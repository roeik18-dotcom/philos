import { useState, useEffect } from 'react';
import { Heart, ThumbsUp, ShieldCheck, MapPin, Filter } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const CATEGORY_LABELS = {
  education: 'Education', environment: 'Environment', health: 'Health',
  community: 'Community', technology: 'Technology', mentorship: 'Mentorship',
  volunteering: 'Volunteering', other: 'Other',
};

const CATEGORY_COLORS = {
  education: '#3b82f6', environment: '#10b981', health: '#f43f5e',
  community: '#8b5cf6', technology: '#06b6d4', mentorship: '#f59e0b',
  volunteering: '#ec4899', other: '#6b7280',
};

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function ActionCard({ action, user, onReact }) {
  const [reacting, setReacting] = useState(false);

  const handleReact = async (type) => {
    if (!user) return;
    setReacting(true);
    try {
      await fetch(`${API}/api/actions/${action.id}/react`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${user.token}` },
        body: JSON.stringify({ reaction_type: type }),
      });
      onReact?.();
    } finally { setReacting(false); }
  };

  const catColor = CATEGORY_COLORS[action.category] || '#6b7280';

  return (
    <div className="bg-[#0d0d1a] border border-white/[0.06] rounded-xl p-4 transition hover:border-white/[0.1]" data-testid="action-card">
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-7 h-7 rounded-full bg-white/[0.06] flex items-center justify-center text-xs font-medium" style={{ color: catColor }}>
              {action.user_name?.[0]?.toUpperCase() || '?'}
            </div>
            <span className="text-sm font-medium">{action.user_name}</span>
            <span className="text-[10px] text-white/30">{timeAgo(action.created_at)}</span>
          </div>
        </div>
        {action.trust_signal > 0 && (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 font-medium">
            +{action.trust_signal.toFixed(1)} trust
          </span>
        )}
      </div>

      <h3 className="text-sm font-semibold mb-1">{action.title}</h3>
      <p className="text-xs text-white/40 mb-3 leading-relaxed">{action.description}</p>

      <div className="flex items-center gap-2 mb-3 flex-wrap">
        <span className="text-[10px] px-2 py-0.5 rounded-full border" style={{ borderColor: catColor + '44', color: catColor }}>
          {CATEGORY_LABELS[action.category] || action.category}
        </span>
        {action.community && (
          <span className="text-[10px] text-white/30 flex items-center gap-1">
            <span className="w-1 h-1 rounded-full bg-white/20" />
            {action.community}
          </span>
        )}
        {action.location?.name && (
          <span className="text-[10px] text-white/30 flex items-center gap-1">
            <MapPin className="w-3 h-3" /> {action.location.name}
          </span>
        )}
      </div>

      <div className="flex items-center gap-1 pt-2 border-t border-white/[0.04]">
        {[
          { type: 'support', icon: Heart, count: action.reactions?.support || 0, color: '#f43f5e' },
          { type: 'useful', icon: ThumbsUp, count: action.reactions?.useful || 0, color: '#3b82f6' },
          { type: 'verified', icon: ShieldCheck, count: action.reactions?.verified || 0, color: '#10b981' },
        ].map(r => (
          <button
            key={r.type}
            onClick={() => handleReact(r.type)}
            disabled={!user || reacting}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[10px] text-white/40 hover:bg-white/[0.04] transition disabled:opacity-30"
            data-testid={`react-${r.type}`}
          >
            <r.icon className="w-3 h-3" style={{ color: r.count > 0 ? r.color : undefined }} />
            {r.count > 0 && <span style={{ color: r.color }}>{r.count}</span>}
            <span className="capitalize">{r.type}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default function FeedPage({ user }) {
  const [actions, setActions] = useState([]);
  const [filter, setFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const loadFeed = async () => {
    try {
      const url = filter ? `${API}/api/actions/feed?category=${filter}` : `${API}/api/actions/feed`;
      const res = await fetch(url);
      const data = await res.json();
      if (data.success) setActions(data.actions);
    } finally { setLoading(false); }
  };

  useEffect(() => { loadFeed(); }, [filter]);

  return (
    <div className="max-w-lg mx-auto px-4 pb-24" data-testid="feed-page">
      <div className="sticky top-0 z-10 pt-4 pb-3" style={{ background: 'linear-gradient(to bottom, #050510 80%, transparent)' }}>
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-lg font-semibold">Impact Feed</h1>
          {user && (
            <a href="/app/post" className="text-xs px-3 py-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 transition" data-testid="post-action-link">
              + Post Action
            </a>
          )}
        </div>
        <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-hide">
          <button onClick={() => setFilter('')}
            className={`text-[10px] px-2.5 py-1 rounded-full border whitespace-nowrap transition ${!filter ? 'border-cyan-500/40 text-cyan-400 bg-cyan-500/10' : 'border-white/[0.06] text-white/40 hover:text-white/60'}`}>
            All
          </button>
          {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
            <button key={k} onClick={() => setFilter(k)}
              className={`text-[10px] px-2.5 py-1 rounded-full border whitespace-nowrap transition ${filter === k ? 'border-cyan-500/40 text-cyan-400 bg-cyan-500/10' : 'border-white/[0.06] text-white/40 hover:text-white/60'}`}>
              {v}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3 mt-2">
        {loading ? (
          <div className="text-center py-12 text-white/30 text-sm">Loading...</div>
        ) : actions.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-white/30 text-sm mb-2">No actions yet</p>
            {user && <a href="/app/post" className="text-xs text-cyan-400">Be the first to post</a>}
          </div>
        ) : (
          actions.map(a => <ActionCard key={a.id} action={a} user={user} onReact={loadFeed} />)
        )}
      </div>
    </div>
  );
}
