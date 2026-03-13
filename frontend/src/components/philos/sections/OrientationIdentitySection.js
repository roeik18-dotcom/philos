import { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Direction colors
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

// Identity icons
const IdentityIcon = ({ identityType, isWarning }) => {
  if (isWarning) {
    return (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    );
  }
  
  switch (identityType) {
    case 'recovery_dominant':
      return (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      );
    case 'order_builder':
      return (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      );
    case 'contribution_oriented':
      return (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      );
    case 'exploration_driven':
      return (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      );
    case 'recovery_to_contribution':
      return (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
        </svg>
      );
    case 'drifting_from_order':
      return (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
        </svg>
      );
    case 'balanced':
      return (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
        </svg>
      );
    default:
      return (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      );
  }
};

// Momentum indicator
const MomentumBadge = ({ momentum }) => {
  const momentumConfig = {
    stabilizing: { label: 'stabilizing', color: 'bg-green-100 text-green-700' },
    drifting: { label: 'drifting', color: 'bg-amber-100 text-amber-700' },
    shifting: { label: 'changing', color: 'bg-violet-100 text-violet-700' },
    stable: { label: 'Stable', color: 'bg-gray-100 text-gray-600' }
  };
  
  const config = momentumConfig[momentum] || momentumConfig.stable;
  
  return (
    <span className={`text-[10px] px-2 py-0.5 rounded-full ${config.color}`}>
      {config.label}
    </span>
  );
};

export default function OrientationIdentitySection({ userId }) {
  const [identityData, setIdentityData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState(false);

  // Get user ID from localStorage if not provided
  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  // Fetch identity data
  useEffect(() => {
    const fetchIdentity = async () => {
      if (!effectiveUserId) return;
      
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/orientation/identity/${effectiveUserId}`);
        
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            setIdentityData(data);
          }
        }
      } catch (error) {
        console.log('Could not fetch identity:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchIdentity();
  }, [effectiveUserId]);

  if (loading && !identityData) {
    return (
      <section className="bg-white rounded-3xl p-5 shadow-sm border border-border animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-3"></div>
        <div className="h-4 bg-gray-200 rounded w-2/3"></div>
      </section>
    );
  }

  if (!identityData) {
    return null;
  }

  const isWarning = identityData.is_warning_state;
  const dominantColor = directionColors[identityData.dominant_direction] || directionColors.recovery;

  return (
    <section 
      className={`rounded-3xl p-5 shadow-sm border transition-all duration-300 ${
        isWarning 
          ? 'bg-gradient-to-br from-red-50 to-orange-50 border-red-200' 
          : `bg-gradient-to-br from-white to-gray-50 border-gray-200`
      }`}
      data-testid="orientation-identity-section"
    >
      {/* Header */}
      <div className="flex items-start gap-3">
        {/* Identity Icon */}
        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0 ${
          isWarning 
            ? 'bg-red-100 text-red-600' 
            : identityData.dominant_direction 
              ? `${dominantColor.bg} ${dominantColor.text}`
              : 'bg-gray-100 text-gray-600'
        }`}>
          <IdentityIcon identityType={identityData.identity_type} isWarning={isWarning} />
        </div>
        
        <div className="flex-1 min-w-0">
          {/* Identity Label */}
          <div className="flex items-center gap-2 flex-wrap">
            <h3 
              className={`text-lg font-bold ${isWarning ? 'text-red-800' : 'text-gray-800'}`}
              data-testid="identity-label"
            >
              {identityData.identity_label}
            </h3>
            {identityData.momentum && (
              <MomentumBadge momentum={identityData.momentum} />
            )}
          </div>
          
          {/* Identity Description */}
          <p 
            className={`text-sm mt-1 ${isWarning ? 'text-red-700' : 'text-gray-600'}`}
            data-testid="identity-description"
          >
            {identityData.identity_description}
          </p>
        </div>
      </div>

      {/* Warning Banner for Avoidance Loop */}
      {isWarning && (
        <div 
          className="mt-4 p-3 rounded-xl bg-red-100 border border-red-200 flex items-start gap-2"
          data-testid="warning-banner"
        >
          <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <div>
            <p className="text-sm text-red-800 font-medium">It's okay to feel this way</p>
            <p className="text-xs text-red-700 mt-1">
              Avoidance is a natural response. The first step is to recognize it. The next step — create one small structure.
            </p>
          </div>
        </div>
      )}

      {/* Stats Row */}
      {identityData.total_actions > 0 && (
        <div className="mt-4 flex flex-wrap gap-3">
          {/* Dominant Direction */}
          {identityData.dominant_direction && (
            <div className="flex items-center gap-1.5">
              <div 
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: dominantColor.fill }}
              />
              <span className="text-xs text-gray-600">
                Leading direction: <span className="font-medium">{directionLabels[identityData.dominant_direction]}</span>
              </span>
            </div>
          )}
          
          {/* Time in Direction */}
          {identityData.time_in_direction > 0 && (
            <div className="flex items-center gap-1.5">
              <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-xs text-gray-600">
                {identityData.time_in_direction} days
              </span>
            </div>
          )}
          
          {/* Action Count */}
          <div className="flex items-center gap-1.5">
            <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span className="text-xs text-gray-600">
              {identityData.total_actions} actions
            </span>
          </div>
        </div>
      )}

      {/* Insight */}
      {identityData.insight && (
        <div 
          className={`mt-4 p-3 rounded-xl ${
            isWarning ? 'bg-white/60' : 'bg-gray-50'
          }`}
        >
          <p className={`text-sm ${isWarning ? 'text-red-700' : 'text-gray-700'}`} data-testid="identity-insight">
            {identityData.insight}
          </p>
        </div>
      )}

      {/* Expandable Details */}
      {identityData.direction_counts && Object.keys(identityData.direction_counts).length > 0 && (
        <details className="mt-3" open={expanded}>
          <summary 
            className="text-xs text-gray-500 cursor-pointer hover:text-gray-700"
            onClick={(e) => {
              e.preventDefault();
              setExpanded(!expanded);
            }}
          >
            {expanded ? 'Hide details' : 'Show details'}
          </summary>
          
          {expanded && (
            <div className="mt-3 space-y-2" data-testid="identity-details">
              {/* Direction Distribution */}
              <div className="text-[10px] text-gray-500 mb-2">Your actions distribution:</div>
              <div className="flex gap-1 h-3 rounded-full overflow-hidden bg-gray-100">
                {Object.entries(identityData.direction_counts)
                  .filter(([dir, count]) => count > 0 && ['recovery', 'order', 'contribution', 'exploration'].includes(dir))
                  .sort((a, b) => b[1] - a[1])
                  .map(([direction, count]) => {
                    const pct = (count / identityData.total_actions) * 100;
                    return (
                      <div 
                        key={direction}
                        className="h-full"
                        style={{ 
                          width: `${pct}%`,
                          backgroundColor: directionColors[direction]?.fill || '#9ca3af',
                          minWidth: pct > 0 ? '4px' : '0'
                        }}
                        title={`${directionLabels[direction]}: ${count}`}
                      />
                    );
                  })}
              </div>
              
              {/* Legend */}
              <div className="flex flex-wrap gap-2 mt-2">
                {Object.entries(identityData.direction_counts)
                  .filter(([dir, count]) => count > 0 && ['recovery', 'order', 'contribution', 'exploration'].includes(dir))
                  .sort((a, b) => b[1] - a[1])
                  .map(([direction, count]) => (
                    <div key={direction} className="flex items-center gap-1">
                      <div 
                        className="w-2 h-2 rounded-sm"
                        style={{ backgroundColor: directionColors[direction]?.fill || '#9ca3af' }}
                      />
                      <span className="text-[9px] text-gray-500">
                        {directionLabels[direction]} ({count})
                      </span>
                    </div>
                  ))}
              </div>
              
              {/* Avoidance Warning */}
              {identityData.avoidance_ratio > 20 && (
                <div className="mt-2 text-[10px] text-amber-600">
                  Avoidance ratio: {identityData.avoidance_ratio}%
                </div>
              )}
            </div>
          )}
        </details>
      )}
    </section>
  );
}
