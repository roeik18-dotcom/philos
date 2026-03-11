import { useState, useEffect } from 'react';
import { Heart, Shield, Lightbulb, Compass } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directions = [
  { key: 'contribution', label: 'תרומה', color: '#22c55e', bg: 'bg-green-50', Icon: Heart },
  { key: 'recovery', label: 'התאוששות', color: '#3b82f6', bg: 'bg-blue-50', Icon: Shield },
  { key: 'order', label: 'סדר', color: '#6366f1', bg: 'bg-indigo-50', Icon: Compass },
  { key: 'exploration', label: 'חקירה', color: '#f59e0b', bg: 'bg-amber-50', Icon: Lightbulb }
];

export default function OrientationCirclesSection() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/api/orientation/circles`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) {
            setData(json);
            setTimeout(() => setVisible(true), 100);
          }
        }
      } catch (e) {
        console.log('Could not fetch orientation circles:', e);
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
        <div className="grid grid-cols-2 gap-3">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-24 bg-gray-100 rounded-2xl"></div>)}
        </div>
      </section>
    );
  }

  if (!data) return null;

  const total = directions.reduce((sum, d) => sum + (data[d.key] || 0), 0) || 1;

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-6" dir="rtl" data-testid="orientation-circles-section">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-xl bg-pink-50 flex items-center justify-center">
          <Heart className="w-5 h-5 text-pink-500" />
        </div>
        <span className="text-sm font-medium text-pink-700">מעגלי התמצאות</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {directions.map(({ key, label, color, bg, Icon }, index) => {
          const count = data[key] || 0;
          const pct = Math.round((count / total) * 100);
          return (
            <div
              key={key}
              className={`${bg} rounded-2xl p-4 flex flex-col items-center gap-2 transition-all duration-300 hover:shadow-md hover:scale-[1.03] cursor-default`}
              style={{
                opacity: visible ? 1 : 0,
                transform: visible ? 'translateY(0)' : 'translateY(8px)',
                transition: `opacity 0.4s ease ${index * 100}ms, transform 0.4s ease ${index * 100}ms`
              }}
              data-testid={`circle-${key}`}
            >
              <Icon className="w-6 h-6" style={{ color }} />
              <span className="text-xl font-black" style={{ color }}>
                {count.toLocaleString('he-IL')}
              </span>
              <span className="text-xs text-gray-600">{label}</span>
              <span className="text-[10px] text-gray-400">{pct}%</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
