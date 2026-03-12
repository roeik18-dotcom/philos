import { useState, useEffect } from 'react';
import { Crown, MapPin, Star } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function LeadersSection() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`${API_URL}/api/orientation/leaders`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.success) setData(d); })
      .catch(() => {});
  }, []);

  if (!data) return null;

  return (
    <section className="philos-section bg-white border-border" dir="rtl" data-testid="leaders-section">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-xl bg-amber-50 flex items-center justify-center">
          <Crown className="w-5 h-5 text-amber-600" />
        </div>
        <div>
          <span className="text-sm font-semibold text-gray-800">מובילי שדה</span>
          <p className="text-[10px] text-gray-400">המשפיעים הגדולים ביותר</p>
        </div>
      </div>

      <div className="space-y-1.5">
        {data.global_leaders.slice(0, 7).map((l, i) => (
          <div key={i} className="flex items-center gap-2 p-2 rounded-xl hover:bg-gray-50 transition-colors" data-testid={`leader-${i}`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${i < 3 ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-500'}`}>
              {i < 3 ? <Star className="w-3 h-3" /> : l.rank}
            </span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-semibold text-gray-800">{l.alias}</span>
                <span className="text-[9px] text-gray-400 flex items-center gap-0.5"><MapPin className="w-2 h-2" />{l.country}</span>
              </div>
              <span className="text-[9px] text-gray-400">{l.niche_he}</span>
            </div>
            <div className="text-left">
              <p className="text-xs font-bold text-gray-800">{Math.round(l.impact_score)}</p>
              <p className="text-[8px] text-gray-400">{l.actions} פעולות</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
