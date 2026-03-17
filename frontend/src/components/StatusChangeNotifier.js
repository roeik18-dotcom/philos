import { useEffect, useRef } from 'react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const STORAGE_KEY = 'philos_last_status_';

const STATUS_MESSAGES = {
  rising: {
    up: (prev) => `Your status improved from ${prev} to Rising — your actions are getting boosted.`,
    neutral: () => 'Your position is now Rising — your actions are getting a visibility boost.',
  },
  stable: {
    up: (prev) => `You recovered from ${prev} to Stable — your visibility is back to normal.`,
    neutral: () => 'Your position is now Stable.',
  },
  decaying: {
    down: (prev) => `Your status dropped from ${prev} to Decaying — your actions are losing visibility.`,
    neutral: () => 'Your position is now Decaying — take action to recover.',
  },
  atRisk: {
    down: (prev) => `Your status dropped to At Risk — your actions have reduced visibility. Take action to recover.`,
    neutral: () => 'Your status is At Risk — take action to recover.',
  },
};

const STATUS_ORDER = { atRisk: 0, decaying: 1, stable: 2, rising: 3 };

function getDirection(prev, next) {
  const prevRank = STATUS_ORDER[prev] ?? -1;
  const nextRank = STATUS_ORDER[next] ?? -1;
  if (nextRank > prevRank) return 'up';
  if (nextRank < prevRank) return 'down';
  return 'neutral';
}

function getStatusLabel(key) {
  const labels = { rising: 'Rising', stable: 'Stable', decaying: 'Decaying', atRisk: 'At Risk' };
  return labels[key] || key;
}

export default function StatusChangeNotifier({ userId }) {
  const fetched = useRef(false);

  useEffect(() => {
    if (!userId || fetched.current) return;
    fetched.current = true;

    const storageKey = STORAGE_KEY + userId;

    fetch(`${API_URL}/api/position/${userId}`)
      .then(r => r.json())
      .then(d => {
        if (!d.success || !d.status) return;

        const currentStatus = d.status.status;
        const prevStatus = localStorage.getItem(storageKey);

        // Always update stored status
        localStorage.setItem(storageKey, currentStatus);

        // Only notify if there was a previous status AND it changed
        if (!prevStatus || prevStatus === currentStatus) return;

        const direction = getDirection(prevStatus, currentStatus);
        const prevLabel = getStatusLabel(prevStatus);
        const msgs = STATUS_MESSAGES[currentStatus];
        const msgFn = msgs?.[direction] || msgs?.neutral;
        const message = msgFn ? msgFn(prevLabel) : `Your status changed to ${getStatusLabel(currentStatus)}.`;

        if (direction === 'up') {
          toast.success(message, { duration: 6000, id: 'status-change' });
        } else if (direction === 'down') {
          toast.error(message, { duration: 8000, id: 'status-change' });
        } else {
          toast(message, { duration: 6000, id: 'status-change' });
        }
      })
      .catch(() => {});
  }, [userId]);

  return null;
}
