import { useMemo } from 'react';

// Hebrew labels for value tags
const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות',
  neutral: 'ניטרלי'
};

// Color mapping for value tags
const valueColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', border: 'border-indigo-300' },
  harm: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-300' }
};

// Predefined action paths database
const actionPathsDatabase = {
  // Recovery-focused actions
  recovery: [
    { action: 'לנשום עמוק 5 פעמים', valueTag: 'recovery', orderDrift: 5, collectiveDrift: 0, harmPressure: -10, recoveryStability: 25 },
    { action: 'לשתות כוס מים', valueTag: 'recovery', orderDrift: 3, collectiveDrift: 0, harmPressure: -5, recoveryStability: 15 },
    { action: 'לצאת להליכה קצרה', valueTag: 'recovery', orderDrift: 10, collectiveDrift: 0, harmPressure: -15, recoveryStability: 30 },
    { action: 'לעשות מתיחות', valueTag: 'recovery', orderDrift: 8, collectiveDrift: 0, harmPressure: -8, recoveryStability: 20 },
    { action: 'להפסיק ולנוח 5 דקות', valueTag: 'recovery', orderDrift: 5, collectiveDrift: 0, harmPressure: -12, recoveryStability: 22 }
  ],
  // Order-focused actions
  order: [
    { action: 'לארגן את השולחן', valueTag: 'order', orderDrift: 20, collectiveDrift: 0, harmPressure: -5, recoveryStability: 10 },
    { action: 'לכתוב רשימת משימות', valueTag: 'order', orderDrift: 25, collectiveDrift: 0, harmPressure: -8, recoveryStability: 15 },
    { action: 'לסדר תיקיות במחשב', valueTag: 'order', orderDrift: 18, collectiveDrift: 0, harmPressure: -3, recoveryStability: 8 },
    { action: 'לתכנן את שאר היום', valueTag: 'order', orderDrift: 22, collectiveDrift: 0, harmPressure: -10, recoveryStability: 12 },
    { action: 'להתמקד במשימה אחת', valueTag: 'order', orderDrift: 15, collectiveDrift: 0, harmPressure: -7, recoveryStability: 10 }
  ],
  // Contribution-focused actions
  contribution: [
    { action: 'לשלוח הודעה חיובית לחבר', valueTag: 'contribution', orderDrift: 5, collectiveDrift: 20, harmPressure: -15, recoveryStability: 10 },
    { action: 'לעזור למישהו קרוב', valueTag: 'contribution', orderDrift: 8, collectiveDrift: 25, harmPressure: -20, recoveryStability: 12 },
    { action: 'להקשיב למישהו', valueTag: 'contribution', orderDrift: 3, collectiveDrift: 18, harmPressure: -12, recoveryStability: 15 },
    { action: 'לשתף רעיון', valueTag: 'contribution', orderDrift: 10, collectiveDrift: 22, harmPressure: -8, recoveryStability: 8 },
    { action: 'להתקשר למישהו', valueTag: 'contribution', orderDrift: 5, collectiveDrift: 15, harmPressure: -10, recoveryStability: 10 }
  ],
  // Risky actions (lower score)
  risky: [
    { action: 'לשלוח הודעה כועסת', valueTag: 'harm', orderDrift: -15, collectiveDrift: -20, harmPressure: 40, recoveryStability: -25 },
    { action: 'להתעלם מהבעיה', valueTag: 'avoidance', orderDrift: -10, collectiveDrift: -5, harmPressure: 15, recoveryStability: -10 },
    { action: 'לגלול ברשתות חברתיות', valueTag: 'avoidance', orderDrift: -8, collectiveDrift: -3, harmPressure: 10, recoveryStability: -15 },
    { action: 'לדחות את ההחלטה', valueTag: 'avoidance', orderDrift: -12, collectiveDrift: -5, harmPressure: 12, recoveryStability: -8 }
  ]
};

// Calculate path score based on preferences
const calculatePathScore = (path, adaptiveScores = null) => {
  // Positive factors: order drift, collective drift (contribution), recovery stability
  // Negative factors: harm pressure
  const orderBonus = path.orderDrift > 0 ? path.orderDrift * 2 : path.orderDrift * 3;
  const collectiveBonus = path.collectiveDrift > 0 ? path.collectiveDrift * 2 : path.collectiveDrift * 2;
  const recoveryBonus = path.recoveryStability > 0 ? path.recoveryStability * 1.5 : path.recoveryStability * 2;
  const harmPenalty = path.harmPressure * -2; // Negative harm is good
  
  let baseScore = orderBonus + collectiveBonus + recoveryBonus + harmPenalty;
  
  // Apply adaptive adjustment if available
  if (adaptiveScores && path.valueTag) {
    const adaptiveAdjustment = adaptiveScores[path.valueTag] || 0;
    baseScore += adaptiveAdjustment * 3; // Scale adaptive scores
  }
  
  return baseScore;
};

// Generate three paths based on current state
const generatePaths = (currentState, history, adaptiveScores = null) => {
  const { chaos_order, ego_collective, physical_capacity } = currentState;
  
  let selectedPaths = [];
  
  // Analyze current situation
  const needsRecovery = physical_capacity < 40;
  const needsOrder = chaos_order < 0;
  const needsCollective = ego_collective < 0;
  
  // Path 1: Best recommended path based on current state
  let bestCategory = 'recovery';
  if (needsOrder && !needsRecovery) bestCategory = 'order';
  if (needsCollective && !needsRecovery && !needsOrder) bestCategory = 'contribution';
  if (physical_capacity > 70 && chaos_order > 20) bestCategory = 'contribution';
  
  const bestCategoryPaths = actionPathsDatabase[bestCategory];
  const bestPath = bestCategoryPaths[Math.floor(Math.random() * bestCategoryPaths.length)];
  selectedPaths.push({ ...bestPath, category: 'recommended' });
  
  // Path 2: Alternative path from different category
  const alternativeCategories = ['recovery', 'order', 'contribution'].filter(c => c !== bestCategory);
  const altCategory = alternativeCategories[Math.floor(Math.random() * alternativeCategories.length)];
  const altCategoryPaths = actionPathsDatabase[altCategory];
  const altPath = altCategoryPaths[Math.floor(Math.random() * altCategoryPaths.length)];
  selectedPaths.push({ ...altPath, category: 'alternative' });
  
  // Path 3: Risky path (to show contrast)
  const riskyPaths = actionPathsDatabase.risky;
  const riskyPath = riskyPaths[Math.floor(Math.random() * riskyPaths.length)];
  selectedPaths.push({ ...riskyPath, category: 'risky' });
  
  // Add additional calculated metrics to each path
  selectedPaths = selectedPaths.map((path, index) => {
    const score = calculatePathScore(path, adaptiveScores);
    const projectedOrder = Math.max(-100, Math.min(100, chaos_order + path.orderDrift));
    const projectedCollective = Math.max(-100, Math.min(100, ego_collective + path.collectiveDrift));
    
    return {
      ...path,
      id: index + 1,
      score,
      projectedOrder,
      projectedCollective,
      isRisky: path.valueTag === 'harm' || path.valueTag === 'avoidance' || path.harmPressure > 10
    };
  });
  
  // Sort by score (highest first)
  selectedPaths.sort((a, b) => b.score - a.score);
  
  // Mark the best path
  if (selectedPaths.length > 0) {
    selectedPaths[0].isBest = true;
  }
  
  return selectedPaths;
};

export default function DecisionPathEngineSection({ state, history, onSelectAction, onSelectPath, adaptiveScores }) {
  // Generate paths based on current state and adaptive scores
  const paths = useMemo(() => {
    return generatePaths(state, history, adaptiveScores);
  }, [state, history, adaptiveScores]);

  const getScoreLabel = (score) => {
    if (score >= 50) return { label: 'מעולה', color: 'text-green-600' };
    if (score >= 30) return { label: 'טוב', color: 'text-blue-600' };
    if (score >= 10) return { label: 'בינוני', color: 'text-yellow-600' };
    if (score >= 0) return { label: 'חלש', color: 'text-orange-600' };
    return { label: 'מסוכן', color: 'text-red-600' };
  };

  const getMetricColor = (value, isHigherBetter = true) => {
    if (isHigherBetter) {
      if (value > 15) return 'text-green-600';
      if (value > 5) return 'text-blue-600';
      if (value >= 0) return 'text-gray-600';
      return 'text-red-600';
    } else {
      // For harm pressure: lower is better
      if (value < -10) return 'text-green-600';
      if (value < 0) return 'text-blue-600';
      if (value <= 10) return 'text-yellow-600';
      return 'text-red-600';
    }
  };

  return (
    <section 
      className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-3xl p-5 shadow-sm border border-violet-200"
      data-testid="decision-path-engine-section"
      dir="rtl"
    >
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground">מנוע מסלולי החלטה</h3>
          <p className="text-xs text-muted-foreground">3 מסלולים מוצעים עם תחזיות</p>
        </div>
        <div className="w-10 h-10 rounded-full bg-violet-200 flex items-center justify-center">
          <svg className="w-5 h-5 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>

      {/* Paths Grid */}
      <div className="space-y-4">
        {paths.map((path, index) => {
          const scoreInfo = getScoreLabel(path.score);
          const colors = valueColors[path.valueTag] || valueColors.recovery;
          
          return (
            <div
              key={path.id}
              className={`relative rounded-2xl p-4 border-2 transition-all ${
                path.isBest 
                  ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-400 shadow-lg' 
                  : path.isRisky 
                    ? 'bg-gradient-to-r from-red-50 to-orange-50 border-red-300' 
                    : 'bg-white/80 border-gray-200'
              }`}
              data-testid={`path-card-${index + 1}`}
            >
              {/* Best Badge */}
              {path.isBest && (
                <div className="absolute -top-3 right-4 px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full shadow-md">
                  מומלץ
                </div>
              )}
              
              {/* Risky Badge */}
              {path.isRisky && !path.isBest && (
                <div className="absolute -top-3 right-4 px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full shadow-md">
                  מסוכן
                </div>
              )}

              {/* Path Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium text-muted-foreground">פעולה מוצעת:</span>
                  </div>
                  <p className="text-lg font-semibold text-foreground" data-testid={`path-action-${index + 1}`}>
                    {path.action}
                  </p>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-medium ${colors.bg} ${colors.text}`}>
                  {valueLabels[path.valueTag]}
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-3 mb-3">
                {/* Value Tag */}
                <div className="bg-white/50 rounded-xl p-2">
                  <p className="text-xs text-muted-foreground mb-1">value_tag חזוי</p>
                  <p className={`text-sm font-bold ${colors.text}`}>
                    {valueLabels[path.valueTag]}
                  </p>
                </div>

                {/* Order Drift */}
                <div className="bg-white/50 rounded-xl p-2">
                  <p className="text-xs text-muted-foreground mb-1">order drift חזוי</p>
                  <p className={`text-sm font-bold ${getMetricColor(path.orderDrift)}`}>
                    {path.orderDrift > 0 ? '+' : ''}{path.orderDrift}
                  </p>
                </div>

                {/* Collective Drift */}
                <div className="bg-white/50 rounded-xl p-2">
                  <p className="text-xs text-muted-foreground mb-1">collective drift חזוי</p>
                  <p className={`text-sm font-bold ${getMetricColor(path.collectiveDrift)}`}>
                    {path.collectiveDrift > 0 ? '+' : ''}{path.collectiveDrift}
                  </p>
                </div>

                {/* Harm Pressure */}
                <div className="bg-white/50 rounded-xl p-2">
                  <p className="text-xs text-muted-foreground mb-1">harm pressure חזוי</p>
                  <p className={`text-sm font-bold ${getMetricColor(path.harmPressure, false)}`}>
                    {path.harmPressure > 0 ? '+' : ''}{path.harmPressure}%
                  </p>
                </div>

                {/* Recovery Stability */}
                <div className="bg-white/50 rounded-xl p-2 col-span-2">
                  <p className="text-xs text-muted-foreground mb-1">recovery stability חזויה</p>
                  <p className={`text-sm font-bold ${getMetricColor(path.recoveryStability)}`}>
                    {path.recoveryStability > 0 ? '+' : ''}{path.recoveryStability}%
                  </p>
                </div>
              </div>

              {/* Score Bar */}
              <div className="flex items-center gap-3">
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all ${
                      path.score >= 50 ? 'bg-green-500' : 
                      path.score >= 30 ? 'bg-blue-500' : 
                      path.score >= 10 ? 'bg-yellow-500' : 
                      path.score >= 0 ? 'bg-orange-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${Math.max(5, Math.min(100, (path.score + 50) / 1.5))}%` }}
                  />
                </div>
                <span className={`text-sm font-bold ${scoreInfo.color}`}>
                  {scoreInfo.label}
                </span>
              </div>

              {/* Select Button */}
              {(onSelectAction || onSelectPath) && (
                <button
                  onClick={() => {
                    if (onSelectPath) {
                      onSelectPath(path);
                    } else if (onSelectAction) {
                      onSelectAction(path.action);
                    }
                  }}
                  className={`mt-3 w-full py-2 rounded-xl text-sm font-medium transition-all ${
                    path.isBest 
                      ? 'bg-green-500 hover:bg-green-600 text-white' 
                      : path.isRisky 
                        ? 'bg-red-100 hover:bg-red-200 text-red-700' 
                        : 'bg-violet-100 hover:bg-violet-200 text-violet-700'
                  }`}
                  data-testid={`select-path-${index + 1}`}
                >
                  בחר מסלול זה
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-4 p-3 bg-white/50 rounded-xl">
        <p className="text-xs font-medium text-muted-foreground mb-2">מקרא:</p>
        <div className="flex flex-wrap gap-3 text-xs">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-green-500"></span>
            <span className="text-muted-foreground">משפר סדר/התאוששות/תרומה</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-red-500"></span>
            <span className="text-muted-foreground">מעלה נזק/הימנעות</span>
          </span>
        </div>
      </div>
    </section>
  );
}
