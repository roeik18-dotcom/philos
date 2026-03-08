import { useMemo } from 'react';

// Hebrew labels
const valueLabels = {
  contribution: 'תרומה',
  recovery: 'התאוששות',
  order: 'סדר',
  harm: 'נזק',
  avoidance: 'הימנעות'
};

// Node colors
const nodeColorClasses = {
  contribution: 'bg-green-500',
  recovery: 'bg-blue-500',
  order: 'bg-indigo-500',
  harm: 'bg-red-500',
  avoidance: 'bg-gray-400'
};

export default function DecisionTreeSection({ history }) {
  // Build tree data
  const treeData = useMemo(() => {
    if (!history || history.length === 0) {
      return { roots: [], flatNodes: [], totalEdges: 0 };
    }

    // Assign IDs
    const items = history.map((item, idx) => ({
      ...item,
      id: item.id || `node_${idx}`,
      childIds: []
    }));

    // Create node map
    const nodeMap = {};
    items.forEach(item => {
      nodeMap[item.id] = item;
    });

    // Build relationships
    const roots = [];
    let edgeCount = 0;
    
    items.forEach(item => {
      if (item.parent_decision_id && nodeMap[item.parent_decision_id]) {
        nodeMap[item.parent_decision_id].childIds.push(item.id);
        edgeCount++;
      } else {
        roots.push(item);
      }
    });

    return { roots, flatNodes: items, nodeMap, totalEdges: edgeCount };
  }, [history]);

  // Check if we should render
  const hasChains = useMemo(() => {
    if (!history || history.length < 2) return false;
    return history.some(h => h.parent_decision_id || 
      history.some(other => other.parent_decision_id === h.id));
  }, [history]);

  if (!hasChains) return null;

  const { roots, flatNodes, nodeMap, totalEdges } = treeData;

  // Render a single node
  const renderNode = (nodeId, depth = 0) => {
    const node = nodeMap[nodeId];
    if (!node || depth > 5) return null; // Limit depth to prevent infinite loops
    
    const colorClass = nodeColorClasses[node.value_tag] || 'bg-gray-400';
    const isHarm = node.value_tag === 'harm';
    const isPositive = node.value_tag === 'contribution' || node.value_tag === 'recovery';

    return (
      <div key={nodeId} className="flex flex-col items-center">
        {/* Node card */}
        <div 
          className={`relative px-4 py-3 rounded-xl text-white text-center min-w-[140px] max-w-[180px] shadow-md ${colorClass} ${
            isHarm ? 'ring-2 ring-red-300 ring-offset-2' : ''
          } ${isPositive ? 'ring-2 ring-green-300 ring-offset-2' : ''}`}
        >
          {/* Status dot */}
          <div 
            className={`absolute -top-1 -left-1 w-4 h-4 rounded-full border-2 border-white ${
              node.decision === 'Allowed' ? 'bg-green-400' : 'bg-red-400'
            }`}
          />
          
          {/* Action text */}
          <p className="text-xs font-semibold truncate">
            {node.action?.slice(0, 18) || 'No action'}
          </p>
          
          {/* Meta */}
          <p className="text-[10px] opacity-80 mt-1">
            {node.time} | {valueLabels[node.value_tag] || node.value_tag}
          </p>
        </div>

        {/* Children */}
        {node.childIds && node.childIds.length > 0 && (
          <>
            <div className="w-0.5 h-6 bg-violet-300" />
            {node.childIds.length > 1 && (
              <div className="h-0.5 bg-violet-300" style={{ width: `${(node.childIds.length - 1) * 180}px` }} />
            )}
            <div className="flex gap-4">
              {node.childIds.map(childId => (
                <div key={childId} className="flex flex-col items-center">
                  <div className="w-0.5 h-6 bg-violet-300" />
                  {renderNode(childId, depth + 1)}
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    );
  };

  return (
    <section 
      className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-3xl p-5 shadow-sm border border-violet-200"
      dir="rtl"
      data-testid="decision-tree-section"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-foreground">עץ החלטות</h3>
        <p className="text-xs text-muted-foreground">מסלולי ההחלטות שלך כמבנה מסועף</p>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mb-4 text-xs">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span>תרומה</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-blue-500"></div>
          <span>התאוששות</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-indigo-500"></div>
          <span>סדר</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <span>נזק</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-gray-400"></div>
          <span>הימנעות</span>
        </div>
      </div>

      {/* Tree visualization */}
      <div className="overflow-x-auto bg-white/80 rounded-2xl p-6 border border-violet-100">
        <div className="flex gap-8 justify-center" style={{ direction: 'ltr' }}>
          {roots.map(root => renderNode(root.id, 0))}
        </div>
      </div>

      {/* Stats */}
      <div className="mt-3 pt-3 border-t border-violet-200 grid grid-cols-3 gap-2 text-xs text-center">
        <div>
          <p className="text-muted-foreground">שורשים</p>
          <p className="font-semibold">{roots.length}</p>
        </div>
        <div>
          <p className="text-muted-foreground">צמתים</p>
          <p className="font-semibold">{flatNodes.length}</p>
        </div>
        <div>
          <p className="text-muted-foreground">קשרים</p>
          <p className="font-semibold">{totalEdges}</p>
        </div>
      </div>
    </section>
  );
}
