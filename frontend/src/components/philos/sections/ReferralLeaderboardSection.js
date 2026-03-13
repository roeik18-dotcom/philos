import { useState, useEffect } from 'react';
import { Trophy, Flame, Medal, Users } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const rankStyles = [
  { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', badge: 'bg-amber-400' },
  { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-600', badge: 'bg-gray-400' },
  { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700', badge: 'bg-orange-400' }
];

const defaultStyle = { bg: 'bg-white', border: 'border-gray-100', text: 'text-gray-600', badge: 'bg-gray-300' };

export default function ReferralLeaderboardSection() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/api/orientation/referral-leaderboard`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) {
            setData(json.leaderboard || []);
            setTimeout(() => setVisible(true), 100);
          }
        }
      } catch (e) {
        console.log('Could not fetch leaderboard:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <section className="philos-section bg-white border-border animate-pulse">
        <div className="h-5 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-2">
          {[1, 2, 3].map(i => <div key={i} className="h-14 bg-gray-100 rounded-2xl"></div>)}
        </div>
      </section>
    );
  }

  return (
    <section className="philos-section bg-white border-border animate-section animate-section-3" data-testid="referral-leaderboard-section">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-xl bg-amber-50 flex items-center justify-center">
          <Trophy className="w-5 h-5 text-amber-600" />
        </div>
        <span className="text-sm font-medium text-amber-700">Top Field Contributors</span>
      </div>

      {data.length > 0 ? (
        <div className="space-y-2" data-testid="leaderboard-list">
          {data.map((entry, index) => {
            const style = index < 3 ? rankStyles[index] : defaultStyle;
            const isTop3 = index < 3;
            return (
              <div
                key={index}
                className={`flex items-center gap-3 p-3 rounded-2xl border transition-all duration-300 hover:shadow-sm ${style.bg} ${style.border}`}
                style={{
                  opacity: visible ? 1 : 0,
                  transform: visible ? 'translateY(0)' : 'translateY(8px)',
                  transition: `opacity 0.4s ease ${index * 80}ms, transform 0.4s ease ${index * 80}ms`
                }}
                data-testid={`leaderboard-entry-${index}`}
              >
                {/* Rank */}
                <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold ${style.badge}`}>
                  {isTop3 ? <Medal className="w-4 h-4" /> : entry.rank}
                </div>

                {/* Alias */}
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-bold ${isTop3 ? style.text : 'text-gray-800'}`} data-testid={`alias-${index}`}>
                    {entry.user_alias}
                  </p>
                </div>

                {/* Streak */}
                {entry.streak > 0 && (
                  <div className="flex items-center gap-1 text-orange-500" data-testid={`streak-${index}`}>
                    <Flame className="w-3.5 h-3.5" />
                    <span className="text-xs font-bold">{entry.streak}</span>
                  </div>
                )}

                {/* Invite count */}
                <div className="flex items-center gap-1 bg-white/80 px-2.5 py-1 rounded-full border border-gray-200" data-testid={`invites-count-${index}`}>
                  <Users className="w-3 h-3 text-gray-500" />
                  <span className="text-xs font-bold text-gray-700">{entry.invites_count}</span>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-400">
          <Trophy className="w-8 h-8 mx-auto mb-2 opacity-30" />
          <p className="text-sm">No more invites. Invite people to the field!</p>
        </div>
      )}
    </section>
  );
}
