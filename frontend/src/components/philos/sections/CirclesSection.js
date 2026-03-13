import { useState, useEffect } from 'react';
import { Users, ChevronLeft, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function CirclesSection({ userId, onViewCircle }) {
  const [circles, setCircles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(null);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    fetch(`${API_URL}/api/orientation/value-circles`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setCircles(d.circles); })
      .catch(() => {}).finally(() => setLoading(false));
  }, []);

  const handleJoin = async (circleId) => {
    if (!effectiveUserId) return;
    setJoining(circleId);
    try {
      const res = await fetch(`${API_URL}/api/orientation/value-circles/join`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: effectiveUserId, circle_id: circleId })
      });
      const data = await res.json();
      if (data.success && !data.already_member) {
        setCircles(prev => prev.map(c => c.id === circleId ? { ...c, member_count: c.member_count + 1 } : c));
      }
    } catch (e) {}
    finally { setJoining(null); }
  };

  if (loading) return null;

  return (
    <section className="philos-section bg-white border-border" data-testid="circles-section">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-xl bg-pink-50 flex items-center justify-center">
          <Users className="w-5 h-5 text-pink-600" />
        </div>
        <div>
          <span className="text-sm font-semibold text-gray-800">Value Circles</span>
          <p className="text-[10px] text-gray-400">Communities by direction and niche</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {circles.map(c => (
          <div
            key={c.id}
            className="rounded-xl p-3 border cursor-pointer hover:shadow-md transition-all"
            style={{ backgroundColor: `${c.color}06`, borderColor: `${c.color}20` }}
            onClick={() => onViewCircle?.(c.id)}
            data-testid={`circle-${c.id}`}
          >
            <div className="w-7 h-7 rounded-lg flex items-center justify-center mb-2" style={{ backgroundColor: `${c.color}15` }}>
              <Users className="w-3.5 h-3.5" style={{ color: c.color }} />
            </div>
            <p className="text-xs font-bold text-gray-800 mb-0.5">{c.label_he}</p>
            <p className="text-[9px] text-gray-400 mb-2 leading-relaxed line-clamp-2">{c.description_he}</p>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-gray-400">{c.member_count.toLocaleString()} members</span>
              <button onClick={(e) => { e.stopPropagation(); handleJoin(c.id); }} disabled={!!joining} className="text-[10px] font-medium flex items-center gap-0.5 transition-opacity hover:opacity-80" style={{ color: c.color }} data-testid={`join-circle-${c.id}`}>
                {joining === c.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><ChevronLeft className="w-3 h-3" />Join</>}
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
