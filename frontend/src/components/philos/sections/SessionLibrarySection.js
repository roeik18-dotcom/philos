import { useState, useEffect } from 'react';
import { listSavedSessions, getSessionById, deleteSession, saveSessionToLibrary } from '../../../services/cloudSync';

const valueLabels = {
  contribution: 'Contribution',
  recovery: 'Recovery',
  order: 'Order',
  harm: 'Harm',
  avoidance: 'Avoidance',
  neutral: 'Neutral'
};

const valueColors = {
  contribution: 'bg-green-100 text-green-700 border-green-200',
  recovery: 'bg-blue-100 text-blue-700 border-blue-200',
  order: 'bg-indigo-100 text-indigo-700 border-indigo-200',
  harm: 'bg-red-100 text-red-700 border-red-200',
  avoidance: 'bg-gray-100 text-gray-700 border-gray-200',
  neutral: 'bg-gray-100 text-gray-600 border-gray-200'
};

export default function SessionLibrarySection({ 
  currentHistory, 
  onLoadSession, 
  cloudAvailable 
}) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(null);

  // Load sessions on mount and when expanded
  useEffect(() => {
    if (expanded && cloudAvailable) {
      loadSessions();
    }
  }, [expanded, cloudAvailable]);

  const loadSessions = async () => {
    setLoading(true);
    const result = await listSavedSessions();
    if (result.success) {
      setSessions(result.sessions || []);
    }
    setLoading(false);
  };

  const handleSaveCurrentSession = async () => {
    if (!currentHistory || currentHistory.length < 3) {
      alert('Need at least 3 decisions to save a session');
      return;
    }
    
    setSaving(true);
    const result = await saveSessionToLibrary(currentHistory);
    if (result.success) {
      await loadSessions();
      alert('Session saved successfully!');
    } else {
      alert('Error saving session');
    }
    setSaving(false);
  };

  const handleLoadSession = async (sessionId) => {
    setLoading(true);
    const result = await getSessionById(sessionId);
    if (result.success && result.session) {
      onLoadSession(result.session.history);
      setExpanded(false);
    } else {
      alert('Error loading session');
    }
    setLoading(false);
  };

  const handleDeleteSession = async (sessionId) => {
    if (!window.confirm('Delete this session?')) return;
    
    setDeleting(sessionId);
    const result = await deleteSession(sessionId);
    if (result.success) {
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
    } else {
      alert('Error loading session');
    }
    setDeleting(null);
  };

  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return dateStr;
    }
  };

  if (!cloudAvailable) {
    return null;
  }

  return (
    <section className="bg-gradient-to-br from-sky-50 to-blue-50 rounded-3xl p-5 shadow-sm border border-sky-200" data-testid="session-library-section">
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div>
          <h3 className="text-lg font-semibold text-foreground">Session Library</h3>
          <p className="text-xs text-muted-foreground">
            {sessions.length > 0 ? `${sessions.length} saved sessions` : 'Load previous sessions'}
          </p>
        </div>
        <button className="text-2xl text-sky-600 transition-transform" style={{ transform: expanded ? 'rotate(180deg)' : 'none' }}>
          ▼
        </button>
      </div>
      
      {expanded && (
        <div className="mt-4 space-y-4">
          {/* Save Current Session Button */}
          <button
            onClick={handleSaveCurrentSession}
            disabled={saving || !currentHistory || currentHistory.length < 3}
            className="w-full px-4 py-3 bg-sky-600 hover:bg-sky-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all flex items-center justify-center gap-2"
            data-testid="save-session-btn"
          >
            {saving ? (
              <span className="animate-pulse">Saving...</span>
            ) : (
              <>
                <span>💾</span>
                <span>Save current session</span>
              </>
            )}
          </button>
          
          {currentHistory && currentHistory.length < 3 && (
            <p className="text-xs text-center text-muted-foreground">
              Need at least 3 decisions to save
            </p>
          )}
          
          {/* Session List */}
          {loading ? (
            <div className="text-center py-8">
              <span className="text-muted-foreground animate-pulse">Loading sessions...</span>
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-8 bg-white/50 rounded-xl">
              <p className="text-muted-foreground">No saved sessions</p>
              <p className="text-xs text-muted-foreground mt-1">Save the current session to get started</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
              {sessions.map(session => (
                <div 
                  key={session.session_id}
                  className="bg-white rounded-xl p-4 border border-sky-100 shadow-sm"
                  data-testid={`session-card-${session.session_id}`}
                >
                  {/* Session Header */}
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="text-sm font-semibold text-foreground">
                        {formatDate(session.date)}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {session.total_decisions} decisions
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${valueColors[session.dominant_value] || valueColors.neutral}`}>
                      {valueLabels[session.dominant_value] || session.dominant_value}
                    </span>
                  </div>
                  
                  {/* Session Metrics */}
                  <div className="grid grid-cols-2 gap-2 mb-3">
                    <div className="bg-sky-50 rounded-lg p-2 text-center">
                      <p className="text-xs text-muted-foreground">Order Drift</p>
                      <p className={`text-sm font-bold ${session.order_drift > 0 ? 'text-green-600' : session.order_drift < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                        {session.order_drift > 0 ? '+' : ''}{session.order_drift}
                      </p>
                    </div>
                    <div className="bg-sky-50 rounded-lg p-2 text-center">
                      <p className="text-xs text-muted-foreground">Social drift</p>
                      <p className={`text-sm font-bold ${session.collective_drift > 0 ? 'text-green-600' : session.collective_drift < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                        {session.collective_drift > 0 ? '+' : ''}{session.collective_drift}
                      </p>
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleLoadSession(session.session_id)}
                      disabled={loading}
                      className="flex-1 px-3 py-2 bg-sky-100 hover:bg-sky-200 text-sky-700 rounded-lg text-sm font-medium transition-all"
                      data-testid={`load-session-${session.session_id}`}
                    >
                      Open session
                    </button>
                    <button
                      onClick={() => handleDeleteSession(session.session_id)}
                      disabled={deleting === session.session_id}
                      className="px-3 py-2 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg text-sm transition-all"
                      data-testid={`delete-session-${session.session_id}`}
                    >
                      {deleting === session.session_id ? '...' : '🗑️'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* Refresh Button */}
          {sessions.length > 0 && (
            <button
              onClick={loadSessions}
              disabled={loading}
              className="w-full px-3 py-2 bg-sky-100 hover:bg-sky-200 text-sky-700 rounded-lg text-sm transition-all"
            >
              {loading ? 'Loading...' : 'Refresh list'}
            </button>
          )}
        </div>
      )}
    </section>
  );
}
