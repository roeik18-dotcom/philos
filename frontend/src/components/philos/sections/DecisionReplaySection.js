import { useState, useMemo } from 'react';

// Hebrew value tag labels
const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Value tag colors
const valueColors = {
  contribution: 'bg-green-100 text-green-700 border-green-300',
  recovery: 'bg-blue-100 text-blue-700 border-blue-300',
  order: 'bg-indigo-100 text-indigo-700 border-indigo-300',
  harm: 'bg-red-100 text-red-700 border-red-300',
  avoidance: 'bg-gray-100 text-gray-600 border-gray-300'
};

// Generate alternative paths based on current state and original decision
const generateAlternativePaths = (originalDecision, adaptiveScores = {}) => {
  const { value_tag, chaos_order, ego_collective, balance_score } = originalDecision;
  
  // Define possible alternative path types (excluding the original)
  const allPathTypes = ['contribution', 'recovery', 'order', 'harm', 'avoidance'];
  const availableTypes = allPathTypes.filter(t => t !== value_tag);
  
  // Path templates with Hebrew descriptions
  const pathTemplates = {
    contribution: {
      action: 'לעזור למישהו',
      hebrewName: 'מסלול תרומה',
      description: 'פעולה שמכוונת לתת ולתרום לאחרים',
      orderDrift: 5,
      collectiveDrift: 15,
      harmPressure: -15,
      recoveryStability: 10
    },
    recovery: {
      action: 'לקחת הפסקה קצרה',
      hebrewName: 'מסלול התאוששות',
      description: 'פעולה שמאפשרת התאוששות ומנוחה',
      orderDrift: -5,
      collectiveDrift: 0,
      harmPressure: -20,
      recoveryStability: 20
    },
    order: {
      action: 'לארגן משהו קטן',
      hebrewName: 'מסלול סדר',
      description: 'פעולה שמגבירה סדר ומבנה',
      orderDrift: 15,
      collectiveDrift: 0,
      harmPressure: -10,
      recoveryStability: 5
    },
    harm: {
      action: 'להגיב באגרסיביות',
      hebrewName: 'מסלול נזק',
      description: 'פעולה שעלולה לגרום נזק',
      orderDrift: -10,
      collectiveDrift: -15,
      harmPressure: 20,
      recoveryStability: -15
    },
    avoidance: {
      action: 'להתעלם מהסיטואציה',
      hebrewName: 'מסלול הימנעות',
      description: 'פעולה של הימנעות או דחייה',
      orderDrift: -5,
      collectiveDrift: -5,
      harmPressure: 5,
      recoveryStability: -10
    }
  };
  
  // Select 2-3 alternative paths, prioritizing positive ones
  const priorityTypes = availableTypes.filter(t => !['harm', 'avoidance'].includes(t));
  const negativePath = availableTypes.find(t => ['harm', 'avoidance'].includes(t));
  
  let selectedTypes = priorityTypes.slice(0, 2);
  if (negativePath && selectedTypes.length < 3) {
    selectedTypes.push(negativePath);
  }
  
  // Generate paths with predicted metrics
  return selectedTypes.map((type, idx) => {
    const template = pathTemplates[type];
    const adaptiveBoost = (adaptiveScores[type] || 0) * 0.5;
    
    // Calculate predicted new state
    const predictedOrder = Math.max(-100, Math.min(100, chaos_order + template.orderDrift));
    const predictedCollective = Math.max(-100, Math.min(100, ego_collective + template.collectiveDrift));
    const predictedBalance = 100 - (Math.abs(predictedOrder) + Math.abs(predictedCollective));
    
    return {
      id: idx + 1,
      type,
      hebrewName: template.hebrewName,
      action: template.action,
      description: template.description,
      valueTag: type,
      metrics: {
        orderDrift: template.orderDrift,
        collectiveDrift: template.collectiveDrift,
        harmPressure: template.harmPressure + adaptiveBoost,
        recoveryStability: template.recoveryStability + adaptiveBoost,
        predictedOrder,
        predictedCollective,
        predictedBalance,
        balanceDiff: predictedBalance - balance_score
      }
    };
  });
};

// Generate Hebrew insight text based on comparison
const generateInsightText = (originalDecision, alternativePath) => {
  const { value_tag: originalTag, balance_score: originalBalance } = originalDecision;
  const { type: altType, metrics } = alternativePath;
  
  const insights = [];
  
  // Balance comparison
  if (metrics.balanceDiff > 10) {
    insights.push(`המסלול החלופי היה עשוי להוביל לאיזון גבוה יותר (+${metrics.balanceDiff} נקודות).`);
  } else if (metrics.balanceDiff < -10) {
    insights.push(`המסלול שבחרת הוביל לאיזון טוב יותר מהחלופה.`);
  }
  
  // Harm pressure comparison
  if (altType === 'recovery' && metrics.harmPressure < 0) {
    insights.push(`אם היית בוחר במסלול התאוששות, לחץ הנזק היה נמוך יותר.`);
  }
  
  // Order/contribution insights
  if (altType === 'order' && metrics.orderDrift > 10) {
    insights.push(`המסלול החלופי היה עשוי להוביל ליותר סדר ופחות הימנעות.`);
  }
  
  if (altType === 'contribution' && metrics.collectiveDrift > 10) {
    insights.push(`מסלול תרומה היה מחזק את הכיוון הקולקטיבי.`);
  }
  
  // Default insight if none generated
  if (insights.length === 0) {
    if (metrics.balanceDiff >= 0) {
      insights.push(`שני המסלולים היו מובילים לתוצאות דומות.`);
    } else {
      insights.push(`הבחירה שלך הייתה מתאימה למצב.`);
    }
  }
  
  return insights[0];
};

export default function DecisionReplaySection({ 
  replayDecision, 
  alternativePaths,
  onClose,
  onSaveReplay,
  adaptiveScores
}) {
  const [selectedAltPath, setSelectedAltPath] = useState(null);
  
  // Generate alternative paths if not provided
  const paths = useMemo(() => {
    if (alternativePaths && alternativePaths.length > 0) {
      return alternativePaths;
    }
    return replayDecision ? generateAlternativePaths(replayDecision, adaptiveScores) : [];
  }, [replayDecision, alternativePaths, adaptiveScores]);
  
  if (!replayDecision) {
    return null;
  }
  
  const handleSelectAltPath = (path) => {
    setSelectedAltPath(path);
    
    // Save replay metadata
    if (onSaveReplay) {
      onSaveReplay({
        replay_of_decision_id: replayDecision.id,
        original_value_tag: replayDecision.value_tag,
        alternative_path_id: path.id,
        alternative_path_type: path.type,
        predicted_metrics: path.metrics,
        timestamp: new Date().toISOString()
      });
    }
  };
  
  return (
    <section 
      className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-3xl p-5 shadow-sm border border-purple-200"
      dir="rtl"
      data-testid="decision-replay-section"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
            <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            הפעלה חוזרת של החלטה
          </h3>
          <p className="text-xs text-muted-foreground mt-1">בדוק מה היה קורה אם היית בוחר אחרת</p>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-purple-100 rounded-full transition-colors"
          data-testid="close-replay-btn"
        >
          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      {/* Original Decision Card */}
      <div className="bg-white/70 rounded-xl p-4 mb-4 border-2 border-purple-300">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-medium text-purple-600 bg-purple-100 px-2 py-1 rounded-full">
            ההחלטה המקורית
          </span>
          <span className="text-xs text-muted-foreground">{replayDecision.time}</span>
        </div>
        <p className="text-sm font-medium text-foreground mb-2">{replayDecision.action}</p>
        <div className="flex items-center gap-3 text-xs">
          <span className={`px-2 py-1 rounded-full ${valueColors[replayDecision.value_tag] || 'bg-gray-100'}`}>
            {valueLabels[replayDecision.value_tag] || replayDecision.value_tag}
          </span>
          <span className="text-muted-foreground">
            איזון: <span className="font-medium">{replayDecision.balance_score}</span>
          </span>
          <span className="text-muted-foreground">
            סדר: <span className="font-medium">{replayDecision.chaos_order}</span>
          </span>
          <span className="text-muted-foreground">
            קולקטיב: <span className="font-medium">{replayDecision.ego_collective}</span>
          </span>
        </div>
      </div>
      
      {/* Alternative Paths */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-foreground mb-3 flex items-center gap-2">
          <svg className="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
          </svg>
          מסלולים חלופיים אפשריים
        </h4>
        
        <div className="space-y-3">
          {paths.map((path) => (
            <div
              key={path.id}
              className={`bg-white/50 rounded-xl p-3 border-2 transition-all cursor-pointer hover:shadow-md ${
                selectedAltPath?.id === path.id 
                  ? 'border-purple-400 bg-purple-50/50' 
                  : 'border-transparent hover:border-purple-200'
              }`}
              onClick={() => handleSelectAltPath(path)}
              data-testid={`alt-path-${path.id}`}
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${valueColors[path.type]}`}>
                    {path.hebrewName}
                  </span>
                </div>
                {path.metrics.balanceDiff > 0 && (
                  <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
                    +{path.metrics.balanceDiff} איזון
                  </span>
                )}
                {path.metrics.balanceDiff < 0 && (
                  <span className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded-full">
                    {path.metrics.balanceDiff} איזון
                  </span>
                )}
              </div>
              
              <p className="text-sm text-foreground mb-1">{path.action}</p>
              <p className="text-xs text-muted-foreground mb-2">{path.description}</p>
              
              {/* Predicted Metrics */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center gap-1">
                  <span className="text-muted-foreground">סדר צפוי:</span>
                  <span className={`font-medium ${path.metrics.orderDrift > 0 ? 'text-indigo-600' : path.metrics.orderDrift < 0 ? 'text-orange-600' : ''}`}>
                    {path.metrics.predictedOrder}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-muted-foreground">קולקטיב צפוי:</span>
                  <span className={`font-medium ${path.metrics.collectiveDrift > 0 ? 'text-green-600' : path.metrics.collectiveDrift < 0 ? 'text-red-600' : ''}`}>
                    {path.metrics.predictedCollective}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-muted-foreground">לחץ נזק:</span>
                  <span className={`font-medium ${path.metrics.harmPressure < 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {path.metrics.harmPressure > 0 ? '+' : ''}{Math.round(path.metrics.harmPressure)}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <span className="text-muted-foreground">יציבות:</span>
                  <span className={`font-medium ${path.metrics.recoveryStability > 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                    {path.metrics.recoveryStability > 0 ? '+' : ''}{Math.round(path.metrics.recoveryStability)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Insight Text */}
      {selectedAltPath && (
        <div className="bg-gradient-to-r from-purple-100 to-violet-100 rounded-xl p-4 border border-purple-200" data-testid="replay-insight">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-purple-200 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-purple-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h5 className="text-sm font-semibold text-purple-800 mb-1">תובנה</h5>
              <p className="text-sm text-purple-700">
                {generateInsightText(replayDecision, selectedAltPath)}
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Help text */}
      {!selectedAltPath && (
        <div className="text-center text-xs text-muted-foreground py-2">
          לחץ על מסלול חלופי כדי לראות את התובנה
        </div>
      )}
    </section>
  );
}

// Export the path generation function for use in usePhilosState
export { generateAlternativePaths };
