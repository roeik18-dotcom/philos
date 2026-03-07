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

export { getUserId };
