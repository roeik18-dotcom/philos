import { useState, useEffect, useRef } from 'react';
import { User, Globe, TrendingUp, ArrowRight, TrendingDown, AlertTriangle } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const FACTOR_COLORS = {
  actions: '#00d4ff',
  reactors: '#7c3aed',
  trust: '#f59e0b',
  referrals: '#10b981',
};

const STATUS_ICONS = {
  up: TrendingUp,
  right: ArrowRight,
  down: TrendingDown,
  warning: AlertTriangle,
};

export default function PositionBar({ userId }) {
  const [data, setData] = useState(null);
  const barRef = useRef(null);

  useEffect(() => {
    if (!userId) return;
    const controller = new AbortController();
    fetch(`${API_URL}/api/position/${userId}`, { signal: controller.signal })
      .then(r => r.json())
      .then(d => { if (d.success) setData(d); })
      .catch(e => { if (e.name !== 'AbortError') console.error(e); });
    return () => controller.abort();
  }, [userId]);

  if (!data) return null;

  const pct = Math.round(data.position * 100);
  const status = data.status || {};
  const StatusIcon = STATUS_ICONS[status.icon] || ArrowRight;

  return (
    <div className="position-bar-wrap" data-testid="position-bar">
      <div className="position-bar-labels">
        <span className="position-label-self" data-testid="position-label-self">
          <User className="w-3 h-3" /> Self
        </span>
        <span className="position-label-tag" data-testid="position-label-tag">
          {data.label}
        </span>
        <span className="position-label-network" data-testid="position-label-network">
          Network <Globe className="w-3 h-3" />
        </span>
      </div>

      <div className="position-bar-track" ref={barRef} data-testid="position-bar-track">
        <div className="position-bar-fill" style={{ width: `${pct}%` }} data-testid="position-bar-fill" />
        <div className="position-bar-marker" style={{ left: `${pct}%` }} data-testid="position-bar-marker">
          <div className="position-marker-dot" />
        </div>
      </div>

      <div className="position-bar-bottom">
        {status.label && (
          <span
            className="position-status-badge"
            style={{ '--status-color': status.color || '#f59e0b' }}
            data-testid="position-status-badge"
          >
            <StatusIcon className="w-3 h-3" />
            {status.label}
          </span>
        )}
        <div className="position-bar-factors" data-testid="position-factors">
          {Object.entries(data.factors).map(([key, val]) => (
            val > 0 && (
              <span
                key={key}
                className="position-factor"
                style={{ '--factor-color': FACTOR_COLORS[key] }}
                data-testid={`position-factor-${key}`}
              >
                {key}
              </span>
            )
          ))}
        </div>
      </div>
    </div>
  );
}
