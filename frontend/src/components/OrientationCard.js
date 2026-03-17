import { useState, useEffect } from 'react';
import { Compass, ArrowRight, Send, Share2, Heart, ShieldCheck } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ACTION_ICONS = {
  post: Send,
  visibility: Send,
  re_engage: Send,
  react: Heart,
  share: Share2,
  verify: ShieldCheck,
};

export default function OrientationCard({ userId, onNavigate }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!userId) return;
    const controller = new AbortController();
    fetch(`${API_URL}/api/orientation/${userId}`, { signal: controller.signal })
      .then(r => r.json())
      .then(d => { if (d.success) setData(d); })
      .catch(e => { if (e.name !== 'AbortError') console.error(e); });
    return () => controller.abort();
  }, [userId]);

  if (!data) return null;

  const Icon = ACTION_ICONS[data.action_type] || Send;
  const ctaTarget = data.action_type === 'post' || data.action_type === 'visibility' || data.action_type === 're_engage'
    ? 'post' : 'feed';

  return (
    <div className="orientation-card" data-testid="orientation-card">
      <div className="orientation-icon">
        <Compass className="w-4 h-4" />
      </div>
      <div className="orientation-body">
        <p className="orientation-msg" data-testid="orientation-msg">{data.message}</p>
      </div>
      <button
        className="orientation-cta"
        onClick={() => onNavigate?.(ctaTarget)}
        data-testid="orientation-cta"
      >
        <Icon className="w-3.5 h-3.5" />
        {data.cta}
        <ArrowRight className="w-3 h-3" />
      </button>
    </div>
  );
}
