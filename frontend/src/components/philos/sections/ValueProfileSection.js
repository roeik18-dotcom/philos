import { useState, useEffect } from 'react';
import { Award, TrendingUp, Shield, Zap, Star, ChevronLeft, Lock } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };
const dirLabels = { contribution: 'תרומה', recovery: 'התאוששות', order: 'סדר', exploration: 'חקירה' };

export default function ValueProfileSection({ userId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    if (!effectiveUserId) { setLoading(false); return; }
    fetch(`${API_URL}/api/orientation/value-profile/${effectiveUserId}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setData(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [effectiveUserId]);

  if (loading || !data) return null;

  const { value_scores, niche, next_niche, progression, stats, leader_status } = data;
  const maxScore = Math.max(value_scores.internal, value_scores.external, value_scores.collective, 1);

  return (
    <section className="philos-section bg-white border-border" dir="rtl" data-testid="value-profile-section">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-emerald-50 flex items-center justify-center">
            <Award className="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <span className="text-sm font-semibold text-gray-800">פרופיל ערך</span>
            <p className="text-[10px] text-gray-400">רמה {progression.level}</p>
          </div>
        </div>
        <div className="text-left">
          <p className="text-lg font-bold text-gray-800">{value_scores.total}</p>
          <p className="text-[9px] text-gray-400">ערך כולל</p>
        </div>
      </div>

      {/* Level progress */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] text-gray-400">רמה {progression.level}</span>
          <span className="text-[10px] text-gray-400">{progression.total_actions}/{progression.next_level_at}</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div className="h-full bg-emerald-500 rounded-full transition-all duration-700" style={{ width: `${progression.level_progress}%` }} />
        </div>
      </div>

      {/* Value breakdown bars */}
      <div className="space-y-2 mb-4">
        {[
          { label: 'ערך פנימי', value: value_scores.internal, color: '#3b82f6', icon: Shield },
          { label: 'ערך חיצוני', value: value_scores.external, color: '#22c55e', icon: TrendingUp },
          { label: 'ערך קולקטיבי', value: value_scores.collective, color: '#8b5cf6', icon: Zap }
        ].map(({ label, value, color, icon: Icon }) => (
          <div key={label} className="flex items-center gap-2">
            <Icon className="w-3.5 h-3.5" style={{ color }} />
            <span className="text-[10px] text-gray-500 w-20">{label}</span>
            <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full rounded-full transition-all duration-500" style={{ width: `${(value / maxScore) * 100}%`, backgroundColor: color }} />
            </div>
            <span className="text-[10px] font-medium text-gray-700 w-8 text-left">{value}</span>
          </div>
        ))}
      </div>

      {/* Niche */}
      {niche && (
        <div className="bg-gray-50 rounded-xl p-3 mb-3" data-testid="value-niche">
          <div className="flex items-center gap-2 mb-1">
            <Star className="w-4 h-4 text-amber-500" />
            <span className="text-sm font-semibold text-gray-800">{niche.label_he}</span>
            {leader_status && <span className="text-[9px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full">מוביל</span>}
          </div>
          <p className="text-xs text-gray-500 mb-2">{niche.description_he}</p>
          <div className="flex flex-wrap gap-1">
            {niche.strengthening_actions_he?.map((a, i) => (
              <span key={i} className="text-[9px] bg-white border border-gray-200 rounded-full px-2 py-0.5 text-gray-600">{a}</span>
            ))}
          </div>
        </div>
      )}

      {/* Next niche */}
      {next_niche && (
        <div className="flex items-center gap-2 p-2 bg-purple-50 rounded-xl mb-3" data-testid="value-next-niche">
          <ChevronLeft className="w-3.5 h-3.5 text-purple-500" />
          <span className="text-[10px] text-purple-700">הנישה הבאה: <strong>{next_niche.label_he}</strong></span>
        </div>
      )}

      {/* Badges */}
      {progression.badges.length > 0 && (
        <div data-testid="value-badges">
          <p className="text-[10px] text-gray-400 mb-2">תגים</p>
          <div className="flex flex-wrap gap-1.5">
            {progression.badges.map((b) => (
              <div key={b.id} className="flex items-center gap-1 bg-amber-50 border border-amber-200 rounded-full px-2 py-1" data-testid={`badge-${b.id}`}>
                <Award className="w-3 h-3 text-amber-500" />
                <span className="text-[10px] font-medium text-amber-800">{b.label_he}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
