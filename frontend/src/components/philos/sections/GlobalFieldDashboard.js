import { useState, useEffect } from 'react';
import { Globe, TrendingUp, MapPin, Zap } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };

export default function GlobalFieldDashboard() {
  const [data, setData] = useState(null);
  const [displayCount, setDisplayCount] = useState(0);

  const fetchField = () => {
    fetch(`${API_URL}/api/orientation/field-dashboard`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setData(d); })
      .catch(() => {});
  };

  useEffect(() => {
    fetchField();
    const interval = setInterval(fetchField, 30000);
    return () => clearInterval(interval);
  }, []);

  // Animate counter
  useEffect(() => {
    if (!data) return;
    const target = data.total_actions_today;
    if (displayCount === target) return;
    const step = Math.max(1, Math.ceil(Math.abs(target - displayCount) / 20));
    const timer = setTimeout(() => {
      setDisplayCount(prev => prev < target ? Math.min(prev + step, target) : Math.max(prev - step, target));
    }, 40);
    return () => clearTimeout(timer);
  }, [data, displayCount]);

  if (!data) return null;

  const domColor = dirColors[data.dominant_direction] || '#6366f1';

  return (
    <section className="relative bg-[#0a0a1a] rounded-3xl p-5 text-white border border-gray-800 animate-section animate-section-1" dir="rtl" data-testid="global-field-dashboard">
      <div className="absolute inset-0 pointer-events-none rounded-3xl" style={{ background: `radial-gradient(ellipse at 30% 50%, ${domColor}10 0%, transparent 50%)` }} />

      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-4">
          <Globe className="w-5 h-5 text-purple-400" />
          <span className="text-sm font-bold">שדה גלובלי</span>
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          <span className="text-[9px] text-green-400">חי</span>
          <span className="mr-auto text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1" style={{ backgroundColor: `${domColor}20`, color: domColor }}>
            <Zap className="w-2.5 h-2.5" /> {data.momentum_he}
          </span>
        </div>

        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="text-center">
            <p className="text-2xl font-black tabular-nums" style={{ color: domColor }} data-testid="field-action-count">{displayCount.toLocaleString()}</p>
            <p className="text-[9px] text-gray-400">פעולות היום</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-bold" style={{ color: domColor }}>{data.dominant_direction_he}</p>
            <p className="text-[9px] text-gray-400">כיוון מוביל</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-bold text-white">{data.active_regions}</p>
            <p className="text-[9px] text-gray-400">אזורים פעילים</p>
          </div>
        </div>

        <div className="flex gap-1 mb-3 h-2 rounded-full overflow-hidden bg-white/5">
          {Object.entries(data.direction_counts).map(([d, c]) => (
            <div key={d} className="h-full transition-all duration-500" style={{ width: `${data.total_actions_today > 0 ? (c / data.total_actions_today) * 100 : 25}%`, backgroundColor: dirColors[d] }} />
          ))}
        </div>

        <div className="flex gap-2 flex-wrap">
          {data.top_regions.slice(0, 4).map(r => (
            <div key={r.code} className="flex items-center gap-1 text-[10px] text-gray-400 bg-white/5 px-2 py-1 rounded-full">
              <MapPin className="w-2.5 h-2.5" />
              <span>{r.name}</span>
              <span className="text-gray-500">{r.count}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
