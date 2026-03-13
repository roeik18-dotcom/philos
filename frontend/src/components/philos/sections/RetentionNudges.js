import { useState, useEffect } from 'react';
import { Target, Globe, Sun, ChevronLeft } from 'lucide-react';

const RETENTION_DISMISSED_KEY = 'philos_retention_dismissed';

const NUDGES = [
  {
    id: 'mission',
    icon: Target,
    text: 'Join the daily mission',
    subtext: 'Collective action strengthens the entire field',
    color: '#6366f1',
    bg: 'bg-indigo-50',
    border: 'border-indigo-100',
    action: 'community',
  },
  {
    id: 'globe',
    icon: Globe,
    text: 'Send a point to the globe',
    subtext: 'Mark your presence on the global map',
    color: '#22c55e',
    bg: 'bg-green-50',
    border: 'border-green-100',
    action: 'scroll_globe',
  },
  {
    id: 'return',
    icon: Sun,
    text: 'Come back tomorrow for your next orientation',
    subtext: 'A daily streak deepens your presence in the field',
    color: '#3b82f6',
    bg: 'bg-blue-50',
    border: 'border-blue-100',
    action: null,
  },
];

export default function RetentionNudges({ visible, onNavigate }) {
  const [dismissed, setDismissed] = useState([]);
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (visible) {
      const timer = setTimeout(() => setShow(true), 1500);
      return () => clearTimeout(timer);
    }
    setShow(false);
  }, [visible]);

  useEffect(() => {
    try {
      const saved = JSON.parse(sessionStorage.getItem(RETENTION_DISMISSED_KEY) || '[]');
      setDismissed(saved);
    } catch { /* ignore */ }
  }, []);

  const handleDismiss = (id) => {
    const next = [...dismissed, id];
    setDismissed(next);
    sessionStorage.setItem(RETENTION_DISMISSED_KEY, JSON.stringify(next));
  };

  const handleAction = (nudge) => {
    handleDismiss(nudge.id);
    if (nudge.action === 'community' && onNavigate) {
      onNavigate('community');
    } else if (nudge.action === 'scroll_globe') {
      const globe = document.querySelector('[data-testid="field-globe-section"]');
      if (globe) globe.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  if (!show || !visible) return null;

  const active = NUDGES.filter(n => !dismissed.includes(n.id));
  if (active.length === 0) return null;

  return (
    <div className="space-y-2 animate-fadeIn" data-testid="retention-nudges">
      <p className="text-[10px] text-gray-400 text-center mb-1">What's next?</p>
      {active.slice(0, 3).map((nudge) => {
        const Icon = nudge.icon;
        return (
          <button
            key={nudge.id}
            onClick={() => handleAction(nudge)}
            className={`w-full flex items-center gap-3 p-3 rounded-xl ${nudge.bg} border ${nudge.border} hover:shadow-sm transition-all active:scale-[0.98] text-right`}
            data-testid={`retention-nudge-${nudge.id}`}
          >
            <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0" style={{ backgroundColor: `${nudge.color}15` }}>
              <Icon className="w-4 h-4" style={{ color: nudge.color }} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gray-800">{nudge.text}</p>
              <p className="text-[10px] text-gray-500 truncate">{nudge.subtext}</p>
            </div>
            {nudge.action && <ChevronLeft className="w-3.5 h-3.5 text-gray-300 flex-shrink-0" />}
          </button>
        );
      })}
    </div>
  );
}
