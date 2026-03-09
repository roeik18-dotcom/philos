import { useState, useRef, useEffect, useCallback } from 'react';
import { 
  syncWithCloud, 
  getCloudData, 
  isCloudAvailable,
  saveDecision,
  savePathSelection,
  savePathLearning,
  getMemoryData,
  getFullUserData,
  fullSyncUserData,
  getUserDecisionStats,
  getUserId
} from '../services/cloudSync';

// LocalStorage keys
const STORAGE_KEY = 'philos_session_data';
const GLOBAL_STORAGE_KEY = 'philos_global_data';
const TREND_STORAGE_KEY = 'philos_trend_history';
const LAST_SYNC_KEY = 'philos_last_sync';
const LEARNING_HISTORY_KEY = 'philos_learning_history';

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

// Value tagging logic
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

// Calculate adaptive scores from learning history
const calculateAdaptiveScores = (learningHist) => {
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
const applyReplayInsightsToScores = (baseScores, replayInsights) => {
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
      // Calculate boost based on exploration frequency (max +8)
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
    // If user repeatedly explores positive alternatives from negative decisions
    if (['harm', 'avoidance'].includes(from) && ['contribution', 'recovery', 'order'].includes(to)) {
      if (count >= 2) {
        const boost = Math.min(5, count);
        adjusted[to] += boost;
        // Check if not already in boosted
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
    // User consciously avoids exploring harm paths - strengthen penalty
    const penalty = -4;
    adjusted['harm'] += penalty;
    adjustments.penalized.push({ type: 'harm', penalty: Math.abs(penalty), reason: 'never_explored' });
  }

  if (avoidanceCount === 0 && totalReplays >= 3) {
    // User consciously avoids exploring avoidance paths
    const penalty = -3;
    adjusted['avoidance'] += penalty;
    adjustments.penalized.push({ type: 'avoidance', penalty: Math.abs(penalty), reason: 'never_explored' });
  }

  // 4. Blind spots - slightly boost unexplored positive transitions
  blindSpots.forEach(spot => {
    if (['contribution', 'recovery', 'order'].includes(spot.to)) {
      // Small boost to encourage exploring these paths
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

// Load functions
const loadFromStorage = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch (e) {
    console.error('Error loading from localStorage:', e);
  }
  return null;
};

const loadGlobalStats = () => {
  try {
    const saved = localStorage.getItem(GLOBAL_STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch (e) {
    console.error('Error loading global stats:', e);
  }
  return {
    contribution: 0, recovery: 0, harm: 0, order: 0, avoidance: 0,
    totalDecisions: 0, sessions: 0
  };
};

const loadTrendHistory = () => {
  try {
    const saved = localStorage.getItem(TREND_STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch (e) {
    console.error('Error loading trend history:', e);
  }
  return [];
};

const loadLearningHistory = () => {
  try {
    const saved = localStorage.getItem(LEARNING_HISTORY_KEY);
    if (saved) return JSON.parse(saved);
  } catch (e) {
    console.error('Error loading learning history:', e);
  }
  return [];
};

export default function usePhilosState(user = null) {
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
  
  // Global and trend state
  const [globalStats, setGlobalStats] = useState(loadGlobalStats);
  const [trendHistory, setTrendHistory] = useState(loadTrendHistory);
  
  // Path learning state
  const [selectedPathData, setSelectedPathData] = useState(null);
  const [learningHistory, setLearningHistory] = useState(loadLearningHistory);
  const [adaptiveScores, setAdaptiveScores] = useState(() => calculateAdaptiveScores(loadLearningHistory()));
  
  // Sync state
  const [syncStatus, setSyncStatus] = useState({ 
    syncing: false, 
    lastSynced: null, 
    cloudAvailable: false,
    deviceSynced: false,
    syncMessage: ''
  });
  
  // UI state
  const [showShareCard, setShowShareCard] = useState(false);
  
  // Decision chain state
  const [parentDecision, setParentDecision] = useState(null);
  
  // Decision replay state
  const [replayDecision, setReplayDecision] = useState(null);
  const [replayHistory, setReplayHistory] = useState([]);
  
  // Replay insights state for adaptive adjustments
  const [replayInsights, setReplayInsights] = useState(null);
  const [replayAdaptiveAdjustments, setReplayAdaptiveAdjustments] = useState(null);
  
  // Refs
  const syncTimeoutRef = useRef(null);
  const hasHydratedFromCloud = useRef(false);

  // Cloud sync function
  const performCloudSync = useCallback(async (forceSync = false) => {
    if (syncStatus.syncing && !forceSync) return;
    
    setSyncStatus(prev => ({ ...prev, syncing: true }));
    
    try {
      const result = await syncWithCloud({
        history,
        globalStats,
        trendHistory
      });
      
      if (result.success) {
        if (result.history && result.history.length > 0) setHistory(result.history);
        if (result.globalStats && Object.keys(result.globalStats).length > 0) setGlobalStats(result.globalStats);
        if (result.trendHistory && result.trendHistory.length > 0) setTrendHistory(result.trendHistory);
        
        localStorage.setItem(LAST_SYNC_KEY, result.lastSynced);
        setSyncStatus(prev => ({ 
          ...prev, syncing: false, lastSynced: result.lastSynced, cloudAvailable: true 
        }));
      } else {
        setSyncStatus(prev => ({ ...prev, syncing: false }));
      }
    } catch (error) {
      console.error('Cloud sync failed:', error);
      setSyncStatus(prev => ({ ...prev, syncing: false }));
    }
  }, [history, globalStats, trendHistory, syncStatus.syncing]);

  // Initial cloud sync on mount
  useEffect(() => {
    const initSync = async () => {
      const cloudOk = await isCloudAvailable();
      setSyncStatus(prev => ({ ...prev, cloudAvailable: cloudOk }));
      
      if (cloudOk) {
        const cloudData = await getCloudData();
        if (cloudData.success && cloudData.lastSynced) {
          if (cloudData.history.length > 0) {
            setHistory(prev => {
              const merged = [...prev];
              cloudData.history.forEach(ch => {
                if (!merged.find(h => h.timestamp === ch.timestamp)) merged.push(ch);
              });
              return merged.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).slice(0, 20);
            });
          }
          if (cloudData.globalStats && cloudData.globalStats.totalDecisions > 0) {
            setGlobalStats(prev => ({
              contribution: Math.max(prev.contribution, cloudData.globalStats.contribution || 0),
              recovery: Math.max(prev.recovery, cloudData.globalStats.recovery || 0),
              harm: Math.max(prev.harm, cloudData.globalStats.harm || 0),
              order: Math.max(prev.order, cloudData.globalStats.order || 0),
              avoidance: Math.max(prev.avoidance, cloudData.globalStats.avoidance || 0),
              totalDecisions: Math.max(prev.totalDecisions, cloudData.globalStats.totalDecisions || 0),
              sessions: Math.max(prev.sessions, cloudData.globalStats.sessions || 0)
            }));
          }
          if (cloudData.trendHistory.length > 0) {
            setTrendHistory(prev => {
              const trendMap = {};
              [...prev, ...cloudData.trendHistory].forEach(t => {
                if (t.date) {
                  if (!trendMap[t.date] || t.totalDecisions >= trendMap[t.date].totalDecisions) {
                    trendMap[t.date] = t;
                  }
                }
              });
              return Object.values(trendMap).sort((a, b) => a.date.localeCompare(b.date)).slice(-30);
            });
          }
          setSyncStatus(prev => ({ ...prev, lastSynced: cloudData.lastSynced }));
        }
      }
    };
    
    initSync();
  }, []);

  // Load memory data from cloud on mount
  useEffect(() => {
    const loadMemoryFromCloud = async () => {
      try {
        const cloudAvailable = await isCloudAvailable();
        if (!cloudAvailable) return;
        
        const memoryData = await getMemoryData();
        if (memoryData.success) {
          if (memoryData.learningHistory && memoryData.learningHistory.length > 0) {
            setLearningHistory(prev => {
              const merged = [...prev];
              memoryData.learningHistory.forEach(entry => {
                if (!merged.find(h => h.timestamp === entry.timestamp)) merged.push(entry);
              });
              return merged.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp)).slice(-50);
            });
          }
          if (memoryData.adaptiveScores && Object.keys(memoryData.adaptiveScores).length > 0) {
            const scores = memoryData.adaptiveScores;
            if (scores.contribution !== undefined || scores.recovery !== undefined) {
              setAdaptiveScores({
                contribution: scores.contribution || 0,
                recovery: scores.recovery || 0,
                order: scores.order || 0,
                harm: scores.harm || 0,
                avoidance: scores.avoidance || 0
              });
            }
          }
        }
      } catch (error) {
        console.log('Failed to load memory from cloud:', error);
      }
    };
    
    loadMemoryFromCloud();
  }, []);

  // Multi-device continuity: Hydrate from cloud when user is authenticated
  useEffect(() => {
    const hydrateFromCloud = async () => {
      // Only hydrate if user is authenticated and we haven't hydrated yet
      if (!user || hasHydratedFromCloud.current) return;
      
      setSyncStatus(prev => ({ ...prev, syncing: true, syncMessage: 'טוען נתונים מהענן...' }));
      
      try {
        const fullData = await getFullUserData(user.id);
        
        if (fullData.success) {
          // Hydrate all state from cloud
          if (fullData.history && fullData.history.length > 0) {
            setHistory(fullData.history);
            // Also update state from latest history entry
            if (fullData.history[0]) {
              setState(prev => ({
                ...prev,
                chaos_order: fullData.history[0].chaos_order || 0,
                ego_collective: fullData.history[0].ego_collective || 0
              }));
            }
          }
          
          if (fullData.globalStats && Object.keys(fullData.globalStats).length > 0) {
            setGlobalStats({
              contribution: fullData.globalStats.contribution || 0,
              recovery: fullData.globalStats.recovery || 0,
              harm: fullData.globalStats.harm || 0,
              order: fullData.globalStats.order || 0,
              avoidance: fullData.globalStats.avoidance || 0,
              totalDecisions: fullData.globalStats.totalDecisions || 0,
              sessions: fullData.globalStats.sessions || 0
            });
          }
          
          if (fullData.trendHistory && fullData.trendHistory.length > 0) {
            setTrendHistory(fullData.trendHistory);
          }
          
          if (fullData.learningHistory && fullData.learningHistory.length > 0) {
            setLearningHistory(fullData.learningHistory);
          }
          
          if (fullData.adaptiveScores && Object.keys(fullData.adaptiveScores).length > 0) {
            setAdaptiveScores({
              contribution: fullData.adaptiveScores.contribution || 0,
              recovery: fullData.adaptiveScores.recovery || 0,
              order: fullData.adaptiveScores.order || 0,
              harm: fullData.adaptiveScores.harm || 0,
              avoidance: fullData.adaptiveScores.avoidance || 0
            });
          }
          
          hasHydratedFromCloud.current = true;
          setSyncStatus(prev => ({ 
            ...prev, 
            syncing: false, 
            deviceSynced: true,
            lastSynced: fullData.lastSynced,
            syncMessage: 'מסונכרן בין מכשירים'
          }));
        } else {
          setSyncStatus(prev => ({ 
            ...prev, 
            syncing: false, 
            syncMessage: 'שגיאה בטעינת נתונים'
          }));
        }
      } catch (error) {
        console.error('Failed to hydrate from cloud:', error);
        setSyncStatus(prev => ({ 
          ...prev, 
          syncing: false, 
          syncMessage: 'שגיאה בסנכרון'
        }));
      }
    };
    
    hydrateFromCloud();
  }, [user]);

  // Reset hydration flag when user changes (logout)
  useEffect(() => {
    if (!user) {
      hasHydratedFromCloud.current = false;
      setSyncStatus(prev => ({ 
        ...prev, 
        deviceSynced: false,
        syncMessage: ''
      }));
    }
  }, [user]);

  // Debounced sync after data changes
  useEffect(() => {
    if (!syncStatus.cloudAvailable) return;
    
    if (syncTimeoutRef.current) clearTimeout(syncTimeoutRef.current);
    
    syncTimeoutRef.current = setTimeout(() => {
      performCloudSync();
    }, 5000);
    
    return () => {
      if (syncTimeoutRef.current) clearTimeout(syncTimeoutRef.current);
    };
  }, [history, globalStats, trendHistory, syncStatus.cloudAvailable]);

  // Save to localStorage whenever state or history changes
  useEffect(() => {
    try {
      const dataToSave = { state, history, decisionResult, savedAt: new Date().toISOString() };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave));
    } catch (e) {
      console.error('Error saving to localStorage:', e);
    }
  }, [state, history, decisionResult]);

  // Save global stats to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(GLOBAL_STORAGE_KEY, JSON.stringify(globalStats));
    } catch (e) {
      console.error('Error saving global stats:', e);
    }
  }, [globalStats]);

  // Save trend history to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(TREND_STORAGE_KEY, JSON.stringify(trendHistory));
    } catch (e) {
      console.error('Error saving trend history:', e);
    }
  }, [trendHistory]);

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
    const fetchAndApplyReplayInsights = async () => {
      // Use authenticated user ID or persistent anonymous ID
      const userId = user?.id || getUserId();

      try {
        const API_URL = process.env.REACT_APP_BACKEND_URL;
        const response = await fetch(`${API_URL}/api/memory/replay-insights/${userId}`);
        
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.total_replays > 0) {
            setReplayInsights(data);
            
            // Apply replay insights to adaptive scores
            const baseScores = calculateAdaptiveScores(learningHistory);
            const { adjustedScores, adjustments } = applyReplayInsightsToScores(baseScores, data);
            
            if (adjustments && (adjustments.boosted.length > 0 || adjustments.penalized.length > 0)) {
              setAdaptiveScores(adjustedScores);
              setReplayAdaptiveAdjustments(adjustments);
            }
          }
        }
      } catch (error) {
        console.log('Failed to fetch replay insights:', error);
      }
    };

    // Fetch on mount and when replay history changes
    fetchAndApplyReplayInsights();
  }, [user, replayHistory.length, learningHistory]);

  // Auto-save session snapshot when significant decisions are made
  useEffect(() => {
    if (history.length > 0 && history.length % 5 === 0) {
      saveSessionSnapshotSilent();
    }
  }, [history.length]);

  // Update global stats
  const updateGlobalStats = (valueTag) => {
    setGlobalStats(prev => ({
      ...prev,
      [valueTag]: (prev[valueTag] || 0) + 1,
      totalDecisions: prev.totalDecisions + 1
    }));
  };

  // Handle path selection
  const handlePathSelection = async (pathData) => {
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
    setActionText(pathData.action);
    
    try {
      await savePathSelection(pathSelectionData);
    } catch (error) {
      console.log('Cloud save failed for path selection:', error);
    }
  };

  // Save learning data
  const saveLearningData = async (selectedPath, actualResult) => {
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
  };

  // Save session snapshot silently
  const saveSessionSnapshotSilent = () => {
    if (history.length < 3) return;
    
    const tagCounts = { contribution: 0, recovery: 0, harm: 0, order: 0, avoidance: 0 };
    history.forEach(h => {
      if (tagCounts.hasOwnProperty(h.value_tag)) tagCounts[h.value_tag]++;
    });
    
    const today = new Date().toISOString().slice(0, 10);
    const existingIndex = trendHistory.findIndex(s => s.date === today);
    
    const snapshot = {
      date: today,
      timestamp: new Date().toISOString(),
      totalDecisions: history.length,
      ...tagCounts
    };
    
    if (existingIndex >= 0) {
      setTrendHistory(prev => {
        const updated = [...prev];
        updated[existingIndex] = snapshot;
        return updated.slice(-30);
      });
    } else {
      setTrendHistory(prev => [...prev, snapshot].slice(-30));
    }
  };

  // Save session snapshot
  const saveSessionSnapshot = () => {
    if (history.length < 3) return;
    
    const tagCounts = { contribution: 0, recovery: 0, harm: 0, order: 0, avoidance: 0 };
    history.forEach(h => {
      if (tagCounts.hasOwnProperty(h.value_tag)) tagCounts[h.value_tag]++;
    });
    
    const today = new Date().toISOString().slice(0, 10);
    const existingIndex = trendHistory.findIndex(s => s.date === today);
    
    const snapshot = {
      date: today,
      timestamp: new Date().toISOString(),
      totalDecisions: history.length,
      ...tagCounts
    };
    
    if (existingIndex >= 0) {
      setTrendHistory(prev => {
        const updated = [...prev];
        updated[existingIndex] = snapshot;
        return updated.slice(-30);
      });
    } else {
      setTrendHistory(prev => [...prev, snapshot].slice(-30));
    }
  };

  // Reset session
  const resetSession = () => {
    if (window.confirm('Are you sure you want to reset the session? All data will be lost.')) {
      saveSessionSnapshot();
      localStorage.removeItem(STORAGE_KEY);
      setState({ physical_capacity: 50, chaos_order: 0, ego_collective: 0, gap_type: 'energy' });
      setActionText("");
      setDecisionResult(null);
      setHistory([]);
    }
  };

  // Reset global stats
  const resetGlobalStats = () => {
    if (window.confirm('Reset all global statistics? This cannot be undone.')) {
      localStorage.removeItem(GLOBAL_STORAGE_KEY);
      localStorage.removeItem(TREND_STORAGE_KEY);
      setGlobalStats({
        contribution: 0, recovery: 0, harm: 0, order: 0, avoidance: 0,
        totalDecisions: 0, sessions: 0
      });
      setTrendHistory([]);
    }
  };

  // Load session from library
  const loadSessionFromLibrary = (sessionHistory) => {
    if (window.confirm('טעינת סשן תחליף את הנתונים הנוכחיים. להמשיך?')) {
      setHistory(sessionHistory);
      
      if (sessionHistory.length > 0) {
        const lastDecision = sessionHistory[0];
        setState(prev => ({
          ...prev,
          chaos_order: lastDecision.chaos_order || 0,
          ego_collective: lastDecision.ego_collective || 0
        }));
        setDecisionResult({
          decision: lastDecision.decision,
          action: lastDecision.action,
          reasons: [],
          projection: {
            chaos_order: lastDecision.chaos_order,
            ego_collective: lastDecision.ego_collective
          },
          value_tag: lastDecision.value_tag,
          balance_score: lastDecision.balance_score
        });
      }
      setActionText('');
    }
  };

  // Evaluate action
  const evaluateAction = async (quickAction = null) => {
    // Handle case where quickAction might be an event object from button click
    const actionToEvaluate = (typeof quickAction === 'string' && quickAction) ? quickAction : actionText;
    
    if (!actionToEvaluate || typeof actionToEvaluate !== 'string') {
      alert('יש להזין פעולה');
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

    if (selectedPathData) {
      saveLearningData(selectedPathData, newResult);
    }

    updateGlobalStats(valueTag);

    const historyEntry = {
      id: 'dec_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
      action: actionToEvaluate,
      decision: decision,
      chaos_order: newChaosOrder,
      ego_collective: newEgoCollective,
      balance_score: newBalanceScore,
      value_tag: valueTag,
      parent_decision_id: parentDecision?.id || null,
      time: new Date().toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' }),
      timestamp: timestamp
    };

    setHistory(prev => [historyEntry, ...prev].slice(0, 50));

    // Auto-save decision to cloud for all users (including anonymous)
    try {
      await saveDecision({
        action: actionToEvaluate,
        decision: decision,
        chaos_order: newChaosOrder,
        ego_collective: newEgoCollective,
        balance_score: newBalanceScore,
        value_tag: valueTag,
        parent_decision_id: parentDecision?.id || null
      });
    } catch (error) {
      console.log('Auto-save decision failed (will retry on sync):', error);
    }
    
    // Clear parent decision and action text after evaluation
    setParentDecision(null);
    if (!quickAction) {
      setActionText('');
    }
  };

  // Handle reset
  const handleReset = () => {
    setState({ physical_capacity: 50, chaos_order: 0, ego_collective: 0, gap_type: 'energy' });
    setActionText("");
    setDecisionResult(null);
    setHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  // Get trajectory direction
  const getTrajectoryDirection = () => {
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
  };

  // Export session
  const exportSession = () => {
    const sessionData = {
      timestamp: new Date().toISOString(),
      state: state,
      history: history,
      balanceScore: 100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective)),
      trajectory: getTrajectoryDirection(),
      totalActions: history.length
    };
    const blob = new Blob([JSON.stringify(sessionData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `philos-session-${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Calculate balance score
  const balanceScore = 100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective));

  // Handle adding a follow-up decision
  const handleAddFollowUp = (parentDecisionItem) => {
    setParentDecision(parentDecisionItem);
    setActionText('');
    // Scroll to action input
    const actionInput = document.querySelector('[data-testid="action-input"]');
    if (actionInput) {
      actionInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      actionInput.focus();
    }
  };

  // Handle decision replay - set the decision to replay
  const handleReplayDecision = (decision) => {
    setReplayDecision(decision);
    // Scroll to replay section when it appears
    setTimeout(() => {
      const replaySection = document.querySelector('[data-testid="decision-replay-section"]');
      if (replaySection) {
        replaySection.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  };

  // Close replay section
  const closeReplay = () => {
    setReplayDecision(null);
  };

  // Save replay metadata
  const saveReplayMetadata = async (replayData) => {
    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      // Use authenticated user ID or persistent anonymous ID
      const userId = user?.id || getUserId();
      
      const response = await fetch(`${API_URL}/api/memory/replay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          ...replayData
        })
      });
      
      if (response.ok) {
        // Add to local replay history
        setReplayHistory(prev => [replayData, ...prev].slice(0, 50));
      }
    } catch (error) {
      console.log('Failed to save replay metadata:', error);
      // Still save locally even if cloud fails
      setReplayHistory(prev => [replayData, ...prev].slice(0, 50));
    }
  };

  return {
    // Core state
    state,
    setState,
    actionText,
    setActionText,
    decisionResult,
    setDecisionResult,
    history,
    setHistory,
    
    // Global and trend
    globalStats,
    setGlobalStats,
    trendHistory,
    setTrendHistory,
    
    // Path learning
    selectedPathData,
    setSelectedPathData,
    learningHistory,
    setLearningHistory,
    adaptiveScores,
    setAdaptiveScores,
    
    // Sync
    syncStatus,
    setSyncStatus,
    performCloudSync,
    
    // UI
    showShareCard,
    setShowShareCard,
    
    // Decision chains
    parentDecision,
    setParentDecision,
    handleAddFollowUp,
    
    // Decision replay
    replayDecision,
    setReplayDecision,
    replayHistory,
    handleReplayDecision,
    closeReplay,
    saveReplayMetadata,
    
    // Replay adaptive effect
    replayInsights,
    replayAdaptiveAdjustments,
    
    // Computed
    balanceScore,
    
    // Actions
    evaluateAction,
    handleReset,
    resetSession,
    resetGlobalStats,
    handlePathSelection,
    loadSessionFromLibrary,
    getTrajectoryDirection,
    exportSession,
    saveSessionSnapshot
  };
}
