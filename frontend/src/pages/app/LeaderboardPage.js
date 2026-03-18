import { useState, useEffect } from 'react';
import { Loader2, Flame, Trophy, Activity, Tag } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const RANK_COLORS = ['#f59e0b', '#94a3b8', '#b45309'];

export default function LeaderboardPage({ user }) {
  const [leaders, setLeaders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const res = await fetch(`${API_URL}/api/leaderboard`);
        const d = await res.json();
        if (d.success) setLeaders(d.leaders);
      } catch (err) {
        console.error('Leaderboard fetch error:', err);
      }
      setLoading(false);
    };
    fetchLeaderboard();
  }, []);

  if (loading) {
    return (
      <div className="leaderboard-page" data-testid="leaderboard-page">
        <div className="feed-loading"><Loader2 className="w-5 h-5 animate-spin" /><span>Loading leaderboard...</span></div>
      </div>
    );
  }

  return (
    <div className="leaderboard-page" data-testid="leaderboard-page">
      <div className="feed-header">
        <h1 className="feed-title" data-testid="leaderboard-title">Leaderboard</h1>
        <p className="feed-subtitle">Top contributors ranked by Trust Score</p>
      </div>

      {/* Top 3 podium */}
      {leaders.length >= 3 && (
        <div className="lb-podium" data-testid="lb-podium">
          {[1, 0, 2].map(idx => {
            const l = leaders[idx];
            const isFirst = idx === 0;
            return (
              <div key={l.user_id} className={`lb-podium-card ${isFirst ? 'first' : ''}`} data-testid={`lb-podium-${idx}`}>
                <div className="lb-podium-rank" style={{ color: RANK_COLORS[idx] || '#fff' }}>
                  {isFirst && <Trophy className="w-5 h-5" />}
                  #{l.rank}
                </div>
                <div className="lb-podium-avatar" style={{ borderColor: RANK_COLORS[idx] || '#333' }}>
                  {(l.user_name || '?')[0].toUpperCase()}
                </div>
                <div className="lb-podium-name">{l.user_name}</div>
                <div className="lb-podium-trust"><Flame className="w-3.5 h-3.5" /> {l.trust_score}</div>
                <div className="lb-podium-actions">{l.total_actions} actions</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Full list */}
      <div className="lb-list" data-testid="lb-list">
        {leaders.map(l => {
          const isMe = user?.id === l.user_id;
          return (
            <div key={l.user_id} className={`lb-row ${isMe ? 'me' : ''}`} data-testid={`lb-row-${l.rank}`}>
              <span className="lb-row-rank" style={{ color: l.rank <= 3 ? RANK_COLORS[l.rank - 1] : 'rgba(255,255,255,0.3)' }}>
                {l.rank}
              </span>
              <div className="lb-row-avatar">{(l.user_name || '?')[0].toUpperCase()}</div>
              <div className="lb-row-info">
                <span className="lb-row-name">{l.user_name}{isMe ? ' (You)' : ''}</span>
                <span className="lb-row-cats">
                  {l.categories.slice(0, 3).map(c => (
                    <span key={c} className="lb-cat-tag"><Tag className="w-2.5 h-2.5" />{c}</span>
                  ))}
                </span>
              </div>
              <div className="lb-row-stats">
                <span className="lb-row-actions"><Activity className="w-3 h-3" /> {l.total_actions}</span>
                <span className="lb-row-trust"><Flame className="w-3.5 h-3.5" /> {l.trust_score}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
