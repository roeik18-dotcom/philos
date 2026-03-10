// Centralized Recommendation Service for Philos Orientation
// Single source of truth for all recommendation calculations

import { fetchCollectiveLayer } from './dataService';

// Hebrew value tag labels
export const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Direction colors (shared across components)
export const directionColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300', fill: '#22c55e' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300', fill: '#3b82f6' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', border: 'border-indigo-300', fill: '#6366f1' },
  harm: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-300', fill: '#ef4444' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-600', border: 'border-gray-300', fill: '#9ca3af' }
};

// Action suggestions for each direction
export const actionSuggestions = {
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

/**
 * Analyze value counts from recent history
 * @param {Array} history - Decision history array
 * @param {number} limit - Number of recent decisions to analyze (default: 10)
 * @returns {Object} Value counts and ratios
 */
export const analyzeRecentHistory = (history, limit = 10) => {
  if (!history || history.length === 0) {
    return {
      valueCounts: {},
      negativeRatio: 0,
      positiveRatio: 0,
      harmCount: 0,
      avoidanceCount: 0,
      contributionCount: 0,
      recoveryCount: 0,
      orderCount: 0,
      recentLength: 0
    };
  }

  const recent = history.slice(0, limit);
  const valueCounts = {};
  
  recent.forEach(item => {
    const tag = item.value_tag;
    if (tag) {
      valueCounts[tag] = (valueCounts[tag] || 0) + 1;
    }
  });

  const harmCount = valueCounts.harm || 0;
  const avoidanceCount = valueCounts.avoidance || 0;
  const contributionCount = valueCounts.contribution || 0;
  const recoveryCount = valueCounts.recovery || 0;
  const orderCount = valueCounts.order || 0;

  const negativeRatio = recent.length > 0 ? (harmCount + avoidanceCount) / recent.length : 0;
  const positiveRatio = recent.length > 0 ? (contributionCount + recoveryCount + orderCount) / recent.length : 0;

  return {
    valueCounts,
    negativeRatio,
    positiveRatio,
    harmCount,
    avoidanceCount,
    contributionCount,
    recoveryCount,
    orderCount,
    recentLength: recent.length
  };
};

/**
 * Calculate calibration weights from follow-through data
 * Extracted from RecommendationCalibrationSection for reuse
 * @param {Array} history - Full decision history
 * @returns {Object} Calibration weights and metadata
 */
export const calculateCalibrationWeights = (history) => {
  const weights = {
    contribution: 0,
    recovery: 0,
    order: 0,
    harm: 0,
    avoidance: 0
  };

  if (!history || history.length === 0) {
    return { weights, hasData: false, insights: [] };
  }

  // Filter decisions that followed recommendations
  const followedDecisions = history.filter(d => d.followed_recommendation === true);
  const followedCount = followedDecisions.length;

  // Need at least 3 followed recommendations to calibrate
  if (followedCount < 3) {
    return { weights, hasData: false, insights: [] };
  }

  // Calculate follow rate and alignment by direction
  const directionStats = {};
  const positiveDirections = ['contribution', 'recovery', 'order'];

  positiveDirections.forEach(dir => {
    directionStats[dir] = {
      followCount: 0,
      alignedCount: 0,
      totalRecommended: 0
    };
  });

  // Count recommendations by direction
  followedDecisions.forEach(decision => {
    const recDir = decision.recommendation_direction;
    const actualTag = decision.value_tag;
    
    if (directionStats[recDir]) {
      directionStats[recDir].followCount++;
      directionStats[recDir].totalRecommended++;
      
      // Check if outcome aligned with recommendation
      if (recDir === actualTag) {
        directionStats[recDir].alignedCount++;
      }
    }
  });

  // Calculate calibration weights based on follow-through and alignment
  const insights = [];
  let strongestDir = null;
  let strongestWeight = -Infinity;
  let weakestDir = null;
  let weakestWeight = Infinity;

  positiveDirections.forEach(dir => {
    const stats = directionStats[dir];
    
    // Only calculate weight if this direction has been recommended at least once
    if (stats.totalRecommended >= 1) {
      // Calculate follow rate for this direction
      const followRate = stats.followCount / followedCount;
      
      // Calculate alignment rate for this direction
      const alignmentRate = stats.totalRecommended > 0 
        ? stats.alignedCount / stats.totalRecommended 
        : 0;

      let weight = 0;

      if (alignmentRate > 0.6) {
        // Strong alignment - significant boost
        weight = Math.round(alignmentRate * 5);
        insights.push({
          type: 'boost',
          direction: dir,
          text: `מסלולי ${valueLabels[dir]} קיבלו חיזוק בעקבות התאמה גבוהה לתוצאות בפועל (${Math.round(alignmentRate * 100)}%)`,
          priority: 'positive'
        });
      } else if (alignmentRate > 0.4) {
        // Moderate alignment - small boost
        weight = Math.round((alignmentRate - 0.3) * 5);
      } else if (alignmentRate < 0.3 && stats.totalRecommended >= 1) {
        // Weak alignment - reduce weight
        weight = -Math.round((0.3 - alignmentRate) * 5);
        if (stats.totalRecommended >= 2) {
          insights.push({
            type: 'reduce',
            direction: dir,
            text: `מסלולי ${valueLabels[dir]} מקבלים כרגע משקל נמוך יותר עקב פער בין המלצה לתוצאה (${Math.round(alignmentRate * 100)}% התאמה)`,
            priority: 'warning'
          });
        }
      }

      // Adjust based on follow rate
      if (followRate > 0.4 && weight > 0) {
        weight = Math.min(5, weight + 1);
      } else if (followRate < 0.2 && stats.totalRecommended >= 1) {
        weight = Math.max(-3, weight - 1);
      }

      // Bound weights between -5 and +5
      weights[dir] = Math.max(-5, Math.min(5, weight));

      // Track strongest and weakest
      if (weights[dir] > strongestWeight) {
        strongestWeight = weights[dir];
        strongestDir = dir;
      }
      if (weights[dir] < weakestWeight) {
        weakestWeight = weights[dir];
        weakestDir = dir;
      }
    }
  });

  // Add summary insight if significant calibration exists
  const hasSignificantCalibration = Object.values(weights).some(w => Math.abs(w) >= 2);
  if (hasSignificantCalibration && strongestDir && strongestDir !== weakestDir) {
    insights.push({
      type: 'summary',
      text: `הכיול הנוכחי מעדיף ${valueLabels[strongestDir]} על פני ${valueLabels[weakestDir]}`,
      priority: 'info'
    });
  }

  return {
    weights,
    hasData: true,
    insights: insights.slice(0, 3),
    strongestDir,
    weakestDir,
    directionStats
  };
};

/**
 * Calculate recommended direction based on multiple data sources
 * This is the SINGLE SOURCE OF TRUTH for recommendation calculations
 * 
 * @param {Object} params - Parameters for recommendation
 * @param {Array} params.history - Decision history
 * @param {Object} params.adaptiveScores - Adaptive scores from learning
 * @param {Object} params.replayInsights - Replay insights data
 * @param {Object} params.collectiveData - Collective comparison data (optional)
 * @param {Object} params.calibrationWeights - Calibration weights (optional, will calculate if not provided)
 * @returns {Object|null} Recommendation result or null if no history
 */
export const calculateRecommendation = ({
  history,
  adaptiveScores = null,
  replayInsights = null,
  collectiveData = null,
  calibrationWeights = null
}) => {
  // Return default recommendation for new users
  if (!history || history.length === 0) {
    return {
      direction: 'recovery',
      reason: 'no_history',
      strength: 35,
      insight: 'אין מספיק נתונים. מומלץ להתחיל עם התאוששות.',
      actionSuggestion: actionSuggestions.recovery[0],
      negativeRatio: 0,
      valueCounts: {},
      calibrationApplied: false
    };
  }

  // Analyze recent history
  const analysis = analyzeRecentHistory(history, 10);
  const { 
    valueCounts, 
    negativeRatio, 
    harmCount, 
    avoidanceCount, 
    contributionCount, 
    recoveryCount, 
    orderCount,
    recentLength 
  } = analysis;

  // Use provided calibration weights or calculate them
  const calibration = calibrationWeights || calculateCalibrationWeights(history);
  const effectiveCalibrationWeights = calibration.hasData ? calibration.weights : null;

  // Use adaptive scores (including replay-based adjustments)
  const scores = adaptiveScores || {};
  
  // Apply calibration weights to scores (adjustment layer)
  const calibratedScores = { ...scores };
  if (effectiveCalibrationWeights) {
    ['contribution', 'recovery', 'order'].forEach(dir => {
      calibratedScores[dir] = (calibratedScores[dir] || 0) + (effectiveCalibrationWeights[dir] || 0);
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
  if (!recommendedDirection && (contributionCount >= 2 || (calibratedScores.contribution || 0) > 5)) {
    recommendedDirection = 'contribution';
    reason = 'positive_contribution_momentum';
    strength = Math.min(100, 50 + (calibratedScores.contribution || 0) * 3);
    insight = 'יש לך מומנטום חיובי של תרומה. המשך בכיוון זה.';
    if (effectiveCalibrationWeights?.contribution > 0) calibrationApplied = true;
  }
  // Priority 5: Follow replay exploration preferences
  else if (!recommendedDirection && mostExploredAlt && mostExploredAlt[1] >= 2) {
    recommendedDirection = mostExploredAlt[0];
    reason = 'replay_preference';
    strength = Math.min(100, 40 + mostExploredAlt[1] * 10);
    insight = `בהפעלות חוזרות בדקת הרבה מסלולי ${valueLabels[mostExploredAlt[0]]}. אולי זה הכיוון שחסר.`;
  }
  // Priority 6: Balance based on calibrated adaptive scores
  else if (!recommendedDirection) {
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
    if (effectiveCalibrationWeights && highestCalibrated.score >= 3) {
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

  // Ensure we have a direction (fallback)
  if (!recommendedDirection) {
    recommendedDirection = 'recovery';
    reason = 'default';
    strength = 35;
    insight = 'אין מספיק נתונים. מומלץ להתחיל עם התאוששות.';
  }

  // Select action suggestion (deterministic based on recent count)
  const suggestions = actionSuggestions[recommendedDirection] || actionSuggestions.recovery;
  const suggestionIndex = recentLength % suggestions.length;
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

/**
 * Calculate collective gap between user and collective metrics
 * @param {Array} history - User's decision history
 * @returns {Promise<Object|null>} Gap data or null
 */
export const calculateCollectiveGap = async (history) => {
  if (!history || history.length < 3) return null;

  try {
    const collectiveData = await fetchCollectiveLayer();
    if (!collectiveData.success) return null;

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
    const collectiveDist = collectiveData.value_distribution || collectiveData.value_counts || {};
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
      return maxGap;
    }

    return null;
  } catch (error) {
    console.log('Failed to calculate collective gap:', error);
    return null;
  }
};

/**
 * Analyze current state from recent decisions (for Home display)
 * @param {Array} history - Decision history
 * @returns {Object} Current state analysis
 */
export const analyzeCurrentState = (history) => {
  if (!history || history.length === 0) {
    return {
      hasData: false,
      summary: 'אין נתונים עדיין',
      pattern: null,
      patternType: 'neutral',
      todayCount: 0,
      totalCount: 0
    };
  }

  // Get today's decisions
  const today = new Date().toDateString();
  const todayDecisions = history.filter(h => {
    const itemDate = h.timestamp ? new Date(h.timestamp).toDateString() : today;
    return itemDate === today;
  });

  // Analyze recent pattern (last 5 decisions for state summary)
  const analysis = analyzeRecentHistory(history, 5);
  const { 
    negativeRatio, 
    positiveRatio,
    harmCount, 
    avoidanceCount, 
    contributionCount, 
    recoveryCount, 
    orderCount 
  } = analysis;

  let summary = '';
  let pattern = null;
  let patternType = 'neutral';

  if (negativeRatio > 0.5) {
    if (harmCount > avoidanceCount) {
      pattern = 'harm';
      patternType = 'negative';
      summary = 'נראה דפוס של לחץ ונזק.';
    } else {
      pattern = 'avoidance';
      patternType = 'negative';
      summary = 'נראה דפוס של הימנעות.';
    }
  } else if (positiveRatio > 0.6) {
    if (contributionCount >= recoveryCount && contributionCount >= orderCount) {
      pattern = 'contribution';
      patternType = 'positive';
      summary = 'מומנטום חיובי של תרומה.';
    } else if (recoveryCount >= orderCount) {
      pattern = 'recovery';
      patternType = 'positive';
      summary = 'איזון טוב של התאוששות.';
    } else {
      pattern = 'order';
      patternType = 'positive';
      summary = 'מיקוד בסדר וארגון.';
    }
  } else {
    pattern = 'balanced';
    patternType = 'neutral';
    summary = 'המערכת מאוזנת.';
  }

  // Get last decision info
  const lastDecision = history[0];

  return {
    hasData: true,
    summary,
    pattern,
    patternType,
    todayCount: todayDecisions.length,
    totalCount: history.length,
    lastValueTag: lastDecision?.value_tag,
    lastAction: lastDecision?.action?.substring(0, 50)
  };
};

/**
 * Build recommendation metadata for saving with decision
 * @param {Object} recommendation - Recommendation result
 * @returns {Object} Metadata to save
 */
export const buildRecommendationMetadata = (recommendation) => {
  if (!recommendation) return null;
  
  return {
    recommendation_text: recommendation.actionSuggestion,
    recommendation_direction: recommendation.direction,
    recommendation_reason: recommendation.reason,
    recommendation_strength: recommendation.strength,
    recommendation_insight: recommendation.insight,
    followed_recommendation: true,
    timestamp: new Date().toISOString()
  };
};
