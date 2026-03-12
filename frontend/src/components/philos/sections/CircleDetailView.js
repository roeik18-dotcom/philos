import { useState, useEffect } from 'react';
import { ArrowRight, Users, Star, Target, Zap, MapPin, Loader2, LogIn, LogOut } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };

const INNER_TABS = ['feed', 'leaders', 'missions'];
const INNER_TAB_LABELS = { feed: 'פיד', leaders: 'מובילים', missions: 'משימות' };

export default function CircleDetailView({ circleId, userId, onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [innerTab, setInnerTab] = useState('feed');
  const [toggling, setToggling] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  const fetchData = () => {
    const qs = effectiveUserId ? `?user_id=${effectiveUserId}` : '';
    fetch(`${API_URL}/api/orientation/value-circles/${circleId}${qs}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setData(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [circleId, effectiveUserId]);

  const handleToggleMembership = async () => {
    if (!effectiveUserId) return;
    setToggling(true);
    const endpoint = data?.is_member ? 'leave' : 'join';
    try {
      await fetch(`${API_URL}/api/orientation/value-circles/${endpoint}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: effectiveUserId, circle_id: circleId })
      });
      fetchData();
    } catch (e) {}
    finally { setToggling(false); }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-3">
        <Loader2 className="w-6 h-6 animate-spin text-purple-500" />
        <span className="text-xs text-gray-400">טוען מעגל...</span>
      </div>
    );
  }

  if (!data) return null;

  const { circle, feed, leaderboard, missions, is_member } = data;
  const color = circle.color || '#6366f1';

  return (
    <div className="space-y-4" data-testid="circle-detail-view" dir="rtl">
      {/* Back button */}
      <button
        onClick={onBack}
        className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700 transition-colors"
        data-testid="circle-detail-back"
      >
        <ArrowRight className="w-3.5 h-3.5" />
        <span>חזרה למעגלים</span>
      </button>

      {/* Circle Header */}
      <div className="rounded-2xl p-5 border" style={{ backgroundColor: `${color}06`, borderColor: `${color}20` }} data-testid="circle-detail-header">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
              <Users className="w-5 h-5" style={{ color }} />
            </div>
            <div>
              <h2 className="text-base font-bold text-gray-800">{circle.label_he}</h2>
              {circle.direction && (
                <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ backgroundColor: `${color}12`, color }}>
                  {circle.direction === 'contribution' ? 'תרומה' : circle.direction === 'recovery' ? 'התאוששות' : circle.direction === 'order' ? 'סדר' : 'חקירה'}
                </span>
              )}
            </div>
          </div>
          <button
            onClick={handleToggleMembership}
            disabled={toggling}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-all"
            style={is_member
              ? { backgroundColor: '#fee2e2', color: '#dc2626' }
              : { backgroundColor: `${color}12`, color }
            }
            data-testid="circle-detail-toggle-membership"
          >
            {toggling ? <Loader2 className="w-3 h-3 animate-spin" /> : is_member ? <><LogOut className="w-3 h-3" />עזוב</> : <><LogIn className="w-3 h-3" />הצטרף</>}
          </button>
        </div>
        <p className="text-xs text-gray-500 leading-relaxed mb-3">{circle.description_he}</p>
        <div className="flex items-center gap-1 text-[10px] text-gray-400">
          <Users className="w-3 h-3" />
          <span>{circle.member_count.toLocaleString()} חברים</span>
        </div>
      </div>

      {/* Inner Tabs */}
      <div className="flex gap-1 p-0.5 rounded-xl bg-gray-100" data-testid="circle-detail-tabs">
        {INNER_TABS.map(t => (
          <button
            key={t}
            onClick={() => setInnerTab(t)}
            className={`flex-1 px-3 py-2 text-xs font-medium rounded-lg transition-all ${innerTab === t ? 'bg-white shadow-sm text-gray-800' : 'text-gray-400 hover:text-gray-600'}`}
            data-testid={`circle-tab-${t}`}
          >
            {INNER_TAB_LABELS[t]}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {innerTab === 'feed' && <CircleFeed feed={feed} color={color} />}
      {innerTab === 'leaders' && <CircleLeaders leaderboard={leaderboard} />}
      {innerTab === 'missions' && <CircleMissions missions={missions} />}
    </div>
  );
}

function CircleFeed({ feed, color }) {
  if (!feed?.length) return <EmptyState text="אין פעולות עדיין" />;
  return (
    <div className="space-y-2" data-testid="circle-feed">
      {feed.map((item, i) => (
        <div key={i} className="bg-white rounded-xl p-3 border border-border" data-testid={`circle-feed-item-${i}`}>
          <div className="flex items-center gap-2 mb-1.5">
            <div className="w-7 h-7 rounded-full flex items-center justify-center text-white text-[10px] font-bold" style={{ backgroundColor: dirColors[item.direction] || color }}>
              {item.alias?.charAt(0)}
            </div>
            <span className="text-xs font-semibold text-gray-800">{item.alias}</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded-full mr-auto" style={{ backgroundColor: `${dirColors[item.direction] || color}12`, color: dirColors[item.direction] || color }}>
              +{item.impact}
            </span>
          </div>
          <p className="text-xs text-gray-600 leading-relaxed">{item.action_he}</p>
        </div>
      ))}
    </div>
  );
}

function CircleLeaders({ leaderboard }) {
  if (!leaderboard?.length) return <EmptyState text="אין מובילים עדיין" />;
  return (
    <div className="bg-white rounded-xl border border-border overflow-hidden" data-testid="circle-leaders">
      {leaderboard.map((l, i) => (
        <div key={i} className="flex items-center gap-2.5 p-3 border-b border-gray-50 last:border-b-0" data-testid={`circle-leader-${i}`}>
          <span className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${i < 3 ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-500'}`}>
            {i < 3 ? <Star className="w-3 h-3" /> : l.rank}
          </span>
          <div className="flex-1 min-w-0">
            <span className="text-xs font-semibold text-gray-800">{l.alias}</span>
            <span className="text-[9px] text-gray-400 flex items-center gap-0.5 mt-0.5"><MapPin className="w-2 h-2" />{l.country}</span>
          </div>
          <div className="text-left">
            <p className="text-xs font-bold text-gray-800">{Math.round(l.impact)}</p>
            <p className="text-[8px] text-gray-400">{l.actions} פעולות</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function CircleMissions({ missions }) {
  if (!missions?.length) return <EmptyState text="אין משימות פעילות" />;
  return (
    <div className="space-y-2" data-testid="circle-missions">
      {missions.map((m, i) => {
        const color = dirColors[m.direction] || '#6366f1';
        const progress = m.target > 0 ? Math.min(100, (m.participants / m.target) * 100) : 0;
        return (
          <div key={i} className="rounded-xl p-3 border" style={{ backgroundColor: `${color}05`, borderColor: `${color}20` }} data-testid={`circle-mission-${i}`}>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-bold" style={{ color }}>{m.title_he}</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded-full" style={{ backgroundColor: `${color}15`, color }}>{m.direction_he}</span>
            </div>
            <p className="text-[10px] text-gray-500 mb-2">{m.description_he}</p>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all" style={{ width: `${progress}%`, backgroundColor: color }} />
              </div>
              <div className="flex items-center gap-1 text-[10px] text-gray-400">
                <Target className="w-3 h-3" />
                <span>{m.participants.toLocaleString()}/{m.target.toLocaleString()}</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function EmptyState({ text }) {
  return (
    <div className="text-center py-8 text-sm text-gray-400">{text}</div>
  );
}
