import { useState, useEffect } from 'react';
import { ArrowLeftRight } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const oppositions = [
  { left: 'סדר', right: 'כאוס', leftDir: 'order', rightDir: 'exploration', leftColor: '#6366f1', rightColor: '#f59e0b',
    desc: 'בין מבנה ליציבות — לבין חופש וגילוי' },
  { left: 'התאוששות', right: 'דלדול', leftDir: 'recovery', rightDir: null, leftColor: '#3b82f6', rightColor: '#ef4444',
    desc: 'בין שיקום פנימי — לבין שחיקה והתעלמות' },
  { left: 'תרומה', right: 'נסיגה', leftDir: 'contribution', rightDir: null, leftColor: '#22c55e', rightColor: '#9ca3af',
    desc: 'בין נתינה לעולם — לבין הסתגרות בעצמי' },
  { left: 'חקירה', right: 'קיבעון', leftDir: 'exploration', rightDir: null, leftColor: '#f59e0b', rightColor: '#6b7280',
    desc: 'בין סקרנות ופתיחות — לבין חזרה על המוכר' }
];

export default function OppositionLayer({ userId }) {
  const [compass, setCompass] = useState(null);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    if (!effectiveUserId) return;
    fetch(`${API_URL}/api/orientation/daily-opening/${effectiveUserId}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setCompass(d.compass_state); })
      .catch(() => {});
  }, [effectiveUserId]);

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-3" dir="rtl" data-testid="opposition-layer">
      <div className="flex items-center gap-2 mb-1">
        <div className="w-8 h-8 rounded-xl bg-slate-100 flex items-center justify-center">
          <ArrowLeftRight className="w-4 h-4 text-slate-600" />
        </div>
        <div>
          <span className="text-sm font-semibold text-gray-800">בין אילו קטבים אתה נע?</span>
        </div>
      </div>
      <p className="text-xs text-gray-400 mb-4 mr-10">הכוחות שמושכים אותך היום</p>

      <div className="space-y-3">
        {oppositions.map((o, i) => {
          const leftPct = compass?.[o.leftDir] || 25;
          const ratio = Math.max(15, Math.min(85, leftPct));

          return (
            <div key={i} className="group" data-testid={`opposition-pair-${i}`}>
              {/* Pole labels */}
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold" style={{ color: o.leftColor }}>{o.left}</span>
                <span className="text-xs font-bold" style={{ color: o.rightColor }}>{o.right}</span>
              </div>

              {/* Tension bar */}
              <div className="relative h-2 rounded-full bg-gray-100 overflow-hidden">
                <div
                  className="absolute inset-y-0 left-0 rounded-full transition-all duration-700 ease-out"
                  style={{
                    width: `${ratio}%`,
                    background: `linear-gradient(90deg, ${o.leftColor}, ${o.leftColor}60)`
                  }}
                />
                {/* Center marker */}
                <div className="absolute top-0 bottom-0 left-1/2 w-px bg-gray-300" />
              </div>

              {/* Description */}
              <p className="text-[10px] text-gray-400 mt-1 leading-relaxed">{o.desc}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
