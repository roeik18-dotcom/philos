import { useState } from 'react';

const valueLabels = {
  order: 'סדר',
  contribution: 'תרומה',
  recovery: 'התאוששות',
  avoidance: 'הימנעות',
  harm: 'נזק'
};

const valueColors = {
  order: '#6366f1',      // indigo
  contribution: '#22c55e', // green
  recovery: '#3b82f6',    // blue
  avoidance: '#6b7280',   // gray
  harm: '#ef4444'         // red
};

// Fixed positions for each value node in the constellation
const nodePositions = {
  order: { x: 150, y: 35 },        // top
  contribution: { x: 250, y: 70 }, // top-right
  recovery: { x: 270, y: 150 },    // right
  avoidance: { x: 30, y: 150 },    // left
  harm: { x: 150, y: 250 }         // bottom
};

export default function ValueConstellationSection({ history }) {
  const [hoveredNode, setHoveredNode] = useState(null);
  
  if (!history || history.length < 3) return null;
  
  // Count decisions by value tag
  const valueCounts = {
    order: 0,
    contribution: 0,
    recovery: 0,
    avoidance: 0,
    harm: 0
  };
  
  history.forEach(h => {
    if (valueCounts.hasOwnProperty(h.value_tag)) {
      valueCounts[h.value_tag]++;
    }
  });
  
  const totalDecisions = history.length;
  const maxCount = Math.max(...Object.values(valueCounts), 1);
  
  // Find dominant value
  const dominantValue = Object.entries(valueCounts)
    .sort((a, b) => b[1] - a[1])[0];
  
  // Build transition lines (chronological connections between decisions)
  const transitions = [];
  const transitionCounts = {};
  
  for (let i = 1; i < history.length; i++) {
    const fromTag = history[i].value_tag;
    const toTag = history[i - 1].value_tag;
    
    if (fromTag && toTag && nodePositions[fromTag] && nodePositions[toTag]) {
      const key = `${fromTag}-${toTag}`;
      transitionCounts[key] = (transitionCounts[key] || 0) + 1;
      
      if (!transitions.find(t => t.key === key)) {
        transitions.push({
          key,
          from: fromTag,
          to: toTag,
          fromPos: nodePositions[fromTag],
          toPos: nodePositions[toTag]
        });
      }
    }
  }
  
  // Calculate node sizes (min 20, max 50 based on count)
  const getNodeSize = (count) => {
    if (count === 0) return 15;
    return 20 + (count / maxCount) * 30;
  };
  
  // Get line opacity based on transition count
  const getLineOpacity = (key) => {
    const count = transitionCounts[key] || 1;
    return Math.min(0.3 + (count / Math.max(...Object.values(transitionCounts), 1)) * 0.5, 0.8);
  };
  
  const width = 300;
  const height = 300;
  
  return (
    <section className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-3xl p-5 shadow-sm border border-purple-200" data-testid="value-constellation-section">
      <h3 className="text-lg font-semibold text-foreground mb-2">מפת קונסטלציית ערכים</h3>
      <p className="text-xs text-muted-foreground mb-4">מבנה מרחבי של החלטות לפי ערכים</p>
      
      {/* Constellation SVG */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <svg 
          width="100%" 
          height={height} 
          viewBox={`0 0 ${width} ${height}`}
          className="overflow-visible"
        >
          {/* Background stars effect */}
          {[...Array(20)].map((_, i) => (
            <circle
              key={`star-${i}`}
              cx={20 + (i * 47) % 260}
              cy={15 + (i * 31) % 270}
              r="1"
              fill="#d1d5db"
              opacity="0.5"
            />
          ))}
          
          {/* Transition lines */}
          {transitions.map((t) => (
            <line
              key={t.key}
              x1={t.fromPos.x}
              y1={t.fromPos.y}
              x2={t.toPos.x}
              y2={t.toPos.y}
              stroke="#9ca3af"
              strokeWidth={1 + (transitionCounts[t.key] || 1) * 0.5}
              strokeDasharray="4 2"
              opacity={getLineOpacity(t.key)}
            />
          ))}
          
          {/* Center connection hub */}
          <circle cx={150} cy={140} r="3" fill="#e5e7eb" />
          
          {/* Value nodes */}
          {Object.entries(nodePositions).map(([tag, pos]) => {
            const count = valueCounts[tag];
            const size = getNodeSize(count);
            const isDominant = dominantValue && dominantValue[0] === tag;
            const isHovered = hoveredNode === tag;
            const percentage = totalDecisions > 0 ? Math.round((count / totalDecisions) * 100) : 0;
            
            return (
              <g 
                key={tag}
                onMouseEnter={() => setHoveredNode(tag)}
                onMouseLeave={() => setHoveredNode(null)}
                style={{ cursor: 'pointer' }}
              >
                {/* Dominant glow */}
                {isDominant && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={size + 12}
                    fill={valueColors[tag]}
                    opacity="0.15"
                  >
                    <animate
                      attributeName="r"
                      values={`${size + 8};${size + 15};${size + 8}`}
                      dur="2s"
                      repeatCount="indefinite"
                    />
                  </circle>
                )}
                
                {/* Hover ring */}
                {isHovered && (
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={size + 6}
                    fill="none"
                    stroke={valueColors[tag]}
                    strokeWidth="2"
                    opacity="0.5"
                  />
                )}
                
                {/* Main node */}
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={size}
                  fill={valueColors[tag]}
                  opacity={count > 0 ? 0.9 : 0.3}
                  stroke={isDominant ? '#fbbf24' : 'white'}
                  strokeWidth={isDominant ? 3 : 2}
                />
                
                {/* Count label */}
                <text
                  x={pos.x}
                  y={pos.y + 4}
                  textAnchor="middle"
                  fontSize="12"
                  fontWeight="bold"
                  fill="white"
                >
                  {count}
                </text>
                
                {/* Value label */}
                <text
                  x={pos.x}
                  y={pos.y + size + 14}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#6b7280"
                >
                  {valueLabels[tag]}
                </text>
                
                {/* Tooltip */}
                {isHovered && (
                  <g>
                    <rect
                      x={pos.x - 45}
                      y={pos.y - size - 45}
                      width="90"
                      height="38"
                      rx="6"
                      fill="white"
                      stroke="#e5e7eb"
                      strokeWidth="1"
                      filter="drop-shadow(0 2px 4px rgba(0,0,0,0.1))"
                    />
                    <text
                      x={pos.x}
                      y={pos.y - size - 30}
                      textAnchor="middle"
                      fontSize="11"
                      fontWeight="bold"
                      fill={valueColors[tag]}
                    >
                      {valueLabels[tag]}
                    </text>
                    <text
                      x={pos.x}
                      y={pos.y - size - 16}
                      textAnchor="middle"
                      fontSize="10"
                      fill="#6b7280"
                    >
                      {count} החלטות ({percentage}%)
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>
      
      {/* Legend & Stats */}
      <div className="grid grid-cols-2 gap-3">
        {/* Dominant Value */}
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-2">ערך דומיננטי</p>
          {dominantValue && dominantValue[1] > 0 ? (
            <div className="flex items-center gap-2">
              <div 
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: valueColors[dominantValue[0]] }}
              />
              <span className="text-sm font-bold text-foreground">
                {valueLabels[dominantValue[0]]}
              </span>
              <span className="text-xs text-muted-foreground">
                ({Math.round((dominantValue[1] / totalDecisions) * 100)}%)
              </span>
            </div>
          ) : (
            <span className="text-sm text-muted-foreground">אין נתונים</span>
          )}
        </div>
        
        {/* Transitions Count */}
        <div className="bg-white/70 rounded-xl p-3">
          <p className="text-xs text-muted-foreground mb-2">מעברים</p>
          <p className="text-lg font-bold text-foreground">{transitions.length}</p>
          <p className="text-xs text-muted-foreground">קשרים בין ערכים</p>
        </div>
      </div>
      
      {/* Value Distribution Bar */}
      <div className="bg-white/70 rounded-xl p-3 mt-3">
        <p className="text-xs text-muted-foreground mb-2">התפלגות ערכים</p>
        <div className="flex h-3 rounded-full overflow-hidden bg-gray-100">
          {Object.entries(valueCounts)
            .filter(([_, count]) => count > 0)
            .sort((a, b) => b[1] - a[1])
            .map(([tag, count]) => (
              <div
                key={tag}
                className="h-full transition-all"
                style={{
                  width: `${(count / totalDecisions) * 100}%`,
                  backgroundColor: valueColors[tag]
                }}
                title={`${valueLabels[tag]}: ${count}`}
              />
            ))}
        </div>
        <div className="flex justify-between mt-2 flex-wrap gap-2">
          {Object.entries(valueCounts)
            .filter(([_, count]) => count > 0)
            .sort((a, b) => b[1] - a[1])
            .map(([tag, count]) => (
              <div key={tag} className="flex items-center gap-1">
                <div 
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: valueColors[tag] }}
                />
                <span className="text-xs text-muted-foreground">{valueLabels[tag]}</span>
              </div>
            ))}
        </div>
      </div>
    </section>
  );
}
