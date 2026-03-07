export default function CollectiveValueMapSection({ history }) {
  if (history.length < 3) return null;
  
  // Aggregate counts by value_tag
  const tagCounts = {
    contribution: 0,
    recovery: 0,
    harm: 0,
    order: 0,
    avoidance: 0
  };
  
  history.forEach(h => {
    if (tagCounts.hasOwnProperty(h.value_tag)) {
      tagCounts[h.value_tag]++;
    }
  });
  
  const totalDecisions = history.length;
  const maxCount = Math.max(...Object.values(tagCounts), 1);
  
  // Calculate collective direction
  const avgOrder = history.reduce((sum, h) => sum + h.chaos_order, 0) / totalDecisions;
  const avgCollective = history.reduce((sum, h) => sum + h.ego_collective, 0) / totalDecisions;
  
  const collectiveOrderDir = avgOrder > 10 ? 'order' : avgOrder < -10 ? 'chaos' : 'balanced';
  const collectiveCollectiveDir = avgCollective > 10 ? 'collective' : avgCollective < -10 ? 'ego' : 'balanced';
  
  // Find dominant value tag
  const dominantTag = Object.entries(tagCounts).sort((a, b) => b[1] - a[1])[0];
  const lowestTag = Object.entries(tagCounts).filter(([_, count]) => count > 0).sort((a, b) => a[1] - b[1])[0];
  
  // Build collective pattern summary
  const collectivePattern = [];
  if (collectiveOrderDir !== 'balanced' || collectiveCollectiveDir !== 'balanced') {
    collectivePattern.push(`This session cluster tends toward ${collectiveOrderDir} and ${collectiveCollectiveDir}.`);
  }
  if (dominantTag && dominantTag[1] > 0) {
    collectivePattern.push(`${dominantTag[0].charAt(0).toUpperCase() + dominantTag[0].slice(1)} is dominant.`);
  }
  if (lowestTag && lowestTag[0] !== dominantTag?.[0]) {
    collectivePattern.push(`${lowestTag[0].charAt(0).toUpperCase() + lowestTag[0].slice(1)} is low.`);
  }
  
  const tagColors = {
    contribution: { bg: 'bg-green-500', text: 'text-green-700', light: 'bg-green-100' },
    recovery: { bg: 'bg-blue-500', text: 'text-blue-700', light: 'bg-blue-100' },
    harm: { bg: 'bg-red-500', text: 'text-red-700', light: 'bg-red-100' },
    order: { bg: 'bg-indigo-500', text: 'text-indigo-700', light: 'bg-indigo-100' },
    avoidance: { bg: 'bg-gray-500', text: 'text-gray-700', light: 'bg-gray-100' }
  };
  
  return (
    <section className="bg-gradient-to-br from-teal-50 to-cyan-50 rounded-3xl p-5 shadow-sm border border-teal-200">
      <h3 className="text-lg font-semibold text-foreground mb-4">Collective Value Map</h3>
      
      {/* Collective Direction */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-white/70 rounded-xl p-3 text-center">
          <p className="text-xs text-muted-foreground mb-1">Collective Order</p>
          <p className={`text-lg font-bold ${
            collectiveOrderDir === 'order' ? 'text-blue-600' : 
            collectiveOrderDir === 'chaos' ? 'text-orange-600' : 'text-gray-500'
          }`}>
            {collectiveOrderDir}
          </p>
        </div>
        <div className="bg-white/70 rounded-xl p-3 text-center">
          <p className="text-xs text-muted-foreground mb-1">Collective Focus</p>
          <p className={`text-lg font-bold ${
            collectiveCollectiveDir === 'collective' ? 'text-green-600' : 
            collectiveCollectiveDir === 'ego' ? 'text-purple-600' : 'text-gray-500'
          }`}>
            {collectiveCollectiveDir}
          </p>
        </div>
      </div>

      {/* Value Tag Counts - Clustered Circles */}
      <div className="bg-white/70 rounded-xl p-4 mb-4">
        <p className="text-xs text-muted-foreground mb-3">Value Distribution ({totalDecisions} decisions)</p>
        <div className="flex justify-center items-end gap-3 h-24">
          {Object.entries(tagCounts).map(([tag, count]) => {
            const size = count > 0 ? 30 + (count / maxCount) * 50 : 20;
            const colors = tagColors[tag];
            return (
              <div key={tag} className="flex flex-col items-center gap-1">
                <div 
                  className={`${colors.bg} rounded-full flex items-center justify-center text-white font-bold transition-all`}
                  style={{ 
                    width: `${size}px`, 
                    height: `${size}px`,
                    opacity: count > 0 ? 0.9 : 0.3
                  }}
                >
                  {count}
                </div>
                <span className={`text-xs ${colors.text}`}>{tag}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Collective Pattern Summary */}
      {collectivePattern.length > 0 && (
        <div className="bg-teal-100/50 border border-teal-200 rounded-xl p-4">
          <p className="text-sm font-semibold text-teal-800 mb-2">Collective Pattern</p>
          <div className="space-y-1">
            {collectivePattern.map((line, idx) => (
              <p key={idx} className="text-sm text-teal-700">{line}</p>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
