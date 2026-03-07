export default function GlobalValueFieldSection({ globalStats, resetGlobalStats }) {
  if (globalStats.totalDecisions < 1) return null;
  
  const total = globalStats.totalDecisions || 1;
  
  // Calculate global metrics
  const globalOrderDrift = (globalStats.order + globalStats.recovery) - (globalStats.harm + globalStats.avoidance);
  const globalCollectiveDrift = globalStats.contribution - globalStats.harm;
  const harmPressureLongTerm = globalStats.harm / total;
  const recoveryStabilityLongTerm = globalStats.recovery / total;
  
  // Determine indicators
  const orderDriftLabel = globalOrderDrift > 2 ? 'חיובי' : globalOrderDrift < -2 ? 'שלילי' : 'מאוזן';
  const collectiveDriftLabel = globalCollectiveDrift > 2 ? 'חיובי' : globalCollectiveDrift < -2 ? 'שלילי' : 'מאוזן';
  const harmPressureLabel = harmPressureLongTerm > 0.25 ? 'גבוה' : harmPressureLongTerm > 0.1 ? 'בינוני' : 'נמוך';
  const recoveryStabilityLabel = recoveryStabilityLongTerm > 0.3 ? 'גבוה' : recoveryStabilityLongTerm > 0.15 ? 'בינוני' : 'נמוך';
  
  const getColor = (label, isPositiveGood = true) => {
    const positiveLabels = ['חיובי', 'גבוה'];
    const negativeLabels = ['שלילי', 'נמוך'];
    if (positiveLabels.includes(label)) {
      return isPositiveGood ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100';
    }
    if (negativeLabels.includes(label)) {
      return isPositiveGood ? 'text-red-600 bg-red-100' : 'text-green-600 bg-green-100';
    }
    return 'text-gray-600 bg-gray-100';
  };
  
  // Find dominant global value
  const valueCounts = {
    contribution: globalStats.contribution,
    recovery: globalStats.recovery,
    order: globalStats.order,
    harm: globalStats.harm,
    avoidance: globalStats.avoidance
  };
  const dominantValue = Object.entries(valueCounts).sort((a, b) => b[1] - a[1])[0];
  
  const valueLabels = {
    contribution: 'תרומה',
    recovery: 'התאוששות',
    order: 'סדר',
    harm: 'נזק',
    avoidance: 'הימנעות'
  };
  
  const valueColors = {
    contribution: 'bg-green-500',
    recovery: 'bg-blue-500',
    order: 'bg-indigo-500',
    harm: 'bg-red-500',
    avoidance: 'bg-gray-500'
  };
  
  return (
    <section className="bg-gradient-to-br from-violet-50 to-fuchsia-50 rounded-3xl p-5 shadow-sm border border-violet-200" data-testid="global-value-field">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-foreground">שדה ערכים גלובלי</h3>
        <button
          onClick={resetGlobalStats}
          className="px-3 py-1 text-xs bg-violet-100 hover:bg-violet-200 text-violet-700 rounded-lg transition-all"
          data-testid="reset-global-stats-btn"
        >
          איפוס
        </button>
      </div>
      <p className="text-xs text-muted-foreground mb-4">ניתוח ארוך טווח מכל הסשנים</p>
      
      {/* Total Stats Overview */}
      <div className="bg-white/70 rounded-xl p-4 mb-4 text-center">
        <p className="text-xs text-muted-foreground mb-2">סה״כ החלטות (כל הסשנים)</p>
        <p className="text-3xl font-bold text-violet-600" data-testid="global-total-decisions">{globalStats.totalDecisions}</p>
      </div>
      
      {/* Global Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* Global Order Drift */}
        <div className="bg-white/70 rounded-xl p-3" data-testid="global-order-drift">
          <p className="text-xs text-muted-foreground mb-1">סחף סדר גלובלי</p>
          <p className="text-xs text-muted-foreground/70 mb-2">(סדר + התאוששות) - (נזק + הימנעות)</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-foreground">{globalOrderDrift > 0 ? '+' : ''}{globalOrderDrift}</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getColor(orderDriftLabel, true)}`}>
              {orderDriftLabel}
            </span>
          </div>
        </div>
        
        {/* Global Collective Drift */}
        <div className="bg-white/70 rounded-xl p-3" data-testid="global-collective-drift">
          <p className="text-xs text-muted-foreground mb-1">סחף חברתי גלובלי</p>
          <p className="text-xs text-muted-foreground/70 mb-2">תרומה - נזק</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-foreground">{globalCollectiveDrift > 0 ? '+' : ''}{globalCollectiveDrift}</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getColor(collectiveDriftLabel, true)}`}>
              {collectiveDriftLabel}
            </span>
          </div>
        </div>
        
        {/* Harm Pressure Long Term */}
        <div className="bg-white/70 rounded-xl p-3" data-testid="harm-pressure-long-term">
          <p className="text-xs text-muted-foreground mb-1">לחץ נזק ארוך טווח</p>
          <p className="text-xs text-muted-foreground/70 mb-2">נזק / סה״כ</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-foreground">{Math.round(harmPressureLongTerm * 100)}%</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getColor(harmPressureLabel, false)}`}>
              {harmPressureLabel}
            </span>
          </div>
        </div>
        
        {/* Recovery Stability Long Term */}
        <div className="bg-white/70 rounded-xl p-3" data-testid="recovery-stability-long-term">
          <p className="text-xs text-muted-foreground mb-1">יציבות התאוששות ארוך טווח</p>
          <p className="text-xs text-muted-foreground/70 mb-2">התאוששות / סה״כ</p>
          <div className="flex items-center justify-between">
            <span className="text-lg font-bold text-foreground">{Math.round(recoveryStabilityLongTerm * 100)}%</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getColor(recoveryStabilityLabel, true)}`}>
              {recoveryStabilityLabel}
            </span>
          </div>
        </div>
      </div>
      
      {/* Dominant Global Value */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <p className="text-xs text-muted-foreground mb-3">אשכול ערכים דומיננטי</p>
        <div className="flex items-center justify-center gap-3">
          <div 
            className={`${valueColors[dominantValue[0]]} w-16 h-16 rounded-full flex items-center justify-center text-white font-bold text-xl shadow-lg`}
            data-testid="dominant-value-cluster"
          >
            {dominantValue[1]}
          </div>
          <div className="text-right">
            <p className="text-lg font-bold text-foreground">{valueLabels[dominantValue[0]]}</p>
            <p className="text-xs text-muted-foreground">
              {Math.round((dominantValue[1] / total) * 100)}% מכלל ההחלטות
            </p>
          </div>
        </div>
      </div>
      
      {/* Global Value Distribution */}
      <div className="bg-white/70 rounded-xl p-4">
        <p className="text-xs text-muted-foreground mb-3">התפלגות ערכים גלובלית</p>
        <div className="flex justify-center items-end gap-2 h-20">
          {Object.entries(valueCounts).map(([tag, count]) => {
            const maxCount = Math.max(...Object.values(valueCounts), 1);
            const size = count > 0 ? 24 + (count / maxCount) * 40 : 16;
            return (
              <div key={tag} className="flex flex-col items-center gap-1">
                <div 
                  className={`${valueColors[tag]} rounded-full flex items-center justify-center text-white font-bold text-xs transition-all`}
                  style={{ 
                    width: `${size}px`, 
                    height: `${size}px`,
                    opacity: count > 0 ? 0.9 : 0.3
                  }}
                  data-testid={`global-value-${tag}`}
                >
                  {count}
                </div>
                <span className="text-xs text-muted-foreground">{valueLabels[tag]}</span>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
