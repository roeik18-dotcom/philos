// Centralized Data Service for Philos Orientation
// Provides caching and deduplication for API calls

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Cache storage
const cache = {
  collectiveLayer: { data: null, timestamp: 0, loading: false, promise: null },
  collectiveTrends: { data: null, timestamp: 0, loading: false, promise: null },
  replayInsights: {} // Keyed by userId
};

// Cache TTL in milliseconds
const CACHE_TTL = {
  collectiveLayer: 30000,  // 30 seconds
  collectiveTrends: 60000, // 60 seconds
  replayInsights: 15000    // 15 seconds
};

// Check if cache is valid
const isCacheValid = (cacheEntry, ttl) => {
  if (!cacheEntry || !cacheEntry.data) return false;
  return (Date.now() - cacheEntry.timestamp) < ttl;
};

// Fetch collective layer data with caching
export const fetchCollectiveLayer = async (forceRefresh = false) => {
  const cacheEntry = cache.collectiveLayer;
  
  // Return cached data if valid
  if (!forceRefresh && isCacheValid(cacheEntry, CACHE_TTL.collectiveLayer)) {
    return { success: true, ...cacheEntry.data, fromCache: true };
  }
  
  // If already loading, return the existing promise
  if (cacheEntry.loading && cacheEntry.promise) {
    return cacheEntry.promise;
  }
  
  // Start new fetch
  cacheEntry.loading = true;
  cacheEntry.promise = (async () => {
    try {
      const response = await fetch(`${API_URL}/api/collective/layer`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      
      if (data.success) {
        cacheEntry.data = data;
        cacheEntry.timestamp = Date.now();
      }
      
      return data;
    } catch (error) {
      console.error('Failed to fetch collective layer:', error);
      // Return cached data on error if available
      if (cacheEntry.data) {
        return { ...cacheEntry.data, fromCache: true, stale: true };
      }
      return { success: false, error: error.message };
    } finally {
      cacheEntry.loading = false;
      cacheEntry.promise = null;
    }
  })();
  
  return cacheEntry.promise;
};

// Fetch collective trends data with caching
export const fetchCollectiveTrends = async (forceRefresh = false) => {
  const cacheEntry = cache.collectiveTrends;
  
  // Return cached data if valid
  if (!forceRefresh && isCacheValid(cacheEntry, CACHE_TTL.collectiveTrends)) {
    return { success: true, ...cacheEntry.data, fromCache: true };
  }
  
  // If already loading, return the existing promise
  if (cacheEntry.loading && cacheEntry.promise) {
    return cacheEntry.promise;
  }
  
  // Start new fetch
  cacheEntry.loading = true;
  cacheEntry.promise = (async () => {
    try {
      const response = await fetch(`${API_URL}/api/collective/trends`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      
      if (data.success) {
        cacheEntry.data = data;
        cacheEntry.timestamp = Date.now();
      }
      
      return data;
    } catch (error) {
      console.error('Failed to fetch collective trends:', error);
      if (cacheEntry.data) {
        return { ...cacheEntry.data, fromCache: true, stale: true };
      }
      return { success: false, error: error.message };
    } finally {
      cacheEntry.loading = false;
      cacheEntry.promise = null;
    }
  })();
  
  return cacheEntry.promise;
};

// Fetch replay insights for a user with caching
export const fetchReplayInsights = async (userId, forceRefresh = false) => {
  if (!userId) {
    return { success: false, error: 'No user ID provided', total_replays: 0 };
  }
  
  // Initialize cache for user if needed
  if (!cache.replayInsights[userId]) {
    cache.replayInsights[userId] = { data: null, timestamp: 0, loading: false, promise: null };
  }
  
  const cacheEntry = cache.replayInsights[userId];
  
  // Return cached data if valid
  if (!forceRefresh && isCacheValid(cacheEntry, CACHE_TTL.replayInsights)) {
    return { ...cacheEntry.data, fromCache: true };
  }
  
  // If already loading, return the existing promise
  if (cacheEntry.loading && cacheEntry.promise) {
    return cacheEntry.promise;
  }
  
  // Start new fetch
  cacheEntry.loading = true;
  cacheEntry.promise = (async () => {
    try {
      const response = await fetch(`${API_URL}/api/memory/replay-insights/${userId}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      
      if (data.success) {
        cacheEntry.data = data;
        cacheEntry.timestamp = Date.now();
      }
      
      return data;
    } catch (error) {
      console.error('Failed to fetch replay insights:', error);
      if (cacheEntry.data) {
        return { ...cacheEntry.data, fromCache: true, stale: true };
      }
      return { success: false, error: error.message, total_replays: 0 };
    } finally {
      cacheEntry.loading = false;
      cacheEntry.promise = null;
    }
  })();
  
  return cacheEntry.promise;
};

// Invalidate cache for replay insights (call after saving new replay)
export const invalidateReplayInsightsCache = (userId) => {
  if (userId && cache.replayInsights[userId]) {
    cache.replayInsights[userId].timestamp = 0;
  }
};

// Invalidate all collective caches (rarely needed)
export const invalidateCollectiveCache = () => {
  cache.collectiveLayer.timestamp = 0;
  cache.collectiveTrends.timestamp = 0;
};

// Get cache status (for debugging)
export const getCacheStatus = () => ({
  collectiveLayer: {
    hasData: !!cache.collectiveLayer.data,
    age: Date.now() - cache.collectiveLayer.timestamp,
    valid: isCacheValid(cache.collectiveLayer, CACHE_TTL.collectiveLayer)
  },
  collectiveTrends: {
    hasData: !!cache.collectiveTrends.data,
    age: Date.now() - cache.collectiveTrends.timestamp,
    valid: isCacheValid(cache.collectiveTrends, CACHE_TTL.collectiveTrends)
  },
  replayInsightsUsers: Object.keys(cache.replayInsights).length
});
