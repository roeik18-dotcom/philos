import { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const tensions = [
  { left: 'Order', right: 'Chaos', axisKey: 'chaos_order', leftColor: '#6366f1', rightColor: '#f59e0b',
    interpret: (v) => v > 60 ? 'You lean towards order — structure and security lead you' : v < 40 ? 'Chaos attracts you — freedom and discovery at the forefront' : 'You are between order and chaos — in both worlds' },
  { left: 'Collective', right: 'Ego', axisKey: 'ego_collective', leftColor: '#22c55e', rightColor: '#ef4444',
    interpret: (v) => v > 60 ? 'Giving is dominant — you act for others' : v < 40 ? 'You are focusing on yourself — internal recovery first' : 'Tension between inside and outside — both live in you' },
  { left: 'stability', right: 'Exploration', axisKey: 'exploration_stability', leftColor: '#3b82f6', rightColor: '#f59e0b',
    interpret: (v) => v > 60 ? 'You seek a stable base — root before movement' : v < 40 ? 'Exploration attracts you — discover new things' : 'Between roots and journey — both forces are equal' }
];

export default function OppositionLayer({ userId }) {
  const [axes, setAxes] = useState(null);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    if (!effectiveUserId) return;
    fetch(`${API_URL}/api/profile/${effectiveUserId}/record`)
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d?.success) {
          setAxes(d.opposition_axes);
          window.dispatchEvent(new CustomEvent('orientation-stage', { detail: { stage: 'opposition' } }));
        }
      })
      .catch(() => {});
  }, [effectiveUserId]);

  // Find the most active tension (furthest from center)
  const activeTension = axes ? tensions.reduce((best, t) => {
    const dist = Math.abs((axes[t.axisKey] ?? 50) - 50);
    return dist > best.dist ? { ...t, dist } : best;
  }, { dist: -1 }) : null;

  return (
    <section className="relative rounded-3xl overflow-hidden bg-[#0a0a1a] text-white p-5" data-testid="opposition-layer">
      {/* Ambient glow from dominant tension */}
      {activeTension?.dist > 0 && (
        <div className="absolute inset-0 pointer-events-none" style={{
          background: `radial-gradient(ellipse at 50% 100%, ${activeTension.leftColor}08 0%, transparent 60%)`
        }} />
      )}

      <div className="relative z-10">
        <p className="text-xs text-gray-500 mb-5">Between which poles you move</p>

        <div className="space-y-6">
          {tensions.map((t) => {
            const value = axes?.[t.axisKey] ?? 50;
            const interpretation = t.interpret(value);
            const dominantColor = value > 55 ? t.leftColor : value < 45 ? t.rightColor : '#6b7280';

            return (
              <div key={t.axisKey} data-testid={`tension-${t.axisKey}`}>
                {/* Pole labels */}
                <div className="flex items-center justify-between mb-2.5">
                  <span className="text-[11px] font-semibold" style={{ color: t.leftColor }}>{t.left}</span>
                  <span className="text-[11px] font-semibold" style={{ color: t.rightColor }}>{t.right}</span>
                </div>

                {/* Tension arc */}
                <div className="relative h-[3px] rounded-full bg-white/[0.06]">
                  {/* Left gradient fill */}
                  <div
                    className="absolute inset-y-0 right-0 rounded-full transition-all duration-1000 ease-out"
                    style={{
                      width: `${value}%`,
                      background: `linear-gradient(to left, ${t.leftColor}50, ${t.leftColor}10)`
                    }}
                  />
                  {/* Right gradient fill */}
                  <div
                    className="absolute inset-y-0 left-0 rounded-full transition-all duration-1000 ease-out"
                    style={{
                      width: `${100 - value}%`,
                      background: `linear-gradient(to right, ${t.rightColor}50, ${t.rightColor}10)`
                    }}
                  />
                  {/* Center line */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-px h-2 bg-white/10" />

                  {/* Personal position — glowing dot */}
                  <div
                    className="absolute top-1/2 -translate-y-1/2 transition-all duration-1000 ease-out"
                    style={{ right: `calc(${value}% - 5px)` }}
                  >
                    {/* Outer glow */}
                    <div className="absolute inset-0 -m-2 rounded-full opacity-40 animate-pulse" style={{ backgroundColor: `${dominantColor}30` }} />
                    {/* Dot */}
                    <div className="w-[10px] h-[10px] rounded-full border-2 border-[#0a0a1a]" style={{ backgroundColor: dominantColor, boxShadow: `0 0 8px ${dominantColor}60` }} />
                  </div>
                </div>

                {/* Interpretive line */}
                <p className="text-[10px] text-gray-500 mt-2 leading-relaxed" data-testid={`tension-interpret-${t.axisKey}`}>
                  {interpretation}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
