import { useMemo } from 'react';
import { 
  calculateCompassPosition, 
  calculateRecommendedArrow,
  compassPositions,
  directionColors,
  valueLabels 
} from '../../../services/recommendationService';

export default function OrientationCompassSection({ history, state }) {
  // Calculate current position using centralized theory-based function
  const currentPosition = useMemo(() => {
    return calculateCompassPosition(history, state);
  }, [history, state]);

  // Calculate trail positions (last 7 days)
  const trailPositions = useMemo(() => {
    if (!history || history.length === 0) return [];

    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);

    return history
      .filter(h => {
        if (!h.timestamp) return true;
        return new Date(h.timestamp) >= weekAgo;
      })
      .slice(0, 15)
      .map((h, idx) => {
        const basePos = compassPositions[h.value_tag] || { x: 50, y: 50 };
        return {
          x: basePos.x,
          y: basePos.y,
          valueTag: h.value_tag,
          opacity: Math.max(0.1, 1 - (idx * 0.06))
        };
      });
  }, [history]);

  // Calculate recommended direction arrow using theory
  const recommendedArrow = useMemo(() => {
    if (!currentPosition.valueTag) return null;
    return calculateRecommendedArrow(currentPosition.valueTag);
  }, [currentPosition]);

  // Hebrew labels for directions
  const directionLabels = {
    recovery: 'התאוששות',
    order: 'סדר',
    contribution: 'תרומה',
    exploration: 'חקירה'
  };

  return (
    <section 
      className="bg-white rounded-3xl p-6 shadow-sm border border-border"
      dir="rtl"
      data-testid="orientation-compass-section"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-foreground">מצפן התמצאות</h3>
        <p className="text-xs text-muted-foreground">המיקום הנוכחי שלך על מפת הכיוונים</p>
      </div>

      {/* Compass Grid */}
      <div className="relative w-full aspect-square max-w-xs mx-auto bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
        {/* Grid lines */}
        <div className="absolute top-1/2 left-0 right-0 h-px bg-gray-300"></div>
        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-300"></div>
        
        {/* Subtle grid */}
        <div className="absolute top-1/4 left-0 right-0 h-px bg-gray-200"></div>
        <div className="absolute top-3/4 left-0 right-0 h-px bg-gray-200"></div>
        <div className="absolute left-1/4 top-0 bottom-0 w-px bg-gray-200"></div>
        <div className="absolute left-3/4 top-0 bottom-0 w-px bg-gray-200"></div>

        {/* Axis Labels */}
        <span className="absolute top-1 left-1/2 -translate-x-1/2 text-[10px] text-gray-500 font-medium bg-gray-50 px-1">סדר</span>
        <span className="absolute bottom-1 left-1/2 -translate-x-1/2 text-[10px] text-gray-500 font-medium bg-gray-50 px-1">כאוס</span>
        <span className="absolute right-1 top-1/2 -translate-y-1/2 text-[10px] text-gray-500 font-medium bg-gray-50 px-1">קולקטיב</span>
        <span className="absolute left-1 top-1/2 -translate-y-1/2 text-[10px] text-gray-500 font-medium bg-gray-50 px-1">אגו</span>

        {/* Quadrant Labels */}
        <div className="absolute top-[15%] left-[15%] text-center opacity-40">
          <span className="text-[10px] text-indigo-600 font-medium">סדר</span>
        </div>
        <div className="absolute top-[15%] right-[15%] text-center opacity-40">
          <span className="text-[10px] text-green-600 font-medium">תרומה</span>
        </div>
        <div className="absolute bottom-[15%] left-[15%] text-center opacity-40">
          <span className="text-[10px] text-blue-600 font-medium">התאוששות</span>
        </div>
        <div className="absolute bottom-[15%] right-[15%] text-center opacity-40">
          <span className="text-[10px] text-amber-600 font-medium">חקירה</span>
        </div>

        {/* Trail */}
        {trailPositions.length > 1 && (
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {/* Trail line */}
            <polyline
              points={trailPositions.map(p => `${p.x}%,${p.y}%`).join(' ')}
              fill="none"
              stroke="#9ca3af"
              strokeWidth="1"
              strokeDasharray="3,3"
              opacity="0.5"
            />
            {/* Trail dots */}
            {trailPositions.slice(1).map((pos, idx) => (
              <circle
                key={idx}
                cx={`${pos.x}%`}
                cy={`${pos.y}%`}
                r="3"
                fill={directionColors[pos.valueTag]?.fill || '#9ca3af'}
                opacity={pos.opacity}
              />
            ))}
          </svg>
        )}

        {/* Recommended Direction Arrow */}
        {recommendedArrow && currentPosition.valueTag && (
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon points="0 0, 10 3.5, 0 7" fill="#22c55e" />
              </marker>
            </defs>
            <line
              x1={`${currentPosition.x}%`}
              y1={`${currentPosition.y}%`}
              x2={`${recommendedArrow.to.x}%`}
              y2={`${recommendedArrow.to.y}%`}
              stroke="#22c55e"
              strokeWidth="2"
              strokeDasharray="4,2"
              markerEnd="url(#arrowhead)"
              opacity="0.7"
            />
          </svg>
        )}

        {/* Current Position Dot */}
        <div
          className="absolute w-4 h-4 rounded-full border-2 border-white shadow-lg transition-all duration-500"
          style={{
            left: `${currentPosition.x}%`,
            top: `${currentPosition.y}%`,
            transform: 'translate(-50%, -50%)',
            backgroundColor: directionColors[currentPosition.valueTag] || '#6b7280'
          }}
          data-testid="compass-current-position"
        >
          {/* Pulse animation */}
          <div 
            className="absolute inset-0 rounded-full animate-ping"
            style={{ backgroundColor: directionColors[currentPosition.valueTag] || '#6b7280', opacity: 0.3 }}
          ></div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap justify-center gap-2">
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <div className="w-3 h-3 rounded-full bg-current border-2 border-white shadow"></div>
          <span>מיקום נוכחי</span>
        </div>
        {recommendedArrow && (
          <div className="flex items-center gap-1 text-xs text-green-600">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
            <span>כיוון מומלץ</span>
          </div>
        )}
        {trailPositions.length > 1 && (
          <div className="flex items-center gap-1 text-xs text-gray-400">
            <div className="w-4 border-t border-dashed border-gray-400"></div>
            <span>מסלול אחרון</span>
          </div>
        )}
      </div>

      {/* Current State Summary */}
      {currentPosition.valueTag && (
        <div className="mt-4 p-3 rounded-xl bg-gray-50 border border-gray-200 text-center">
          <p className="text-sm text-muted-foreground">
            הכיוון הנוכחי: 
            <span 
              className="font-bold mr-1"
              style={{ color: directionColors[currentPosition.valueTag]?.fill || '#6b7280' }}
            >
              {directionLabels[currentPosition.valueTag] || currentPosition.valueTag}
            </span>
          </p>
          {currentPosition.actionsAnalyzed && (
            <p className="text-[10px] text-muted-foreground mt-1">
              מבוסס על {currentPosition.actionsAnalyzed} פעולות ב-7 ימים אחרונים
            </p>
          )}
          {recommendedArrow && (
            <p className="text-xs text-green-600 mt-1">
              כיוון מאזן מומלץ: {directionLabels[recommendedArrow.direction]}
            </p>
          )}
        </div>
      )}

      {/* Empty State */}
      {!currentPosition.valueTag && (
        <div className="mt-4 p-4 rounded-xl bg-gray-50 border border-gray-200 text-center">
          <p className="text-sm text-muted-foreground">
            אין מספיק נתונים להצגת מיקום.
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            בצע פעולה ראשונה כדי להתחיל.
          </p>
        </div>
      )}
    </section>
  );
}
