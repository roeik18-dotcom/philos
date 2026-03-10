// Session management: global stats, trend history, snapshots
import { useState, useEffect, useCallback } from 'react';

// LocalStorage keys
const GLOBAL_STORAGE_KEY = 'philos_global_data';
const TREND_STORAGE_KEY = 'philos_trend_history';
const STORAGE_KEY = 'philos_session_data';

// Load global stats from localStorage
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

// Load trend history from localStorage
const loadTrendHistory = () => {
  try {
    const saved = localStorage.getItem(TREND_STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch (e) {
    console.error('Error loading trend history:', e);
  }
  return [];
};

/**
 * Session management hook
 * Manages: globalStats, trendHistory, session snapshots, reset functions
 */
export function useSessionManagement({ history, state, setHistory, setState, setDecisionResult }) {
  // Global and trend state
  const [globalStats, setGlobalStats] = useState(loadGlobalStats);
  const [trendHistory, setTrendHistory] = useState(loadTrendHistory);
  
  // UI state
  const [showShareCard, setShowShareCard] = useState(false);
  
  // Decision chain state
  const [parentDecision, setParentDecision] = useState(null);

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

  // Auto-save session snapshot when significant decisions are made
  useEffect(() => {
    if (history.length > 0 && history.length % 5 === 0) {
      saveSessionSnapshotSilent();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [history.length]);

  // Update global stats
  const updateGlobalStats = useCallback((valueTag) => {
    setGlobalStats(prev => ({
      ...prev,
      [valueTag]: (prev[valueTag] || 0) + 1,
      totalDecisions: prev.totalDecisions + 1
    }));
  }, []);

  // Save session snapshot silently
  const saveSessionSnapshotSilent = useCallback(() => {
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
  }, [history, trendHistory]);

  // Save session snapshot (public API)
  const saveSessionSnapshot = useCallback(() => {
    saveSessionSnapshotSilent();
  }, [saveSessionSnapshotSilent]);

  // Reset session
  const resetSession = useCallback(() => {
    if (window.confirm('Are you sure you want to reset the session? All data will be lost.')) {
      saveSessionSnapshot();
      localStorage.removeItem(STORAGE_KEY);
      setState({ physical_capacity: 50, chaos_order: 0, ego_collective: 0, gap_type: 'energy' });
      setDecisionResult(null);
      setHistory([]);
    }
  }, [saveSessionSnapshot, setState, setDecisionResult, setHistory]);

  // Reset global stats
  const resetGlobalStats = useCallback(() => {
    if (window.confirm('Reset all global statistics? This cannot be undone.')) {
      localStorage.removeItem(GLOBAL_STORAGE_KEY);
      localStorage.removeItem(TREND_STORAGE_KEY);
      setGlobalStats({
        contribution: 0, recovery: 0, harm: 0, order: 0, avoidance: 0,
        totalDecisions: 0, sessions: 0
      });
      setTrendHistory([]);
    }
  }, []);

  // Load session from library
  const loadSessionFromLibrary = useCallback((sessionHistory) => {
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
    }
  }, [setHistory, setState, setDecisionResult]);

  // Export session
  const exportSession = useCallback(() => {
    const sessionData = {
      timestamp: new Date().toISOString(),
      state: state,
      history: history,
      balanceScore: 100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective)),
      totalActions: history.length
    };
    const blob = new Blob([JSON.stringify(sessionData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `philos-session-${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [state, history]);

  // Handle adding a follow-up decision
  const handleAddFollowUp = useCallback((parentDecisionItem) => {
    setParentDecision(parentDecisionItem);
    // Scroll to action input
    const actionInput = document.querySelector('[data-testid="action-input"]');
    if (actionInput) {
      actionInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      actionInput.focus();
    }
  }, []);

  return {
    // Global and trend
    globalStats,
    setGlobalStats,
    trendHistory,
    setTrendHistory,
    
    // UI
    showShareCard,
    setShowShareCard,
    
    // Decision chains
    parentDecision,
    setParentDecision,
    handleAddFollowUp,
    
    // Actions
    updateGlobalStats,
    resetSession,
    resetGlobalStats,
    loadSessionFromLibrary,
    exportSession,
    saveSessionSnapshot
  };
}
