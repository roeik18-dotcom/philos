// Decision replay state and actions
import { useState, useCallback } from 'react';
import { getUserId } from '../services/cloudSync';

/**
 * Decision replay hook
 * Manages: replayDecision, replayHistory, saveReplayMetadata, closeReplay
 */
export function useReplayState({ user }) {
  // Decision replay state
  const [replayDecision, setReplayDecision] = useState(null);
  const [replayHistory, setReplayHistory] = useState([]);

  // Handle decision replay - set the decision to replay
  const handleReplayDecision = useCallback((decision) => {
    setReplayDecision(decision);
    // Scroll to replay section when it appears
    setTimeout(() => {
      const replaySection = document.querySelector('[data-testid="decision-replay-section"]');
      if (replaySection) {
        replaySection.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  }, []);

  // Close replay section
  const closeReplay = useCallback(() => {
    setReplayDecision(null);
  }, []);

  // Save replay metadata
  const saveReplayMetadata = useCallback(async (replayData) => {
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
  }, [user]);

  return {
    replayDecision,
    setReplayDecision,
    replayHistory,
    handleReplayDecision,
    closeReplay,
    saveReplayMetadata
  };
}
