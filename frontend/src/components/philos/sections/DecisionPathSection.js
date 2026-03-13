import { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Direction colors matching the rest of the app
const directionColors = {
  recovery: { fill: '#3b82f6', bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700' },
  order: { fill: '#6366f1', bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-700' },
  contribution: { fill: '#22c55e', bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700' },
  exploration: { fill: '#f59e0b', bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700' }
};

const directionLabels = {
  recovery: 'Recovery',
  order: 'Order',
  contribution: 'Contribution',
  exploration: 'Exploration'
};

// Icons for each drift type
const DriftIcon = ({ driftType }) => {
  if (driftType === 'harm') {
    return (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    );
  }
  if (driftType === 'avoidance') {
    return (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
      </svg>
    );
  }
  if (driftType === 'isolation') {
    return (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    );
  }
  if (driftType === 'rigidity') {
    return (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
      </svg>
    );
  }
  // Positive state
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
};

export default function DecisionPathSection({ userId, onActionFollowed }) {
  const [pathData, setPathData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [actionCompleted, setActionCompleted] = useState(false);
  const [sessionKey, setSessionKey] = useState(null);

  // Get user ID from localStorage if not provided (use same key as cloudSync.js)
  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  // Check if action was already completed this session
  useEffect(() => {
    const completedKey = localStorage.getItem('philos_path_completed');
    const storedSession = localStorage.getItem('philos_path_session');
    
    if (completedKey && storedSession) {
      setActionCompleted(true);
      setSessionKey(storedSession);
    }
  }, []);

  // Fetch decision path
  useEffect(() => {
    const fetchDecisionPath = async () => {
      if (!effectiveUserId) return;
      
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/decision-path/${effectiveUserId}`);
        
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            setPathData(data);
            
            // Store session ID to maintain consistency
            if (data.session_id) {
              const existingSession = localStorage.getItem('philos_path_session');
              if (!existingSession || existingSession !== data.session_id) {
                // New session - reset completion
                localStorage.setItem('philos_path_session', data.session_id);
                localStorage.removeItem('philos_path_completed');
                setActionCompleted(false);
              }
            }
          }
        }
      } catch (error) {
        console.log('Could not fetch decision path:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDecisionPath();
  }, [effectiveUserId]);

  // Handle marking action as complete
  const handleActionComplete = () => {
    setActionCompleted(true);
    localStorage.setItem('philos_path_completed', 'true');
    
    if (onActionFollowed && pathData) {
      onActionFollowed({
        recommended_direction: pathData.recommended_direction,
        concrete_action: pathData.concrete_action,
        drift_type: pathData.drift_type,
        followed: true,
        timestamp: new Date().toISOString()
      });
    }
  };

  // Handle refreshing for new action
  const handleRefresh = () => {
    localStorage.removeItem('philos_path_session');
    localStorage.removeItem('philos_path_completed');
    setActionCompleted(false);
    setPathData(null);
    
    // Trigger refetch
    const fetchNew = async () => {
      if (!effectiveUserId) return;
      setLoading(true);
      try {
        const response = await fetch(`${API_URL}/api/decision-path/${effectiveUserId}`);
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            setPathData(data);
            localStorage.setItem('philos_path_session', data.session_id);
          }
        }
      } catch (error) {
        console.log('Refresh error:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchNew();
  };

  if (loading && !pathData) {
    return (
      <section className="bg-white rounded-3xl p-6 shadow-sm border border-border animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </section>
    );
  }

  if (!pathData) {
    return null;
  }

  const colors = directionColors[pathData.recommended_direction] || directionColors.recovery;
  const isDrift = !!pathData.drift_type;

  return (
    <section 
      className={`rounded-3xl p-5 shadow-sm border transition-all duration-300 ${
        isDrift 
          ? 'bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200' 
          : `bg-gradient-to-br ${colors.bg} ${colors.border}`
      }`}
      data-testid="decision-path-section"
    >
      {/* Header */}
      <div className="flex items-start gap-3 mb-4">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
          isDrift ? 'bg-amber-100 text-amber-600' : `bg-white/80 ${colors.text}`
        }`}>
          <DriftIcon driftType={pathData.drift_type} />
        </div>
        
        <div className="flex-1">
          <h3 className={`text-lg font-bold ${isDrift ? 'text-amber-800' : colors.text}`} data-testid="path-headline">
            {pathData.headline}
          </h3>
          <p className={`text-sm mt-0.5 ${isDrift ? 'text-amber-700' : colors.text} opacity-80`}>
            {pathData.recommended_step}
          </p>
        </div>
      </div>

      {/* Concrete Action Card */}
      <div 
        className={`p-4 rounded-2xl border-2 border-dashed transition-all duration-300 ${
          actionCompleted 
            ? 'bg-green-50 border-green-300' 
            : 'bg-white/60 border-gray-300'
        }`}
        data-testid="action-card"
      >
        {/* Direction badge */}
        <div className="flex items-center justify-between mb-2">
          <span 
            className={`text-xs px-2 py-1 rounded-full font-medium ${colors.bg} ${colors.text}`}
            style={{ backgroundColor: `${directionColors[pathData.recommended_direction]?.fill}20` }}
          >
            {directionLabels[pathData.recommended_direction] || pathData.recommended_direction}
          </span>
          
          {actionCompleted && (
            <span className="text-xs text-green-600 flex items-center gap-1">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Done
            </span>
          )}
        </div>
        
        {/* Action text */}
        <p className={`text-base font-medium ${actionCompleted ? 'text-green-700 line-through opacity-70' : 'text-gray-800'}`} data-testid="concrete-action">
          {pathData.concrete_action}
        </p>
        
        {/* Action button */}
        {!actionCompleted ? (
          <button
            onClick={handleActionComplete}
            className={`mt-3 w-full py-2.5 px-4 rounded-xl font-medium transition-all duration-200 ${
              isDrift 
                ? 'bg-amber-500 hover:bg-amber-600 text-white' 
                : 'bg-white hover:bg-gray-50 text-gray-700 border border-gray-300'
            }`}
            data-testid="complete-action-btn"
          >
            I did it ✓
          </button>
        ) : (
          <div className="mt-3 text-center">
            <p className="text-sm text-green-600 mb-2">Excellent! Keep going.</p>
            <button
              onClick={handleRefresh}
              className="text-xs text-gray-500 hover:text-gray-700 underline"
              data-testid="refresh-action-btn"
            >
              Get new recommendation
            </button>
          </div>
        )}
      </div>

      {/* Theory basis (collapsed) */}
      {pathData.theory_basis && (
        <details className="mt-3">
          <summary className={`text-xs cursor-pointer ${isDrift ? 'text-amber-600' : 'text-gray-500'} hover:underline`}>
            Why is this recommended?
          </summary>
          <p className={`text-xs mt-2 p-2 rounded-lg ${isDrift ? 'bg-amber-100/50 text-amber-700' : 'bg-white/50 text-gray-600'}`} data-testid="theory-basis">
            {pathData.theory_basis}
          </p>
        </details>
      )}
    </section>
  );
}
