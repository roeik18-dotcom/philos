import { useState, useEffect } from 'react';
import { Target, Users, Zap } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionColors = {
  contribution: { color: '#22c55e', bg: 'from-green-50 to-emerald-50', border: 'border-green-200', text: 'text-green-700', bar: 'bg-green-500' },
  recovery: { color: '#3b82f6', bg: 'from-blue-50 to-sky-50', border: 'border-blue-200', text: 'text-blue-700', bar: 'bg-blue-500' },
  order: { color: '#6366f1', bg: 'from-indigo-50 to-violet-50', border: 'border-indigo-200', text: 'text-indigo-700', bar: 'bg-indigo-500' },
  exploration: { color: '#f59e0b', bg: 'from-amber-50 to-yellow-50', border: 'border-amber-200', text: 'text-amber-700', bar: 'bg-amber-500' }
};

export default function FieldMissionSection({ missionContributed }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchMission = async () => {
    try {
      const res = await fetch(`${API_URL}/api/orientation/mission-today`);
      if (res.ok) {
        const json = await res.json();
        if (json.success) setData(json);
      }
    } catch (e) {
      console.log('Could not fetch mission:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchMission(); }, []);

  // Refresh when user contributes
  useEffect(() => {
    if (missionContributed) fetchMission();
  }, [missionContributed]);

  if (loading) {
    return (
      <section className="bg-white rounded-3xl p-5 shadow-sm border border-border animate-pulse" dir="rtl">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-3"></div>
        <div className="h-3 bg-gray-200 rounded w-full mb-3"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </section>
    );
  }

  if (!data) return null;

  const style = directionColors[data.direction] || directionColors.contribution;

  return (
    <section
      className={`rounded-3xl p-5 shadow-sm border ${style.border} bg-gradient-to-br ${style.bg}`}
      dir="rtl"
      data-testid="field-mission-section"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-white/70 flex items-center justify-center">
            <Target className="w-5 h-5" style={{ color: style.color }} />
          </div>
          <span className={`text-sm font-bold ${style.text}`} data-testid="mission-title">
            {data.mission_he}
          </span>
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <Zap className="w-3 h-3" />
          <span>{data.progress_percent}%</span>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-700 mb-4" data-testid="mission-description">
        {data.description_he}
      </p>

      {/* Progress bar */}
      <div className="h-3 bg-white/60 rounded-full overflow-hidden mb-3" data-testid="mission-progress-bar">
        <div
          className={`h-full rounded-full transition-all duration-1000 ${style.bar}`}
          style={{ width: `${Math.max(data.progress_percent, 1)}%` }}
        />
      </div>

      {/* Stats */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-1 text-gray-600" data-testid="mission-participants">
          <Users className="w-3.5 h-3.5" />
          <span>{data.participants.toLocaleString('he-IL')} אנשים כבר השתתפו</span>
        </div>
        <span className="text-gray-400" data-testid="mission-target">
          יעד: {data.target.toLocaleString('he-IL')}
        </span>
      </div>

      {/* Contribution confirmation */}
      {missionContributed && (
        <div className="mt-3 p-2.5 bg-white/70 rounded-2xl text-center" data-testid="mission-contributed">
          <p className={`text-sm font-medium ${style.text}`}>
            הפעולה שלך תרמה למשימת היום
          </p>
        </div>
      )}
    </section>
  );
}
