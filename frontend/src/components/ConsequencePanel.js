import { useState, useEffect } from 'react';
import { TrendingUp, ArrowRight, TrendingDown, AlertTriangle, Eye } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const STATUS_ICONS = {
  up: TrendingUp,
  right: ArrowRight,
  down: TrendingDown,
  warning: AlertTriangle,
};

export default function ConsequencePanel({ userId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!userId) return;
    const controller = new AbortController();
    fetch(`${API_URL}/api/position/${userId}`, { signal: controller.signal })
      .then(r => r.json())
      .then(d => { if (d.success && d.consequence_panel) setData(d); })
      .catch(e => { if (e.name !== 'AbortError') console.error(e); });
    return () => controller.abort();
  }, [userId]);

  if (!data || !data.consequence_panel) return null;

  const { status, consequence_multiplier, consequence_panel } = data;
  const StatusIcon = STATUS_ICONS[status?.icon] || ArrowRight;
  const mult = consequence_multiplier ?? 1.0;
  const isReduced = mult < 1.0;
  const isBoosted = mult > 1.0;

  return (
    <div className="consequence-panel" data-testid="consequence-panel">
      <div className="consequence-panel-header">
        <Eye className="w-4 h-4" style={{ color: 'rgba(255,255,255,0.3)' }} />
        <span className="consequence-panel-title">Action Visibility</span>
      </div>
      <div className="consequence-panel-body">
        <div className="consequence-row" data-testid="consequence-status-row">
          <span className="consequence-label">Status</span>
          <span
            className="consequence-value consequence-status-pill"
            style={{ '--status-color': status?.color || '#f59e0b' }}
            data-testid="consequence-status-value"
          >
            <StatusIcon className="w-3 h-3" />
            {status?.label || 'Unknown'}
          </span>
        </div>
        <div className="consequence-row" data-testid="consequence-multiplier-row">
          <span className="consequence-label">Visibility</span>
          <span
            className={`consequence-value consequence-mult ${isReduced ? 'mult-reduced' : ''} ${isBoosted ? 'mult-boosted' : ''}`}
            data-testid="consequence-multiplier-value"
          >
            {mult.toFixed(2)}x
          </span>
        </div>
        <p className="consequence-meaning" data-testid="consequence-meaning">
          {consequence_panel.meaning}
        </p>
        <p className="consequence-next-step" data-testid="consequence-next-step">
          {consequence_panel.next_step}
        </p>
      </div>
    </div>
  );
}
