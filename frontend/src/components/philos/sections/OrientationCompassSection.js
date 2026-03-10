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
  const [historyData, setHistoryData] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Get user ID from localStorage if not provided
  const effectiveUserId = userId || localStorage.getItem('philos_anon_id');

  // Fetch collective field data, history, and comparison
  useEffect(() => {
    const fetchCollectiveField = async () => {
      try {
        setLoading(true);
        
        // Build fetch promises
        const fetchPromises = [
          fetch(`${API_URL}/api/orientation/field`),
          fetch(`${API_URL}/api/orientation/history`)
        ];
        
        // Add comparison fetch if we have a user ID
        if (effectiveUserId) {
          fetchPromises.push(fetch(`${API_URL}/api/orientation/compare/${effectiveUserId}`));
        }
        
        const responses = await Promise.all(fetchPromises);
        
        // Process field response
        if (responses[0].ok) {
          const data = await responses[0].json();
          if (data.success) {
            setCollectiveData(data);
          }
        }
        
        // Process history response
        if (responses[1].ok) {
          const data = await responses[1].json();
          if (data.success) {
            setHistoryData(data);
          }
        }
        
        // Process comparison response (if available)
        if (responses[2]?.ok) {
          const data = await responses[2].json();
          if (data.success) {
            setComparisonData(data);
          }
        }
      } catch (error) {
        console.log('Could not fetch collective field:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCollectiveField();
  }, [history?.length, effectiveUserId]); // Refetch when history changes

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
          {/* Arrow marker definitions */}
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
            <marker
              id="momentum-arrowhead"
              markerWidth="8"
              markerHeight="6"
              refX="7"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 8 3, 0 6" fill="#8b5cf6" />
            </marker>
          </defs>

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

          {/* Momentum Arrow (collective field movement) */}
          {collectiveData?.momentum_arrow?.from_x && collectiveData?.field_momentum !== 'stable' && (
            <line
              x1={`${collectiveData.momentum_arrow.from_x}%`}
              y1={`${collectiveData.momentum_arrow.from_y}%`}
              x2={`${collectiveData.momentum_arrow.to_x}%`}
              y2={`${collectiveData.momentum_arrow.to_y}%`}
              stroke="#8b5cf6"
              strokeWidth="2.5"
              markerEnd="url(#momentum-arrowhead)"
              opacity="0.8"
              data-testid="momentum-arrow"
            >
              {/* Animate the arrow */}
              <animate
                attributeName="stroke-dashoffset"
                values="20;0"
                dur="1.5s"
                repeatCount="indefinite"
              />
            </line>
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
        {collectiveData?.momentum_arrow?.from_x && collectiveData?.field_momentum !== 'stable' && (
          <div className="flex items-center gap-1 text-xs text-violet-600">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
            <span>מומנטום</span>
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

      {/* Momentum Indicator */}
      {collectiveData?.momentum_insight && (
        <div 
          className={`mt-3 p-3 rounded-xl border flex items-center gap-3 ${
            collectiveData.field_momentum === 'stabilizing' 
              ? 'bg-green-50 border-green-200' 
              : collectiveData.field_momentum === 'drifting'
              ? 'bg-amber-50 border-amber-200'
              : collectiveData.field_momentum === 'shifting'
              ? 'bg-violet-50 border-violet-200'
              : 'bg-gray-50 border-gray-200'
          }`}
          data-testid="momentum-indicator"
        >
          {/* Momentum Icon */}
          <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
            collectiveData.field_momentum === 'stabilizing' 
              ? 'bg-green-100' 
              : collectiveData.field_momentum === 'drifting'
              ? 'bg-amber-100'
              : collectiveData.field_momentum === 'shifting'
              ? 'bg-violet-100'
              : 'bg-gray-100'
          }`}>
            {collectiveData.field_momentum === 'stabilizing' && (
              <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
            {collectiveData.field_momentum === 'drifting' && (
              <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            )}
            {collectiveData.field_momentum === 'shifting' && (
              <svg className="w-4 h-4 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            )}
            {collectiveData.field_momentum === 'stable' && (
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            )}
          </div>
          
          {/* Momentum Text */}
          <div className="flex-1">
            <p className={`text-sm font-medium ${
              collectiveData.field_momentum === 'stabilizing' 
                ? 'text-green-700' 
                : collectiveData.field_momentum === 'drifting'
                ? 'text-amber-700'
                : collectiveData.field_momentum === 'shifting'
                ? 'text-violet-700'
                : 'text-gray-600'
            }`} data-testid="momentum-insight">
              {collectiveData.momentum_insight}
            </p>
            {collectiveData.momentum_strength > 0 && (
              <div className="mt-1.5 flex items-center gap-2">
                <span className="text-[10px] text-muted-foreground">עוצמה:</span>
                <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden max-w-[100px]">
                  <div 
                    className={`h-full rounded-full transition-all duration-500 ${
                      collectiveData.field_momentum === 'stabilizing' 
                        ? 'bg-green-400' 
                        : collectiveData.field_momentum === 'drifting'
                        ? 'bg-amber-400'
                        : 'bg-violet-400'
                    }`}
                    style={{ width: `${collectiveData.momentum_strength}%` }}
                  />
                </div>
                <span className="text-[10px] text-muted-foreground">{Math.round(collectiveData.momentum_strength)}%</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Historical Trend Sparkline (4 weeks) */}
      {historyData && historyData.weekly_snapshots?.length > 0 && (
        <div 
          className="mt-3 p-3 rounded-xl bg-gradient-to-r from-slate-50 to-gray-50 border border-slate-200"
          data-testid="field-history-section"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-700">מגמת השדה (4 שבועות)</span>
            {historyData.trend_type && historyData.trend_type !== 'stable' && (
              <span className={`text-xs px-2 py-0.5 rounded-full ${
                historyData.trend_type === 'stabilizing' 
                  ? 'bg-green-100 text-green-700'
                  : historyData.trend_type === 'drifting'
                  ? 'bg-amber-100 text-amber-700'
                  : 'bg-violet-100 text-violet-700'
              }`}>
                {historyData.trend_type === 'stabilizing' ? 'מתייצב' :
                 historyData.trend_type === 'drifting' ? 'נסחף' :
                 historyData.trend_direction ? `נע ל${directionLabels[historyData.trend_direction] || historyData.trend_direction}` : 'משתנה'}
              </span>
            )}
          </div>
          
          {/* Sparkline */}
          <div className="relative h-12 mt-2" data-testid="sparkline-container">
            <svg className="w-full h-full" viewBox="0 0 200 48" preserveAspectRatio="none">
              {/* Background grid lines */}
              <line x1="0" y1="12" x2="200" y2="12" stroke="#e5e7eb" strokeWidth="1" strokeDasharray="2,2" />
              <line x1="0" y1="24" x2="200" y2="24" stroke="#e5e7eb" strokeWidth="1" />
              <line x1="0" y1="36" x2="200" y2="36" stroke="#e5e7eb" strokeWidth="1" strokeDasharray="2,2" />
              
              {/* Sparkline path */}
              {historyData.sparkline_data?.length > 1 && (
                <>
                  {/* Fill area under line */}
                  <path
                    d={`M 0 ${48 - (historyData.sparkline_data[0] / 100 * 48)} 
                        ${historyData.sparkline_data.map((val, i) => 
                          `L ${(i / (historyData.sparkline_data.length - 1)) * 200} ${48 - (val / 100 * 48)}`
                        ).join(' ')}
                        L 200 48 L 0 48 Z`}
                    fill="url(#sparkline-gradient)"
                    opacity="0.3"
                  />
                  
                  {/* Line */}
                  <polyline
                    points={historyData.sparkline_data.map((val, i) => 
                      `${(i / (historyData.sparkline_data.length - 1)) * 200},${48 - (val / 100 * 48)}`
                    ).join(' ')}
                    fill="none"
                    stroke={
                      historyData.trend_type === 'stabilizing' ? '#22c55e' :
                      historyData.trend_type === 'drifting' ? '#f59e0b' :
                      '#8b5cf6'
                    }
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  
                  {/* Data points */}
                  {historyData.sparkline_data.map((val, i) => (
                    <circle
                      key={i}
                      cx={(i / (historyData.sparkline_data.length - 1)) * 200}
                      cy={48 - (val / 100 * 48)}
                      r="3"
                      fill={
                        historyData.trend_type === 'stabilizing' ? '#22c55e' :
                        historyData.trend_type === 'drifting' ? '#f59e0b' :
                        '#8b5cf6'
                      }
                      stroke="white"
                      strokeWidth="1.5"
                    />
                  ))}
                  
                  {/* Gradient definition */}
                  <defs>
                    <linearGradient id="sparkline-gradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={
                        historyData.trend_type === 'stabilizing' ? '#22c55e' :
                        historyData.trend_type === 'drifting' ? '#f59e0b' :
                        '#8b5cf6'
                      } />
                      <stop offset="100%" stopColor="white" />
                    </linearGradient>
                  </defs>
                </>
              )}
            </svg>
            
            {/* Week labels */}
            <div className="flex justify-between text-[9px] text-muted-foreground mt-1">
              {historyData.weekly_snapshots.map((week, i) => (
                <span key={i} className="text-center">
                  {week.week_label}
                </span>
              ))}
            </div>
          </div>
          
          {/* Weekly detail dots showing dominant direction */}
          <div className="flex justify-between mt-2 px-1">
            {historyData.weekly_snapshots.map((week, i) => (
              <div key={i} className="flex flex-col items-center">
                <div 
                  className="w-2 h-2 rounded-full"
                  style={{ 
                    backgroundColor: week.dominant_direction 
                      ? (directionColors[week.dominant_direction]?.fill || '#9ca3af')
                      : '#e5e7eb'
                  }}
                  title={week.dominant_direction ? directionLabels[week.dominant_direction] : 'אין נתונים'}
                />
                <span className="text-[8px] text-muted-foreground mt-0.5">
                  {week.total_actions > 0 ? week.total_actions : '-'}
                </span>
              </div>
            ))}
          </div>
          
          {/* Trend Insight */}
          {historyData.trend_insight && (
            <p className="text-xs text-slate-600 mt-3 text-center" data-testid="trend-insight">
              {historyData.trend_insight}
            </p>
          )}
        </div>
      )}

      {/* User Comparison Section */}
      {comparisonData && comparisonData.total_user_actions > 0 && (
        <div 
          className="mt-3 p-3 rounded-xl bg-gradient-to-r from-sky-50 to-cyan-50 border border-sky-200"
          data-testid="user-comparison-section"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-sky-800">המיקום שלך השבוע</span>
            <span className="text-xs text-sky-600">{comparisonData.total_user_actions} פעולות</span>
          </div>
          
          {/* Direction Percentile Bars */}
          <div className="space-y-2">
            {comparisonData.direction_percentiles
              .filter(dp => dp.user_count > 0)
              .sort((a, b) => b.percentile - a.percentile)
              .slice(0, 3)  // Show top 3 directions
              .map((dp, idx) => (
                <div key={dp.direction} className="flex items-center gap-2">
                  {/* Direction label */}
                  <span className="text-xs text-sky-700 w-16 text-left">
                    {directionLabels[dp.direction] || dp.direction}
                  </span>
                  
                  {/* Percentile bar */}
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-700 ${
                        dp.percentile >= 75 ? 'bg-sky-500' :
                        dp.percentile >= 50 ? 'bg-sky-400' :
                        'bg-sky-300'
                      }`}
                      style={{ width: `${dp.percentile}%` }}
                    />
                  </div>
                  
                  {/* Rank label */}
                  {dp.rank_label && (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full whitespace-nowrap ${
                      dp.percentile >= 90 ? 'bg-sky-100 text-sky-700 font-medium' :
                      dp.percentile >= 75 ? 'bg-sky-50 text-sky-600' :
                      'text-sky-500'
                    }`}>
                      {dp.rank_label}
                    </span>
                  )}
                </div>
              ))}
          </div>
          
          {/* Visual Position Indicator */}
          {comparisonData.dominant_direction && comparisonData.dominant_percentile > 0 && (
            <div className="mt-3 pt-3 border-t border-sky-200">
              <div className="flex items-center gap-2">
                {/* Small compass indicator */}
                <div className="relative w-10 h-10 bg-white rounded-lg border border-sky-200 flex-shrink-0">
                  {/* User position dot */}
                  <div 
                    className="absolute w-2 h-2 rounded-full"
                    style={{
                      left: '50%',
                      top: '50%',
                      transform: 'translate(-50%, -50%)',
                      backgroundColor: directionColors[comparisonData.dominant_direction]?.fill || '#0ea5e9'
                    }}
                  />
                  {/* Direction label */}
                  <span className="absolute bottom-0 left-1/2 -translate-x-1/2 text-[6px] text-sky-600">
                    {directionLabels[comparisonData.dominant_direction]?.slice(0, 3)}
                  </span>
                </div>
                
                {/* Comparison insight */}
                <p className="text-xs text-sky-700 flex-1" data-testid="comparison-insight">
                  {comparisonData.comparison_insight}
                </p>
              </div>
            </div>
          )}
          
          {/* Week Distribution Mini-Chart */}
          {comparisonData.week_comparison && Object.keys(comparisonData.week_comparison).length > 0 && (
            <div className="mt-3 pt-3 border-t border-sky-200">
              <div className="text-[10px] text-sky-600 mb-2">התפלגות השבוע שלך:</div>
              <div className="flex gap-1 h-4">
                {Object.entries(comparisonData.week_comparison)
                  .filter(([, pct]) => pct > 0)
                  .sort((a, b) => b[1] - a[1])
                  .map(([direction, pct]) => (
                    <div 
                      key={direction}
                      className="rounded-sm"
                      style={{ 
                        width: `${pct}%`,
                        backgroundColor: directionColors[direction]?.fill || '#9ca3af',
                        minWidth: pct > 0 ? '8px' : '0'
                      }}
                      title={`${directionLabels[direction]}: ${pct}%`}
                    />
                  ))}
              </div>
              {/* Legend for distribution */}
              <div className="flex flex-wrap gap-2 mt-2 justify-center">
                {Object.entries(comparisonData.week_comparison)
                  .filter(([, pct]) => pct > 0)
                  .sort((a, b) => b[1] - a[1])
                  .map(([direction, pct]) => (
                    <div key={direction} className="flex items-center gap-1">
                      <div 
                        className="w-2 h-2 rounded-sm"
                        style={{ backgroundColor: directionColors[direction]?.fill || '#9ca3af' }}
                      />
                      <span className="text-[9px] text-muted-foreground">
                        {directionLabels[direction]} {Math.round(pct)}%
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      )}

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
