// Cloud Sync Service for Philos Orientation
const API_URL = process.env.REACT_APP_BACKEND_URL;

// Generate or get user ID from localStorage
const getUserId = () => {
  let userId = localStorage.getItem('philos_user_id');
  if (!userId) {
    userId = 'user_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    localStorage.setItem('philos_user_id', userId);
  }
  return userId;
};

// Sync local data with cloud
export const syncWithCloud = async (localData) => {
  try {
    const userId = getUserId();
    
    const response = await fetch(`${API_URL}/api/philos/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        history: localData.history || [],
        global_stats: localData.globalStats || {},
        trend_history: localData.trendHistory || []
      })
    });
    
    if (!response.ok) {
      throw new Error(`Sync failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    return {
      success: true,
      history: result.history || [],
      globalStats: result.global_stats || {},
      trendHistory: result.trend_history || [],
      lastSynced: result.last_synced
    };
  } catch (error) {
    console.error('Cloud sync error:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

// Get cloud data only (without syncing)
export const getCloudData = async () => {
  try {
    const userId = getUserId();
    
    const response = await fetch(`${API_URL}/api/philos/sync/${userId}`);
    
    if (!response.ok) {
      throw new Error(`Fetch failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    return {
      success: true,
      history: result.history || [],
      globalStats: result.global_stats || {},
      trendHistory: result.trend_history || [],
      lastSynced: result.last_synced
    };
  } catch (error) {
    console.error('Cloud fetch error:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

// Check if cloud sync is available
export const isCloudAvailable = async () => {
  try {
    const response = await fetch(`${API_URL}/api/`, { method: 'GET' });
    return response.ok;
  } catch {
    return false;
  }
};

// Session Library Functions

// Save a session to the library
export const saveSessionToLibrary = async (history) => {
  try {
    const userId = getUserId();
    
    const response = await fetch(`${API_URL}/api/philos/sessions/save?user_id=${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(history)
    });
    
    if (!response.ok) {
      throw new Error(`Save failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Save session error:', error);
    return { success: false, error: error.message };
  }
};

// List all saved sessions
export const listSavedSessions = async () => {
  try {
    const userId = getUserId();
    
    const response = await fetch(`${API_URL}/api/philos/sessions/${userId}`);
    
    if (!response.ok) {
      throw new Error(`List failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('List sessions error:', error);
    return { success: false, sessions: [], error: error.message };
  }
};

// Get a specific session with full history
export const getSessionById = async (sessionId) => {
  try {
    const userId = getUserId();
    
    const response = await fetch(`${API_URL}/api/philos/sessions/${userId}/${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`Get session failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Get session error:', error);
    return { success: false, error: error.message };
  }
};

// Delete a saved session
export const deleteSession = async (sessionId) => {
  try {
    const userId = getUserId();
    
    const response = await fetch(`${API_URL}/api/philos/sessions/${userId}/${sessionId}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      throw new Error(`Delete failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Delete session error:', error);
    return { success: false, error: error.message };
  }
};


// ============================================================
// Persistent Memory Layer - Path Learning & Adaptive Engine
// ============================================================

// Save a decision to persistent storage
export const saveDecision = async (decisionData) => {
  try {
    const userId = getUserId();
    
    const response = await fetch(`${API_URL}/api/memory/decision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        ...decisionData
      })
    });
    
    if (!response.ok) {
      throw new Error(`Save decision failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Save decision error:', error);
    return { success: false, error: error.message };
  }
};

// Save a path selection to persistent storage
export const savePathSelection = async (pathData) => {
  try {
    const userId = getUserId();
    
    const response = await fetch(`${API_URL}/api/memory/path-selection`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        ...pathData
      })
    });
    
    if (!response.ok) {
      throw new Error(`Save path selection failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Save path selection error:', error);
    return { success: false, error: error.message };
  }
};

// Save path learning result to persistent storage
export const savePathLearning = async (learningData) => {
  try {
    const userId = getUserId();
    
    const response = await fetch(`${API_URL}/api/memory/path-learning`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        ...learningData
      })
    });
    
    if (!response.ok) {
      throw new Error(`Save path learning failed: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Save path learning error:', error);
    return { success: false, error: error.message };
  }
};

// Get memory data (learning history + adaptive scores) from cloud
export const getMemoryData = async () => {
  try {
    const userId = getUserId();
    
    const response = await fetch(`${API_URL}/api/memory/${userId}`);
    
    if (!response.ok) {
      throw new Error(`Get memory data failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    return {
      success: true,
      learningHistory: result.learning_history || [],
      adaptiveScores: result.adaptive_scores || {},
      lastSynced: result.last_synced
    };
  } catch (error) {
    console.error('Get memory data error:', error);
    return {
      success: false,
      learningHistory: [],
      adaptiveScores: {},
      error: error.message
    };
  }
};

// Sync local memory data with cloud
export const syncMemoryData = async (localLearningHistory) => {
  try {
    const userId = getUserId();
    
    const response = await fetch(`${API_URL}/api/memory/sync?user_id=${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(localLearningHistory)
    });
    
    if (!response.ok) {
      throw new Error(`Sync memory failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    return {
      success: true,
      learningHistory: result.learning_history || [],
      adaptiveScores: result.adaptive_scores || {},
      lastSynced: result.last_synced
    };
  } catch (error) {
    console.error('Sync memory error:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

export { getUserId };


// ============================================================
// Multi-Device Continuity - Full User Data Sync
// ============================================================

// Get ALL user data for multi-device continuity
export const getFullUserData = async (userId = null) => {
  try {
    const userIdToUse = userId || getUserId();
    
    const response = await fetch(`${API_URL}/api/user/full-data/${userIdToUse}`);
    
    if (!response.ok) {
      throw new Error(`Get full user data failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    return {
      success: true,
      history: result.history || [],
      globalStats: result.global_stats || {},
      trendHistory: result.trend_history || [],
      learningHistory: result.learning_history || [],
      adaptiveScores: result.adaptive_scores || {},
      savedSessions: result.saved_sessions || [],
      lastSynced: result.last_synced,
      deviceSyncStatus: result.device_sync_status || 'synced'
    };
  } catch (error) {
    console.error('Get full user data error:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

// Full sync of all user data from device to cloud
export const fullSyncUserData = async (localData, userId = null) => {
  try {
    const userIdToUse = userId || getUserId();
    
    const response = await fetch(`${API_URL}/api/user/full-sync/${userIdToUse}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        history: localData.history || [],
        global_stats: localData.globalStats || {},
        trend_history: localData.trendHistory || [],
        learning_history: localData.learningHistory || []
      })
    });
    
    if (!response.ok) {
      throw new Error(`Full sync failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    return {
      success: true,
      history: result.history || [],
      globalStats: result.global_stats || {},
      trendHistory: result.trend_history || [],
      learningHistory: result.learning_history || [],
      adaptiveScores: result.adaptive_scores || {},
      savedSessions: result.saved_sessions || [],
      lastSynced: result.last_synced,
      deviceSyncStatus: result.device_sync_status || 'synced'
    };
  } catch (error) {
    console.error('Full sync error:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

