// Adaptive scores and path learning logic
import { useState, useEffect, useCallback } from 'react';
import { savePathSelection, savePathLearning, getUserId } from '../services/cloudSync';
import { fetchReplayInsights } from '../services/dataService';

// LocalStorage keys
const LEARNING_HISTORY_KEY = 'philos_learning_history';

// Load learning history from localStorage
const loadLearningHistory = () => {
  try {
    const saved = localStorage.getItem(LEARNING_HISTORY_KEY);
    if (saved) return JSON.parse(saved);
  } catch (e) {
    console.error('Error loading learning history:', e);
  }
  return [];
};

// Calculate adaptive scores from learning history
export const calculateAdaptiveScores = (learningHist) => {
  const scores = {
    contribution: 0,
    recovery: 0,
    order: 0,
    harm: 0,
    avoidance: 0
  };

  if (!learningHist || learningHist.length === 0) {
    return scores;
  }

  learningHist.forEach(entry => {
    const type = entry.predicted_value_tag;
    if (!type || !scores.hasOwnProperty(type)) return;

    if (entry.actual_recovery_stability > entry.predicted_recovery_stability) scores[type] += 2;
    if (entry.actual_harm_pressure < entry.predicted_harm_pressure) scores[type] += 2;
    if (entry.actual_order_drift > entry.predicted_order_drift && entry.actual_order_drift > 0) scores[type] += 1;
    if (entry.actual_harm_pressure > entry.predicted_harm_pressure) scores[type] -= 3;
    if (entry.match_quality === 'low') scores[type] -= 2;
    if (entry.actual_value_tag === 'avoidance' || entry.actual_value_tag === 'harm') scores[type] -= 4;
    if (entry.match_quality === 'high') scores[type] += 3;
  });

  Object.keys(scores).forEach(key => {
    scores[key] = Math.max(-20, Math.min(20, scores[key]));
  });

  return scores;
};

// Apply replay insights adjustments to adaptive scores
export const applyReplayInsightsToScores = (baseScores, replayInsights) => {
  if (!replayInsights || !replayInsights.total_replays || replayInsights.total_replays === 0) {
    return { adjustedScores: baseScores, adjustments: null };
  }

  const adjustments = {
    boosted: [],
    penalized: [],
    insights: []
  };

  const adjusted = { ...baseScores };
  const altCounts = replayInsights.alternative_path_counts || {};
  const transitions = replayInsights.transition_patterns || [];
  const blindSpots = replayInsights.blind_spots || [];
  const totalReplays = replayInsights.total_replays;

  // 1. Boost frequently explored positive alternatives
  const positiveTypes = ['contribution', 'recovery', 'order'];
  positiveTypes.forEach(type => {
    const count = altCounts[type] || 0;
    if (count > 0) {
      const boost = Math.min(8, Math.round((count / totalReplays) * 10));
      if (boost > 0) {
        adjusted[type] += boost;
        adjustments.boosted.push({ type, boost, reason: 'explored' });
      }
    }
  });

  // 2. Identify repeated transition patterns - boost the "to" path
  transitions.forEach(pattern => {
    const { from, to, count } = pattern;
    if (['harm', 'avoidance'].includes(from) && ['contribution', 'recovery', 'order'].includes(to)) {
      if (count >= 2) {
        const boost = Math.min(5, count);
        adjusted[to] += boost;
        const existing = adjustments.boosted.find(b => b.type === to && b.reason === 'transition');
        if (!existing) {
          adjustments.boosted.push({ type: to, boost, reason: 'transition', from });
        }
      }
    }
  });

  // 3. Penalize harmful paths more strongly if user never explores them as alternatives
  const harmCount = altCounts['harm'] || 0;
  const avoidanceCount = altCounts['avoidance'] || 0;
  
  if (harmCount === 0 && totalReplays >= 3) {
    const penalty = -4;
    adjusted['harm'] += penalty;
    adjustments.penalized.push({ type: 'harm', penalty: Math.abs(penalty), reason: 'never_explored' });
  }

  if (avoidanceCount === 0 && totalReplays >= 3) {
    const penalty = -3;
    adjusted['avoidance'] += penalty;
    adjustments.penalized.push({ type: 'avoidance', penalty: Math.abs(penalty), reason: 'never_explored' });
  }

  // 4. Blind spots - slightly boost unexplored positive transitions
  blindSpots.forEach(spot => {
    if (['contribution', 'recovery', 'order'].includes(spot.to)) {
      adjusted[spot.to] += 1;
    }
  });

  // 5. Generate Hebrew insight texts
  if (adjustments.boosted.length > 0) {
    const topBoosted = adjustments.boosted.sort((a, b) => b.boost - a.boost)[0];
    const typeLabels = {
      contribution: 'תרומה',
      recovery: 'התאוששות',
      order: 'סדר'
    };
    adjustments.insights.push(
      `מסלולי ${typeLabels[topBoosted.type]} קיבלו חיזוק בעקבות דפוסי הפעלה חוזרת.`
    );
  }

  if (adjustments.penalized.length > 0) {
    const topPenalized = adjustments.penalized[0];
    const typeLabels = {
      harm: 'נזק',
      avoidance: 'הימנעות'
    };
    adjustments.insights.push(
      `מסלולי ${typeLabels[topPenalized.type]} מקבלים כעת הפחתת משקל חזקה יותר.`
    );
  }

  // Clamp final scores
  Object.keys(adjusted).forEach(key => {
    adjusted[key] = Math.max(-25, Math.min(25, adjusted[key]));
  });

  return { adjustedScores: adjusted, adjustments };
};

/**
 * Adaptive scores hook
 * Manages: adaptiveScores, learningHistory, path selection, learning data
 */
export function useAdaptiveScores({ user, replayHistoryLength = 0 }) {
  // Path learning state
  const [selectedPathData, setSelectedPathData] = useState(null);
  const [learningHistory, setLearningHistory] = useState(loadLearningHistory);
  const [adaptiveScores, setAdaptiveScores] = useState(() => calculateAdaptiveScores(loadLearningHistory()));
  
  // Replay insights state for adaptive adjustments
  const [replayInsights, setReplayInsights] = useState(null);
  const [replayAdaptiveAdjustments, setReplayAdaptiveAdjustments] = useState(null);

  // Save learning history to localStorage and update adaptive scores
  useEffect(() => {
    try {
      localStorage.setItem(LEARNING_HISTORY_KEY, JSON.stringify(learningHistory));
      setAdaptiveScores(calculateAdaptiveScores(learningHistory));
    } catch (e) {
      console.error('Error saving learning history:', e);
    }
  }, [learningHistory]);

  // Fetch replay insights and apply to adaptive scores
  useEffect(() => {
    const loadAndApplyReplayInsights = async () => {
      const userId = user?.id || getUserId();

      try {
        const forceRefresh = replayHistoryLength > 0;
        const data = await fetchReplayInsights(userId, forceRefresh);
        
        if (data.success && data.total_replays > 0) {
          setReplayInsights(data);
          
          const baseScores = calculateAdaptiveScores(learningHistory);
          const { adjustedScores, adjustments } = applyReplayInsightsToScores(baseScores, data);
          
          if (adjustments && (adjustments.boosted.length > 0 || adjustments.penalized.length > 0)) {
            setAdaptiveScores(adjustedScores);
            setReplayAdaptiveAdjustments(adjustments);
          }
        }
      } catch (error) {
        console.log('Failed to fetch replay insights:', error);
      }
    };

    loadAndApplyReplayInsights();
  }, [user, replayHistoryLength, learningHistory]);

  // Handle path selection
  const handlePathSelection = useCallback(async (pathData) => {
    const pathSelectionData = {
      selected_path_id: pathData.id,
      suggested_action: pathData.action,
      predicted_value_tag: pathData.valueTag,
      predicted_order_drift: pathData.orderDrift,
      predicted_collective_drift: pathData.collectiveDrift,
      predicted_harm_pressure: pathData.harmPressure,
      predicted_recovery_stability: pathData.recoveryStability,
      timestamp: new Date().toISOString()
    };
    
    setSelectedPathData(pathSelectionData);
    
    try {
      await savePathSelection(pathSelectionData);
    } catch (error) {
      console.log('Cloud save failed for path selection:', error);
    }
    
    return pathData.action; // Return action for setting in actionText
  }, []);

  // Save learning data
  const saveLearningData = useCallback(async (selectedPath, actualResult) => {
    if (!selectedPath || !actualResult) return;

    const actualOrderDrift = actualResult.projection?.chaos_order || 0;
    const actualCollectiveDrift = actualResult.projection?.ego_collective || 0;
    const actualHarmPressure = actualResult.value_tag === 'harm' ? 20 : actualResult.value_tag === 'avoidance' ? 10 : -10;
    const actualRecoveryStability = actualResult.value_tag === 'recovery' ? 20 : actualResult.balance_score > 60 ? 10 : -5;

    let matchScore = 0;
    if (selectedPath.predicted_value_tag === actualResult.value_tag) matchScore += 3;
    if (Math.sign(selectedPath.predicted_order_drift) === Math.sign(actualOrderDrift)) matchScore += 1;
    if (Math.sign(selectedPath.predicted_collective_drift) === Math.sign(actualCollectiveDrift)) matchScore += 1;
    if ((selectedPath.predicted_harm_pressure < 0) === (actualHarmPressure < 0)) matchScore += 1;

    const matchQuality = matchScore >= 5 ? 'high' : matchScore >= 3 ? 'medium' : 'low';

    const learningEntry = {
      predicted_value_tag: selectedPath.predicted_value_tag,
      actual_value_tag: actualResult.value_tag,
      predicted_order_drift: selectedPath.predicted_order_drift,
      actual_order_drift: actualOrderDrift,
      predicted_collective_drift: selectedPath.predicted_collective_drift,
      actual_collective_drift: actualCollectiveDrift,
      predicted_harm_pressure: selectedPath.predicted_harm_pressure,
      actual_harm_pressure: actualHarmPressure,
      predicted_recovery_stability: selectedPath.predicted_recovery_stability,
      actual_recovery_stability: actualRecoveryStability,
      match_quality: matchQuality,
      timestamp: new Date().toISOString()
    };

    setLearningHistory(prev => [...prev, learningEntry].slice(-50));

    try {
      await savePathLearning(learningEntry);
    } catch (error) {
      console.log('Cloud save failed, using localStorage fallback:', error);
    }
  }, []);

  return {
    selectedPathData,
    setSelectedPathData,
    learningHistory,
    setLearningHistory,
    adaptiveScores,
    setAdaptiveScores,
    replayInsights,
    replayAdaptiveAdjustments,
    handlePathSelection,
    saveLearningData
  };
}
