import { useState, useEffect } from 'react';
import { Target, Users, Zap, ChevronLeft, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };

export default function MissionsSection({ userId }) {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(null);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    fetch(`${API_URL}/api/orientation/missions`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setMissions(d.missions); })
      .catch(() => {}).finally(() => setLoading(false));
  }, []);

  const handleJoin = async (mission) => {
    if (!effectiveUserId) return;
    setJoining(mission.id);
    try {
      await fetch(`${API_URL}/api/orientation/missions/join`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: effectiveUserId, mission_id: mission.id })
      });
      setMissions(prev => prev.map(m => m.id === mission.id ? { ...m, participants: m.participants + 1 } : m));
    } catch (e) {}
    finally { setJoining(null); }
  };

  if (loading) return null;

  return (
    <section className="philos-section bg-white border-border" dir="rtl" data-testid="missions-section">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-xl bg-indigo-50 flex items-center justify-center">
          <Target className="w-5 h-5 text-indigo-600" />
        </div>
        <div>
          <span className="text-sm font-semibold text-gray-800">משימות שדה</span>
          <p className="text-[10px] text-gray-400">הצטרף למאמץ הקולקטיבי</p>
        </div>
      </div>

      <div className="space-y-2">
        {missions.map(m => {
          const color = dirColors[m.direction] || '#6366f1';
          const progress = m.participants > 0 ? Math.min(100, (m.participants / Math.max(m.participants * 1.3, 100)) * 100) : 0;
          return (
            <div key={m.id} className="rounded-xl p-3 border" style={{ backgroundColor: `${color}05`, borderColor: `${color}20` }} data-testid={`mission-${m.id}`}>
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold" style={{ color }}>{m.title_he}</span>
                  {m.is_today && <span className="text-[8px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full">פעיל היום</span>}
                </div>
                <span className="text-[10px] px-1.5 py-0.5 rounded-full" style={{ backgroundColor: `${color}15`, color }}>{m.direction_he}</span>
              </div>
              <p className="text-[10px] text-gray-500 mb-2">{m.description_he}</p>
              <div className="flex items-center gap-2 mb-2">
                <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div className="h-full rounded-full transition-all" style={{ width: `${progress}%`, backgroundColor: color }} />
                </div>
                <div className="flex items-center gap-1 text-[10px] text-gray-400">
                  <Users className="w-3 h-3" />
                  <span>{m.participants.toLocaleString()}</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-gray-400 flex items-center gap-1"><Zap className="w-2.5 h-2.5" /> השפעה: +{m.total_field_impact.toLocaleString()}</span>
                <button onClick={() => handleJoin(m)} disabled={!!joining} className="text-[10px] font-medium flex items-center gap-0.5 hover:opacity-80 transition-opacity" style={{ color }} data-testid={`join-mission-${m.id}`}>
                  {joining === m.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><ChevronLeft className="w-3 h-3" />הצטרף</>}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
