export default function PersonalMapSection({ history, analyzePersonalMap }) {
  if (history.length < 3) return null;
  
  const analysis = analyzePersonalMap(history);
  
  return (
    <section className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-3xl p-5 shadow-sm border border-amber-200">
      <h3 className="text-lg font-semibold text-foreground mb-4">Personal Map</h3>
      
      {/* Direction Indicators */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-white/70 rounded-xl p-3 text-center">
          <p className="text-xs text-muted-foreground mb-1">Order vs Chaos</p>
          <div className="flex items-center justify-center gap-2">
            <span className="text-xs text-orange-500">chaos</span>
            <div className="w-20 h-2 bg-gray-200 rounded-full relative">
              <div 
                className="absolute top-0 h-2 bg-blue-500 rounded-full transition-all"
                style={{ 
                  left: '50%',
                  width: `${Math.abs(analysis.avgOrder || 0) / 2}%`,
                  marginLeft: analysis.avgOrder >= 0 ? '0' : `-${Math.abs(analysis.avgOrder || 0) / 2}%`
                }}
              />
              <div className="absolute top-1/2 left-1/2 w-1 h-3 bg-gray-400 -translate-x-1/2 -translate-y-1/2" />
            </div>
            <span className="text-xs text-blue-500">order</span>
          </div>
          <p className={`text-sm font-bold mt-1 ${
            analysis.dominantOrder === 'order' ? 'text-blue-600' : 
            analysis.dominantOrder === 'chaos' ? 'text-orange-600' : 'text-gray-500'
          }`}>
            {analysis.dominantOrder}
          </p>
        </div>
        
        <div className="bg-white/70 rounded-xl p-3 text-center">
          <p className="text-xs text-muted-foreground mb-1">Ego vs Collective</p>
          <div className="flex items-center justify-center gap-2">
            <span className="text-xs text-purple-500">ego</span>
            <div className="w-20 h-2 bg-gray-200 rounded-full relative">
              <div 
                className="absolute top-0 h-2 bg-green-500 rounded-full transition-all"
                style={{ 
                  left: '50%',
                  width: `${Math.abs(analysis.avgCollective || 0) / 2}%`,
                  marginLeft: analysis.avgCollective >= 0 ? '0' : `-${Math.abs(analysis.avgCollective || 0) / 2}%`
                }}
              />
              <div className="absolute top-1/2 left-1/2 w-1 h-3 bg-gray-400 -translate-x-1/2 -translate-y-1/2" />
            </div>
            <span className="text-xs text-green-500">collective</span>
          </div>
          <p className={`text-sm font-bold mt-1 ${
            analysis.dominantCollective === 'collective' ? 'text-green-600' : 
            analysis.dominantCollective === 'ego' ? 'text-purple-600' : 'text-gray-500'
          }`}>
            {analysis.dominantCollective}
          </p>
        </div>
      </div>

      {/* Top Value Tags */}
      {analysis.topValueTags.length > 0 && (
        <div className="bg-white/70 rounded-xl p-3 mb-4">
          <p className="text-xs text-muted-foreground mb-2">Top Values</p>
          <div className="flex flex-wrap gap-2">
            {analysis.topValueTags.map((item, idx) => (
              <span 
                key={idx}
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  item.tag === 'contribution' ? 'bg-green-100 text-green-700' :
                  item.tag === 'recovery' ? 'bg-blue-100 text-blue-700' :
                  item.tag === 'order' ? 'bg-indigo-100 text-indigo-700' :
                  item.tag === 'harm' ? 'bg-red-100 text-red-700' :
                  item.tag === 'avoidance' ? 'bg-gray-100 text-gray-700' :
                  'bg-gray-100 text-gray-600'
                }`}
              >
                {item.tag} ({item.count})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Mini Timeline */}
      <div className="bg-white/70 rounded-xl p-3 mb-4">
        <p className="text-xs text-muted-foreground mb-2">Decision Timeline (last {history.length})</p>
        <div className="flex gap-1 overflow-x-auto pb-1">
          {[...history].reverse().map((item, idx) => (
            <div 
              key={idx}
              className={`w-3 h-8 rounded-sm flex-shrink-0 ${
                item.decision === 'Allowed' ? 'bg-green-400' : 'bg-red-400'
              }`}
              style={{
                opacity: 0.4 + (idx / history.length) * 0.6
              }}
              title={`${item.time}: ${item.action}`}
            />
          ))}
        </div>
        <div className="flex justify-between text-xs text-muted-foreground mt-1">
          <span>oldest</span>
          <span>newest</span>
        </div>
      </div>

      {/* Value Graph */}
      <div className="bg-white/70 rounded-xl p-3 mb-4">
        <p className="text-xs text-muted-foreground mb-2">Value Graph</p>
        <div className="relative" style={{ height: '220px' }}>
          <svg width="100%" height="100%" viewBox="0 0 300 220" className="overflow-hidden">
            {/* Safe area boundary (for reference) */}
            <rect x="30" y="25" width="240" height="170" fill="none" stroke="#e5e7eb" strokeWidth="1" strokeDasharray="4 4" rx="8" />
            
            {/* Background zone labels */}
            <text x="150" y="18" textAnchor="middle" className="fill-indigo-500" fontSize="11" fontWeight="500">order</text>
            <text x="255" y="110" textAnchor="middle" className="fill-blue-500" fontSize="11" fontWeight="500">recovery</text>
            <text x="230" y="40" textAnchor="middle" className="fill-green-500" fontSize="11" fontWeight="500">contribution</text>
            <text x="150" y="212" textAnchor="middle" className="fill-red-500" fontSize="11" fontWeight="500">harm</text>
            <text x="45" y="110" textAnchor="middle" className="fill-gray-500" fontSize="11" fontWeight="500">avoidance</text>
            
            {/* Center crosshair */}
            <line x1="150" y1="85" x2="150" y2="135" stroke="#e5e7eb" strokeWidth="1" />
            <line x1="100" y1="110" x2="200" y2="110" stroke="#e5e7eb" strokeWidth="1" />
            <circle cx="150" cy="110" r="4" fill="#d1d5db" />
            
            {/* Connection lines */}
            {[...history].reverse().slice(0, 20).map((item, idx, arr) => {
              if (idx === 0) return null;
              const prev = arr[idx - 1];
              
              // Safe positioning function with padding
              const getPosition = (tag, index) => {
                const spread = Math.min(index * 2, 15);
                const jitter = ((index * 13) % 20) - 10;
                switch(tag) {
                  case 'order': return { x: 150 + jitter, y: 45 + spread };
                  case 'recovery': return { x: 220 + jitter/2, y: 90 + spread };
                  case 'contribution': return { x: 200 + jitter, y: 55 + spread };
                  case 'harm': return { x: 150 + jitter, y: 170 - spread };
                  case 'avoidance': return { x: 80 + jitter/2, y: 100 + spread };
                  default: return { x: 150 + jitter, y: 110 + (spread/2) };
                }
              };
              
              const prevPos = getPosition(prev.value_tag, idx - 1);
              const currPos = getPosition(item.value_tag, idx);
              
              return (
                <line
                  key={`line-${idx}`}
                  x1={prevPos.x}
                  y1={prevPos.y}
                  x2={currPos.x}
                  y2={currPos.y}
                  stroke="#94a3b8"
                  strokeWidth="1.5"
                  strokeDasharray="3 2"
                  opacity={0.3 + (idx / arr.length) * 0.5}
                />
              );
            })}
            
            {/* Decision nodes */}
            {[...history].reverse().slice(0, 20).map((item, idx) => {
              // Safe positioning function with padding
              const getPosition = (tag, index) => {
                const spread = Math.min(index * 2, 15);
                const jitter = ((index * 13) % 20) - 10;
                switch(tag) {
                  case 'order': return { x: 150 + jitter, y: 45 + spread };
                  case 'recovery': return { x: 220 + jitter/2, y: 90 + spread };
                  case 'contribution': return { x: 200 + jitter, y: 55 + spread };
                  case 'harm': return { x: 150 + jitter, y: 170 - spread };
                  case 'avoidance': return { x: 80 + jitter/2, y: 100 + spread };
                  default: return { x: 150 + jitter, y: 110 + (spread/2) };
                }
              };
              
              const pos = getPosition(item.value_tag, idx);
              const color = item.decision === 'Allowed' ? '#22c55e' : '#ef4444';
              const size = 7 + (idx / Math.max(history.length, 1)) * 5;
              
              return (
                <g key={`node-${idx}`} className="cursor-pointer">
                  {/* Outer glow */}
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={size + 3}
                    fill={color}
                    opacity={0.15}
                  />
                  {/* Main node */}
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={size}
                    fill={color}
                    opacity={0.8}
                    stroke="white"
                    strokeWidth="2"
                  >
                    <title>{`${item.time}: ${item.action}\nDecision: ${item.decision}\nBalance: ${item.balance_score}\nValue: ${item.value_tag}`}</title>
                  </circle>
                  {/* Node number */}
                  <text
                    x={pos.x}
                    y={pos.y + 3}
                    textAnchor="middle"
                    fontSize="8"
                    fill="white"
                    fontWeight="bold"
                  >
                    {idx + 1}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
        <div className="flex justify-center gap-4 mt-2 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-green-500"></span> Allowed
          </span>
          <span className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-red-500"></span> Blocked
          </span>
        </div>
      </div>

      {/* Your Pattern Summary */}
      {analysis.patternSummary.length > 0 && (
        <div className="bg-amber-100/50 border border-amber-200 rounded-xl p-4">
          <p className="text-sm font-semibold text-amber-800 mb-2">Your Pattern</p>
          <div className="space-y-1">
            {analysis.patternSummary.map((line, idx) => (
              <p key={idx} className="text-sm text-amber-700">{line}</p>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
