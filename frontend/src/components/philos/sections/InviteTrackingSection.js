import { useState, useEffect } from 'react';
import { Link, Eye, UserCheck, TrendingUp } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const funnelSteps = [
  { key: 'invites_sent', label: 'נשלחו', Icon: Link, color: '#6366f1' },
  { key: 'invites_opened', label: 'נפתחו', Icon: Eye, color: '#f59e0b' },
  { key: 'invites_accepted', label: 'התקבלו', Icon: UserCheck, color: '#22c55e' }
];

export default function InviteTrackingSection() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [animateBars, setAnimateBars] = useState(false);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await fetch(`${API_URL}/api/orientation/invite-report`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) {
            setData(json);
            setTimeout(() => setAnimateBars(true), 200);
          }
        }
      } catch (e) {
        console.log('Could not fetch invite report:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, []);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse" dir="rtl">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-24 bg-gray-200 rounded mb-3"></div>
      </section>
    );
  }

  if (!data) return null;

  const maxVal = Math.max(data.invites_sent, 1);

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-4" dir="rtl" data-testid="invite-tracking-section">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-xl bg-violet-50 flex items-center justify-center">
          <TrendingUp className="w-5 h-5 text-violet-600" />
        </div>
        <span className="text-sm font-medium text-violet-700">דוח המרת הזמנות</span>
      </div>

      {/* Funnel visualization */}
      <div className="space-y-3 mb-4">
        {funnelSteps.map(({ key, label, Icon, color }, index) => {
          const val = data[key] || 0;
          const pct = maxVal > 0 ? (val / maxVal) * 100 : 0;
          return (
            <div key={key} className="flex items-center gap-3" data-testid={`funnel-${key}`}>
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
                <Icon className="w-4 h-4" style={{ color }} />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-600">{label}</span>
                  <span className="text-xs font-bold" style={{ color }}>{val}</span>
                </div>
                <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-700 ease-out"
                    style={{
                      width: animateBars ? `${Math.max(pct, val > 0 ? 4 : 0)}%` : '0%',
                      backgroundColor: color,
                      transitionDelay: `${index * 150}ms`
                    }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Conversion rates */}
      <div className="grid grid-cols-3 gap-2 border-t border-gray-100 pt-3">
        <div className="text-center" data-testid="open-rate">
          <span className="text-lg font-bold text-amber-600">{data.open_rate}%</span>
          <p className="text-[10px] text-gray-500">פתיחה</p>
        </div>
        <div className="text-center" data-testid="accept-rate">
          <span className="text-lg font-bold text-green-600">{data.accept_rate}%</span>
          <p className="text-[10px] text-gray-500">קבלה</p>
        </div>
        <div className="text-center" data-testid="overall-conversion">
          <span className="text-lg font-bold text-violet-600">{data.overall_conversion}%</span>
          <p className="text-[10px] text-gray-500">המרה כוללת</p>
        </div>
      </div>
    </section>
  );
}
