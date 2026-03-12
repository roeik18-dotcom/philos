import { useState, useEffect } from 'react';
import { Compass, Zap, ArrowLeft } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const dirColors = { contribution: '#22c55e', recovery: '#3b82f6', order: '#6366f1', exploration: '#f59e0b' };

export default function EntryLayer({ userId }) {
  const [field, setField] = useState(null);
  const [compass, setCompass] = useState(null);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    fetch(`${API_URL}/api/orientation/field-dashboard`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setField(d); })
      .catch(() => {});

    if (effectiveUserId) {
      fetch(`${API_URL}/api/orientation/compass-ai/${effectiveUserId}`)
        .then(r => r.ok ? r.json() : null)
        .then(d => { if (d?.success) setCompass(d); })
        .catch(() => {});
    }
  }, [effectiveUserId]);

  const worldDir = field?.dominant_direction_he || 'חקירה';
  const worldColor = dirColors[field?.dominant_direction] || '#6366f1';
  const userForce = compass?.dominant_direction_he || null;
  const userColor = dirColors[compass?.dominant_direction] || '#6366f1';
  const suggested = compass?.suggested_action_he || 'בחר כיוון ופעל';

  const scrollToAction = () => {
    const el = document.querySelector('[data-testid="daily-orientation-question"]');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  return (
    <section className="relative rounded-3xl overflow-hidden bg-[#0a0a1a] text-white p-5 pb-6" dir="rtl" data-testid="entry-layer">
      <div className="absolute inset-0 pointer-events-none" style={{ background: `radial-gradient(ellipse at 50% 80%, ${worldColor}12 0%, transparent 60%)` }} />

      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-4 opacity-60">
          <Compass className="w-4 h-4" />
          <span className="text-xs tracking-wide">Philos Orientation</span>
        </div>

        {/* World direction */}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-[10px] text-gray-400">כיוון השדה היום</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold" style={{ backgroundColor: `${worldColor}20`, color: worldColor }} data-testid="entry-world-direction">
            <Zap className="w-2.5 h-2.5 inline mr-0.5" />{worldDir}
          </span>
          {field && <span className="text-[10px] text-gray-500">{field.total_actions_today} פעולות</span>}
        </div>

        {/* User's dominant force */}
        {userForce && (
          <div className="flex items-center gap-2 mb-3">
            <span className="text-[10px] text-gray-400">הכוח הדומיננטי שלך</span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold" style={{ backgroundColor: `${userColor}20`, color: userColor }} data-testid="entry-user-force">
              {userForce}
            </span>
          </div>
        )}

        {/* Recommended action */}
        <p className="text-base font-bold leading-relaxed mb-4" data-testid="entry-suggested-action">
          {suggested}
        </p>

        {/* CTA */}
        <button
          onClick={scrollToAction}
          className="flex items-center gap-2 px-4 py-2.5 rounded-2xl font-medium text-sm transition-all active:scale-[0.97]"
          style={{ backgroundColor: `${worldColor}20`, color: worldColor }}
          data-testid="entry-cta"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>התחל פעולה</span>
        </button>

        <div className="flex items-center gap-2 pt-3 mt-3 border-t border-white/10">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
          <span className="text-xs text-gray-500">בחר כיוון. פעל. השפע.</span>
        </div>
      </div>
    </section>
  );
}
