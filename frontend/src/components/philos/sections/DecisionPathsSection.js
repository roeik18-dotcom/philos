import { useState, useMemo } from 'react';

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

// Action path templates based on context keywords
const pathTemplates = {
  conflict: [
    { action: 'שיחה פתוחה ורגועה', valueTag: 'contribution', orderDelta: 1, collectiveDelta: 2, harmRisk: 5, recoveryBoost: 0 },
    { action: 'לקחת הפסקה לפני תגובה', valueTag: 'recovery', orderDelta: 2, collectiveDelta: 0, harmRisk: 0, recoveryBoost: 30 },
    { action: 'להתעלם ולהמשיך הלאה', valueTag: 'avoidance', orderDelta: -1, collectiveDelta: -1, harmRisk: 10, recoveryBoost: 0 }
  ],
  stress: [
    { action: 'תרגיל נשימות עמוקות', valueTag: 'recovery', orderDelta: 1, collectiveDelta: 0, harmRisk: 0, recoveryBoost: 40 },
    { action: 'לארגן את סביבת העבודה', valueTag: 'order', orderDelta: 3, collectiveDelta: 0, harmRisk: 0, recoveryBoost: 10 },
    { action: 'לשתף מישהו קרוב', valueTag: 'contribution', orderDelta: 0, collectiveDelta: 2, harmRisk: 5, recoveryBoost: 20 }
  ],
  decision: [
    { action: 'לרשום יתרונות וחסרונות', valueTag: 'order', orderDelta: 3, collectiveDelta: 0, harmRisk: 0, recoveryBoost: 5 },
    { action: 'להתייעץ עם מישהו מנוסה', valueTag: 'contribution', orderDelta: 1, collectiveDelta: 2, harmRisk: 5, recoveryBoost: 10 },
    { action: 'לדחות את ההחלטה ליום', valueTag: 'avoidance', orderDelta: -1, collectiveDelta: 0, harmRisk: 15, recoveryBoost: 10 }
  ],
  anger: [
    { action: 'הליכה קצרה בחוץ', valueTag: 'recovery', orderDelta: 2, collectiveDelta: 0, harmRisk: 0, recoveryBoost: 35 },
    { action: 'כתיבה ביומן (לא לשלוח)', valueTag: 'order', orderDelta: 2, collectiveDelta: 0, harmRisk: 0, recoveryBoost: 20 },
    { action: 'להביע את הרגש בשיחה', valueTag: 'contribution', orderDelta: 0, collectiveDelta: 1, harmRisk: 20, recoveryBoost: 15 }
  ],
  tired: [
    { action: 'מנוחה קצרה של 20 דקות', valueTag: 'recovery', orderDelta: 1, collectiveDelta: 0, harmRisk: 0, recoveryBoost: 50 },
    { action: 'שתיית מים וחטיף בריא', valueTag: 'recovery', orderDelta: 1, collectiveDelta: 0, harmRisk: 0, recoveryBoost: 25 },
    { action: 'להמשיך לעבוד בכל זאת', valueTag: 'avoidance', orderDelta: -2, collectiveDelta: 0, harmRisk: 25, recoveryBoost: -10 }
  ],
  default: [
    { action: 'לפעול לטובת אחרים', valueTag: 'contribution', orderDelta: 1, collectiveDelta: 2, harmRisk: 5, recoveryBoost: 10 },
    { action: 'לקחת רגע להתאוששות', valueTag: 'recovery', orderDelta: 1, collectiveDelta: 0, harmRisk: 0, recoveryBoost: 30 },
    { action: 'לארגן ולתכנן', valueTag: 'order', orderDelta: 3, collectiveDelta: 0, harmRisk: 0, recoveryBoost: 5 }
  ]
};

// Detect context from input text
const detectContext = (text) => {
  const lower = text.toLowerCase();
  if (lower.match(/כעס|עצבני|מתוסכל|רוגז|anger|angry|frustrated/)) return 'anger';
  if (lower.match(/לחץ|מתח|stress|stressed|overwhelmed|עמוס/)) return 'stress';
  if (lower.match(/קונפליקט|ויכוח|conflict|argument|מריבה/)) return 'conflict';
  if (lower.match(/החלטה|לבחור|decision|choose|דילמה/)) return 'decision';
  if (lower.match(/עייף|עייפות|tired|exhausted|מותש/)) return 'tired';
  return 'default';
};

export default function DecisionPathsSection({ currentState, onSelectPath }) {
  const [contextInput, setContextInput] = useState('');
  const [showPaths, setShowPaths] = useState(false);

  // Generate paths based on context
  const paths = useMemo(() => {
    if (!contextInput.trim()) return [];
    
    const context = detectContext(contextInput);
    const templates = pathTemplates[context] || pathTemplates.default;
    
    return templates.map((template, idx) => {
      const baseOrder = currentState?.chaos_order || 0;
      const baseCollective = currentState?.ego_collective || 0;
      
      // Calculate predicted metrics
      const predictedOrderDrift = template.orderDelta;
      const predictedCollectiveDrift = template.collectiveDelta;
      const predictedHarmPressure = template.harmRisk;
      const predictedRecoveryStability = template.recoveryBoost;
      
      // Calculate orientation score (higher = better)
      const orientationScore = 
        (template.orderDelta * 2) + 
        (template.collectiveDelta * 2) + 
        (template.recoveryBoost * 0.5) - 
        (template.harmRisk * 1.5);
      
      return {
        id: `path-${idx}`,
        label: ['א׳', 'ב׳', 'ג׳'][idx],
        action: template.action,
        valueTag: template.valueTag,
        predictedOrderDrift,
        predictedCollectiveDrift,
        predictedHarmPressure,
        predictedRecoveryStability,
        orientationScore,
        projectedOrder: baseOrder + template.orderDelta * 10,
        projectedCollective: baseCollective + template.collectiveDelta * 10
      };
    });
  }, [contextInput, currentState]);

  // Find best path
  const bestPathId = useMemo(() => {
    if (paths.length === 0) return null;
    const best = paths.reduce((a, b) => a.orientationScore > b.orientationScore ? a : b);
    return best.id;
  }, [paths]);

  const handleSelectPath = (path) => {
    if (onSelectPath) {
      onSelectPath(path.action, path.valueTag, path.projectedOrder, path.projectedCollective);
    }
  };

  return (
    <section className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-3xl p-5 shadow-sm border border-emerald-200" data-testid="decision-paths-section">
      <h3 className="text-lg font-semibold text-foreground mb-2">מסלולי החלטה</h3>
      <p className="text-xs text-muted-foreground mb-4">הזן הקשר או אירוע לקבלת מסלולים אפשריים</p>
      
      {/* Context Input */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <label className="text-xs text-muted-foreground block mb-2">מה קורה עכשיו?</label>
        <input
          type="text"
          value={contextInput}
          onChange={(e) => setContextInput(e.target.value)}
          placeholder="לדוגמה: אני מרגיש לחץ בעבודה..."
          className="w-full px-4 py-3 border border-emerald-200 rounded-xl text-base mb-3"
          data-testid="context-input"
        />
        <button
          onClick={() => setShowPaths(contextInput.trim().length > 0)}
          disabled={!contextInput.trim()}
          className="w-full px-4 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all"
          data-testid="generate-paths-btn"
        >
          הצג מסלולים אפשריים
        </button>
      </div>
      
      {/* Path Cards */}
      {showPaths && paths.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm font-semibold text-foreground mb-2">3 מסלולים אפשריים:</p>
          
          {paths.map((path) => {
            const isBest = path.id === bestPathId;
            
            return (
              <div
                key={path.id}
                className={`bg-white rounded-xl p-4 border-2 transition-all ${
                  isBest 
                    ? 'border-emerald-400 shadow-md ring-2 ring-emerald-200' 
                    : 'border-gray-100'
                }`}
                data-testid={`path-card-${path.label}`}
              >
                {/* Path Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${
                      isBest ? 'bg-emerald-500' : 'bg-gray-400'
                    }`}>
                      {path.label}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${valueColors[path.valueTag]} text-white`}>
                      {valueLabels[path.valueTag]}
                    </span>
                    {isBest && (
                      <span className="px-2 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium">
                        מומלץ ⭐
                      </span>
                    )}
                  </div>
                </div>
                
                {/* Action */}
                <p className="text-base font-medium text-foreground mb-3">{path.action}</p>
                
                {/* Predicted Metrics */}
                <div className="grid grid-cols-2 gap-2 mb-3">
                  <div className="bg-gray-50 rounded-lg p-2 text-center">
                    <p className="text-xs text-muted-foreground">סחף סדר צפוי</p>
                    <p className={`text-sm font-bold ${path.predictedOrderDrift > 0 ? 'text-green-600' : path.predictedOrderDrift < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                      {path.predictedOrderDrift > 0 ? '+' : ''}{path.predictedOrderDrift}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2 text-center">
                    <p className="text-xs text-muted-foreground">סחף חברתי צפוי</p>
                    <p className={`text-sm font-bold ${path.predictedCollectiveDrift > 0 ? 'text-green-600' : path.predictedCollectiveDrift < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                      {path.predictedCollectiveDrift > 0 ? '+' : ''}{path.predictedCollectiveDrift}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2 text-center">
                    <p className="text-xs text-muted-foreground">סיכון נזק</p>
                    <p className={`text-sm font-bold ${path.predictedHarmPressure > 15 ? 'text-red-600' : path.predictedHarmPressure > 5 ? 'text-yellow-600' : 'text-green-600'}`}>
                      {path.predictedHarmPressure}%
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-2 text-center">
                    <p className="text-xs text-muted-foreground">תמיכה בהתאוששות</p>
                    <p className={`text-sm font-bold ${path.predictedRecoveryStability > 20 ? 'text-green-600' : path.predictedRecoveryStability > 0 ? 'text-blue-600' : 'text-gray-500'}`}>
                      {path.predictedRecoveryStability > 0 ? '+' : ''}{path.predictedRecoveryStability}%
                    </p>
                  </div>
                </div>
                
                {/* Select Button */}
                <button
                  onClick={() => handleSelectPath(path)}
                  className={`w-full px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isBest 
                      ? 'bg-emerald-100 hover:bg-emerald-200 text-emerald-700' 
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                  }`}
                  data-testid={`select-path-${path.label}`}
                >
                  בחר מסלול זה
                </button>
              </div>
            );
          })}
          
          {/* Insight */}
          <div className="bg-emerald-100/50 border border-emerald-200 rounded-xl p-4 mt-4">
            <p className="text-sm font-semibold text-emerald-800 mb-1">תובנה</p>
            <p className="text-sm text-emerald-700">
              מסלול {paths.find(p => p.id === bestPathId)?.label} מומלץ כי הוא משפר את האוריינטציה הכוללת (סדר + התאוששות + תרומה) עם סיכון נזק מינימלי.
            </p>
          </div>
        </div>
      )}
      
      {/* Empty State */}
      {!showPaths && (
        <div className="text-center py-6 bg-white/50 rounded-xl">
          <p className="text-muted-foreground text-sm">הזן הקשר או מצב כדי לקבל מסלולי החלטה</p>
          <div className="flex flex-wrap justify-center gap-2 mt-3">
            {['לחץ בעבודה', 'ויכוח עם חבר', 'עייפות', 'החלטה קשה'].map(example => (
              <button
                key={example}
                onClick={() => setContextInput(example)}
                className="px-3 py-1 text-xs bg-emerald-100 hover:bg-emerald-200 text-emerald-700 rounded-lg transition-all"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
