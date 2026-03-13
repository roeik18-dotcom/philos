// Core decision evaluation logic and state
import { useState, useCallback } from 'react';
import { saveDecision } from '../services/cloudSync';

// LocalStorage keys
const STORAGE_KEY = 'philos_session_data';

// Value tagging logic - determines the behavioral tag for an action
export const getValueTag = (action, gapType = 'energy') => {
  const actionLower = action.toLowerCase();
  
  if (actionLower.match(/angry|attack|insult|shout|hurt|revenge|fight|yell|scream|curse|blame|criticize|hostile|aggressive/)) {
    return 'harm';
  }
  
  if (actionLower.match(/ignore|avoid|delay|scroll|escape|postpone|hide|skip|cancel|procrastinate|distract/)) {
    return 'avoidance';
  }
  
  if (actionLower.match(/walk|breathe|breathing|stretch|water|rest|sleep|pause|calm|relax|meditate|nap|break/)) {
    return 'recovery';
  }
  
  if (actionLower.match(/organize|clean|plan|focus|work|structure|sort|tidy|arrange|schedule|prioritize|desk|project/)) {
    return 'order';
  }
  
  if (actionLower.match(/help|support|friend|give|assist|share|care|call|connect|encourage|listen|positive/)) {
    return 'contribution';
  }
  
  if (gapType === 'energy') return 'recovery';
  if (gapType === 'clarity' || gapType === 'order') return 'order';
  if (gapType === 'relation') return 'contribution';
  
  return 'recovery';
};

// Load session data from localStorage
const loadFromStorage = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch (e) {
    console.error('Error loading from localStorage:', e);
  }
  return null;
};

// Save session data to localStorage
const saveToStorage = (data) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (e) {
    console.error('Error saving to localStorage:', e);
  }
};

/**
 * Core decision state hook
 * Manages: state (physical_capacity, chaos_order, ego_collective, gap_type),
 * actionText, decisionResult, history, and the evaluation logic
 */
export function useDecisionState({ 
  onDecisionMade,
  onGlobalStatsUpdate,
  onLearningDataSave,
  selectedPathData,
  parentDecision,
  setParentDecision,
  user
}) {
  const savedData = loadFromStorage();

  // Core state
  const [state, setState] = useState(savedData?.state || {
    physical_capacity: 50,
    chaos_order: 0,
    ego_collective: 0,
    gap_type: 'energy'
  });
  const [actionText, setActionText] = useState("");
  const [decisionResult, setDecisionResult] = useState(savedData?.decisionResult || null);
  const [history, setHistory] = useState(savedData?.history || []);

  // Save to localStorage whenever state or history changes
  const persistToStorage = useCallback(() => {
    saveToStorage({ 
      state, 
      history, 
      decisionResult, 
      savedAt: new Date().toISOString() 
    });
  }, [state, history, decisionResult]);

  // Evaluate action - core decision logic
  const evaluateAction = useCallback(async (recommendationMetadata = null) => {
    // Handle case where recommendationMetadata might be an event object
    const isRecommendationMetadata = recommendationMetadata && 
      typeof recommendationMetadata === 'object' && 
      recommendationMetadata.followed_recommendation === true;
    
    const actionToEvaluate = actionText;
    
    if (!actionToEvaluate || typeof actionToEvaluate !== 'string') {
      alert('There is a need to enter an action');
      return;
    }

    let decision = "Allowed";
    let reasons = [];

    if (state.gap_type === "energy" && state.physical_capacity < 30) {
      decision = "Blocked";
      reasons.push("Energy gap blocks action - physical capacity too low");
    } else {
      reasons.push("Energy gap allows the action");
    }

    const actionLower = actionToEvaluate.toLowerCase();
    let newChaosOrder = state.chaos_order;
    let newEgoCollective = state.ego_collective;

    if (actionLower.includes('walk') || actionLower.includes('exercise') || actionLower.includes('organize')) {
      newChaosOrder = Math.min(100, state.chaos_order + 20);
      reasons.push("The action increases order and structure");
    }
    
    if (actionLower.includes('help') || actionLower.includes('share') || actionLower.includes('call')) {
      newEgoCollective = Math.min(100, state.ego_collective + 20);
      reasons.push("The action increases collective orientation");
    }

    if (actionLower.includes('rest') || actionLower.includes('sleep') || actionLower.includes('relax')) {
      newChaosOrder = Math.max(-100, state.chaos_order - 15);
      reasons.push("The action allows for spontaneity and rest");
    }

    if (actionLower.includes('meditate') || actionLower.includes('journal') || actionLower.includes('think')) {
      newEgoCollective = Math.max(-100, state.ego_collective - 15);
      reasons.push("The action focuses on self-reflection");
    }

    if (reasons.length === 1) {
      reasons.push("Action maintains current orientation balance");
    }

    setState(prev => ({ ...prev, chaos_order: newChaosOrder, ego_collective: newEgoCollective }));

    const newBalanceScore = 100 - (Math.abs(newChaosOrder) + Math.abs(newEgoCollective));
    const valueTag = getValueTag(actionToEvaluate, state.gap_type);
    const timestamp = new Date().toISOString();

    const newResult = {
      decision,
      action: actionToEvaluate,
      reasons,
      projection: { chaos_order: newChaosOrder, ego_collective: newEgoCollective },
      value_tag: valueTag,
      balance_score: newBalanceScore
    };

    setDecisionResult(newResult);

    // Callback for learning data
    if (selectedPathData && onLearningDataSave) {
      onLearningDataSave(selectedPathData, newResult);
    }

    // Callback for global stats
    if (onGlobalStatsUpdate) {
      onGlobalStatsUpdate(valueTag);
    }

    const historyEntry = {
      id: 'dec_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
      action: actionToEvaluate,
      decision: decision,
      chaos_order: newChaosOrder,
      ego_collective: newEgoCollective,
      balance_score: newBalanceScore,
      value_tag: valueTag,
      parent_decision_id: parentDecision?.id || null,
      time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      timestamp: timestamp,
      ...(isRecommendationMetadata && {
        followed_recommendation: true,
        recommendation_direction: recommendationMetadata.recommendation_direction,
        recommendation_reason: recommendationMetadata.recommendation_reason,
        recommendation_strength: recommendationMetadata.recommendation_strength
      })
    };

    setHistory(prev => [historyEntry, ...prev].slice(0, 50));

    // Auto-save decision to cloud for all users
    try {
      await saveDecision({
        action: actionToEvaluate,
        decision: decision,
        chaos_order: newChaosOrder,
        ego_collective: newEgoCollective,
        balance_score: newBalanceScore,
        value_tag: valueTag,
        parent_decision_id: parentDecision?.id || null,
        ...(isRecommendationMetadata && {
          followed_recommendation: true,
          recommendation_direction: recommendationMetadata.recommendation_direction,
          recommendation_reason: recommendationMetadata.recommendation_reason,
          recommendation_strength: recommendationMetadata.recommendation_strength
        })
      });
    } catch (error) {
      console.log('Auto-save decision failed (will retry on sync):', error);
    }
    
    // Callback for decision made
    if (onDecisionMade) {
      onDecisionMade(historyEntry);
    }
    
    // Clear parent decision and action text after evaluation
    if (setParentDecision) {
      setParentDecision(null);
    }
    setActionText('');
  }, [actionText, state, selectedPathData, parentDecision, setParentDecision, onDecisionMade, onGlobalStatsUpdate, onLearningDataSave]);

  // Handle reset
  const handleReset = useCallback(() => {
    setState({ physical_capacity: 50, chaos_order: 0, ego_collective: 0, gap_type: 'energy' });
    setActionText("");
    setDecisionResult(null);
    setHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  // Calculate balance score
  const balanceScore = 100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective));

  // Get trajectory direction
  const getTrajectoryDirection = useCallback(() => {
    if (history.length < 2) return 'starting';
    const latest = history[0];
    const previous = history[1];
    const orderDelta = latest.chaos_order - previous.chaos_order;
    const collectiveDelta = latest.ego_collective - previous.ego_collective;
    
    if (orderDelta > 0) return 'toward order';
    if (orderDelta < 0) return 'toward chaos';
    if (collectiveDelta > 0) return 'toward collective';
    if (collectiveDelta < 0) return 'toward ego';
    return 'stable';
  }, [history]);

  return {
    // State
    state,
    setState,
    actionText,
    setActionText,
    decisionResult,
    setDecisionResult,
    history,
    setHistory,
    
    // Computed
    balanceScore,
    
    // Actions
    evaluateAction,
    handleReset,
    getTrajectoryDirection,
    persistToStorage
  };
}
