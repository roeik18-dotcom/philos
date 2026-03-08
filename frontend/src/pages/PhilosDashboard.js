import { useState, useRef, useEffect, useCallback } from 'react';
import { toPng } from 'html-to-image';
import {
  DailyOrientationSection,
  ActionEvaluationSection,
  DecisionMapSection,
  PersonalMapSection,
  CollectiveValueMapSection,
  OrientationFieldSection,
  GlobalValueFieldSection,
  GlobalTrendSection,
  SessionSummarySection,
  SessionLibrarySection,
  ValueConstellationSection,
  SessionComparisonSection,
  WeeklySummarySection,
  DecisionPathEngineSection
} from '../components/philos/sections';
import { syncWithCloud, getCloudData, isCloudAvailable } from '../services/cloudSync';

// LocalStorage keys
const STORAGE_KEY = 'philos_session_data';
const GLOBAL_STORAGE_KEY = 'philos_global_data';
const TREND_STORAGE_KEY = 'philos_trend_history';
const LAST_SYNC_KEY = 'philos_last_sync';

// Optimal zone definition
const OPTIMAL_ZONE = {
  order: { min: 20, max: 60 },
  collective: { min: 10, max: 50 }
};

// Calculate suggested vector toward optimal zone
const calculateSuggestedVector = (chaosOrder, egoCollective) => {
  let suggestedOrder = 0;
  let suggestedCollective = 0;
  let suggestions = [];
  let reasons = [];

  // Check order axis (chaos_order)
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

  // Check collective axis (ego_collective)
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

  // Check if in optimal zone
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

// Value tagging logic with expanded keywords and smart fallbacks
const getValueTag = (action, gapType = 'energy') => {
  const actionLower = action.toLowerCase();
  
  // Check harm first (prioritize negative actions)
  if (actionLower.match(/angry|attack|insult|shout|hurt|revenge|fight|yell|scream|curse|blame|criticize|hostile|aggressive/)) {
    return 'harm';
  }
  
  // Avoidance: escaping, postponing, hiding
  if (actionLower.match(/ignore|avoid|delay|scroll|escape|postpone|hide|skip|cancel|procrastinate|distract/)) {
    return 'avoidance';
  }
  
  // Recovery: self-care, rest, restoration
  if (actionLower.match(/walk|breathe|breathing|stretch|water|rest|sleep|pause|calm|relax|meditate|nap|break/)) {
    return 'recovery';
  }
  
  // Order: organizing, structuring, focusing
  if (actionLower.match(/organize|clean|plan|focus|work|structure|sort|tidy|arrange|schedule|prioritize|desk|project/)) {
    return 'order';
  }
  
  // Contribution: helping, supporting, connecting with others (check last as "message" is generic)
  if (actionLower.match(/help|support|friend|give|assist|share|care|call|connect|encourage|listen|positive/)) {
    return 'contribution';
  }
  
  // Smart fallbacks based on gap_type
  if (gapType === 'energy') {
    return 'recovery';
  }
  if (gapType === 'clarity' || gapType === 'order') {
    return 'order';
  }
  if (gapType === 'relation') {
    return 'contribution';
  }
  
  // Default fallback
  return 'recovery';
};

// Analyze personal patterns
const analyzePersonalMap = (historyData) => {
  if (historyData.length === 0) {
    return {
      dominantOrder: 'balanced',
      dominantCollective: 'balanced',
      topValueTags: [],
      patternSummary: []
    };
  }

  // Calculate averages
  const avgOrder = historyData.reduce((sum, h) => sum + h.chaos_order, 0) / historyData.length;
  const avgCollective = historyData.reduce((sum, h) => sum + h.ego_collective, 0) / historyData.length;

  // Dominant direction
  const dominantOrder = avgOrder > 10 ? 'order' : avgOrder < -10 ? 'chaos' : 'balanced';
  const dominantCollective = avgCollective > 10 ? 'collective' : avgCollective < -10 ? 'ego' : 'balanced';

  // Count value tags
  const tagCounts = {};
  historyData.forEach(h => {
    if (h.value_tag && h.value_tag !== 'neutral') {
      tagCounts[h.value_tag] = (tagCounts[h.value_tag] || 0) + 1;
    }
  });

  // Top 3 value tags
  const topValueTags = Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([tag, count]) => ({ tag, count }));

  // Find unstable moments pattern
  const unstableMoments = historyData.filter(h => h.balance_score < 40);
  let unstablePattern = '';
  if (unstableMoments.length > 0) {
    const unstableAvgOrder = unstableMoments.reduce((sum, h) => sum + h.chaos_order, 0) / unstableMoments.length;
    const unstableAvgCollective = unstableMoments.reduce((sum, h) => sum + h.ego_collective, 0) / unstableMoments.length;
    const orderDir = unstableAvgOrder < 0 ? 'chaos' : 'order';
    const collectiveDir = unstableAvgCollective < 0 ? 'ego' : 'collective';
    unstablePattern = `${orderDir}/${collectiveDir}`;
  }

  // Build pattern summary
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

export default function PhilosDashboard() {
  // Load initial state from localStorage
  const loadFromStorage = () => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.error('Error loading from localStorage:', e);
    }
    return null;
  };

  // Load global stats from localStorage
  const loadGlobalStats = () => {
    try {
      const saved = localStorage.getItem(GLOBAL_STORAGE_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.error('Error loading global stats:', e);
    }
    return {
      contribution: 0,
      recovery: 0,
      harm: 0,
      order: 0,
      avoidance: 0,
      totalDecisions: 0,
      sessions: 0
    };
  };

  // Load trend history from localStorage
  const loadTrendHistory = () => {
    try {
      const saved = localStorage.getItem(TREND_STORAGE_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.error('Error loading trend history:', e);
    }
    return [];
  };

  const savedData = loadFromStorage();

  const [state, setState] = useState(savedData?.state || {
    physical_capacity: 50,
    chaos_order: 0,
    ego_collective: 0,
    gap_type: 'energy'
  });
  const [actionText, setActionText] = useState("");
  const [decisionResult, setDecisionResult] = useState(savedData?.decisionResult || null);
  const [history, setHistory] = useState(savedData?.history || []);
  const [globalStats, setGlobalStats] = useState(loadGlobalStats);
  const [trendHistory, setTrendHistory] = useState(loadTrendHistory);
  const [showShareCard, setShowShareCard] = useState(false);
  const [syncStatus, setSyncStatus] = useState({ syncing: false, lastSynced: null, cloudAvailable: false });
  const shareCardRef = useRef(null);
  const syncTimeoutRef = useRef(null);

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
        // Update local state with merged cloud data
        if (result.history && result.history.length > 0) {
          setHistory(result.history);
        }
        if (result.globalStats && Object.keys(result.globalStats).length > 0) {
          setGlobalStats(result.globalStats);
        }
        if (result.trendHistory && result.trendHistory.length > 0) {
          setTrendHistory(result.trendHistory);
        }
        
        localStorage.setItem(LAST_SYNC_KEY, result.lastSynced);
        setSyncStatus(prev => ({ 
          ...prev, 
          syncing: false, 
          lastSynced: result.lastSynced,
          cloudAvailable: true 
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
        // First, fetch cloud data
        const cloudData = await getCloudData();
        if (cloudData.success && cloudData.lastSynced) {
          // Merge cloud data with local
          if (cloudData.history.length > 0) {
            setHistory(prev => {
              const merged = [...prev];
              cloudData.history.forEach(ch => {
                if (!merged.find(h => h.timestamp === ch.timestamp)) {
                  merged.push(ch);
                }
              });
              return merged.sort((a, b) => 
                new Date(b.timestamp) - new Date(a.timestamp)
              ).slice(0, 20);
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

  // Debounced sync after data changes
  useEffect(() => {
    if (!syncStatus.cloudAvailable) return;
    
    // Clear existing timeout
    if (syncTimeoutRef.current) {
      clearTimeout(syncTimeoutRef.current);
    }
    
    // Set new timeout for debounced sync (5 seconds after last change)
    syncTimeoutRef.current = setTimeout(() => {
      performCloudSync();
    }, 5000);
    
    return () => {
      if (syncTimeoutRef.current) {
        clearTimeout(syncTimeoutRef.current);
      }
    };
  }, [history, globalStats, trendHistory, syncStatus.cloudAvailable]);

  // Save to localStorage whenever state or history changes
  useEffect(() => {
    try {
      const dataToSave = {
        state,
        history,
        decisionResult,
        savedAt: new Date().toISOString()
      };
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

  // Auto-save session snapshot when significant decisions are made (every 5 decisions)
  useEffect(() => {
    if (history.length > 0 && history.length % 5 === 0) {
      saveSessionSnapshotSilent();
    }
  }, [history.length]);

  // Update global stats when a new decision is made
  const updateGlobalStats = (valueTag) => {
    setGlobalStats(prev => ({
      ...prev,
      [valueTag]: (prev[valueTag] || 0) + 1,
      totalDecisions: prev.totalDecisions + 1
    }));
  };

  // Save session snapshot silently (without confirmation)
  const saveSessionSnapshotSilent = () => {
    if (history.length < 3) return;
    
    const tagCounts = { contribution: 0, recovery: 0, harm: 0, order: 0, avoidance: 0 };
    history.forEach(h => {
      if (tagCounts.hasOwnProperty(h.value_tag)) {
        tagCounts[h.value_tag]++;
      }
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

  // Save session snapshot to trend history
  const saveSessionSnapshot = () => {
    if (history.length < 3) return; // Only save sessions with at least 3 decisions
    
    // Calculate session metrics
    const tagCounts = { contribution: 0, recovery: 0, harm: 0, order: 0, avoidance: 0 };
    history.forEach(h => {
      if (tagCounts.hasOwnProperty(h.value_tag)) {
        tagCounts[h.value_tag]++;
      }
    });
    
    const today = new Date().toISOString().slice(0, 10);
    
    // Check if we already have a snapshot for today
    const existingIndex = trendHistory.findIndex(s => s.date === today);
    
    const snapshot = {
      date: today,
      timestamp: new Date().toISOString(),
      totalDecisions: history.length,
      ...tagCounts
    };
    
    if (existingIndex >= 0) {
      // Update existing snapshot for today
      setTrendHistory(prev => {
        const updated = [...prev];
        updated[existingIndex] = snapshot;
        return updated.slice(-30); // Keep last 30 sessions
      });
    } else {
      // Add new snapshot
      setTrendHistory(prev => [...prev, snapshot].slice(-30));
    }
  };

  // Reset session - clear localStorage and reset state
  const resetSession = () => {
    if (window.confirm('Are you sure you want to reset the session? All data will be lost.')) {
      // Save snapshot before resetting
      saveSessionSnapshot();
      
      localStorage.removeItem(STORAGE_KEY);
      setState({
        physical_capacity: 50,
        chaos_order: 0,
        ego_collective: 0,
        gap_type: 'energy'
      });
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
        contribution: 0,
        recovery: 0,
        harm: 0,
        order: 0,
        avoidance: 0,
        totalDecisions: 0,
        sessions: 0
      });
      setTrendHistory([]);
    }
  };

  // Load a session from the library
  const loadSessionFromLibrary = (sessionHistory) => {
    if (window.confirm('טעינת סשן תחליף את הנתונים הנוכחיים. להמשיך?')) {
      setHistory(sessionHistory);
      
      // Recalculate state from the loaded session
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

  const evaluateAction = () => {
    if (!actionText) {
      alert('יש להזין פעולה');
      return;
    }

    let decision = "Allowed";
    let reasons = [];

    // Evaluate based on gap type and capacity
    if (state.gap_type === "energy" && state.physical_capacity < 30) {
      decision = "Blocked";
      reasons.push("Energy gap blocks action - physical capacity too low");
    } else {
      reasons.push("Energy gap allows the action");
    }

    // Calculate new projection values based on action
    const actionLower = actionText.toLowerCase();
    
    let newChaosOrder = state.chaos_order;
    let newEgoCollective = state.ego_collective;

    // Actions that increase order
    if (actionLower.includes('walk') || actionLower.includes('exercise') || actionLower.includes('organize')) {
      newChaosOrder = Math.min(100, state.chaos_order + 20);
      reasons.push("The action increases order and structure");
    }
    
    // Actions that increase collective orientation
    if (actionLower.includes('help') || actionLower.includes('share') || actionLower.includes('call')) {
      newEgoCollective = Math.min(100, state.ego_collective + 20);
      reasons.push("The action increases collective orientation");
    }

    // Actions that increase chaos/spontaneity  
    if (actionLower.includes('rest') || actionLower.includes('sleep') || actionLower.includes('relax')) {
      newChaosOrder = Math.max(-100, state.chaos_order - 15);
      reasons.push("The action allows for spontaneity and rest");
    }

    // Actions that increase ego focus
    if (actionLower.includes('meditate') || actionLower.includes('journal') || actionLower.includes('think')) {
      newEgoCollective = Math.max(-100, state.ego_collective - 15);
      reasons.push("The action focuses on self-reflection");
    }

    // Default reason if no specific match
    if (reasons.length === 1) {
      reasons.push("Action maintains current orientation balance");
    }

    // Update state with new projection values
    setState(prev => ({
      ...prev,
      chaos_order: newChaosOrder,
      ego_collective: newEgoCollective
    }));

    const newBalanceScore = 100 - (Math.abs(newChaosOrder) + Math.abs(newEgoCollective));
    const valueTag = getValueTag(actionText, state.gap_type);

    const newResult = {
      decision,
      action: actionText,
      reasons,
      projection: {
        chaos_order: newChaosOrder,
        ego_collective: newEgoCollective
      },
      value_tag: valueTag,
      balance_score: newBalanceScore
    };

    setDecisionResult(newResult);

    // Update global stats
    updateGlobalStats(valueTag);

    // Add to history (limit to last 20 for personal map)
    setHistory(prev => [
      {
        action: actionText,
        decision: decision,
        chaos_order: newChaosOrder,
        ego_collective: newEgoCollective,
        balance_score: newBalanceScore,
        value_tag: valueTag,
        time: new Date().toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' }),
        timestamp: new Date().toISOString()
      },
      ...prev
    ].slice(0, 20));
  };

  const handleReset = () => {
    setState({
      physical_capacity: 50,
      chaos_order: 0,
      ego_collective: 0,
      gap_type: 'energy'
    });
    setActionText("");
    setDecisionResult(null);
    setHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  // Calculate trajectory direction
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

  // Export session data
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

  // Download share card as image
  const downloadShareCard = async () => {
    if (shareCardRef.current === null) return;
    try {
      const dataUrl = await toPng(shareCardRef.current, { quality: 0.95 });
      const link = document.createElement('a');
      link.download = `philos-decision-${new Date().toISOString().slice(0,10)}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error('Error generating image:', err);
    }
  };

  // Calculate balance score
  const balanceScore = 100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective));

  return (
    <div className="min-h-screen bg-background p-6 pb-24">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground">Philos Orientation</h1>
          <p className="text-lg text-primary font-medium mt-1">Mental Navigation System</p>
          <p className="text-sm text-muted-foreground mt-1">Navigate your decisions in real time</p>
          {history.length > 0 && (
            <p className="text-xs text-muted-foreground mt-2">
              Session: {history.length} decisions saved
            </p>
          )}
          {/* Cloud Sync Status */}
          <div className="flex items-center justify-center gap-2 mt-2">
            {syncStatus.cloudAvailable ? (
              <>
                <span className={`w-2 h-2 rounded-full ${syncStatus.syncing ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}></span>
                <span className="text-xs text-muted-foreground">
                  {syncStatus.syncing ? 'מסנכרן...' : 'מסונכרן לענן'}
                </span>
                {syncStatus.lastSynced && !syncStatus.syncing && (
                  <button
                    onClick={() => performCloudSync(true)}
                    className="text-xs text-blue-500 hover:text-blue-700 underline"
                    data-testid="manual-sync-btn"
                  >
                    סנכרן עכשיו
                  </button>
                )}
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-gray-400"></span>
                <span className="text-xs text-muted-foreground">מצב לא מקוון</span>
              </>
            )}
          </div>
        </div>

        {/* Reset Session Button */}
        {history.length > 0 && (
          <div className="flex justify-center">
            <button
              onClick={resetSession}
              className="px-4 py-2 text-sm bg-red-100 hover:bg-red-200 text-red-700 rounded-xl transition-all"
            >
              Reset Session
            </button>
          </div>
        )}

        {/* State Sliders */}
        <section className="bg-white rounded-3xl p-6 shadow-sm border border-border space-y-4">
          
          {/* Gap Type */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Gap Type</label>
            <select
              value={state.gap_type}
              onChange={(e) => setState({ ...state, gap_type: e.target.value })}
              className="w-full px-4 py-2 border border-border rounded-xl"
            >
              <option value="energy">energy</option>
              <option value="clarity">clarity</option>
              <option value="order">order</option>
              <option value="relation">relation</option>
            </select>
          </div>

          {/* Physical Capacity */}
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-foreground">Physical Capacity</label>
              <span className="text-sm font-bold">{state.physical_capacity}</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={state.physical_capacity}
              onChange={(e) => setState({ ...state, physical_capacity: parseInt(e.target.value) })}
              className="w-full"
            />
          </div>

          {/* Chaos / Order */}
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-foreground">chaos / order</label>
              <span className="text-sm font-bold">{state.chaos_order}</span>
            </div>
            <input
              type="range"
              min="-100"
              max="100"
              value={state.chaos_order}
              onChange={(e) => setState({ ...state, chaos_order: parseInt(e.target.value) })}
              className="w-full"
            />
          </div>

          {/* Ego / Collective */}
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-foreground">ego / collective</label>
              <span className="text-sm font-bold">{state.ego_collective}</span>
            </div>
            <input
              type="range"
              min="-100"
              max="100"
              value={state.ego_collective}
              onChange={(e) => setState({ ...state, ego_collective: parseInt(e.target.value) })}
              className="w-full"
            />
          </div>
        </section>

        {/* How do you feel right now? */}
        <section className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl p-4 shadow-sm border border-purple-200">
          <h3 className="text-sm font-medium text-foreground mb-3">How do you feel right now?</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setState(prev => ({ ...prev, chaos_order: Math.min(100, prev.chaos_order + 20) }))}
              className="px-4 py-2 text-sm bg-green-100 hover:bg-green-200 text-green-700 rounded-lg transition-all"
            >
              Calm
            </button>
            <button
              onClick={() => setState(prev => ({ ...prev, chaos_order: Math.max(-100, prev.chaos_order - 20) }))}
              className="px-4 py-2 text-sm bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-all"
            >
              Stressed
            </button>
            <button
              onClick={() => setState(prev => ({ ...prev, chaos_order: Math.max(-100, prev.chaos_order - 10) }))}
              className="px-4 py-2 text-sm bg-orange-100 hover:bg-orange-200 text-orange-700 rounded-lg transition-all"
            >
              Confused
            </button>
          </div>
        </section>

        {/* Micro Actions */}
        <section className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-3xl p-4 shadow-sm border border-blue-200">
          <h3 className="text-sm font-medium text-foreground mb-3">Micro Actions</h3>
          <div className="flex flex-wrap gap-2">
            {[
              { text: 'Drink water', icon: '' },
              { text: 'Take 5 deep breaths', icon: '' },
              { text: 'Stand up and stretch', icon: '' },
              { text: 'Send a positive message', icon: '' }
            ].map((action) => (
              <button
                key={action.text}
                onClick={() => setActionText(action.text)}
                className="px-3 py-2 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg transition-all"
              >
                {action.text}
              </button>
            ))}
          </div>
        </section>

        {/* Quick Actions */}
        <section className="bg-white rounded-3xl p-4 shadow-sm border border-border">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Quick Actions</h3>
          <div className="flex flex-wrap gap-2">
            {[
              'Help a friend',
              'Take a walk',
              'Send angry message',
              'Ignore someone',
              'Organize your desk'
            ].map((action) => (
              <button
                key={action}
                onClick={() => setActionText(action)}
                className="px-3 py-2 text-sm bg-muted/50 hover:bg-muted text-foreground rounded-lg transition-all"
              >
                {action}
              </button>
            ))}
          </div>
        </section>

        {/* Action Evaluation Section */}
        <ActionEvaluationSection
          actionText={actionText}
          setActionText={setActionText}
          evaluateAction={evaluateAction}
          decisionResult={decisionResult}
          state={state}
          calculateSuggestedVector={calculateSuggestedVector}
        />

        {/* Decision Path Engine Section */}
        <DecisionPathEngineSection
          state={state}
          history={history}
          onSelectAction={setActionText}
        />

        {/* Orientation Status Panel */}
        <section className="bg-white rounded-3xl p-4 shadow-sm border border-border">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-foreground">Orientation Status</h3>
            <button
              onClick={handleReset}
              className="px-4 py-2 text-sm bg-muted hover:bg-muted/80 text-foreground rounded-xl transition-all"
            >
              Start New Session
            </button>
          </div>
          
          <div className="grid grid-cols-3 gap-3">
            {/* Order */}
            <div className="text-center p-3 bg-muted/20 rounded-xl">
              <p className="text-xs text-muted-foreground mb-1">Order</p>
              <p className={`text-2xl font-bold ${state.chaos_order >= 0 ? 'text-blue-600' : 'text-orange-500'}`}>
                {state.chaos_order >= 0 ? '+' : ''}{state.chaos_order}
              </p>
            </div>
            
            {/* Collective */}
            <div className="text-center p-3 bg-muted/20 rounded-xl">
              <p className="text-xs text-muted-foreground mb-1">Collective</p>
              <p className={`text-2xl font-bold ${state.ego_collective >= 0 ? 'text-green-600' : 'text-purple-500'}`}>
                {state.ego_collective >= 0 ? '+' : ''}{state.ego_collective}
              </p>
            </div>
            
            {/* Energy Gap */}
            <div className="text-center p-3 bg-muted/20 rounded-xl">
              <p className="text-xs text-muted-foreground mb-1">Energy</p>
              <p className={`text-2xl font-bold ${state.physical_capacity >= 30 ? 'text-green-600' : 'text-red-500'}`}>
                {state.physical_capacity}%
              </p>
            </div>
          </div>

          {/* Balance Score */}
          {(() => {
            const score = 100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective));
            const scoreColor = score >= 70 ? 'text-green-600' : score >= 40 ? 'text-yellow-500' : 'text-red-500';
            const scoreBg = score >= 70 ? 'bg-green-100' : score >= 40 ? 'bg-yellow-100' : 'bg-red-100';
            const scoreLabel = score >= 70 ? 'Balanced' : score >= 40 ? 'Unstable' : 'Conflict';
            return (
              <div className={`mt-3 p-3 ${scoreBg} rounded-xl text-center`}>
                <p className="text-xs text-muted-foreground mb-1">Balance Score</p>
                <p className={`text-3xl font-bold ${scoreColor}`}>{score}</p>
                <p className={`text-sm font-medium ${scoreColor}`}>{scoreLabel}</p>
              </div>
            );
          })()}

          {/* Suggested Stabilizing Action - show when balance < 30 */}
          {(() => {
            const score = 100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective));
            if (score >= 30) return null;
            return (
              <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-xl">
                <p className="text-sm font-semibold text-red-700 mb-2">Suggested Stabilizing Action</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    'Take a short walk',
                    'Drink water',
                    'Write it but don\'t send',
                    'Pause for 2 minutes'
                  ].map(action => (
                    <button
                      key={action}
                      onClick={() => setActionText(action)}
                      className="px-2 py-1 text-xs bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-all"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              </div>
            );
          })()}
        </section>

        {/* Recover Energy */}
        <section className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-3xl p-4 shadow-sm border border-emerald-200">
          <h3 className="text-sm font-medium text-foreground mb-2">Recover Energy (+10)</h3>
          <div className="flex flex-wrap gap-2">
            {[
              { text: 'Deep breathing', icon: '' },
              { text: 'Short walk', icon: '' },
              { text: 'Stretch', icon: '' },
              { text: 'Drink water', icon: '' }
            ].map(action => (
              <button
                key={action.text}
                onClick={() => {
                  setActionText(action.text);
                  setState(prev => ({ ...prev, physical_capacity: Math.min(100, prev.physical_capacity + 10) }));
                }}
                className="px-3 py-2 text-sm bg-emerald-100 hover:bg-emerald-200 text-emerald-700 rounded-lg transition-all"
              >
                {action.text}
              </button>
            ))}
          </div>
        </section>

        {/* Daily Orientation Section */}
        <DailyOrientationSection />

        {/* Decision Map Section */}
        <DecisionMapSection
          state={state}
          decisionResult={decisionResult}
          history={history}
          calculateSuggestedVector={calculateSuggestedVector}
        />

        {/* Decision History */}
        {history.length > 0 && (
          <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
            <h3 className="text-xl font-semibold text-foreground mb-4">Decision History</h3>
            
            <div className="space-y-3">
              {history.map((item, idx) => (
                <div 
                  key={idx} 
                  className="p-3 bg-muted/20 rounded-xl border border-border/50"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-muted-foreground">{item.time}</span>
                    <span className={`text-sm font-bold ${item.decision === 'Allowed' ? 'text-green-600' : 'text-red-600'}`}>
                      {item.decision}
                    </span>
                  </div>
                  <p className="font-medium text-foreground mb-1">{item.action}</p>
                  <p className="text-sm text-muted-foreground">
                    {item.chaos_order !== 0 && (
                      <span>order {item.chaos_order > 0 ? '+' : ''}{item.chaos_order} </span>
                    )}
                    {item.ego_collective !== 0 && (
                      <span>| collective {item.ego_collective > 0 ? '+' : ''}{item.ego_collective}</span>
                    )}
                    {item.chaos_order === 0 && item.ego_collective === 0 && (
                      <span>balanced</span>
                    )}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Session Summary Section */}
        <SessionSummarySection
          history={history}
          state={state}
          getTrajectoryDirection={getTrajectoryDirection}
          exportSession={exportSession}
          setShowShareCard={setShowShareCard}
          decisionResult={decisionResult}
        />

        {/* Session Library Section */}
        <SessionLibrarySection
          currentHistory={history}
          onLoadSession={loadSessionFromLibrary}
          cloudAvailable={syncStatus.cloudAvailable}
        />

        {/* Session Comparison Section */}
        <SessionComparisonSection cloudAvailable={syncStatus.cloudAvailable} />

        {/* Personal Map Section */}
        <PersonalMapSection
          history={history}
          analyzePersonalMap={analyzePersonalMap}
        />

        {/* Value Constellation Section */}
        <ValueConstellationSection history={history} />

        {/* Orientation Field Section */}
        <OrientationFieldSection history={history} />

        {/* Collective Value Map Section */}
        <CollectiveValueMapSection history={history} />

        {/* Global Value Field Section */}
        <GlobalValueFieldSection
          globalStats={globalStats}
          resetGlobalStats={resetGlobalStats}
        />

        {/* Global Trend Section */}
        <GlobalTrendSection trendHistory={trendHistory} />

        {/* Weekly Summary Section */}
        <WeeklySummarySection trendHistory={trendHistory} globalStats={globalStats} />

        {/* Share Card Modal */}
        {showShareCard && decisionResult && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-3xl p-6 max-w-md w-full">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Share Card Preview</h3>
                <button
                  onClick={() => setShowShareCard(false)}
                  className="text-muted-foreground hover:text-foreground text-xl"
                >
                  x
                </button>
              </div>

              {/* Share Card Content */}
              <div 
                ref={shareCardRef}
                className="bg-gradient-to-br from-indigo-50 via-white to-purple-50 rounded-2xl p-6 border border-indigo-100"
                style={{ direction: 'rtl' }}
              >
                {/* Header */}
                <div className="text-center mb-4">
                  <h4 className="text-xl font-bold text-indigo-600">Philos Orientation</h4>
                  <p className="text-xs text-muted-foreground">Mental Navigation System</p>
                </div>

                {/* Action */}
                <div className="bg-white rounded-xl p-4 mb-3 text-center">
                  <p className="text-xs text-muted-foreground mb-1">Action</p>
                  <p className="text-lg font-semibold text-foreground">{decisionResult.action}</p>
                </div>

                {/* Decision Result */}
                <div className={`rounded-xl p-4 mb-3 text-center ${
                  decisionResult.decision === 'Allowed' 
                    ? 'bg-green-100' 
                    : 'bg-red-100'
                }`}>
                  <p className="text-xs text-muted-foreground mb-1">Decision</p>
                  <p className={`text-2xl font-bold ${
                    decisionResult.decision === 'Allowed' 
                      ? 'text-green-600' 
                      : 'text-red-600'
                  }`}>
                    {decisionResult.decision === 'Allowed' ? 'Allowed' : 'Blocked'}
                  </p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-2 mb-3">
                  <div className="bg-white rounded-xl p-3 text-center">
                    <p className="text-xs text-muted-foreground">Balance</p>
                    <p className={`text-xl font-bold ${
                      balanceScore >= 70 ? 'text-green-600' : balanceScore >= 40 ? 'text-yellow-500' : 'text-red-500'
                    }`}>{balanceScore}</p>
                  </div>
                  <div className="bg-white rounded-xl p-3 text-center">
                    <p className="text-xs text-muted-foreground">Trajectory</p>
                    <p className="text-sm font-bold text-purple-600">{getTrajectoryDirection()}</p>
                  </div>
                </div>

                {/* Projection */}
                <div className="bg-white rounded-xl p-3 text-center">
                  <p className="text-xs text-muted-foreground mb-1">Projection</p>
                  <p className="text-sm font-medium text-foreground">
                    order {decisionResult.projection.chaos_order} | collective {decisionResult.projection.ego_collective}
                  </p>
                </div>

                {/* Footer */}
                <div className="text-center mt-4 pt-3 border-t border-indigo-100">
                  <p className="text-xs text-muted-foreground">philos-orientation.app</p>
                </div>
              </div>

              {/* Download Button */}
              <button
                onClick={downloadShareCard}
                className="w-full px-4 py-3 bg-green-500 hover:bg-green-600 text-white rounded-xl font-medium transition-all flex items-center justify-center gap-2 mt-4"
              >
                <span>Download Image</span>
              </button>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-xs text-muted-foreground pt-4">
          <p>Interactive Decision Engine</p>
          <p className="mt-1">Deploy - test with real decisions</p>
        </div>

      </div>
    </div>
  );
}
