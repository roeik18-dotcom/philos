import { useState, useEffect, useMemo } from 'react';
import { Globe, ArrowDown, Activity } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionLabels = {
  contribution: 'Contribution', recovery: 'Recovery', order: 'Order', exploration: 'Exploration'
};
const directionColors = {
  contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b'
};

export default function FieldImpactLayer({ userId, actionCompleted, actionDirection }) {
  const [fieldData, setFieldData] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/orientation/globe-activity`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setFieldData(d); })
      .catch(() => {});
  }, [actionCompleted]);

  const stats = fieldData?.today_stats;
  const totalToday = stats?.total_actions || 0;
  const dominant = stats?.dominant_direction;
  const dominantHe = stats?.dominant_direction_he || '';
  const dirCounts = useMemo(() => stats?.direction_counts || {}, [stats]);

  // Calculate bar widths
  const maxCount = useMemo(() => Math.max(...Object.values(dirCounts), 1), [dirCounts]);

  return (
    <section className="philos-section bg-[#0a0a1a] text-white border-gray-800 animate-section animate-section-5" data-testid="field-impact-layer">
      {/* Narrative header */}
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-2">
          <Globe className="w-5 h-5 text-purple-400" />
          <span className="text-sm font-semibold">How does your action impact the world?</span>
        </div>
        <p className="text-xs text-gray-400 leading-relaxed">
          Every action you take is added to the global human field.
          <br />
          The field is the sum of all choices — yours and others.
        </p>
      </div>

      {/* Connection visual: action → field */}
      {actionCompleted && actionDirection && (
        <div className="flex flex-col items-center gap-1 mb-4 animate-fadeIn" data-testid="field-action-connection">
          <span className="text-xs px-3 py-1 rounded-full border border-white/20"
            style={{ color: directionColors[actionDirection], borderColor: `${directionColors[actionDirection]}40` }}>
            Your action: {directionLabels[actionDirection] || actionDirection}
          </span>
          <ArrowDown className="w-4 h-4 text-gray-500" />
          <span className="text-[10px] text-gray-500">Added to the field</span>
        </div>
      )}

      {/* Field state today */}
      {totalToday > 0 && (
        <div className="bg-white/5 rounded-2xl p-3 border border-white/10">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-purple-400" />
              <span className="text-xs text-gray-300">{totalToday} actions in the field today</span>
            </div>
            {dominantHe && (
              <span className="text-xs px-2 py-0.5 rounded-full" style={{
                color: directionColors[dominant],
                backgroundColor: `${directionColors[dominant]}15`
              }}>
                {dominantHe} Leading
              </span>
            )}
          </div>

          {/* Mini field bars */}
          <div className="space-y-2">
            {Object.entries(dirCounts).map(([dir, count]) => (
              <div key={dir} className="flex items-center gap-2">
                <span className="text-[10px] text-gray-400 w-14">{directionLabels[dir]}</span>
                <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{
                      width: `${(count / maxCount) * 100}%`,
                      backgroundColor: directionColors[dir]
                    }}
                  />
                </div>
                <span className="text-[10px] text-gray-500 w-6 text-left">{count}</span>
              </div>
            ))}
          </div>

          <p className="text-[10px] text-gray-500 mt-3 text-center">
            Go to the system to see the full globe
          </p>
        </div>
      )}

      {!totalToday && (
        <div className="text-center py-4 text-xs text-gray-500">
          The field awaits your first action of today
        </div>
      )}
    </section>
  );
}
