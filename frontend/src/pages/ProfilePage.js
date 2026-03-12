import { useState, useEffect } from 'react';
import { Compass, MapPin, Shield, Zap, Target, Award, ArrowRight, ChevronDown, ChevronUp, Loader2, Flame } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };
const dirLabels = { contribution: 'תרומה', recovery: 'התאוששות', order: 'סדר', exploration: 'חקירה' };

export default function ProfilePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedAction, setExpandedAction] = useState(null);

  const pathParts = window.location.pathname.split('/');
  const userId = pathParts[pathParts.length - 1];

  useEffect(() => {
    fetch(`${API_URL}/api/profile/${userId}/record`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setData(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#faf9f6] flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-[#faf9f6] flex flex-col items-center justify-center gap-3 px-4">
        <p className="text-sm text-gray-400">Record not found</p>
        <a href="/" className="text-xs text-indigo-500 hover:underline">Back to Philos</a>
      </div>
    );
  }

  const { identity, action_record, opposition_axes, value_growth, direction_distribution } = data;
  const dominantColor = dirColors[identity.dominant_direction] || '#6366f1';

  return (
    <div className="min-h-screen bg-[#faf9f6]" dir="rtl" data-testid="profile-page">
      {/* Top bar */}
      <div className="sticky top-0 z-10 bg-[#faf9f6]/90 backdrop-blur-sm border-b border-gray-100 px-4 py-2.5 flex items-center justify-between">
        <span className="text-[10px] tracking-widest text-gray-300 uppercase font-medium">Human Action Record</span>
        <a href="/" className="flex items-center gap-1 text-[10px] text-gray-400 hover:text-gray-600" data-testid="profile-back">
          <ArrowRight className="w-3 h-3" />Philos
        </a>
      </div>

      <div className="max-w-lg mx-auto px-4 py-6 space-y-6">
        <IdentityHeader identity={identity} dominantColor={dominantColor} />
        <OppositionAxes axes={opposition_axes} />
        <ValueGrowth growth={value_growth} dominantColor={dominantColor} />
        <DirectionBar distribution={direction_distribution} total={value_growth.total_actions} />
        <ActionRecord actions={action_record} expandedAction={expandedAction} setExpandedAction={setExpandedAction} />
      </div>
    </div>
  );
}


function IdentityHeader({ identity, dominantColor }) {
  const initial = identity.alias?.charAt(0) || '?';
  return (
    <section className="text-center" data-testid="profile-identity">
      <div className="w-16 h-16 mx-auto rounded-2xl flex items-center justify-center text-white text-xl font-bold mb-3 shadow-lg" style={{ backgroundColor: dominantColor }}>
        {initial}
      </div>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">{identity.alias}</h1>
      <div className="flex items-center justify-center gap-2 text-xs text-gray-400 mb-2">
        <span className="flex items-center gap-0.5"><MapPin className="w-3 h-3" />{identity.country}</span>
        <span className="text-gray-200">|</span>
        <span>חבר מ-{new Date(identity.member_since).toLocaleDateString('he-IL', { month: 'short', year: 'numeric' })}</span>
      </div>
      <div className="flex items-center justify-center gap-2 flex-wrap">
        {identity.dominant_direction_he && (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold" style={{ backgroundColor: `${dominantColor}12`, color: dominantColor }} data-testid="profile-direction-badge">
            {identity.dominant_direction_he}
          </span>
        )}
        {identity.niche_label_he && (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-purple-50 text-purple-600" data-testid="profile-niche-badge">
            {identity.niche_label_he}
          </span>
        )}
      </div>
    </section>
  );
}


function OppositionAxes({ axes }) {
  const axisData = [
    { key: 'chaos_order', leftLabel: 'כאוס', rightLabel: 'סדר', leftColor: '#f59e0b', rightColor: '#6366f1' },
    { key: 'ego_collective', leftLabel: 'אגו', rightLabel: 'קולקטיב', leftColor: '#ef4444', rightColor: '#22c55e' },
    { key: 'exploration_stability', leftLabel: 'חקירה', rightLabel: 'יציבות', leftColor: '#f59e0b', rightColor: '#3b82f6' }
  ];

  return (
    <section className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm" data-testid="profile-opposition-axes">
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-4 h-4 text-gray-600" />
        <h2 className="text-sm font-bold text-gray-800">ציר הניגודים</h2>
      </div>
      <div className="space-y-4">
        {axisData.map(axis => {
          const value = axes[axis.key] ?? 50;
          return (
            <div key={axis.key} data-testid={`axis-${axis.key}`}>
              <div className="flex justify-between text-[10px] mb-1.5">
                <span className="font-semibold" style={{ color: axis.leftColor }}>{axis.leftLabel}</span>
                <span className="font-semibold" style={{ color: axis.rightColor }}>{axis.rightLabel}</span>
              </div>
              <div className="relative h-2.5 bg-gray-100 rounded-full overflow-hidden">
                <div className="absolute top-0 h-full rounded-full transition-all duration-500" style={{ right: 0, width: `${value}%`, background: `linear-gradient(to left, ${axis.rightColor}, ${axis.rightColor}40)` }} />
                <div className="absolute top-0 w-3.5 h-3.5 -mt-[2px] rounded-full bg-white border-2 shadow-sm transition-all duration-500" style={{ right: `calc(${value}% - 7px)`, borderColor: value > 50 ? axis.rightColor : axis.leftColor }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}


function ValueGrowth({ growth, dominantColor }) {
  return (
    <section className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm" data-testid="profile-value-growth">
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-4 h-4 text-gray-600" />
        <h2 className="text-sm font-bold text-gray-800">צמיחת ערך</h2>
      </div>
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-xl">
          <p className="text-lg font-bold" style={{ color: dominantColor }}>{growth.impact_score}</p>
          <p className="text-[9px] text-gray-400">השפעה</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-xl">
          <p className="text-lg font-bold text-gray-800">Lv.{growth.level}</p>
          <p className="text-[9px] text-gray-400">דרגה</p>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-xl">
          <p className="text-lg font-bold text-gray-800">{growth.circle_memberships}</p>
          <p className="text-[9px] text-gray-400">מעגלים</p>
        </div>
      </div>
      <div className="space-y-2.5">
        <ProgressRow label="התקדמות דרגה" value={growth.level_progress} color={dominantColor} />
        {growth.niche_progress > 0 && <ProgressRow label="התקדמות נישה" value={growth.niche_progress} color="#a855f7" />}
      </div>
      <div className="flex items-center gap-3 mt-3 pt-3 border-t border-gray-50">
        {growth.streak > 0 && (
          <span className="flex items-center gap-1 text-[10px] text-orange-500 font-medium" data-testid="profile-streak">
            <Flame className="w-3 h-3" />{growth.streak} ימים רצף
          </span>
        )}
        {growth.badges?.length > 0 && (
          <span className="flex items-center gap-1 text-[10px] text-amber-500 font-medium">
            <Award className="w-3 h-3" />{growth.badges.length} תגים
          </span>
        )}
        <span className="flex items-center gap-1 text-[10px] text-gray-400">
          <Zap className="w-3 h-3" />{growth.total_actions} פעולות
        </span>
      </div>
    </section>
  );
}


function DirectionBar({ distribution, total }) {
  if (!total) return null;
  const dirs = ['contribution', 'recovery', 'order', 'exploration'];
  return (
    <section data-testid="profile-direction-bar">
      <div className="flex h-2 rounded-full overflow-hidden">
        {dirs.map(d => {
          const pct = (distribution[d] || 0) / total * 100;
          return pct > 0 ? <div key={d} style={{ width: `${pct}%`, backgroundColor: dirColors[d] }} className="transition-all" /> : null;
        })}
      </div>
      <div className="flex justify-between mt-1.5">
        {dirs.map(d => (
          <span key={d} className="text-[9px] flex items-center gap-0.5" style={{ color: dirColors[d] }}>
            <span className="w-1.5 h-1.5 rounded-full inline-block" style={{ backgroundColor: dirColors[d] }} />
            {dirLabels[d]} {distribution[d] || 0}
          </span>
        ))}
      </div>
    </section>
  );
}


function ActionRecord({ actions, expandedAction, setExpandedAction }) {
  if (!actions?.length) {
    return (
      <section className="text-center py-8">
        <p className="text-sm text-gray-400">אין פעולות מתועדות עדיין</p>
      </section>
    );
  }

  return (
    <section data-testid="profile-action-record">
      <div className="flex items-center gap-2 mb-3">
        <Compass className="w-4 h-4 text-gray-600" />
        <h2 className="text-sm font-bold text-gray-800">רשומת פעולות</h2>
        <span className="text-[10px] text-gray-300 mr-auto">{actions.length} פעולות</span>
      </div>
      <div className="space-y-2">
        {actions.map((a, i) => {
          const color = dirColors[a.direction] || '#6366f1';
          const isExpanded = expandedAction === i;
          const dateStr = a.date ? new Date(a.date).toLocaleDateString('he-IL', { day: 'numeric', month: 'short' }) : '';
          return (
            <div key={i} className="bg-white rounded-xl border border-gray-100 overflow-hidden transition-all shadow-sm" data-testid={`action-record-${i}`}>
              <button className="w-full flex items-center gap-2.5 p-3 text-right" onClick={() => setExpandedAction(isExpanded ? null : i)}>
                <div className="w-1 h-8 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <span className="text-[10px] font-semibold" style={{ color }}>{a.direction_he}</span>
                    <span className="text-[9px] text-gray-300">{dateStr}</span>
                  </div>
                  <p className="text-xs text-gray-700 truncate">{a.action_he}</p>
                </div>
                <span className="text-xs font-bold flex-shrink-0" style={{ color }}>+{a.impact}</span>
                {isExpanded ? <ChevronUp className="w-3.5 h-3.5 text-gray-300 flex-shrink-0" /> : <ChevronDown className="w-3.5 h-3.5 text-gray-300 flex-shrink-0" />}
              </button>
              {isExpanded && (
                <div className="px-3 pb-3 pt-0 border-t border-gray-50" data-testid={`action-meanings-${i}`}>
                  <p className="text-[9px] text-gray-300 mb-2 mt-2">פרשנות רב-ממדית</p>
                  <div className="grid grid-cols-2 gap-1.5">
                    <MeaningCard label="אישי" text={a.meanings.personal_he} color="#6366f1" />
                    <MeaningCard label="חברתי" text={a.meanings.social_he} color="#22c55e" />
                    <MeaningCard label="ערכי" text={a.meanings.value_he} color="#f59e0b" />
                    <MeaningCard label="מערכתי" text={a.meanings.system_he} color="#3b82f6" />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}


function MeaningCard({ label, text, color }) {
  return (
    <div className="p-2 rounded-lg" style={{ backgroundColor: `${color}06`, border: `1px solid ${color}15` }}>
      <p className="text-[9px] font-semibold mb-0.5" style={{ color }}>{label}</p>
      <p className="text-[9px] text-gray-600 leading-relaxed">{text}</p>
    </div>
  );
}


function ProgressRow({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between text-[10px] mb-1">
        <span className="text-gray-500">{label}</span>
        <span className="font-semibold" style={{ color }}>{value}%</span>
      </div>
      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all" style={{ width: `${value}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}
