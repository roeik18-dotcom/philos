import { useState, useEffect } from 'react';
import { Zap } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };

export default function GlobalFieldDashboard() {
  const [data, setData] = useState(null);
  const [count, setCount] = useState(0);

  const fetchField = () => {
    fetch(`${API_URL}/api/orientation/field-dashboard`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setData(d); })
      .catch(() => {});
  };

  useEffect(() => { fetchField(); const i = setInterval(fetchField, 30000); return () => clearInterval(i); }, []);

  useEffect(() => {
    if (!data) return;
    const target = data.total_actions_today;
    if (count === target) return;
    const step = Math.max(1, Math.ceil(Math.abs(target - count) / 15));
    const t = setTimeout(() => setCount(prev => prev < target ? Math.min(prev + step, target) : Math.max(prev - step, target)), 50);
    return () => clearTimeout(t);
  }, [data, count]);

  if (!data) return null;
  const domColor = dirColors[data.dominant_direction] || '#6366f1';

  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-[#0a0a1a] rounded-2xl border border-gray-800" dir="rtl" data-testid="global-field-dashboard">
      <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse flex-shrink-0" />
      <span className="text-[10px] text-gray-400">שדה:</span>
      <span className="text-[10px] font-bold tabular-nums" style={{ color: domColor }} data-testid="field-action-count">{count.toLocaleString()}</span>
      <span className="text-[10px] text-gray-500">פעולות</span>
      <span className="text-gray-700">·</span>
      <Zap className="w-2.5 h-2.5 flex-shrink-0" style={{ color: domColor }} />
      <span className="text-[10px] font-medium" style={{ color: domColor }}>{data.dominant_direction_he}</span>
      <span className="text-gray-700">·</span>
      <span className="text-[10px] text-gray-500">{data.active_regions} אזורים</span>
    </div>
  );
}
