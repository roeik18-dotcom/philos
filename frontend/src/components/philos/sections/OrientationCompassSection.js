import { useMemo, useState, useEffect } from 'react';
import { 
  calculateCompassPosition, 
  calculateRecommendedArrow,
  compassPositions,
  directionColors,
  valueLabels 
} from '../../../services/recommendationService';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function OrientationCompassSection({ history, state, userId }) {
  // State for collective field data
  const [collectiveData, setCollectiveData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch collective field data
  useEffect(() => {
    const fetchCollectiveField = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/api/orientation/field`);
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            setCollectiveData(data);
          }
        }
      } catch (error) {
        console.log('Could not fetch collective field:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCollectiveField();
  }, [history?.length]); // Refetch when history changes

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

  // Calculate drift from collective center
  const driftInfo = useMemo(() => {
    if (!collectiveData?.field_center || !currentPosition.valueTag) {
      return null;
    }
    
    const userX = currentPosition.x;
    const userY = currentPosition.y;
    const collectiveX = collectiveData.field_center.x;
    const collectiveY = collectiveData.field_center.y;
    
    // Calculate distance
    const distance = Math.sqrt(
      Math.pow(userX - collectiveX, 2) + Math.pow(userY - collectiveY, 2)
    );
    
    // Alignment score (0-100, higher = more aligned)
    const maxDistance = 70;
    const alignmentScore = Math.max(0, Math.round(100 - (distance / maxDistance * 100)));
    
    // Determine drift direction
    let driftDirection = null;
    const dx = userX - collectiveX;
    const dy = userY - collectiveY;
    
    if (Math.abs(dx) > 10 || Math.abs(dy) > 10) {
      if (dx < -10 && dy < -10) driftDirection = 'toward_order_ego';
      else if (dx > 10 && dy < -10) driftDirection = 'toward_order_collective';
      else if (dx < -10 && dy > 10) driftDirection = 'toward_chaos_ego';
      else if (dx > 10 && dy > 10) driftDirection = 'toward_chaos_collective';
      else if (dx < -10) driftDirection = 'toward_ego';
      else if (dx > 10) driftDirection = 'toward_collective';
      else if (dy < -10) driftDirection = 'toward_order';
      else if (dy > 10) driftDirection = 'toward_chaos';
    }
    
    return {
      distance: Math.round(distance),
      alignmentScore,
      driftDirection,
      dx,
      dy
    };
  }, [collectiveData, currentPosition]);

  // Generate insight text
  const insightText = useMemo(() => {
    if (!driftInfo) return null;
    
    if (driftInfo.alignmentScore > 70) {
      return 'אתה מיושר היטב עם השדה הקולקטיבי.';
    } else if (driftInfo.alignmentScore > 50) {
      return 'המיקום שלך קרוב למרכז השדה הקולקטיבי.';
    } else if (driftInfo.alignmentScore < 30) {
      return 'אתה רחוק ממרכז השדה הקולקטיבי.';
    } else {
      return 'יש מרחק בין המיקום שלך לבין מרכז השדה.';
    }
  }, [driftInfo]);

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
        <p className="text-xs text-muted-foreground">המיקום שלך מול השדה הקולקטיבי</p>
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

        {/* SVG Layer for Lines and Markers */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none">
          {/* Collective Center Zone (subtle circle) */}
          {collectiveData?.field_center && (
            <circle
              cx={`${collectiveData.field_center.x}%`}
              cy={`${collectiveData.field_center.y}%`}
              r="12%"
              fill="rgba(139, 92, 246, 0.08)"
              stroke="rgba(139, 92, 246, 0.3)"
              strokeWidth="1"
              strokeDasharray="4,2"
              data-testid="collective-zone"
            />
          )}

          {/* Drift Line (user to collective center) */}
          {collectiveData?.field_center && currentPosition.valueTag && driftInfo && driftInfo.distance > 5 && (
            <line
              x1={`${currentPosition.x}%`}
              y1={`${currentPosition.y}%`}
              x2={`${collectiveData.field_center.x}%`}
              y2={`${collectiveData.field_center.y}%`}
              stroke="rgba(139, 92, 246, 0.4)"
              strokeWidth="1"
              strokeDasharray="3,3"
              data-testid="drift-line"
            />
          )}

          {/* Trail line */}
          {trailPositions.length > 1 && (
            <polyline
              points={trailPositions.map(p => `${p.x}%,${p.y}%`).join(' ')}
              fill="none"
              stroke="#9ca3af"
              strokeWidth="1"
              strokeDasharray="3,3"
              opacity="0.5"
            />
          )}

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

          {/* Recommended Direction Arrow */}
          {recommendedArrow && currentPosition.valueTag && (
            <>
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
            </>
          )}
        </svg>

        {/* Collective Center Marker */}
        {collectiveData?.field_center && (
          <div
            className="absolute w-3 h-3 rounded-full border-2 border-violet-400 bg-violet-200 transition-all duration-500"
            style={{
              left: `${collectiveData.field_center.x}%`,
              top: `${collectiveData.field_center.y}%`,
              transform: 'translate(-50%, -50%)'
            }}
            data-testid="collective-center"
            title="מרכז השדה הקולקטיבי"
          />
        )}

        {/* Current Position Dot */}
        <div
          className="absolute w-4 h-4 rounded-full border-2 border-white shadow-lg transition-all duration-500"
          style={{
            left: `${currentPosition.x}%`,
            top: `${currentPosition.y}%`,
            transform: 'translate(-50%, -50%)',
            backgroundColor: directionColors[currentPosition.valueTag]?.fill || '#6b7280'
          }}
          data-testid="compass-current-position"
        >
          {/* Pulse animation */}
          <div 
            className="absolute inset-0 rounded-full animate-ping"
            style={{ backgroundColor: directionColors[currentPosition.valueTag]?.fill || '#6b7280', opacity: 0.3 }}
          ></div>
        </div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap justify-center gap-2">
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <div className="w-3 h-3 rounded-full bg-gray-600 border-2 border-white shadow"></div>
          <span>מיקום שלך</span>
        </div>
        {collectiveData?.field_center && (
          <div className="flex items-center gap-1 text-xs text-violet-600">
            <div className="w-3 h-3 rounded-full bg-violet-200 border-2 border-violet-400"></div>
            <span>מרכז קולקטיבי</span>
          </div>
        )}
        {recommendedArrow && (
          <div className="flex items-center gap-1 text-xs text-green-600">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
            <span>כיוון מומלץ</span>
          </div>
        )}
      </div>

      {/* Alignment Score */}
      {driftInfo && currentPosition.valueTag && (
        <div className="mt-4 p-3 rounded-xl bg-gradient-to-r from-violet-50 to-purple-50 border border-violet-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-violet-800">התאמה לשדה</span>
            <span className={`text-lg font-bold ${
              driftInfo.alignmentScore > 70 ? 'text-green-600' :
              driftInfo.alignmentScore > 40 ? 'text-amber-600' :
              'text-red-500'
            }`}>
              {driftInfo.alignmentScore}%
            </span>
          </div>
          {/* Alignment Bar */}
          <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                driftInfo.alignmentScore > 70 ? 'bg-green-500' :
                driftInfo.alignmentScore > 40 ? 'bg-amber-500' :
                'bg-red-400'
              }`}
              style={{ width: `${driftInfo.alignmentScore}%` }}
            />
          </div>
          {/* Insight */}
          {insightText && (
            <p className="text-xs text-violet-700 mt-2" data-testid="drift-insight">
              {insightText}
            </p>
          )}
        </div>
      )}

      {/* Current State Summary */}
      {currentPosition.valueTag && (
        <div className="mt-3 p-3 rounded-xl bg-gray-50 border border-gray-200 text-center">
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

      {/* Collective Field Info */}
      {collectiveData && collectiveData.total_users > 0 && (
        <div className="mt-3 p-3 rounded-xl bg-violet-50/50 border border-violet-100 text-center">
          <p className="text-xs text-violet-700">
            {collectiveData.field_insight || `השדה הקולקטיבי מבוסס על ${collectiveData.total_users} משתמשים`}
          </p>
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
