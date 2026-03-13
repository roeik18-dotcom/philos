import { useState, useEffect } from 'react';
import { Award } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const directionLabels = {
  recovery: 'Recovery',
  order: 'Order',
  contribution: 'Contribution',
  exploration: 'Exploration'
};

const directionColors = {
  recovery: '#3b82f6',
  order: '#6366f1',
  contribution: '#22c55e',
  exploration: '#f59e0b'
};

export default function RelativeScoreSection({ userId }) {
  const [data, setData] = useState(null);
  const [animateBar, setAnimateBar] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    const fetchData = async () => {
      if (!effectiveUserId) return;
      try {
        const res = await fetch(`${API_URL}/api/orientation/relative-score/${effectiveUserId}`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) {
            setData(json);
            setTimeout(() => setAnimateBar(true), 200);
          }
        }
      } catch (e) {
        console.log('Could not fetch relative score:', e);
      }
    };
    fetchData();
  }, [effectiveUserId]);

  if (!data) return null;

  const color = directionColors[data.direction] || '#8b5cf6';

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-3" data-testid="relative-score-section">
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-2xl flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
          <Award className="w-6 h-6" style={{ color }} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-bold text-gray-800" data-testid="relative-score-message">
            You are more active than {data.percentile}% of users today
          </p>
          <p className="text-xs text-gray-500 mt-0.5">
            Leading direction: {directionLabels[data.direction] || data.direction}
          </p>
        </div>
        <div className="text-2xl font-black animate-glow-in" style={{ color }} data-testid="relative-score-percentile">
          {data.percentile}%
        </div>
      </div>

      {/* Animated percentile bar */}
      <div className="mt-3 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-1000 ease-out"
          style={{ width: animateBar ? `${Math.max(data.percentile, 2)}%` : '0%', backgroundColor: color }}
        />
      </div>
    </section>
  );
}
