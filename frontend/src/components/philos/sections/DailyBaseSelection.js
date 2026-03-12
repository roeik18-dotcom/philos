import { useState, useEffect, useCallback } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const baseConfig = {
  heart: {
    key: 'heart',
    label: 'לב',
    color: '#ef4444',
    bgColor: '#ef444410',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-6 h-6">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
      </svg>
    )
  },
  head: {
    key: 'head',
    label: 'ראש',
    color: '#6366f1',
    bgColor: '#6366f110',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-6 h-6">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 16v-4M12 8h.01" />
      </svg>
    )
  },
  body: {
    key: 'body',
    label: 'גוף',
    color: '#f59e0b',
    bgColor: '#f59e0b10',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-6 h-6">
        <circle cx="12" cy="5" r="2" />
        <path d="M12 7v6M8 21l2-6h4l2 6M8 13l-2 2M16 13l2 2" />
      </svg>
    )
  }
};

export default function DailyBaseSelection({ userId, onBaseSelected }) {
  const [data, setData] = useState(null);
  const [selectedBase, setSelectedBase] = useState(null);
  const [saving, setSaving] = useState(false);
  const [confirmed, setConfirmed] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  const fetchBase = useCallback(async () => {
    if (!effectiveUserId) return;
    try {
      const res = await fetch(`${API_URL}/api/orientation/daily-base/${effectiveUserId}`);
      if (res.ok) {
        const json = await res.json();
        if (json.success) {
          setData(json);
          if (json.base_selected) {
            setSelectedBase(json.today_base);
            setConfirmed(true);
            onBaseSelected?.(json.today_base);
          }
        }
      }
    } catch (e) {}
  }, [effectiveUserId, onBaseSelected]);

  useEffect(() => { fetchBase(); }, [fetchBase]);

  const handleSelect = async (base) => {
    if (confirmed) return;
    setSelectedBase(base);
  };

  const handleConfirm = async () => {
    if (!selectedBase || !effectiveUserId || saving) return;
    setSaving(true);
    try {
      const res = await fetch(`${API_URL}/api/orientation/daily-base/${effectiveUserId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base: selectedBase })
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success) {
          setConfirmed(true);
          setData(prev => ({
            ...prev,
            base_selected: true,
            today_base: selectedBase,
            today_base_he: json.base_he,
            allocations_he: json.allocations_he
          }));
          onBaseSelected?.(selectedBase);
        }
      }
    } catch (e) {}
    finally { setSaving(false); }
  };

  if (!data) return null;

  const cfg = selectedBase ? baseConfig[selectedBase] : null;

  // Compact view after confirmation
  if (confirmed && selectedBase) {
    const allocations = data.allocations_he || BASE_DEFINITIONS_FE[selectedBase] || [];
    return (
      <section className="relative rounded-3xl overflow-hidden bg-[#0a0a1a] p-4" dir="rtl" data-testid="daily-base-confirmed">
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">המרכז שלך היום</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: cfg.color }} />
              <span className="text-sm font-semibold" style={{ color: cfg.color }}>{cfg.label}</span>
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {allocations.map((a, i) => (
              <span key={i} className="text-[10px] px-2 py-0.5 rounded-full text-gray-400" style={{ backgroundColor: `${cfg.color}10` }}>
                {a}
              </span>
            ))}
          </div>
        </div>
      </section>
    );
  }

  // Full selection view
  return (
    <section className="relative rounded-3xl overflow-hidden bg-[#0a0a1a] p-5" dir="rtl" data-testid="daily-base-selection">
      {/* Ambient glow */}
      {cfg && <div className="absolute inset-0 pointer-events-none" style={{ background: `radial-gradient(ellipse at 50% 80%, ${cfg.color}08 0%, transparent 60%)` }} />}

      <div className="relative z-10">
        <p className="text-sm text-gray-300 font-medium mb-1">מאיזה מרכז אתה פועל היום?</p>
        <p className="text-[10px] text-gray-600 mb-5">בחר את הבסיס שממנו תפעל — לב, ראש או גוף</p>

        {/* Three base options */}
        <div className="grid grid-cols-3 gap-2.5 mb-4">
          {Object.values(baseConfig).map((b) => {
            const isSelected = selectedBase === b.key;
            return (
              <button
                key={b.key}
                onClick={() => handleSelect(b.key)}
                className="relative flex flex-col items-center gap-2 p-3.5 rounded-2xl border transition-all duration-300"
                style={{
                  borderColor: isSelected ? `${b.color}60` : 'rgba(255,255,255,0.06)',
                  backgroundColor: isSelected ? `${b.color}10` : 'rgba(255,255,255,0.03)',
                }}
                data-testid={`base-option-${b.key}`}
              >
                {/* Glow ring when selected */}
                {isSelected && (
                  <div className="absolute inset-0 rounded-2xl pointer-events-none" style={{ boxShadow: `inset 0 0 20px ${b.color}15` }} />
                )}
                <span style={{ color: isSelected ? b.color : '#6b7280' }}>{b.icon}</span>
                <span className="text-xs font-semibold" style={{ color: isSelected ? b.color : '#9ca3af' }}>{b.label}</span>
              </button>
            );
          })}
        </div>

        {/* Potential allocations for selected base */}
        {selectedBase && !confirmed && (
          <div className="mb-4 animate-fadeIn">
            <p className="text-[10px] text-gray-500 mb-2">הקצאות אפשריות היום:</p>
            <div className="flex flex-wrap gap-1.5">
              {(BASE_DEFINITIONS_FE[selectedBase] || []).map((a, i) => (
                <span key={i} className="text-[10px] px-2.5 py-1 rounded-full text-gray-300" style={{ backgroundColor: `${cfg.color}12`, border: `1px solid ${cfg.color}20` }}>
                  {a}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Confirm button */}
        {selectedBase && !confirmed && (
          <button
            onClick={handleConfirm}
            disabled={saving}
            className="w-full py-2.5 rounded-2xl text-sm font-medium transition-all duration-300 active:scale-[0.98]"
            style={{ backgroundColor: `${cfg.color}20`, color: cfg.color }}
            data-testid="base-confirm-btn"
          >
            {saving ? '...' : 'אישור'}
          </button>
        )}
      </div>
    </section>
  );
}

const BASE_DEFINITIONS_FE = {
  heart: ['קשרים ומערכות יחסים', 'אמפתיה והקשבה', 'תרומה ונתינה', 'תיקון רגשי'],
  head: ['סדר ותכנון', 'למידה וחקירה', 'קבלת החלטות', 'חשיבה אסטרטגית'],
  body: ['תנועה ובריאות', 'פעולה מעשית', 'משמעת ומחויבות', 'סדר פיזי']
};
