export default function OrientationFieldSection({ history }) {
  if (history.length < 3) return null;
  
  // Count value tags
  const tagCounts = { contribution: 0, recovery: 0, harm: 0, order: 0, avoidance: 0 };
  history.forEach(h => {
    if (tagCounts.hasOwnProperty(h.value_tag)) {
      tagCounts[h.value_tag]++;
    }
  });
  
  const total = history.length;
  
  // Compute metrics
  const orderDrift = (tagCounts.order + tagCounts.recovery) - (tagCounts.harm + tagCounts.avoidance);
  const collectiveDrift = tagCounts.contribution - tagCounts.harm;
  const harmPressure = total > 0 ? tagCounts.harm / total : 0;
  const recoveryStability = total > 0 ? tagCounts.recovery / total : 0;
  
  // Determine indicators
  const orderDriftLabel = orderDrift > 1 ? 'positive' : orderDrift < -1 ? 'negative' : 'neutral';
  const collectiveDriftLabel = collectiveDrift > 1 ? 'positive' : collectiveDrift < -1 ? 'negative' : 'neutral';
  const harmPressureLabel = harmPressure > 0.3 ? 'high' : harmPressure > 0.1 ? 'medium' : 'low';
  const recoveryStabilityLabel = recoveryStability > 0.3 ? 'high' : recoveryStability > 0.1 ? 'medium' : 'low';
  
  const getColor = (label, isPositiveGood = true) => {
    if (label === 'positive' || label === 'high') {
      return isPositiveGood ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100';
    }
    if (label === 'negative' || label === 'low') {
      return isPositiveGood ? 'text-red-600 bg-red-100' : 'text-green-600 bg-green-100';
    }
    return 'text-gray-600 bg-gray-100';
  };
  
  return (
    <section className="bg-gradient-to-br from-slate-50 to-zinc-100 rounded-3xl p-5 shadow-sm border border-slate-200">
      <h3 className="text-lg font-semibold text-foreground mb-4">Orientation Field</h3>
      
      <div className="grid grid-cols-2 gap-3">
        {/* Order Drift */}
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">Order Drift</p>
          <p className="text-sm text-muted-foreground mb-2">(order + recovery) - (harm + avoidance)</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-foreground">{orderDrift > 0 ? '+' : ''}{orderDrift}</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getColor(orderDriftLabel, true)}`}>
              {orderDriftLabel}
            </span>
          </div>
        </div>
        
        {/* Collective Drift */}
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">Collective Drift</p>
          <p className="text-sm text-muted-foreground mb-2">contribution - harm</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-foreground">{collectiveDrift > 0 ? '+' : ''}{collectiveDrift}</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getColor(collectiveDriftLabel, true)}`}>
              {collectiveDriftLabel}
            </span>
          </div>
        </div>
        
        {/* Harm Pressure */}
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">Harm Pressure</p>
          <p className="text-sm text-muted-foreground mb-2">harm / total</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-foreground">{Math.round(harmPressure * 100)}%</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getColor(harmPressureLabel, false)}`}>
              {harmPressureLabel}
            </span>
          </div>
        </div>
        
        {/* Recovery Stability */}
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-1">Recovery Stability</p>
          <p className="text-sm text-muted-foreground mb-2">recovery / total</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-foreground">{Math.round(recoveryStability * 100)}%</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getColor(recoveryStabilityLabel, true)}`}>
              {recoveryStabilityLabel}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
