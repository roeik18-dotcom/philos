import { useState, useEffect } from 'react';
import { Users, Flame } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ActiveUsersIndicator() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/api/orientation/active-users`);
        if (res.ok) {
          const json = await res.json();
          if (json.success) setData(json);
        }
      } catch (e) {
        console.log('Could not fetch active users:', e);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  if (!data) return null;

  return (
    <div className="flex items-center justify-center gap-4 text-xs text-gray-500" dir="rtl" data-testid="active-users-indicator">
      <div className="flex items-center gap-1">
        <Users className="w-3.5 h-3.5 text-teal-500" />
        <span data-testid="active-users-count">
          {data.active_users_today.toLocaleString('he-IL')} משתמשים פעילים היום
        </span>
      </div>
      {data.active_streak_users > 0 && (
        <div className="flex items-center gap-1">
          <Flame className="w-3.5 h-3.5 text-orange-500" />
          <span data-testid="active-streak-count">
            {data.active_streak_users.toLocaleString('he-IL')} ברצף
          </span>
        </div>
      )}
    </div>
  );
}
