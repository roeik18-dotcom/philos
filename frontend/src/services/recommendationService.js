// Centralized Recommendation Service for Philos Orientation
// Single source of truth for all recommendation calculations
// Connected directly to the theoretical framework

import { fetchCollectiveLayer } from './dataService';

// ==================== THEORETICAL FRAMEWORK ====================
// These are the core rules from the theory that drive all recommendations

/**
 * THEORY-BASED BALANCING PATHS
 * The fundamental rules that connect current direction to recommended direction
 */
export const theoryBalancingPaths = {
  harm: {
    balancingDirection: 'recovery',
    explanation: 'פעולות נזק דורשות איזון דרך התאוששות',
    explanationEn: 'Harm actions require balancing through recovery'
  },
  avoidance: {
    balancingDirection: 'order',
    explanation: 'הימנעות מאוזנת על ידי יצירת סדר ומבנה',
    explanationEn: 'Avoidance is balanced by creating order and structure'
  },
  isolation: {
    balancingDirection: 'contribution',
    explanation: 'מיקוד עצמי מאוזן על ידי תרומה לאחרים',
    explanationEn: 'Self-focus is balanced by contributing to others'
  },
  rigidity: {
    balancingDirection: 'exploration',
    explanation: 'קיפאון מאוזן על ידי פתיחות וחקירה',
    explanationEn: 'Rigidity is balanced by openness and exploration'
  }
};

/**
 * POSITIVE DIRECTION REINFORCEMENT
 * When current direction is already positive, suggest strengthening or adjacent positive
 */
export const positiveReinforcement = {
  recovery: {
    strengthen: 'recovery',
    adjacent: 'order',
    explanation: 'להמשיך בהתאוששות או להוסיף סדר'
  },
  order: {
    strengthen: 'order',
    adjacent: 'contribution',
    explanation: 'לחזק את הסדר או לפתוח לתרומה'
  },
  contribution: {
    strengthen: 'contribution',
    adjacent: 'exploration',
    explanation: 'להמשיך בתרומה או לפתוח לחקירה'
  },
  exploration: {
    strengthen: 'exploration',
    adjacent: 'recovery',
    explanation: 'להמשיך בחקירה או לאזן עם התאוששות'
  }
};

/**
 * COMPASS POSITION MAPPING
 * Maps value tags to positions on the quadrant grid
 * X axis: Ego (0) ↔ Collective (100)
 * Y axis: Chaos (100) ↔ Order (0)
 */
export const compassPositions = {
  // Positive directions
  recovery: { x: 30, y: 65, quadrant: 'lower-left' },      // Ego side, toward chaos (stabilizing)
  order: { x: 30, y: 25, quadrant: 'upper-left' },         // Ego side, toward order
  contribution: { x: 70, y: 25, quadrant: 'upper-right' }, // Collective side, toward order
  exploration: { x: 70, y: 65, quadrant: 'lower-right' },  // Collective side, toward chaos (opening)
  // Negative directions
  harm: { x: 15, y: 85, quadrant: 'far-lower-left' },      // Extreme ego, extreme chaos
  avoidance: { x: 50, y: 90, quadrant: 'bottom-center' }   // Center, extreme chaos
};

// ==================== LABELS AND COLORS ====================

// Hebrew value tag labels (extended for theory)
export const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  exploration: 'חקירה',
  harm: 'נזק',
  avoidance: 'הימנעות',
  isolation: 'בידוד',
  rigidity: 'נוקשות'
};

// Direction colors (shared across components)
export const directionColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-300', fill: '#22c55e' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-300', fill: '#3b82f6' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', border: 'border-indigo-300', fill: '#6366f1' },
  exploration: { bg: 'bg-amber-100', text: 'text-amber-700', border: 'border-amber-300', fill: '#f59e0b' },
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
  exploration: [
    'לנסות משהו חדש',
    'לשאול שאלה פתוחה',
    'לצאת מאזור הנוחות'
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

// ==================== CORE THEORY FUNCTIONS ====================

/**
 * Get the theory-based balancing direction for a given current direction
 * This is the PRIMARY recommendation logic based on the theoretical framework
 * 
 * @param {string} currentDirection - The current/dominant direction
 * @returns {Object} Balancing recommendation { direction, reason, explanation }
 */
export const getTheoryBasedRecommendation = (currentDirection) => {
  // Negative directions → Apply balancing path from theory
  if (theoryBalancingPaths[currentDirection]) {
    const path = theoryBalancingPaths[currentDirection];
    return {
      direction: path.balancingDirection,
      reason: 'theory_balancing',
      explanation: path.explanation,
      fromTheory: true
    };
  }

  // Positive directions → Strengthen or suggest adjacent
  if (positiveReinforcement[currentDirection]) {
    const reinforcement = positiveReinforcement[currentDirection];
    return {
      direction: reinforcement.adjacent, // Default to adjacent for variety
      reason: 'theory_reinforcement',
      explanation: reinforcement.explanation,
      fromTheory: true,
      alternativeDirection: reinforcement.strengthen
    };
  }

  // Default fallback
  return {
    direction: 'recovery',
    reason: 'default',
    explanation: 'התאוששות היא תמיד בחירה טובה',
    fromTheory: false
  };
};

/**
 * Identify the dominant pattern from recent history
 * Maps actual value tags to theory categories (including isolation, rigidity)
 * 
 * @param {Array} history - Decision history
 * @param {number} limit - Number of recent decisions to analyze
 * @returns {Object} Pattern analysis
 */
export const identifyDominantPattern = (history, limit = 10) => {
  if (!history || history.length === 0) {
    return {
      dominantDirection: null,
      patternType: 'none',
      valueCounts: {},
      theoryCategory: null
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

  // Find dominant direction
  const sorted = Object.entries(valueCounts).sort((a, b) => b[1] - a[1]);
  const dominant = sorted[0];

  if (!dominant) {
    return {
      dominantDirection: null,
      patternType: 'balanced',
      valueCounts,
      theoryCategory: null
    };
  }

  const [dominantTag, dominantCount] = dominant;
  const dominanceRatio = dominantCount / recent.length;

  // Map to theory categories
  let theoryCategory = dominantTag;
  let patternType = 'positive';

  // Detect negative patterns
  if (dominantTag === 'harm') {
    theoryCategory = 'harm';
    patternType = 'negative';
  } else if (dominantTag === 'avoidance') {
    theoryCategory = 'avoidance';
    patternType = 'negative';
  }

  // Detect isolation pattern (too much self-focus, low contribution)
  const contributionCount = valueCounts.contribution || 0;
  const totalPositive = (valueCounts.recovery || 0) + (valueCounts.order || 0) + contributionCount;
  if (totalPositive > 0 && contributionCount === 0 && dominanceRatio > 0.5) {
    theoryCategory = 'isolation';
    patternType = 'negative';
  }

  // Detect rigidity pattern (too much order, no exploration/flexibility)
  const explorationCount = valueCounts.exploration || 0;
  const orderCount = valueCounts.order || 0;
  if (orderCount >= 3 && explorationCount === 0 && (valueCounts.recovery || 0) === 0) {
    theoryCategory = 'rigidity';
    patternType = 'negative';
  }

  return {
    dominantDirection: dominantTag,
    dominantCount,
    dominanceRatio,
    patternType,
    valueCounts,
    theoryCategory
  };
};

/**
 * Calculate compass position from history
 * Uses LAST 7 DAYS of actions to determine weighted position on the quadrant grid
 * 
 * @param {Array} history - Decision history
 * @param {Object} currentState - Current state object (optional)
 * @returns {Object} Compass position { x, y, valueTag, quadrant, dominantDirection }
 */
export const calculateCompassPosition = (history, currentState = {}) => {
  if (!history || history.length === 0) {
    return { x: 50, y: 50, valueTag: null, quadrant: 'center', dominantDirection: null };
  }

  // Filter to last 7 days
  const now = new Date();
  const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  
  const recentHistory = history.filter(h => {
    if (!h.timestamp) return true; // Include if no timestamp (assume recent)
    const itemDate = new Date(h.timestamp);
    return itemDate >= sevenDaysAgo;
  });

  // If no recent history, use all history but limit to 20
  const relevantHistory = recentHistory.length > 0 ? recentHistory : history.slice(0, 20);

  if (relevantHistory.length === 0) {
    return { x: 50, y: 50, valueTag: null, quadrant: 'center', dominantDirection: null };
  }

  // Count value tags and calculate weighted averages
  const valueCounts = {};
  let totalChaosOrder = 0;
  let totalEgoCollective = 0;
  let countWithValues = 0;

  relevantHistory.forEach((h, index) => {
    const tag = h.value_tag;
    if (tag) {
      // More recent actions have higher weight (decay factor)
      const weight = Math.max(0.3, 1 - (index * 0.05));
      valueCounts[tag] = (valueCounts[tag] || 0) + weight;
    }
    
    // Accumulate chaos_order and ego_collective for position
    if (h.chaos_order !== undefined || h.ego_collective !== undefined) {
      const weight = Math.max(0.3, 1 - (index * 0.05));
      totalChaosOrder += (h.chaos_order || 0) * weight;
      totalEgoCollective += (h.ego_collective || 0) * weight;
      countWithValues += weight;
    }
  });

  // Find dominant direction (highest weighted count)
  const sortedTags = Object.entries(valueCounts).sort((a, b) => b[1] - a[1]);
  const dominantDirection = sortedTags.length > 0 ? sortedTags[0][0] : null;
  
  // Get latest value tag for display
  const latestValueTag = relevantHistory[0]?.value_tag || dominantDirection;

  // Calculate average position from actual values
  const avgChaosOrder = countWithValues > 0 ? totalChaosOrder / countWithValues : 0;
  const avgEgoCollective = countWithValues > 0 ? totalEgoCollective / countWithValues : 0;

  // Map values to compass coordinates
  // ego_collective: -100 (ego/left) to +100 (collective/right) → x: 0 to 100
  // chaos_order: -100 (chaos/bottom) to +100 (order/top) → y: 100 to 0
  const stateX = 50 + (avgEgoCollective / 2);
  const stateY = 50 - (avgChaosOrder / 2);

  // Get theory position for dominant direction
  const theoryPosition = compassPositions[dominantDirection] || { x: 50, y: 50 };

  // Blend theory position with actual state values (60% theory, 40% actual)
  const x = Math.round((theoryPosition.x * 0.6) + (stateX * 0.4));
  const y = Math.round((theoryPosition.y * 0.6) + (stateY * 0.4));

  // Determine quadrant
  let quadrant = 'center';
  if (x < 50 && y < 50) quadrant = 'upper-left';      // Order + Ego
  else if (x >= 50 && y < 50) quadrant = 'upper-right'; // Order + Collective
  else if (x < 50 && y >= 50) quadrant = 'lower-left';  // Chaos + Ego
  else if (x >= 50 && y >= 50) quadrant = 'lower-right'; // Chaos + Collective

  return { 
    x, 
    y, 
    valueTag: latestValueTag, 
    quadrant, 
    dominantDirection,
    valueCounts,
    actionsAnalyzed: relevantHistory.length
  };
};

/**
 * Calculate recommended direction arrow on compass
 * Directly from theory: current position → recommended position
 * 
 * @param {string} currentValueTag - Current direction
 * @returns {Object} Arrow data { from, to, direction }
 */
export const calculateRecommendedArrow = (currentValueTag) => {
  if (!currentValueTag) return null;

  const recommendation = getTheoryBasedRecommendation(currentValueTag);
  const fromPosition = compassPositions[currentValueTag] || { x: 50, y: 50 };
  const toPosition = compassPositions[recommendation.direction] || { x: 50, y: 50 };

  return {
    from: fromPosition,
    to: toPosition,
    direction: recommendation.direction,
    reason: recommendation.reason,
    explanation: recommendation.explanation
  };
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
 * Calculate recommended direction based on the THEORETICAL FRAMEWORK
 * This is the SINGLE SOURCE OF TRUTH for recommendation calculations
 * 
 * STRICT THEORY BALANCING PATHS:
 * - harm → recovery
 * - avoidance → order
 * - isolation → contribution
 * - rigidity → exploration
 * 
 * When current direction is already positive → suggest adjacent or strengthen
 * 
 * @param {Object} params - Parameters for recommendation
 * @param {Array} params.history - Decision history (uses last 7 days)
 * @returns {Object} Recommendation result
 */
export const calculateRecommendation = ({ history }) => {
  // Return default recommendation for new users
  if (!history || history.length === 0) {
    return {
      direction: 'recovery',
      reason: 'no_history',
      strength: 50,
      insight: 'אין מספיק נתונים. מומלץ להתחיל עם התאוששות.',
      actionSuggestion: actionSuggestions.recovery[0],
      fromTheory: true,
      theoryPath: null,
      currentDirection: null
    };
  }

  // Step 1: Get last 7 days of history
  const now = new Date();
  const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  
  const recentHistory = history.filter(h => {
    if (!h.timestamp) return true;
    return new Date(h.timestamp) >= sevenDaysAgo;
  });

  const relevantHistory = recentHistory.length > 0 ? recentHistory : history.slice(0, 10);

  // Step 2: Find the LAST NEGATIVE action (most important for balancing)
  const lastNegativeAction = relevantHistory.find(h => 
    ['harm', 'avoidance'].includes(h.value_tag)
  );

  // Step 3: Count patterns for isolation/rigidity detection
  const valueCounts = {};
  relevantHistory.forEach(h => {
    if (h.value_tag) {
      valueCounts[h.value_tag] = (valueCounts[h.value_tag] || 0) + 1;
    }
  });

  // Step 4: Determine theory category and apply STRICT balancing
  let theoryCategory = null;
  let recommendedDirection = 'recovery';
  let reason = 'default';
  let insight = '';
  let strength = 60;
  let theoryPath = null;

  // PRIORITY 1: If last action was negative → apply direct balancing path
  if (lastNegativeAction) {
    const lastTag = lastNegativeAction.value_tag;
    
    if (lastTag === 'harm') {
      theoryCategory = 'harm';
      recommendedDirection = 'recovery';
      reason = 'theory_balancing';
      insight = 'פעולות נזק דורשות איזון דרך התאוששות.';
      theoryPath = 'נזק → התאוששות';
      strength = 80;
    } else if (lastTag === 'avoidance') {
      theoryCategory = 'avoidance';
      recommendedDirection = 'order';
      reason = 'theory_balancing';
      insight = 'הימנעות מאוזנת על ידי יצירת סדר ומבנה.';
      theoryPath = 'הימנעות → סדר';
      strength = 80;
    }
  }

  // PRIORITY 2: Detect isolation pattern (no contribution, self-focused)
  if (!theoryCategory) {
    const contributionCount = valueCounts.contribution || 0;
    const totalCount = relevantHistory.length;
    
    if (totalCount >= 3 && contributionCount === 0) {
      theoryCategory = 'isolation';
      recommendedDirection = 'contribution';
      reason = 'theory_balancing';
      insight = 'מיקוד עצמי מאוזן על ידי תרומה לאחרים.';
      theoryPath = 'בידוד → תרומה';
      strength = 70;
    }
  }

  // PRIORITY 3: Detect rigidity pattern (too much order, no exploration)
  if (!theoryCategory) {
    const orderCount = valueCounts.order || 0;
    const explorationCount = valueCounts.exploration || 0;
    const totalCount = relevantHistory.length;
    
    if (totalCount >= 4 && orderCount >= 3 && explorationCount === 0) {
      theoryCategory = 'rigidity';
      recommendedDirection = 'exploration';
      reason = 'theory_balancing';
      insight = 'קיפאון מאוזן על ידי פתיחות וחקירה.';
      theoryPath = 'נוקשות → חקירה';
      strength = 70;
    }
  }

  // PRIORITY 4: Current direction is positive → suggest adjacent for balance
  if (!theoryCategory) {
    const dominantTag = Object.entries(valueCounts)
      .sort((a, b) => b[1] - a[1])[0]?.[0];

    if (dominantTag && positiveReinforcement[dominantTag]) {
      const reinforcement = positiveReinforcement[dominantTag];
      recommendedDirection = reinforcement.adjacent;
      reason = 'theory_reinforcement';
      insight = reinforcement.explanation;
      strength = 55;
    }
  }

  // Step 5: Select action suggestion
  const suggestions = actionSuggestions[recommendedDirection] || actionSuggestions.recovery;
  const suggestionIndex = relevantHistory.length % suggestions.length;
  const actionSuggestion = suggestions[suggestionIndex];

  return {
    direction: recommendedDirection,
    reason,
    strength,
    insight,
    actionSuggestion,
    fromTheory: true,
    theoryPath,
    theoryCategory,
    currentDirection: relevantHistory[0]?.value_tag || null,
    valueCounts,
    actionsAnalyzed: relevantHistory.length
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
