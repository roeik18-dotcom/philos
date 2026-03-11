import { useState, useEffect } from 'react';
import { Radio, Heart, Shield, Compass, Lightbulb, MapPin } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionIcons = {
  contribution: Heart,
  recovery: Shield,
  order: Compass,
  exploration: Lightbulb
};

const directionColors = {
  contribution: '#22c55e',
  recovery: '#3b82f6',
  order: '#6366f1',
  exploration: '#f59e0b'
};

const directionLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  exploration: 'חקירה'
};

const countryFlags = {
  BR: '\u{1F1E7}\u{1F1F7}', IN: '\u{1F1EE}\u{1F1F3}', DE: '\u{1F1E9}\u{1F1EA}', US: '\u{1F1FA}\u{1F1F8}',
  JP: '\u{1F1EF}\u{1F1F5}', NG: '\u{1F1F3}\u{1F1EC}', IL: '\u{1F1EE}\u{1F1F1}', FR: '\u{1F1EB}\u{1F1F7}',
  AU: '\u{1F1E6}\u{1F1FA}', KR: '\u{1F1F0}\u{1F1F7}', MX: '\u{1F1F2}\u{1F1FD}', GB: '\u{1F1EC}\u{1F1E7}',
  CA: '\u{1F1E8}\u{1F1E6}', IT: '\u{1F1EE}\u{1F1F9}', ES: '\u{1F1EA}\u{1F1F8}', AR: '\u{1F1E6}\u{1F1F7}',
  TR: '\u{1F1F9}\u{1F1F7}', TH: '\u{1F1F9}\u{1F1ED}', PL: '\u{1F1F5}\u{1F1F1}', NL: '\u{1F1F3}\u{1F1F1}'
};

export default function OrientationFeedSection() {
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchFeed = async () => {
    try {
      const res = await fetch(`${API_URL}/api/orientation/feed`);
      if (res.ok) {
        const json = await res.json();
        if (json.success) setFeed(json.feed || []);
      }
    } catch (e) {
      console.log('Could not fetch feed:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeed();
    const interval = setInterval(fetchFeed, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse" dir="rtl">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-3"></div>
        <div className="space-y-2">
          {[1, 2, 3].map(i => <div key={i} className="h-8 bg-gray-100 rounded-xl"></div>)}
        </div>
      </section>
    );
  }

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-4" dir="rtl" data-testid="orientation-feed-section">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-cyan-50 flex items-center justify-center">
            <Radio className="w-5 h-5 text-cyan-600" />
          </div>
          <span className="text-sm font-medium text-cyan-700">פעילות השדה</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          <span className="text-[10px] text-gray-400">חי</span>
        </div>
      </div>

      {feed.length > 0 ? (
        <div className="space-y-1 max-h-56 overflow-y-auto" data-testid="feed-list">
          {feed.map((item, index) => {
            const Icon = directionIcons[item.direction] || Heart;
            const color = directionColors[item.direction] || '#8b5cf6';
            const label = directionLabels[item.direction] || item.direction;
            const flag = item.country_code ? countryFlags[item.country_code] : null;
            return (
              <div
                key={index}
                className="flex items-center gap-2.5 py-1.5 px-2 rounded-xl hover:bg-gray-50 transition-colors"
                style={{ animation: `fadeInUp 0.3s ease ${Math.min(index, 10) * 40}ms both` }}
                data-testid={`feed-item-${index}`}
              >
                <div className="w-6 h-6 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
                  <Icon className="w-3.5 h-3.5" style={{ color }} />
                </div>
                <span className="text-xs text-gray-600 flex-1">{label}</span>
                {flag && (
                  <span className="text-sm" data-testid={`feed-flag-${index}`}>{flag}</span>
                )}
                {item.location && !flag && (
                  <span className="flex items-center gap-0.5 text-[10px] text-gray-400">
                    <MapPin className="w-2.5 h-2.5" />
                    {item.location}
                  </span>
                )}
                <span className="text-[10px] text-gray-400 w-8 text-left" dir="ltr">{item.time}</span>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-6 text-gray-400">
          <Radio className="w-6 h-6 mx-auto mb-2 opacity-30" />
          <p className="text-xs">אין פעילות אחרונה</p>
        </div>
      )}
    </section>
  );
}
