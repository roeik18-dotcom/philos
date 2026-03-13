import { useState, useEffect } from 'react';
import { Moon, TrendingUp, Flame, Globe, ArrowLeft } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionColors = {
  contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b'
};
const directionLabels = {
  recovery: 'Recovery', order: 'Order', contribution: 'Contribution', exploration: 'Exploration'
};
const deptColors = { heart: '#ef4444', head: '#6366f1', body: '#f59e0b' };
const deptLabels = { heart: 'Connection', head: 'Mind', body: 'Body' };

const tomorrowHints = {
  contribution: "Tomorrow, consider if there's room for recovery — constant giving requires recharging.",
  recovery: 'Tomorrow, when you feel ready, try going outward — a small act of contribution or exploration.',
  order: 'Tomorrow, after building structure, allow yourself a moment of exploration — discovering new things.',
  exploration: 'Tomorrow, try giving structure to what you discovered — order helps anchor exploration.'
};

const tensionNarratives = {
  contribution: { opposing: 'recovery', text_he: 'Recovery force is rising in the background. The field balances: when giving is strong, the need for rest grows.' },
  recovery: { opposing: 'contribution', text_he: 'The force of contribution awakens. Your recharging creates energy — tomorrow it will seek direction.' },
  order: { opposing: 'exploration', text_he: 'The force of exploration expands on the side. As order strengthens, the urge to discover grows.' },
  exploration: { opposing: 'order', text_he: 'The force of order solidifies. What you discovered today needs a framework — and it will draw you tomorrow.' }
};

const returnReasons = {
  contribution: 'Someone may continue what you started. Come back to see.',
  recovery: 'The energy you charged will turn into action. Come back to direct it.',
  order: 'The structure you built will affect the field. Come back to see how.',
  exploration: 'What you discovered is not over yet. Come back to continue.'
};

export default function ClosingLayer({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [animateBars, setAnimateBars] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    if (!effectiveUserId) { setLoading(false); return; }
    fetch(`${API_URL}/api/orientation/day-summary/${effectiveUserId}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d?.success) { setData(d); setTimeout(() => setAnimateBars(true), 200); }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [effectiveUserId]);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="h-20 bg-gray-200 rounded" />
      </section>
    );
  }

  if (!data) return null;

  const chosenDir = data.chosen_direction;
  const chosenEn = directionLabels[chosenDir] || '';
  const chosenColor = directionColors[chosenDir] || '#6366f1';

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-6" data-testid="closing-layer">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <div className="w-8 h-8 rounded-xl bg-violet-50 flex items-center justify-center">
          <Moon className="w-5 h-5 text-violet-600" />
        </div>
        <div>
          <span className="text-sm font-semibold text-gray-800">What changed today?</span>
          <p className="text-[10px] text-gray-400">{data.date}</p>
        </div>
      </div>

      {/* Reflection narrative */}
      <div className="bg-violet-50 rounded-2xl p-3 mb-4 border border-violet-100">
        <p className="text-sm text-violet-800 font-medium leading-relaxed" data-testid="closing-reflection">
          {data.reflection_he}
        </p>
      </div>

      {data.total_actions > 0 ? (
        <>
          {/* ═══ DEPARTMENT SUMMARY ═══ */}
          {data.chosen_base && (
            <div className="bg-[#0a0a1a] rounded-2xl p-3.5 mb-4" data-testid="closing-dept-summary">
              {/* Chosen base */}
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] text-gray-500">Your chosen base today</span>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: deptColors[data.chosen_base] }} />
                  <span className="text-xs font-semibold" style={{ color: deptColors[data.chosen_base] }}>
                    {data.chosen_base_he}
                  </span>
                </div>
              </div>

              {/* Energy allocation bars */}
              <div className="space-y-2 mb-3">
                {Object.entries(data.dept_allocation || {}).map(([dept, pct]) => (
                  <div key={dept} className="flex items-center gap-2">
                    <span className="text-[10px] w-6 text-right font-medium" style={{ color: deptColors[dept] }}>
                      {deptLabels[dept]}
                    </span>
                    <div className="flex-1 h-[3px] bg-white/[0.06] rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-1000 ease-out"
                        style={{
                          width: animateBars ? `${pct}%` : '0%',
                          backgroundColor: deptColors[dept],
                          opacity: 0.7
                        }}
                      />
                    </div>
                    <span className="text-[9px] text-gray-600 w-7 text-left tabular-nums">{pct}%</span>
                  </div>
                ))}
              </div>

              {/* Department insights — compact row */}
              <div className="flex gap-2">
                {data.most_used_dept && (
                  <div className="flex-1 rounded-xl p-2 text-center" style={{ backgroundColor: `${deptColors[data.most_used_dept]}08` }} data-testid="closing-most-used-dept">
                    <p className="text-[9px] text-gray-500 mb-0.5">Most active</p>
                    <p className="text-[10px] font-semibold" style={{ color: deptColors[data.most_used_dept] }}>{data.most_used_dept_he}</p>
                  </div>
                )}
                {data.preferred_dept && (
                  <div className="flex-1 rounded-xl p-2 text-center" style={{ backgroundColor: `${deptColors[data.preferred_dept]}08` }} data-testid="closing-preferred-dept">
                    <p className="text-[9px] text-gray-500 mb-0.5">Preferred</p>
                    <p className="text-[10px] font-semibold" style={{ color: deptColors[data.preferred_dept] }}>{data.preferred_dept_he}</p>
                  </div>
                )}
                {data.neglected_dept && (
                  <div className="flex-1 rounded-xl p-2 text-center bg-white/[0.03]" data-testid="closing-neglected-dept">
                    <p className="text-[9px] text-gray-500 mb-0.5">Neglected</p>
                    <p className="text-[10px] font-semibold text-gray-400">{data.neglected_dept_he}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Base reflection — observational sentence */}
          {data.base_reflection_he && (
            <p className="text-xs text-gray-500 leading-relaxed mb-4 px-1" data-testid="closing-base-reflection">
              {data.base_reflection_he}
            </p>
          )}

          {/* Direction moved */}
          <div className="flex items-center gap-2 mb-3 p-2.5 rounded-xl" style={{ backgroundColor: `${chosenColor}08`, border: `1px solid ${chosenColor}20` }}>
            <ArrowLeft className="w-4 h-4" style={{ color: chosenColor }} />
            <div>
              <p className="text-sm font-semibold" style={{ color: chosenColor }}>
                You moved in the direction of: {chosenEn}
              </p>
              <p className="text-[10px] text-gray-500">The dominant direction of your actions today</p>
            </div>
          </div>

          {/* Stats row */}
          <div className="flex gap-2 mb-4">
            <div className="flex-1 bg-orange-50 rounded-xl p-2 text-center border border-orange-100" data-testid="closing-streak">
              <Flame className="w-3.5 h-3.5 text-orange-500 mx-auto mb-0.5" />
              <p className="text-base font-bold text-orange-700">{data.streak}</p>
              <p className="text-[9px] text-orange-500">Streak</p>
            </div>
            <div className="flex-1 bg-emerald-50 rounded-xl p-2 text-center border border-emerald-100" data-testid="closing-impact">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-500 mx-auto mb-0.5" />
              <p className="text-base font-bold text-emerald-700">{data.impact_on_field}%</p>
              <p className="text-[9px] text-emerald-500">Impact</p>
            </div>
            <div className="flex-1 bg-blue-50 rounded-xl p-2 text-center border border-blue-100" data-testid="closing-actions">
              <Globe className="w-3.5 h-3.5 text-blue-500 mx-auto mb-0.5" />
              <p className="text-base font-bold text-blue-700">{data.total_actions}</p>
              <p className="text-[9px] text-blue-500">actions</p>
            </div>
          </div>

          {/* Field effect bars */}
          <div className="mb-4">
            <p className="text-[10px] text-gray-400 mb-2 flex items-center gap-1">
              <Globe className="w-3 h-3" /> Change in the global field
            </p>
            <div className="space-y-1.5">
              {Object.entries(data.global_field_effect || {}).map(([dir, pct], i) => (
                <div key={dir} className="flex items-center gap-2">
                  <span className="text-[10px] text-gray-500 w-14">{directionLabels[dir]}</span>
                  <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700 ease-out"
                      style={{
                        width: animateBars ? `${pct}%` : '0%',
                        backgroundColor: directionColors[dir],
                        transitionDelay: `${i * 80}ms`
                      }}
                    />
                  </div>
                  <span className="text-[10px] font-medium text-gray-600 w-8 text-left">{pct}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Tomorrow hint */}
          {chosenDir && tomorrowHints[chosenDir] && (
            <div className="bg-gray-50 rounded-xl p-3 border border-gray-100 mb-3" data-testid="closing-tomorrow">
              <p className="text-[10px] text-gray-400 mb-1">Looking ahead to tomorrow</p>
              <p className="text-xs text-gray-600 leading-relaxed">{tomorrowHints[chosenDir]}</p>
            </div>
          )}

          {/* Tension narrative */}
          {chosenDir && tensionNarratives[chosenDir] && (
            <div className="rounded-xl p-3 border mb-3" style={{ backgroundColor: `${directionColors[tensionNarratives[chosenDir].opposing]}06`, borderColor: `${directionColors[tensionNarratives[chosenDir].opposing]}20` }} data-testid="closing-tension">
              <p className="text-[10px] font-semibold mb-1" style={{ color: directionColors[tensionNarratives[chosenDir].opposing] }}>Rising tension</p>
              <p className="text-xs text-gray-600 leading-relaxed">{tensionNarratives[chosenDir].text_he}</p>
            </div>
          )}

          {/* Return hook */}
          {chosenDir && returnReasons[chosenDir] && (
            <div className="bg-[#0a0a1a] rounded-xl p-3 text-center" data-testid="closing-return-hook">
              <p className="text-xs text-gray-300 leading-relaxed">{returnReasons[chosenDir]}</p>
              <div className="flex items-center justify-center gap-1.5 mt-2">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
                <span className="text-[10px] text-indigo-400 font-medium">The field keeps changing</span>
              </div>
            </div>
          )}
        </>
      ) : null}
    </section>
  );
}
