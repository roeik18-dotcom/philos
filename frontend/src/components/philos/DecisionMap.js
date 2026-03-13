export default function DecisionMap({ state, decisionState, gapType, history = [], suggestion = null }) {
  if (!state) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        Set state values to see position in the decision map
      </div>
    );
  }

  // Transform values from -100/100 to 0-100% for positioning
  // ego_collective: -100 (left/ego) to +100 (right/collective)
  // chaos_order: -100 (top/chaos) to +100 (bottom/order)
  const xPosition = ((state.ego_collective + 100) / 200) * 100;
  const yPosition = ((state.chaos_order + 100) / 200) * 100;

  // Determine dot color based on decision status
  const isAllowed = decisionState?.result?.status === 'allowed';
  const dotColor = isAllowed ? '#22c55e' : '#ef4444'; // green-500 : red-500
  const dotBgColor = isAllowed ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)';

  // Convert history to trajectory points (reverse to get chronological order)
  const trajectoryPoints = [...history].reverse().map(item => ({
    x: ((item.ego_collective + 100) / 200) * 100,
    y: ((item.chaos_order + 100) / 200) * 100,
    decision: item.decision
  }));

  // Calculate arrow endpoint based on suggestion vector
  const arrowLength = 15; // percentage of map
  let arrowEndX = xPosition;
  let arrowEndY = yPosition;
  
  if (suggestion && !suggestion.inOptimalZone) {
    // Convert suggestion deltas to direction
    // suggestedCollective > 0 means move left (toward collective)
    // suggestedOrder > 0 means move down (toward order)
    const deltaX = suggestion.suggestedCollective > 0 ? -1 : (suggestion.suggestedCollective < 0 ? 1 : 0);
    const deltaY = suggestion.suggestedOrder > 0 ? 1 : (suggestion.suggestedOrder < 0 ? -1 : 0);
    
    // Normalize and scale the arrow
    const magnitude = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
    if (magnitude > 0) {
      arrowEndX = xPosition + (deltaX / magnitude) * arrowLength;
      arrowEndY = yPosition + (deltaY / magnitude) * arrowLength;
    }
  }

  return (
    <div className="space-y-4">
      {/* Grid Container */}
      <div className="relative w-full aspect-square bg-gradient-to-br from-muted/20 to-muted/40 rounded-2xl border-2 border-border p-4">
        {/* Grid Lines */}
        <svg className="absolute inset-4 w-[calc(100%-2rem)] h-[calc(100%-2rem)]" style={{ pointerEvents: 'none' }}>
          {/* Vertical center line */}
          <line
            x1="50%"
            y1="0"
            x2="50%"
            y2="100%"
            stroke="currentColor"
            strokeWidth="1"
            className="text-border"
            strokeDasharray="4 4"
          />
          {/* Horizontal center line */}
          <line
            x1="0"
            y1="50%"
            x2="100%"
            y2="50%"
            stroke="currentColor"
            strokeWidth="1"
            className="text-border"
            strokeDasharray="4 4"
          />
        </svg>

        {/* Trajectory Path SVG */}
        {trajectoryPoints.length > 1 && (
          <svg 
            className="absolute inset-4 w-[calc(100%-2rem)] h-[calc(100%-2rem)]" 
            style={{ pointerEvents: 'none' }}
          >
            {/* Trajectory line connecting points */}
            <polyline
              points={trajectoryPoints.map(p => `${p.x}%,${p.y}%`).join(' ')}
              fill="none"
              stroke="#9ca3af"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray="4 2"
              style={{ 
                opacity: 0.5,
                transition: 'all 0.5s ease-out'
              }}
            />
          </svg>
        )}

        {/* Suggestion Vector Arrow - using div positioning */}
        {suggestion && !suggestion.inOptimalZone && (arrowEndX !== xPosition || arrowEndY !== yPosition) && (
          <div
            className="absolute"
            style={{
              left: `calc(${xPosition}% + 1rem)`,
              top: `calc(${yPosition}% + 1rem)`,
              width: '0',
              height: '0',
              zIndex: 5
            }}
          >
            {/* Arrow line */}
            <svg
              width="100"
              height="100"
              style={{
                position: 'absolute',
                left: '-50px',
                top: '-50px',
                overflow: 'visible'
              }}
            >
              <defs>
                <marker
                  id="arrowhead"
                  markerWidth="8"
                  markerHeight="6"
                  refX="7"
                  refY="3"
                  orient="auto"
                >
                  <polygon
                    points="0 0, 8 3, 0 6"
                    fill="#3b82f6"
                  />
                </marker>
              </defs>
              <line
                x1="50"
                y1="50"
                x2={50 + (arrowEndX - xPosition) * 3}
                y2={50 + (arrowEndY - yPosition) * 3}
                stroke="#3b82f6"
                strokeWidth="3"
                strokeLinecap="round"
                markerEnd="url(#arrowhead)"
                style={{ opacity: 0.7 }}
              />
            </svg>
          </div>
        )}
        
        {/* Optimal zone glow */}
        {suggestion && suggestion.inOptimalZone && (
          <div
            className="absolute rounded-full"
            style={{
              left: `calc(${xPosition}% + 1rem - 20px)`,
              top: `calc(${yPosition}% + 1rem - 20px)`,
              width: '40px',
              height: '40px',
              border: '2px solid #22c55e',
              opacity: 0.5,
              animation: 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
              zIndex: 4
            }}
          />
        )}

        {/* Previous decision dots (trajectory) */}
        {trajectoryPoints.slice(0, -1).map((point, idx) => (
          <div
            key={idx}
            className="absolute w-3 h-3 rounded-full"
            style={{
              left: `${point.x}%`,
              top: `${point.y}%`,
              transform: 'translate(-50%, -50%)',
              backgroundColor: point.decision === 'Allowed' ? '#86efac' : '#fca5a5',
              opacity: 0.4 + (idx * 0.1),
              transition: 'all 0.3s ease-out',
              boxShadow: '0 0 4px rgba(0,0,0,0.2)'
            }}
          />
        ))}

        {/* Axes Labels (Hebrew RTL) */}
        <div className="absolute top-2 left-1/2 -translate-x-1/2 text-xs font-medium text-muted-foreground">
          chaos ↑
        </div>
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-xs font-medium text-muted-foreground">
          order ↓
        </div>
        <div className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-medium text-muted-foreground">
          ← ego
        </div>
        <div className="absolute left-2 top-1/2 -translate-y-1/2 text-xs font-medium text-muted-foreground">
          collective →
        </div>

        {/* Current Position Dot */}
        <div
          className="absolute w-8 h-8 -mt-4 -ml-4 z-10"
          style={{
            left: `${xPosition}%`,
            top: `${yPosition}%`,
            transition: 'left 0.5s cubic-bezier(0.34, 1.56, 0.64, 1), top 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)'
          }}
        >
          {/* Pulse effect */}
          <div 
            className="absolute inset-0 rounded-full animate-ping opacity-75" 
            style={{ backgroundColor: dotColor }}
          />
          {/* Main dot */}
          <div 
            className="relative w-full h-full rounded-full border-2 border-white shadow-lg flex items-center justify-center"
            style={{ backgroundColor: dotColor }}
          >
            {/* Gap type label */}
            {gapType && (
              <span 
                className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs font-medium whitespace-nowrap px-2 py-1 rounded-lg border"
                style={{ 
                  backgroundColor: dotBgColor,
                  color: dotColor,
                  borderColor: dotColor
                }}
              >
                {gapType}
              </span>
            )}
          </div>
        </div>

        {/* Crosshair at position */}
        <div
          className="absolute w-px h-full"
          style={{ 
            left: `${xPosition}%`,
            backgroundColor: dotColor,
            opacity: 0.2,
            transition: 'left 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)'
          }}
        />
        <div
          className="absolute h-px w-full"
          style={{ 
            top: `${yPosition}%`,
            backgroundColor: dotColor,
            opacity: 0.2,
            transition: 'top 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)'
          }}
        />
      </div>

      {/* Current Values Display */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-3 bg-muted/30 rounded-xl text-center">
          <div className="text-xs text-muted-foreground mb-1">ego ← → collective</div>
          <div className="text-lg font-bold text-foreground">
            {state.ego_collective > 0 ? '+' : ''}{state.ego_collective}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {state.ego_collective < -30 ? 'ego-focused' :
             state.ego_collective > 30 ? 'collective-focused' :
             'balanced'}
          </div>
        </div>

        <div className="p-3 bg-muted/30 rounded-xl text-center">
          <div className="text-xs text-muted-foreground mb-1">chaos ↑ ↓ order</div>
          <div className="text-lg font-bold text-foreground">
            {state.chaos_order > 0 ? '+' : ''}{state.chaos_order}
          </div>
          <div className="text-xs text-muted-foreground mt-1">
            {state.chaos_order < -30 ? 'chaotic' :
             state.chaos_order > 30 ? 'ordered' :
             'balanced'}
          </div>
        </div>
      </div>

      {/* Decision Status Indicator */}
      {decisionState && (
        <div 
          className="p-3 rounded-xl border-2 text-center font-medium"
          style={{
            backgroundColor: dotBgColor,
            borderColor: dotColor,
            color: dotColor
          }}
        >
          {isAllowed ? '✓ Decision Allowed' : '✗ Decision Blocked'}
        </div>
      )}
    </div>
  );
}
