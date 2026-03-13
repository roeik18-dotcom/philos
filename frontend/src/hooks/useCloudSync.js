// Cloud sync and multi-device continuity
import { useState, useEffect, useRef, useCallback } from 'react';
import { 
  syncWithCloud, 
  getCloudData, 
  isCloudAvailable,
  getMemoryData,
  getFullUserData
} from '../services/cloudSync';

// LocalStorage keys
const LAST_SYNC_KEY = 'philos_last_sync';

/**
 * Cloud sync hook
 * Manages: syncStatus, cloud hydration, debounced sync, memory loading
 */
export function useCloudSync({
  user,
  history,
  setHistory,
  globalStats,
  setGlobalStats,
  trendHistory,
  setTrendHistory,
  learningHistory,
  setLearningHistory,
  adaptiveScores,
  setAdaptiveScores,
  setState
}) {
  // Sync state
  const [syncStatus, setSyncStatus] = useState({ 
    syncing: false, 
    lastSynced: null, 
    cloudAvailable: false,
    deviceSynced: false,
    syncMessage: ''
  });
  
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
  }, [history, globalStats, trendHistory, syncStatus.syncing, setHistory, setGlobalStats, setTrendHistory]);

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
  }, [setHistory, setGlobalStats, setTrendHistory]);

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
  }, [setLearningHistory, setAdaptiveScores]);

  // Multi-device continuity: Hydrate from cloud when user is authenticated
  useEffect(() => {
    const hydrateFromCloud = async () => {
      if (!user || hasHydratedFromCloud.current) return;
      
      setSyncStatus(prev => ({ ...prev, syncing: true, syncMessage: 'Loading data from cloud...' }));
      
      try {
        const fullData = await getFullUserData(user.id);
        
        if (fullData.success) {
          if (fullData.history && fullData.history.length > 0) {
            setHistory(fullData.history);
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
            syncMessage: 'Synced across devices'
          }));
        } else {
          setSyncStatus(prev => ({ 
            ...prev, 
            syncing: false, 
            syncMessage: 'Error loading data'
          }));
        }
      } catch (error) {
        console.error('Failed to hydrate from cloud:', error);
        setSyncStatus(prev => ({ 
          ...prev, 
          syncing: false, 
          syncMessage: 'Error syncing'
        }));
      }
    };
    
    hydrateFromCloud();
  }, [user, setHistory, setGlobalStats, setTrendHistory, setLearningHistory, setAdaptiveScores, setState]);

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [history, globalStats, trendHistory, syncStatus.cloudAvailable]);

  return {
    syncStatus,
    setSyncStatus,
    performCloudSync
  };
}
