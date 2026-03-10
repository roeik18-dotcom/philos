import { useState, useEffect, useCallback } from 'react';

// Import domain-specific hooks
import { useDecisionState, getValueTag } from './useDecisionState';
import { useCloudSync } from './useCloudSync';
import { useReplayState } from './useReplayState';
import { useAdaptiveScores, calculateAdaptiveScores, applyReplayInsightsToScores } from './useAdaptiveScores';
import { useSessionManagement } from './useSessionManagement';

// Re-export helper functions for backward compatibility
export { getValueTag } from './useDecisionState';
export { calculateAdaptiveScores, applyReplayInsightsToScores } from './useAdaptiveScores';

// LocalStorage key for session data persistence
const STORAGE_KEY = 'philos_session_data';

// Optimal zone definition
const OPTIMAL_ZONE = {
  order: { min: 20, max: 60 },
  collective: { min: 10, max: 50 }
};

// Calculate suggested vector toward optimal zone
export const calculateSuggestedVector = (chaosOrder, egoCollective) => {
  let suggestedOrder = 0;
  let suggestedCollective = 0;
  let suggestions = [];
  let reasons = [];

  if (chaosOrder < OPTIMAL_ZONE.order.min) {
    suggestedOrder = Math.min(20, OPTIMAL_ZONE.order.min - chaosOrder);
    suggestions.push("Take a short walk");
    suggestions.push("Organize something small");
    reasons.push("moves toward order");
    reasons.push("reduces chaos");
  } else if (chaosOrder > OPTIMAL_ZONE.order.max) {
    suggestedOrder = -Math.min(15, chaosOrder - OPTIMAL_ZONE.order.max);
    suggestions.push("Rest for a moment");
    suggestions.push("Let go of control");
    reasons.push("allows flexibility");
    reasons.push("reduces rigidity");
  }

  if (egoCollective < OPTIMAL_ZONE.collective.min) {
    suggestedCollective = Math.min(20, OPTIMAL_ZONE.collective.min - egoCollective);
    suggestions.push("Help someone nearby");
    suggestions.push("Share an idea");
    reasons.push("increases collective balance");
  } else if (egoCollective > OPTIMAL_ZONE.collective.max) {
    suggestedCollective = -Math.min(15, egoCollective - OPTIMAL_ZONE.collective.max);
    suggestions.push("Take time for yourself");
    suggestions.push("Reflect quietly");
    reasons.push("restores personal balance");
  }

  const inOptimalZone = 
    chaosOrder >= OPTIMAL_ZONE.order.min && 
    chaosOrder <= OPTIMAL_ZONE.order.max &&
    egoCollective >= OPTIMAL_ZONE.collective.min && 
    egoCollective <= OPTIMAL_ZONE.collective.max;

  if (inOptimalZone) {
    suggestions = ["Maintain current balance"];
    reasons = ["You are in the optimal zone"];
  }

  return {
    suggestedOrder,
    suggestedCollective,
    suggestions: suggestions.slice(0, 2),
    reasons: reasons.slice(0, 3),
    inOptimalZone
  };
};

// Analyze personal patterns
export const analyzePersonalMap = (historyData) => {
  if (historyData.length === 0) {
    return {
      dominantOrder: 'balanced',
      dominantCollective: 'balanced',
      topValueTags: [],
      patternSummary: []
    };
  }

  const avgOrder = historyData.reduce((sum, h) => sum + h.chaos_order, 0) / historyData.length;
  const avgCollective = historyData.reduce((sum, h) => sum + h.ego_collective, 0) / historyData.length;

  const dominantOrder = avgOrder > 10 ? 'order' : avgOrder < -10 ? 'chaos' : 'balanced';
  const dominantCollective = avgCollective > 10 ? 'collective' : avgCollective < -10 ? 'ego' : 'balanced';

  const tagCounts = {};
  historyData.forEach(h => {
    if (h.value_tag && h.value_tag !== 'neutral') {
      tagCounts[h.value_tag] = (tagCounts[h.value_tag] || 0) + 1;
    }
  });

  const topValueTags = Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([tag, count]) => ({ tag, count }));

  const unstableMoments = historyData.filter(h => h.balance_score < 40);
  let unstablePattern = '';
  if (unstableMoments.length > 0) {
    const unstableAvgOrder = unstableMoments.reduce((sum, h) => sum + h.chaos_order, 0) / unstableMoments.length;
    const unstableAvgCollective = unstableMoments.reduce((sum, h) => sum + h.ego_collective, 0) / unstableMoments.length;
    const orderDir = unstableAvgOrder < 0 ? 'chaos' : 'order';
    const collectiveDir = unstableAvgCollective < 0 ? 'ego' : 'collective';
    unstablePattern = `${orderDir}/${collectiveDir}`;
  }

  const patternSummary = [];
  if (dominantOrder !== 'balanced') {
    patternSummary.push(`You tend toward ${dominantOrder}.`);
  }
  if (topValueTags.length > 0) {
    patternSummary.push(`You often act from ${topValueTags[0].tag}.`);
  }
  if (unstablePattern) {
    patternSummary.push(`Your unstable moments move toward ${unstablePattern}.`);
  }

  return {
    dominantOrder,
    dominantCollective,
    topValueTags,
    patternSummary,
    avgOrder: Math.round(avgOrder),
    avgCollective: Math.round(avgCollective)
  };
};

/**
 * Main Philos state hook - composes domain-specific hooks
 * Maintains backward compatibility with the original API
 */
export default function usePhilosState(user = null) {
  // Session management (global stats, trend history, snapshots)
  // Initialize with empty setters first, will be connected below
  const [_history, _setHistory] = useState([]);
  const [_state, _setState] = useState({
    physical_capacity: 50,
    chaos_order: 0,
    ego_collective: 0,
    gap_type: 'energy'
  });
  const [_decisionResult, _setDecisionResult] = useState(null);

  // Session management hook
  const sessionManagement = useSessionManagement({
    history: _history,
    state: _state,
    setHistory: _setHistory,
    setState: _setState,
    setDecisionResult: _setDecisionResult
  });

  // Replay state hook
  const replayState = useReplayState({ user });

  // Adaptive scores hook
  const adaptiveScoresHook = useAdaptiveScores({
    user,
    replayHistoryLength: replayState.replayHistory.length
  });

  // Decision state hook
  const decisionState = useDecisionState({
    onDecisionMade: () => {},
    onGlobalStatsUpdate: sessionManagement.updateGlobalStats,
    onLearningDataSave: adaptiveScoresHook.saveLearningData,
    selectedPathData: adaptiveScoresHook.selectedPathData,
    parentDecision: sessionManagement.parentDecision,
    setParentDecision: sessionManagement.setParentDecision,
    user
  });

  // Cloud sync hook
  const cloudSync = useCloudSync({
    user,
    history: decisionState.history,
    setHistory: decisionState.setHistory,
    globalStats: sessionManagement.globalStats,
    setGlobalStats: sessionManagement.setGlobalStats,
    trendHistory: sessionManagement.trendHistory,
    setTrendHistory: sessionManagement.setTrendHistory,
    learningHistory: adaptiveScoresHook.learningHistory,
    setLearningHistory: adaptiveScoresHook.setLearningHistory,
    adaptiveScores: adaptiveScoresHook.adaptiveScores,
    setAdaptiveScores: adaptiveScoresHook.setAdaptiveScores,
    setState: decisionState.setState
  });

  // Handle path selection with action text update
  const handlePathSelection = useCallback(async (pathData) => {
    const action = await adaptiveScoresHook.handlePathSelection(pathData);
    decisionState.setActionText(action);
  }, [adaptiveScoresHook, decisionState]);

  // Persist to storage on state changes
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    decisionState.persistToStorage();
  }, [decisionState.state, decisionState.history, decisionState.decisionResult]);

  // Return the combined API (backward compatible)
  return {
    // Core state (from useDecisionState)
    state: decisionState.state,
    setState: decisionState.setState,
    actionText: decisionState.actionText,
    setActionText: decisionState.setActionText,
    decisionResult: decisionState.decisionResult,
    setDecisionResult: decisionState.setDecisionResult,
    history: decisionState.history,
    setHistory: decisionState.setHistory,
    
    // Global and trend (from useSessionManagement)
    globalStats: sessionManagement.globalStats,
    setGlobalStats: sessionManagement.setGlobalStats,
    trendHistory: sessionManagement.trendHistory,
    setTrendHistory: sessionManagement.setTrendHistory,
    
    // Path learning (from useAdaptiveScores)
    selectedPathData: adaptiveScoresHook.selectedPathData,
    setSelectedPathData: adaptiveScoresHook.setSelectedPathData,
    learningHistory: adaptiveScoresHook.learningHistory,
    setLearningHistory: adaptiveScoresHook.setLearningHistory,
    adaptiveScores: adaptiveScoresHook.adaptiveScores,
    setAdaptiveScores: adaptiveScoresHook.setAdaptiveScores,
    
    // Sync (from useCloudSync)
    syncStatus: cloudSync.syncStatus,
    setSyncStatus: cloudSync.setSyncStatus,
    performCloudSync: cloudSync.performCloudSync,
    
    // UI (from useSessionManagement)
    showShareCard: sessionManagement.showShareCard,
    setShowShareCard: sessionManagement.setShowShareCard,
    
    // Decision chains (from useSessionManagement)
    parentDecision: sessionManagement.parentDecision,
    setParentDecision: sessionManagement.setParentDecision,
    handleAddFollowUp: sessionManagement.handleAddFollowUp,
    
    // Decision replay (from useReplayState)
    replayDecision: replayState.replayDecision,
    setReplayDecision: replayState.setReplayDecision,
    replayHistory: replayState.replayHistory,
    handleReplayDecision: replayState.handleReplayDecision,
    closeReplay: replayState.closeReplay,
    saveReplayMetadata: replayState.saveReplayMetadata,
    
    // Replay adaptive effect (from useAdaptiveScores)
    replayInsights: adaptiveScoresHook.replayInsights,
    replayAdaptiveAdjustments: adaptiveScoresHook.replayAdaptiveAdjustments,
    
    // Computed (from useDecisionState)
    balanceScore: decisionState.balanceScore,
    
    // Actions
    evaluateAction: decisionState.evaluateAction,
    handleReset: decisionState.handleReset,
    resetSession: sessionManagement.resetSession,
    resetGlobalStats: sessionManagement.resetGlobalStats,
    handlePathSelection,
    loadSessionFromLibrary: sessionManagement.loadSessionFromLibrary,
    getTrajectoryDirection: decisionState.getTrajectoryDirection,
    exportSession: sessionManagement.exportSession,
    saveSessionSnapshot: sessionManagement.saveSessionSnapshot
  };
}
