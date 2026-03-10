// Centralized Analytics Service for Philos Orientation
// Single source of truth for all analytics calculations

// Hebrew value tag labels
export const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Value tag colors
export const valueColors = {
  contribution: { bg: 'bg-green-100', text: 'text-green-700', fill: '#22c55e' },
  recovery: { bg: 'bg-blue-100', text: 'text-blue-700', fill: '#3b82f6' },
  order: { bg: 'bg-indigo-100', text: 'text-indigo-700', fill: '#6366f1' },
  harm: { bg: 'bg-red-100', text: 'text-red-700', fill: '#ef4444' },
  avoidance: { bg: 'bg-gray-100', text: 'text-gray-600', fill: '#9ca3af' }
};

/**
 * Count value tags in history
 * @param {Array} history - Decision history array
 * @returns {Object} Value counts { contribution, recovery, order, harm, avoidance }
 */
export const countValueTags = (history) => {
  const counts = {
    contribution: 0,
    recovery: 0,
    order: 0,
    harm: 0,
    avoidance: 0
  };

  if (!history || history.length === 0) return counts;

  history.forEach(item => {
    const tag = item.value_tag;
    if (tag && counts.hasOwnProperty(tag)) {
      counts[tag]++;
    }
  });

  return counts;
};

/**
 * Filter history by date range
 * @param {Array} history - Decision history array
 * @param {Date} startDate - Start date
 * @param {Date} endDate - End date (optional, defaults to now)
 * @returns {Array} Filtered history
 */
export const filterHistoryByDateRange = (history, startDate, endDate = new Date()) => {
  if (!history || history.length === 0) return [];

  return history.filter(item => {
    if (!item.timestamp) return false;
    const itemDate = new Date(item.timestamp);
    return itemDate >= startDate && itemDate <= endDate;
  });
};

/**
 * Filter history for today
 * @param {Array} history - Decision history array
 * @returns {Array} Today's decisions
 */
export const filterTodayHistory = (history) => {
  if (!history || history.length === 0) return [];

  const today = new Date().toDateString();
  return history.filter(item => {
    const itemDate = item.timestamp ? new Date(item.timestamp).toDateString() : today;
    return itemDate === today;
  });
};

/**
 * Filter history for yesterday
 * @param {Array} history - Decision history array
 * @returns {Array} Yesterday's decisions
 */
export const filterYesterdayHistory = (history) => {
  if (!history || history.length === 0) return [];

  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayStr = yesterday.toDateString();

  return history.filter(item => {
    if (!item.timestamp) return false;
    const itemDate = new Date(item.timestamp).toDateString();
    return itemDate === yesterdayStr;
  });
};

/**
 * Filter history for last N days
 * @param {Array} history - Decision history array
 * @param {number} days - Number of days to look back
 * @returns {Array} Filtered history
 */
export const filterLastNDays = (history, days) => {
  if (!history || history.length === 0) return [];

  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  startDate.setHours(0, 0, 0, 0);

  return filterHistoryByDateRange(history, startDate);
};

/**
 * Filter history for last week
 * @param {Array} history - Decision history array
 * @returns {Array} Last week's decisions
 */
export const filterLastWeekHistory = (history) => {
  return filterLastNDays(history, 7);
};

/**
 * Filter history for last month
 * @param {Array} history - Decision history array
 * @returns {Array} Last month's decisions
 */
export const filterLastMonthHistory = (history) => {
  return filterLastNDays(history, 30);
};

/**
 * Filter history for a specific month
 * @param {Array} history - Decision history array
 * @param {number} year - Year
 * @param {number} month - Month (0-11)
 * @returns {Array} Month's decisions
 */
export const filterByMonth = (history, year, month) => {
  if (!history || history.length === 0) return [];

  return history.filter(item => {
    if (!item.timestamp) return false;
    const itemDate = new Date(item.timestamp);
    return itemDate.getFullYear() === year && itemDate.getMonth() === month;
  });
};

/**
 * Calculate drift metrics from value counts
 * @param {Object} valueCounts - Value counts from countValueTags
 * @returns {Object} Drift metrics
 */
export const calculateDriftMetrics = (valueCounts) => {
  const total = Object.values(valueCounts).reduce((a, b) => a + b, 0) || 1;

  // Order drift: positive values (order, recovery) vs negative (harm, avoidance)
  const orderDrift = (valueCounts.order + valueCounts.recovery) - (valueCounts.harm + valueCounts.avoidance);

  // Collective drift: contribution vs harm
  const collectiveDrift = valueCounts.contribution - valueCounts.harm;

  // Harm pressure: percentage of harm decisions
  const harmPressure = (valueCounts.harm / total) * 100;

  // Recovery stability: percentage of recovery decisions
  const recoveryStability = (valueCounts.recovery / total) * 100;

  // Negative ratio
  const negativeRatio = (valueCounts.harm + valueCounts.avoidance) / total;

  // Positive ratio
  const positiveRatio = (valueCounts.contribution + valueCounts.recovery + valueCounts.order) / total;

  return {
    orderDrift,
    collectiveDrift,
    harmPressure: Math.round(harmPressure),
    recoveryStability: Math.round(recoveryStability),
    negativeRatio,
    positiveRatio,
    total
  };
};

/**
 * Identify dominant pattern from value counts
 * @param {Object} valueCounts - Value counts from countValueTags
 * @returns {Object} Pattern analysis
 */
export const identifyDominantPattern = (valueCounts) => {
  const total = Object.values(valueCounts).reduce((a, b) => a + b, 0) || 1;

  // Find dominant (highest count)
  const sorted = Object.entries(valueCounts).sort((a, b) => b[1] - a[1]);
  const dominantTag = sorted[0];
  const lowestTag = sorted.filter(([_, count]) => count > 0).sort((a, b) => a[1] - b[1])[0];

  // Categorize positive and negative
  const positiveTypes = ['contribution', 'recovery', 'order'];
  const negativeTypes = ['harm', 'avoidance'];

  const strongestPositive = sorted.find(([tag]) => positiveTypes.includes(tag));
  const strongestNegative = sorted.find(([tag]) => negativeTypes.includes(tag));

  // Determine overall pattern type
  const harmCount = valueCounts.harm || 0;
  const avoidanceCount = valueCounts.avoidance || 0;
  const negativeRatio = (harmCount + avoidanceCount) / total;

  let patternType = 'neutral';
  let dominantPattern = null;

  if (negativeRatio > 0.5) {
    patternType = 'negative';
    dominantPattern = harmCount > avoidanceCount ? 'harm' : 'avoidance';
  } else if (negativeRatio < 0.3) {
    patternType = 'positive';
    dominantPattern = dominantTag ? dominantTag[0] : 'balanced';
  } else {
    patternType = 'mixed';
    dominantPattern = 'balanced';
  }

  return {
    dominantTag: dominantTag ? { tag: dominantTag[0], count: dominantTag[1] } : null,
    lowestTag: lowestTag ? { tag: lowestTag[0], count: lowestTag[1] } : null,
    strongestPositive: strongestPositive ? { tag: strongestPositive[0], count: strongestPositive[1] } : null,
    strongestNegative: strongestNegative ? { tag: strongestNegative[0], count: strongestNegative[1] } : null,
    patternType,
    dominantPattern,
    valueCounts,
    total
  };
};

/**
 * Analyze period comparison (e.g., this week vs last week)
 * @param {Array} currentPeriod - Current period decisions
 * @param {Array} previousPeriod - Previous period decisions
 * @returns {Object} Comparison analysis
 */
export const analyzePeriodComparison = (currentPeriod, previousPeriod) => {
  const currentCounts = countValueTags(currentPeriod);
  const previousCounts = countValueTags(previousPeriod);
  const currentMetrics = calculateDriftMetrics(currentCounts);
  const previousMetrics = calculateDriftMetrics(previousCounts);

  const changes = {
    orderDrift: currentMetrics.orderDrift - previousMetrics.orderDrift,
    collectiveDrift: currentMetrics.collectiveDrift - previousMetrics.collectiveDrift,
    harmPressure: currentMetrics.harmPressure - previousMetrics.harmPressure,
    recoveryStability: currentMetrics.recoveryStability - previousMetrics.recoveryStability,
    totalDecisions: currentPeriod.length - previousPeriod.length
  };

  // Determine trend direction
  let trend = 'stable';
  if (changes.harmPressure < -10 || changes.recoveryStability > 10) {
    trend = 'improving';
  } else if (changes.harmPressure > 10 || changes.recoveryStability < -10) {
    trend = 'declining';
  }

  return {
    current: {
      counts: currentCounts,
      metrics: currentMetrics,
      total: currentPeriod.length
    },
    previous: {
      counts: previousCounts,
      metrics: previousMetrics,
      total: previousPeriod.length
    },
    changes,
    trend
  };
};

/**
 * Calculate weekly summary for orientation loops
 * @param {Array} history - Full decision history
 * @returns {Object} Weekly summary
 */
export const calculateWeeklySummary = (history) => {
  const thisWeek = filterLastNDays(history, 7);
  const lastWeek = filterHistoryByDateRange(
    history,
    new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
    new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  );

  return analyzePeriodComparison(thisWeek, lastWeek);
};

/**
 * Calculate monthly summary for orientation loops
 * @param {Array} history - Full decision history
 * @returns {Object} Monthly summary
 */
export const calculateMonthlySummary = (history) => {
  const thisMonth = filterLastNDays(history, 30);
  const lastMonth = filterHistoryByDateRange(
    history,
    new Date(Date.now() - 60 * 24 * 60 * 60 * 1000),
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  );

  return analyzePeriodComparison(thisMonth, lastMonth);
};

/**
 * Analyze recommendation follow-through
 * @param {Array} history - Decision history
 * @returns {Object} Follow-through analysis
 */
export const analyzeFollowThrough = (history) => {
  if (!history || history.length === 0) {
    return {
      followedCount: 0,
      totalDecisions: 0,
      followRate: 0,
      byDirection: {},
      alignmentRate: 0
    };
  }

  const followedDecisions = history.filter(d => d.followed_recommendation === true);
  const followedCount = followedDecisions.length;
  const totalDecisions = history.length;
  const followRate = totalDecisions > 0 ? (followedCount / totalDecisions) * 100 : 0;

  // Analyze by direction
  const byDirection = {};
  let alignedCount = 0;

  followedDecisions.forEach(decision => {
    const recDir = decision.recommendation_direction;
    const actualTag = decision.value_tag;

    if (!byDirection[recDir]) {
      byDirection[recDir] = { count: 0, aligned: 0 };
    }
    byDirection[recDir].count++;

    if (recDir === actualTag) {
      byDirection[recDir].aligned++;
      alignedCount++;
    }
  });

  const alignmentRate = followedCount > 0 ? (alignedCount / followedCount) * 100 : 0;

  return {
    followedCount,
    totalDecisions,
    followRate: Math.round(followRate),
    byDirection,
    alignmentRate: Math.round(alignmentRate)
  };
};

/**
 * Generate summary text for pattern (Hebrew)
 * @param {Object} pattern - Pattern analysis from identifyDominantPattern
 * @returns {string} Hebrew summary text
 */
export const generatePatternSummary = (pattern) => {
  if (!pattern || pattern.total === 0) {
    return 'אין מספיק נתונים לניתוח.';
  }

  const { dominantTag, patternType, dominantPattern } = pattern;

  if (patternType === 'positive') {
    return `נראה דפוס חיובי עם דגש על ${valueLabels[dominantTag?.tag] || 'איזון'}.`;
  } else if (patternType === 'negative') {
    const negativeLabel = dominantPattern === 'harm' ? 'נזק' : 'הימנעות';
    return `זוהה דפוס של ${negativeLabel}. מומלץ לשקול פעולות התאוששות.`;
  } else {
    return 'המערכת מאוזנת. המשך לעקוב אחר הדפוסים.';
  }
};

/**
 * Get recommended direction based on analysis
 * @param {Object} pattern - Pattern analysis
 * @param {Object} metrics - Drift metrics
 * @returns {Object} Recommendation { direction, reason }
 */
export const getRecommendedDirection = (pattern, metrics) => {
  // If negative pattern, recommend recovery or order
  if (pattern.patternType === 'negative') {
    if (pattern.dominantPattern === 'harm') {
      return { direction: 'recovery', reason: 'balance_harm' };
    } else {
      return { direction: 'order', reason: 'balance_avoidance' };
    }
  }

  // If positive pattern, recommend lowest positive to balance
  if (pattern.lowestTag && ['contribution', 'recovery', 'order'].includes(pattern.lowestTag.tag)) {
    return { direction: pattern.lowestTag.tag, reason: 'balance_positive' };
  }

  // Default to recovery
  return { direction: 'recovery', reason: 'default' };
};

/**
 * Calculate balance score from chaos_order and ego_collective
 * @param {number} chaosOrder - Chaos/Order value
 * @param {number} egoCollective - Ego/Collective value
 * @returns {number} Balance score (0-100)
 */
export const calculateBalanceScore = (chaosOrder, egoCollective) => {
  return 100 - (Math.abs(chaosOrder) + Math.abs(egoCollective));
};

/**
 * Get child decisions count for a parent decision
 * @param {Array} history - Decision history
 * @param {string} parentId - Parent decision ID
 * @returns {number} Count of child decisions
 */
export const getChildDecisionsCount = (history, parentId) => {
  if (!history || !parentId) return 0;
  return history.filter(h => h.parent_decision_id === parentId).length;
};
