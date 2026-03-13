import { useMemo } from 'react';

// Hebrew value labels
const valueLabels = {
  contribution: 'Contribution',
  recovery: 'Recovery',
  order: 'Order',
  harm: 'Harm',
  avoidance: 'Avoidance'
};

// Value categories
const positiveValues = ['contribution', 'recovery', 'order'];
const negativeValues = ['harm', 'avoidance'];

// Insight types with icons and colors
const insightTypes = {
  recovery_chain: {
    icon: '🌱',
    color: 'bg-green-50 border-green-200 text-green-800',
    titleColor: 'text-green-700'
  },
  harm_chain: {
    icon: '⚠️',
    color: 'bg-red-50 border-red-200 text-red-800',
    titleColor: 'text-red-700'
  },
  correction: {
    icon: '🔄',
    color: 'bg-blue-50 border-blue-200 text-blue-800',
    titleColor: 'text-blue-700'
  },
  pattern: {
    icon: '🔁',
    color: 'bg-purple-50 border-purple-200 text-purple-800',
    titleColor: 'text-purple-700'
  },
  growth: {
    icon: '📈',
    color: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    titleColor: 'text-emerald-700'
  },
  warning: {
    icon: '🔻',
    color: 'bg-amber-50 border-amber-200 text-amber-800',
    titleColor: 'text-amber-700'
  }
};

export default function ChainInsightsSection({ history }) {
  // Analyze chains and generate insights
  const insights = useMemo(() => {
    if (!history || history.length < 2) return [];

    // Build chain data
    const items = history.map((item, idx) => ({
      ...item,
      id: item.id || `node_${idx}`
    }));

    // Create maps
    const nodeMap = {};
    items.forEach(item => {
      nodeMap[item.id] = { ...item, children: [] };
    });

    // Build relationships
    const chains = []; // Array of chain arrays
    const roots = [];
    
    items.forEach(item => {
      if (item.parent_decision_id && nodeMap[item.parent_decision_id]) {
        nodeMap[item.parent_decision_id].children.push(nodeMap[item.id]);
      } else {
        roots.push(nodeMap[item.id]);
      }
    });

    // Extract all chains (paths from root to leaves)
    const extractChains = (node, currentChain = []) => {
      const newChain = [...currentChain, node];
      
      if (!node.children || node.children.length === 0) {
        if (newChain.length >= 2) {
          chains.push(newChain);
        }
      } else {
        node.children.forEach(child => {
          extractChains(child, newChain);
        });
      }
    };

    roots.forEach(root => extractChains(root));

    // If no chains, check for any parent-child pairs
    if (chains.length === 0) {
      items.forEach(item => {
        if (item.parent_decision_id && nodeMap[item.parent_decision_id]) {
          chains.push([nodeMap[item.parent_decision_id], nodeMap[item.id]]);
        }
      });
    }

    const generatedInsights = [];

    // Analyze each chain
    chains.forEach((chain, chainIdx) => {
      if (chain.length < 2) return;

      const values = chain.map(n => n.value_tag);
      const firstValue = values[0];
      const lastValue = values[values.length - 1];
      
      // Check for recovery trajectory
      const startsNegative = negativeValues.includes(firstValue);
      const endsPositive = positiveValues.includes(lastValue);
      const startsPositive = positiveValues.includes(firstValue);
      const endsNegative = negativeValues.includes(lastValue);

      // Recovery chain: negative → positive
      if (startsNegative && endsPositive) {
        generatedInsights.push({
          type: 'recovery_chain',
          title: 'Recovery Path',
          text: `This chain shows direction correction from ${valueLabels[firstValue]} to ${valueLabels[lastValue]}`,
          chain: chain.map(n => n.action?.slice(0, 15)).join(' → '),
          priority: 1
        });
      }

      // Harm chain: positive → negative
      if (startsPositive && endsNegative) {
        generatedInsights.push({
          type: 'harm_chain',
          title: 'Risk Path',
          text: `This chain shows decline from ${valueLabels[firstValue]} to ${valueLabels[lastValue]}`,
          chain: chain.map(n => n.action?.slice(0, 15)).join(' → '),
          priority: 2
        });
      }

      // Check for mid-chain correction (negative in middle, then positive)
      for (let i = 1; i < values.length - 1; i++) {
        if (negativeValues.includes(values[i]) && positiveValues.includes(values[i + 1])) {
          generatedInsights.push({
            type: 'correction',
            title: 'Mid-path Correction',
            text: `Correction found: from ${valueLabels[values[i]]} to ${valueLabels[values[i + 1]]}`,
            chain: chain.slice(i, i + 2).map(n => n.action?.slice(0, 15)).join(' → '),
            priority: 3
          });
          break;
        }
      }

      // Check for consistent positive chain
      const allPositive = values.every(v => positiveValues.includes(v));
      if (allPositive && chain.length >= 2) {
        generatedInsights.push({
          type: 'growth',
          title: 'Growth Path',
          text: 'Consistent chain of positive decisions',
          chain: chain.map(n => n.action?.slice(0, 15)).join(' → '),
          priority: 4
        });
      }

      // Check for consistent negative chain (warning)
      const allNegative = values.every(v => negativeValues.includes(v));
      if (allNegative && chain.length >= 2) {
        generatedInsights.push({
          type: 'warning',
          title: 'Warning',
          text: 'Chain of problematic decisions — consider changing direction',
          chain: chain.map(n => n.action?.slice(0, 15)).join(' → '),
          priority: 1
        });
      }
    });

    // Check for repeated patterns across chains
    if (chains.length >= 2) {
      const patterns = {};
      chains.forEach(chain => {
        const pattern = chain.map(n => n.value_tag).join('→');
        patterns[pattern] = (patterns[pattern] || 0) + 1;
      });

      Object.entries(patterns).forEach(([pattern, count]) => {
        if (count >= 2) {
          const patternLabels = pattern.split('→').map(v => valueLabels[v] || v).join(' → ');
          generatedInsights.push({
            type: 'pattern',
            title: 'Repeating Pattern',
            text: `Repeating pattern (${count} times): ${patternLabels}`,
            chain: patternLabels,
            priority: 2
          });
        }
      });
    }

    // Check for emotional reaction followed by correction pattern
    const emotionalCorrections = chains.filter(chain => {
      const values = chain.map(n => n.value_tag);
      for (let i = 0; i < values.length - 1; i++) {
        if ((values[i] === 'harm' || values[i] === 'avoidance') && 
            (values[i + 1] === 'recovery' || values[i + 1] === 'contribution')) {
          return true;
        }
      }
      return false;
    });

    if (emotionalCorrections.length >= 2) {
      generatedInsights.push({
        type: 'pattern',
        title: 'Emotional Correction Pattern',
        text: `Repeating pattern of negative reaction followed by correction (${emotionalCorrections.length} times)`,
        chain: '',
        priority: 2
      });
    }

    // Sort by priority and limit
    return generatedInsights
      .sort((a, b) => a.priority - b.priority)
      .slice(0, 5);
  }, [history]);

  // Check if we have chains to analyze
  const hasChains = useMemo(() => {
    if (!history || history.length < 2) return false;
    return history.some(h => h.parent_decision_id || 
      history.some(other => other.parent_decision_id === h.id));
  }, [history]);

  if (!hasChains || insights.length === 0) return null;

  return (
    <section 
      className="bg-gradient-to-br from-cyan-50 to-teal-50 rounded-3xl p-5 shadow-sm border border-cyan-200"
      data-testid="chain-insights-section"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-foreground">Chain Insights</h3>
        <p className="text-xs text-muted-foreground">Analyzing behavioral patterns from your paths</p>
      </div>

      {/* Insights list */}
      <div className="space-y-3">
        {insights.map((insight, idx) => {
          const typeConfig = insightTypes[insight.type] || insightTypes.pattern;
          
          return (
            <div 
              key={idx}
              className={`p-4 rounded-xl border ${typeConfig.color}`}
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl">{typeConfig.icon}</span>
                <div className="flex-1">
                  <h4 className={`font-semibold text-sm ${typeConfig.titleColor}`}>
                    {insight.title}
                  </h4>
                  <p className="text-sm mt-1">
                    {insight.text}
                  </p>
                  {insight.chain && (
                    <p className="text-xs mt-2 opacity-70 font-mono" dir="ltr">
                      {insight.chain}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary stats */}
      <div className="mt-4 pt-3 border-t border-cyan-200">
        <div className="flex flex-wrap gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-green-500">●</span>
            <span>Recovery paths: {insights.filter(i => i.type === 'recovery_chain' || i.type === 'growth').length}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-red-500">●</span>
            <span>Warnings: {insights.filter(i => i.type === 'harm_chain' || i.type === 'warning').length}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-blue-500">●</span>
            <span>Corrections: {insights.filter(i => i.type === 'correction').length}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-purple-500">●</span>
            <span>Patterns: {insights.filter(i => i.type === 'pattern').length}</span>
          </div>
        </div>
      </div>
    </section>
  );
}
