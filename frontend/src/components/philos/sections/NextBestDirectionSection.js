import { useMemo, useState, useEffect } from 'react';
import { fetchCollectiveLayer } from '../../../services/dataService';
import { calculateCalibrationWeights } from './RecommendationCalibrationSection';

// Hebrew value tag labels
const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Direction colors
const directionColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300', fill: '#22c55e' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300', fill: '#3b82f6' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', border: 'border-indigo-300', fill: '#6366f1' },
  harm: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300', fill: '#ef4444' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-300', fill: '#9ca3af' }
};

// Action suggestions for each direction
const actionSuggestions = {
  contribution: [
    'פעולה קטנה של עזרה למישהו',
    'לשתף משהו שלמדת',
    'להציע סיוע לחבר'
  ],
  recovery: [
    'הפסקה קצרה ומודעת',
    'נשימות עמוקות לכמה דקות',
    'לצאת להליכה קצרה'
  ],
  order: [
    'פעולה קטנה של סדר',
    'לארגן משהו קטן בסביבה',
    'לסיים משימה פתוחה אחת'
  ],
  harm: [
    'לעצור ולנשום לפני תגובה',
    'לזהות את הרגש ולתת לו מקום',
    'לבחור בתגובה מתונה'
  ],
  avoidance: [
    'לבצע החלטה קטנה במקום דחייה',
    'לקחת צעד ראשון קטן',
    'להתמודד עם משהו אחד קטן'
  ]
};

// Calculate recommended direction based on multiple data sources
// calibrationWeights is an optional adjustment layer from follow-through data
const calculateRecommendation = (history, adaptiveScores, replayInsights, collectiveData, calibrationWeights = null) => {
  if (!history || history.length === 0) {
    return null;
  }

  // Analyze recent history (last 10 decisions)
  const recent = history.slice(0, 10);
  const valueCounts = {};
  recent.forEach(item => {
    const tag = item.value_tag;
    if (tag) {
      valueCounts[tag] = (valueCounts[tag] || 0) + 1;
    }
  });

  // Detect negative patterns
  const harmCount = valueCounts.harm || 0;
  const avoidanceCount = valueCounts.avoidance || 0;
  const negativeRatio = (harmCount + avoidanceCount) / recent.length;

  // Detect positive patterns
  const contributionCount = valueCounts.contribution || 0;
  const recoveryCount = valueCounts.recovery || 0;
  const orderCount = valueCounts.order || 0;

  // Use adaptive scores (including replay-based adjustments)
  const scores = adaptiveScores || {};
  
  // Apply calibration weights to scores (adjustment layer)
  const calibratedScores = { ...scores };
  if (calibrationWeights) {
    ['contribution', 'recovery', 'order'].forEach(dir => {
      calibratedScores[dir] = (calibratedScores[dir] || 0) + (calibrationWeights[dir] || 0);
    });
  }
  
  // Use replay insights for blind spots and preferences
  const replayAltCounts = replayInsights?.alternative_path_counts || {};
  const blindSpots = replayInsights?.blind_spots || [];
  const mostExploredAlt = Object.entries(replayAltCounts)
    .filter(([key]) => ['contribution', 'recovery', 'order'].includes(key))
    .sort((a, b) => b[1] - a[1])[0];

  // Use collective comparison if available
  const collectiveGap = collectiveData?.gap || null;

  // Decision logic with priority order
  let recommendedDirection = null;
  let reason = '';
  let strength = 0;
  let insight = '';
  let calibrationApplied = false;

  // Priority 1: Address strong negative drift (harm/avoidance patterns)
  if (negativeRatio > 0.4) {
    if (harmCount > avoidanceCount) {
      recommendedDirection = 'recovery';
      reason = 'negative_harm_drift';
      strength = Math.min(100, negativeRatio * 100 + 20);
      insight = 'זוהה דפוס של לחץ נזק גבוה. מומלץ לאזן עם התאוששות.';
    } else {
      recommendedDirection = 'order';
      reason = 'negative_avoidance_drift';
      strength = Math.min(100, negativeRatio * 100 + 10);
      insight = 'המערכת מזהה דפוס של הימנעות. מומלץ לבצע החלטה קטנה במקום דחייה.';
    }
  }
  // Priority 2: Address collective gap (user behind collective trend)
  else if (collectiveGap && collectiveGap.metric && collectiveGap.difference > 15) {
    recommendedDirection = collectiveGap.metric;
    reason = 'collective_gap';
    strength = Math.min(100, 45 + collectiveGap.difference);
    insight = `נראה פער מול מגמת ה${valueLabels[collectiveGap.metric]}. מומלץ לבצע פעולה קטנה בכיוון זה.`;
  }
  // Priority 3: Address replay blind spots
  else if (blindSpots.length > 0) {
    const relevantBlindSpot = blindSpots.find(spot => 
      ['contribution', 'recovery', 'order'].includes(spot.to)
    );
    if (relevantBlindSpot) {
      recommendedDirection = relevantBlindSpot.to;
      reason = 'replay_blind_spot';
      strength = 55;
      insight = `בהפעלות חוזרות מעולם לא בדקת מסלולי ${valueLabels[relevantBlindSpot.to]}. כדאי לנסות.`;
    }
  }
  // Priority 4: Reinforce positive momentum (with calibration adjustment)
  else if (contributionCount >= 2 || (calibratedScores.contribution || 0) > 5) {
    recommendedDirection = 'contribution';
    reason = 'positive_contribution_momentum';
    strength = Math.min(100, 50 + (calibratedScores.contribution || 0) * 3);
    insight = 'יש לך מומנטום חיובי של תרומה. המשך בכיוון זה.';
    if (calibrationWeights?.contribution > 0) calibrationApplied = true;
  }
  // Priority 5: Follow replay exploration preferences
  else if (mostExploredAlt && mostExploredAlt[1] >= 2) {
    recommendedDirection = mostExploredAlt[0];
    reason = 'replay_preference';
    strength = Math.min(100, 40 + mostExploredAlt[1] * 10);
    insight = `בהפעלות חוזרות בדקת הרבה מסלולי ${valueLabels[mostExploredAlt[0]]}. אולי זה הכיוון שחסר.`;
  }
  // Priority 6: Balance based on calibrated adaptive scores
  else {
    const positiveScores = [
      { type: 'contribution', score: calibratedScores.contribution || 0, count: contributionCount },
      { type: 'recovery', score: calibratedScores.recovery || 0, count: recoveryCount },
      { type: 'order', score: calibratedScores.order || 0, count: orderCount }
    ];
    
    // Sort by score descending to find the highest calibrated direction
    const sortedByScore = [...positiveScores].sort((a, b) => b.score - a.score);
    const highestCalibrated = sortedByScore[0];
    
    // Sort ascending to find lowest (for deficit detection)
    const sortedAsc = [...positiveScores].sort((a, b) => a.score - b.score);
    const lowestPositive = sortedAsc[0];
    
    // If calibration strongly favors a direction, use it
    if (calibrationWeights && highestCalibrated.score >= 3) {
      recommendedDirection = highestCalibrated.type;
      reason = 'calibration_boost';
      strength = Math.min(100, 45 + highestCalibrated.score * 5);
      insight = `הכיול מצביע על ${valueLabels[highestCalibrated.type]} כבעל הביצועים הטובים ביותר.`;
      calibrationApplied = true;
    } else if (lowestPositive.score < 0 || lowestPositive.count === 0) {
      recommendedDirection = lowestPositive.type;
      reason = 'balance_deficit';
      strength = Math.min(100, 35 + Math.abs(lowestPositive.score) * 2);
      insight = `מסלולי ${valueLabels[lowestPositive.type]} פחות נוכחים. כדאי לשקול פעולה בכיוון זה.`;
    } else {
      // Default to recovery as a safe recommendation
      recommendedDirection = 'recovery';
      reason = 'general_balance';
      strength = 40;
      insight = 'המערכת מאוזנת. התאוששות תמיד בחירה טובה.';
    }
  }

  // Ensure we have a direction
  if (!recommendedDirection) {
    recommendedDirection = 'recovery';
    reason = 'default';
    strength = 35;
    insight = 'אין מספיק נתונים. מומלץ להתחיל עם התאוששות.';
  }

  // Select action suggestion (deterministic based on recent count)
  const suggestions = actionSuggestions[recommendedDirection] || actionSuggestions.recovery;
  const suggestionIndex = recent.length % suggestions.length;
  const actionSuggestion = suggestions[suggestionIndex];

  return {
    direction: recommendedDirection,
    reason,
    strength,
    insight,
    actionSuggestion,
    negativeRatio,
    valueCounts,
    calibrationApplied
  };
};

export default function NextBestDirectionSection({ history, adaptiveScores, replayInsights, onFollowRecommendation }) {
  // State for collective data comparison
  const [collectiveGap, setCollectiveGap] = useState(null);

  // Fetch collective data and calculate gap
  useEffect(() => {
    const calculateCollectiveGap = async () => {
      if (!history || history.length < 3) return;

      try {
        const collectiveData = await fetchCollectiveLayer();
        if (!collectiveData.success) return;

        // Calculate user's value distribution
        const recent = history.slice(0, 20);
        const userCounts = { contribution: 0, recovery: 0, order: 0 };
        recent.forEach(item => {
          if (userCounts.hasOwnProperty(item.value_tag)) {
            userCounts[item.value_tag]++;
          }
        });

        // Normalize to percentages
        const userTotal = recent.length || 1;
        const userPcts = {
          contribution: (userCounts.contribution / userTotal) * 100,
          recovery: (userCounts.recovery / userTotal) * 100,
          order: (userCounts.order / userTotal) * 100
        };

        // Get collective distribution
        const collectiveDist = collectiveData.value_distribution || {};
        const collectiveTotal = Object.values(collectiveDist).reduce((a, b) => a + b, 1);
        const collectivePcts = {
          contribution: ((collectiveDist.contribution || 0) / collectiveTotal) * 100,
          recovery: ((collectiveDist.recovery || 0) / collectiveTotal) * 100,
          order: ((collectiveDist.order || 0) / collectiveTotal) * 100
        };

        // Find the largest gap where user is below collective
        let maxGap = { metric: null, difference: 0 };
        ['contribution', 'recovery', 'order'].forEach(metric => {
          const diff = collectivePcts[metric] - userPcts[metric];
          if (diff > maxGap.difference) {
            maxGap = { metric, difference: Math.round(diff) };
          }
        });

        if (maxGap.metric && maxGap.difference > 10) {
          setCollectiveGap(maxGap);
        }
      } catch (error) {
        console.log('Failed to calculate collective gap:', error);
      }
    };

    calculateCollectiveGap();
  }, [history]);

  // Build collective data object for calculation
  const collectiveDataForCalc = useMemo(() => {
    return collectiveGap ? { gap: collectiveGap } : null;
  }, [collectiveGap]);

  // Calculate calibration weights from follow-through data
  const calibration = useMemo(() => {
    return calculateCalibrationWeights(history);
  }, [history]);

  // Calculate recommendation using all available data sources + calibration
  const recommendation = useMemo(() => {
    const calibrationWeights = calibration.hasData ? calibration.weights : null;
    return calculateRecommendation(history, adaptiveScores, replayInsights, collectiveDataForCalc, calibrationWeights);
  }, [history, adaptiveScores, replayInsights, collectiveDataForCalc, calibration]);

  // Don't render if no recommendation
  if (!recommendation) {
    return null;
  }

  const { direction, strength, insight, actionSuggestion, reason, calibrationApplied } = recommendation;
  const colors = directionColors[direction] || directionColors.recovery;

  // Handler for following recommendation
  const handleFollowRecommendation = () => {
    if (onFollowRecommendation) {
      onFollowRecommendation({
        recommendation_text: actionSuggestion,
        recommendation_direction: direction,
        recommendation_reason: reason,
        recommendation_strength: strength,
        recommendation_insight: insight,
        followed_recommendation: true,
        timestamp: new Date().toISOString()
      });
    }
  };

  // SVG compass indicator
  const compassAngle = {
    contribution: -45,
    recovery: 45,
    order: 0,
    harm: 135,
    avoidance: 180
  }[direction] || 0;

  return (
    <section 
      className="bg-gradient-to-br from-sky-50 to-blue-50 rounded-3xl p-5 shadow-sm border border-sky-200"
      dir="rtl"
      data-testid="next-best-direction-section"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-sky-200 rounded-full flex items-center justify-center">
          <svg className="w-5 h-5 text-sky-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-foreground">כיוון מומלץ</h3>
          <p className="text-xs text-muted-foreground">
            ניווט התנהגותי מבוסס דפוסים
          </p>
        </div>
      </div>

      {/* Direction Card */}
      <div className={`${colors.bg} rounded-xl p-4 mb-4 border ${colors.border}`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            {/* Direction compass SVG */}
            <svg width="48" height="48" viewBox="0 0 48 48" data-testid="direction-compass">
              {/* Background circle */}
              <circle cx="24" cy="24" r="22" fill="white" stroke={colors.fill} strokeWidth="2" opacity="0.3" />
              
              {/* Strength arc */}
              <path
                d={`M 24 4 A 20 20 0 ${strength > 50 ? 1 : 0} 1 ${24 + 20 * Math.sin(strength * 3.6 * Math.PI / 180)} ${24 - 20 * Math.cos(strength * 3.6 * Math.PI / 180)}`}
                fill="none"
                stroke={colors.fill}
                strokeWidth="3"
                strokeLinecap="round"
              />
              
              {/* Direction arrow */}
              <g transform={`rotate(${compassAngle}, 24, 24)`}>
                <path
                  d="M 24 8 L 28 20 L 24 16 L 20 20 Z"
                  fill={colors.fill}
                />
                <circle cx="24" cy="24" r="4" fill={colors.fill} />
              </g>
              
              {/* Center dot */}
              <circle cx="24" cy="24" r="2" fill="white" />
            </svg>

            <div>
              <span className={`text-lg font-bold ${colors.text}`}>
                {valueLabels[direction]}
              </span>
              <div className="flex items-center gap-1 mt-1">
                <span className="text-xs text-muted-foreground">עוצמה:</span>
                <div className="w-16 h-1.5 bg-white/50 rounded-full overflow-hidden">
                  <div 
                    className="h-full rounded-full transition-all duration-500"
                    style={{ width: `${strength}%`, backgroundColor: colors.fill }}
                  />
                </div>
                <span className="text-xs text-muted-foreground">{strength}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Action suggestion */}
        <div className="bg-white/60 rounded-lg px-4 py-3" data-testid="action-suggestion">
          <p className={`text-sm font-medium ${colors.text}`}>
            כיוון מומלץ להיום: {actionSuggestion}
          </p>
        </div>
      </div>

      {/* Insight */}
      <div className="bg-white/60 rounded-xl p-4" data-testid="direction-insight">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-sky-200 rounded-full flex items-center justify-center flex-shrink-0">
            <svg className="w-4 h-4 text-sky-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div>
            <p className="text-sm text-sky-800">{insight}</p>
            <p className="text-xs text-muted-foreground mt-2">
              {reason === 'negative_harm_drift' && 'מבוסס על ניתוח דפוסי נזק אחרונים'}
              {reason === 'negative_avoidance_drift' && 'מבוסס על זיהוי דפוסי הימנעות'}
              {reason === 'collective_gap' && 'מבוסס על פער מול השדה הקולקטיבי'}
              {reason === 'replay_blind_spot' && 'מבוסס על נקודות עיוורות בהפעלות חוזרות'}
              {reason === 'positive_contribution_momentum' && 'מבוסס על מומנטום חיובי קיים'}
              {reason === 'replay_preference' && 'מבוסס על דפוסי הפעלה חוזרת'}
              {reason === 'calibration_boost' && 'מבוסס על כיול אוטומטי מתוצאות בפועל'}
              {reason === 'balance_deficit' && 'מבוסס על ניתוח איזון כיוונים'}
              {reason === 'general_balance' && 'המלצה כללית לאיזון'}
              {reason === 'default' && 'המלצה ראשונית'}
              {calibrationApplied && <span className="mr-1 text-amber-600">• משקל מכויל</span>}
            </p>
          </div>
        </div>
      </div>

      {/* Follow Recommendation Button */}
      <button
        onClick={handleFollowRecommendation}
        className={`w-full mt-4 px-4 py-3 ${colors.bg} ${colors.text} border-2 ${colors.border} rounded-xl font-medium hover:opacity-90 transition-all flex items-center justify-center gap-2`}
        data-testid="follow-recommendation-btn"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
        </svg>
        <span>פעל לפי ההמלצה</span>
      </button>
    </section>
  );
}
