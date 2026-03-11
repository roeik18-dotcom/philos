import { useState, useEffect } from 'react';
import { Crown, Check, ArrowLeft, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const planAccents = {
  free: { bg: 'bg-gray-50', border: 'border-gray-200', text: 'text-gray-700', btn: 'bg-gray-200 text-gray-600' },
  plus: { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-700', btn: 'bg-indigo-600 text-white hover:bg-indigo-700' },
  collective: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', btn: 'bg-amber-600 text-white hover:bg-amber-700' }
};

export default function SubscriptionSection({ userId }) {
  const [plans, setPlans] = useState(null);
  const [currentPlan, setCurrentPlan] = useState('free');
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(null);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/api/orientation/subscription/plans`).then(r => r.ok ? r.json() : null),
      effectiveUserId ? fetch(`${API_URL}/api/orientation/subscription/status/${effectiveUserId}`).then(r => r.ok ? r.json() : null) : null
    ]).then(([plansData, statusData]) => {
      if (plansData?.success) setPlans(plansData.plans);
      if (statusData?.success) setCurrentPlan(statusData.plan);
    }).catch(() => {}).finally(() => setLoading(false));
  }, [effectiveUserId]);

  const handleUpgrade = async (planId) => {
    if (!effectiveUserId || planId === 'free') return;
    setUpgrading(planId);
    try {
      const res = await fetch(`${API_URL}/api/orientation/subscription/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_id: planId, user_id: effectiveUserId, origin_url: window.location.origin })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.success && data.checkout_url) {
          window.location.href = data.checkout_url;
        }
      }
    } catch (e) {
      console.log('Checkout error:', e);
    } finally {
      setUpgrading(null);
    }
  };

  if (loading || !plans) return null;

  const planOrder = ['free', 'plus', 'collective'];

  return (
    <section className="philos-section bg-white border-border" dir="rtl" data-testid="subscription-section">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-xl bg-amber-50 flex items-center justify-center">
          <Crown className="w-5 h-5 text-amber-600" />
        </div>
        <div>
          <span className="text-sm font-semibold text-gray-800">מנוי</span>
          <p className="text-[10px] text-gray-400">בחר את הרמה שלך</p>
        </div>
      </div>

      <div className="space-y-3">
        {planOrder.map(pid => {
          const plan = plans[pid];
          if (!plan) return null;
          const accent = planAccents[pid];
          const isCurrent = currentPlan === pid;

          return (
            <div key={pid} className={`rounded-2xl p-4 border ${accent.bg} ${accent.border} ${isCurrent ? 'ring-2 ring-offset-1' : ''}`} style={isCurrent ? { ringColor: '#6366f1' } : {}} data-testid={`plan-${pid}`}>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-bold ${accent.text}`}>{plan.label_he}</span>
                  {isCurrent && <span className="text-[9px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full">פעיל</span>}
                </div>
                <span className={`text-lg font-bold ${accent.text}`}>
                  {plan.price > 0 ? `$${plan.price}/חודש` : 'חינם'}
                </span>
              </div>

              <div className="space-y-1 mb-3">
                {plan.features_he.map((f, i) => (
                  <div key={i} className="flex items-center gap-1.5">
                    <Check className="w-3 h-3 text-green-500" />
                    <span className="text-xs text-gray-600">{f}</span>
                  </div>
                ))}
              </div>

              {!isCurrent && pid !== 'free' && (
                <button
                  onClick={() => handleUpgrade(pid)}
                  disabled={!!upgrading}
                  className={`w-full py-2 rounded-xl text-sm font-medium transition-all duration-200 active:scale-[0.98] ${accent.btn}`}
                  data-testid={`upgrade-${pid}`}
                >
                  {upgrading === pid ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'שדרג'}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
