import { useState, useEffect } from 'react';
import { BookOpen, ChevronDown, ChevronUp, Sparkles, Users, Heart } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionMeta = {
  contribution: { icon: Users, colorClass: 'bg-green-50 text-green-700 border-green-200', accentBg: 'bg-green-100', barColor: '#22c55e' },
  recovery: { icon: Heart, colorClass: 'bg-blue-50 text-blue-700 border-blue-200', accentBg: 'bg-blue-100', barColor: '#3b82f6' },
  order: { icon: BookOpen, colorClass: 'bg-indigo-50 text-indigo-700 border-indigo-200', accentBg: 'bg-indigo-100', barColor: '#6366f1' },
  exploration: { icon: Sparkles, colorClass: 'bg-amber-50 text-amber-700 border-amber-200', accentBg: 'bg-amber-100', barColor: '#f59e0b' }
};

const dirOrder = ['contribution', 'recovery', 'order', 'exploration'];

export default function DirectionExplanationsSection() {
  const [directions, setDirections] = useState(null);
  const [expanded, setExpanded] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/api/orientation/directions`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) setDirections(json.directions);
        }
      } catch (e) {
        console.log('Could not fetch directions:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse" dir="rtl">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-16 bg-gray-200 rounded-xl"></div>)}
        </div>
      </section>
    );
  }

  if (!directions) return null;

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-4" dir="rtl" data-testid="direction-explanations-section">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-xl bg-slate-100 flex items-center justify-center">
          <BookOpen className="w-5 h-5 text-slate-600" />
        </div>
        <div>
          <span className="text-sm font-semibold text-gray-800">ארבעת הכיוונים</span>
          <p className="text-[10px] text-gray-400">משמעות סמלית, התנהגות אנושית, השפעה על השדה</p>
        </div>
      </div>

      <div className="space-y-2">
        {dirOrder.map((key) => {
          const dir = directions[key];
          if (!dir) return null;
          const meta = directionMeta[key];
          const Icon = meta.icon;
          const isOpen = expanded === key;

          return (
            <div key={key} className={`rounded-2xl border transition-all duration-300 ${meta.colorClass}`} data-testid={`direction-card-${key}`}>
              {/* Header row */}
              <button
                className="w-full flex items-center justify-between p-3 text-right"
                onClick={() => setExpanded(isOpen ? null : key)}
                data-testid={`direction-toggle-${key}`}
              >
                <div className="flex items-center gap-2">
                  <div className={`w-7 h-7 rounded-lg ${meta.accentBg} flex items-center justify-center`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-sm font-bold">{dir.label_he}</span>
                    <span className="text-[10px] opacity-60 mr-2">{dir.symbol}</span>
                  </div>
                </div>
                {isOpen ? <ChevronUp className="w-4 h-4 opacity-50" /> : <ChevronDown className="w-4 h-4 opacity-50" />}
              </button>

              {/* Expanded details */}
              {isOpen && (
                <div className="px-3 pb-3 space-y-2.5 animate-fadeIn">
                  {/* Symbolic Meaning */}
                  <div className="bg-white/60 rounded-xl p-2.5">
                    <p className="text-[10px] font-semibold opacity-60 mb-1">משמעות סמלית</p>
                    <p className="text-xs leading-relaxed">{dir.symbolic_meaning_he || dir.explanation_he}</p>
                  </div>

                  {/* Human Behavior Example */}
                  <div className="bg-white/60 rounded-xl p-2.5">
                    <p className="text-[10px] font-semibold opacity-60 mb-1">דוגמה להתנהגות</p>
                    <p className="text-xs leading-relaxed">{dir.behavior_example_he || dir.meaning_he}</p>
                  </div>

                  {/* Field Effect */}
                  <div className="bg-white/60 rounded-xl p-2.5">
                    <p className="text-[10px] font-semibold opacity-60 mb-1">השפעה על השדה הקולקטיבי</p>
                    <p className="text-xs leading-relaxed">{dir.field_effect_he || ''}</p>
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
