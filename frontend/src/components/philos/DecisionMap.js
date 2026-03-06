export default function DecisionMap({ state, decisionState, gapType }) {
  if (!state) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        הגדר ערכי מצב כדי לראות מיקום במפת ההחלטה
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

        {/* Position Dot */}
        <div
          className="absolute w-8 h-8 -mt-4 -ml-4 transition-all duration-300 ease-out"
          style={{
            left: `${xPosition}%`,
            top: `${yPosition}%`
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
          className="absolute w-px h-full transition-all duration-300"
          style={{ 
            left: `${xPosition}%`,
            backgroundColor: dotColor,
            opacity: 0.2
          }}
        />
        <div
          className="absolute h-px w-full transition-all duration-300"
          style={{ 
            top: `${yPosition}%`,
            backgroundColor: dotColor,
            opacity: 0.2
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
