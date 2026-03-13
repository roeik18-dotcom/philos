import { useState, useEffect } from 'react';
import { Flame, Trophy } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function CommunityStreakSection() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/api/orientation/streaks`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) setData(json);
        }
      } catch (e) {
        console.log('Could not fetch community streaks:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-3"></div>
        <div className="h-10 bg-gray-200 rounded w-2/3"></div>
      </section>
    );
  }

  if (!data) return null;

  return (
    <section className="philos-section animate-section animate-section-7 bg-gradient-to-br from-orange-50 to-amber-50 border-orange-200" data-testid="community-streak-section">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-8 h-8 rounded-xl bg-orange-100 flex items-center justify-center">
          <Flame className="w-5 h-5 text-orange-600" />
        </div>
        <span className="text-sm font-medium text-orange-700">Community Streak</span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <p className="text-base font-bold text-gray-800" data-testid="streak-users-message">
            {data.users_on_streak.toLocaleString('en-US')} people are on a streak today
          </p>
          {data.longest_streak_today > 0 && (
            <div className="flex items-center gap-1.5 mt-1.5">
              <Trophy className="w-3.5 h-3.5 text-amber-500" />
              <span className="text-xs text-gray-500" data-testid="longest-streak-value">
                Longest streak: {data.longest_streak_today} days
              </span>
            </div>
          )}
        </div>
        <div className="text-3xl font-black text-orange-500 opacity-80 animate-glow-in" data-testid="streak-users-count">
          {data.users_on_streak}
        </div>
      </div>
    </section>
  );
}
