import { useMemo, useRef, useEffect, useState } from 'react';

// Hebrew labels
const valueLabels = {
  contribution: 'Contribution',
  recovery: 'Recovery',
  order: 'Order',
  harm: 'Harm',
  avoidance: 'Avoidance'
};

// Node colors
const nodeColors = {
  contribution: { bg: '#22c55e', ring: '#86efac' },
  recovery: { bg: '#3b82f6', ring: '#93c5fd' },
  order: { bg: '#6366f1', ring: '#a5b4fc' },
  harm: { bg: '#ef4444', ring: '#fca5a5' },
  avoidance: { bg: '#9ca3af', ring: '#d1d5db' }
};

// Recursively measure tree width (in node units)
function getTreeWidth(nodeId, nodeMap) {
  const node = nodeMap[nodeId];
  if (!node || !node.childIds || node.childIds.length === 0) return 1;
  return node.childIds.reduce((sum, cid) => sum + getTreeWidth(cid, nodeMap), 0);
}

// Layout nodes with x,y positions
function layoutTree(roots, nodeMap) {
  const NODE_W = 150;
  const NODE_H = 56;
  const GAP_X = 20;
  const GAP_Y = 80;
  const positions = {};

  function place(nodeId, x, y, depth) {
    const node = nodeMap[nodeId];
    if (!node || depth > 6) return;
    positions[nodeId] = { x, y, w: NODE_W, h: NODE_H };

    if (node.childIds && node.childIds.length > 0) {
      const childWidths = node.childIds.map(cid => getTreeWidth(cid, nodeMap));
      const totalChildWidth = childWidths.reduce((a, b) => a + b, 0);
      const totalGaps = totalChildWidth - 1;
      const totalSpan = totalChildWidth * NODE_W + totalGaps * GAP_X;
      let cx = x + NODE_W / 2 - totalSpan / 2;

      node.childIds.forEach((cid, i) => {
        const cw = childWidths[i];
        const childSpan = cw * NODE_W + (cw - 1) * GAP_X;
        const childX = cx + childSpan / 2 - NODE_W / 2;
        place(cid, childX, y + NODE_H + GAP_Y, depth + 1);
        cx += childSpan + GAP_X;
      });
    }
  }

  let startX = 0;
  roots.forEach(root => {
    const w = getTreeWidth(root.id, nodeMap);
    const span = w * NODE_W + (w - 1) * GAP_X;
    place(root.id, startX + span / 2 - NODE_W / 2, 0, 0);
    startX += span + GAP_X * 2;
  });

  return positions;
}

export default function DecisionTreeSection({ history }) {
  const containerRef = useRef(null);
  const [svgSize, setSvgSize] = useState({ w: 0, h: 0 });

  // Build tree data
  const treeData = useMemo(() => {
    if (!history || history.length === 0) {
      return { roots: [], flatNodes: [], nodeMap: {}, totalEdges: 0 };
    }

    const items = history.map((item, idx) => ({
      ...item,
      id: item.id || `node_${idx}`,
      childIds: []
    }));

    const nodeMap = {};
    items.forEach(item => { nodeMap[item.id] = item; });

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

  const hasChains = useMemo(() => {
    if (!history || history.length < 2) return false;
    return history.some(h => h.parent_decision_id ||
      history.some(other => other.parent_decision_id === h.id));
  }, [history]);

  // Compute layout positions
  const positions = useMemo(() => {
    if (!hasChains) return {};
    return layoutTree(treeData.roots, treeData.nodeMap);
  }, [hasChains, treeData]);

  // Compute SVG size from positions
  useEffect(() => {
    if (Object.keys(positions).length === 0) return;
    let maxX = 0, maxY = 0;
    Object.values(positions).forEach(p => {
      if (p.x + p.w > maxX) maxX = p.x + p.w;
      if (p.y + p.h > maxY) maxY = p.y + p.h;
    });
    setSvgSize({ w: maxX + 20, h: maxY + 20 });
  }, [positions]);

  if (!hasChains) return null;

  const { roots, flatNodes, nodeMap, totalEdges } = treeData;

  // Build SVG edges
  const edges = [];
  flatNodes.forEach(node => {
    if (!node.childIds) return;
    const parentPos = positions[node.id];
    if (!parentPos) return;
    const px = parentPos.x + parentPos.w / 2;
    const py = parentPos.y + parentPos.h;

    node.childIds.forEach(cid => {
      const childPos = positions[cid];
      if (!childPos) return;
      const cx = childPos.x + childPos.w / 2;
      const cy = childPos.y;
      const midY = py + (cy - py) / 2;
      edges.push({
        key: `${node.id}-${cid}`,
        d: `M ${px} ${py} C ${px} ${midY}, ${cx} ${midY}, ${cx} ${cy}`,
        color: nodeColors[nodeMap[cid]?.value_tag]?.bg || '#d1d5db'
      });
    });
  });

  return (
    <section
      className="bg-gradient-to-br from-violet-50 to-purple-50 rounded-3xl p-5 shadow-sm border border-violet-200"
      data-testid="decision-tree-section"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-foreground">Decision Tree</h3>
        <p className="text-xs text-muted-foreground">Your decision paths as a branching structure</p>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mb-4 text-xs">
        {Object.entries(valueLabels).map(([key, label]) => (
          <div key={key} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: nodeColors[key]?.bg }} />
            <span>{label}</span>
          </div>
        ))}
      </div>

      {/* Tree visualization with SVG */}
      <div ref={containerRef} className="overflow-x-auto bg-white/80 rounded-2xl p-4 border border-violet-100">
        <div style={{ position: 'relative', width: svgSize.w || 'auto', height: svgSize.h || 'auto', direction: 'ltr', minHeight: 80 }}>
          {/* SVG edges layer */}
          {svgSize.w > 0 && (
            <svg
              width={svgSize.w}
              height={svgSize.h}
              style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }}
              data-testid="decision-tree-svg"
            >
              {edges.map(e => (
                <path
                  key={e.key}
                  d={e.d}
                  fill="none"
                  stroke={e.color}
                  strokeWidth={2}
                  strokeOpacity={0.5}
                />
              ))}
            </svg>
          )}

          {/* Node cards layer */}
          {flatNodes.map(node => {
            const pos = positions[node.id];
            if (!pos) return null;
            const colors = nodeColors[node.value_tag] || nodeColors.avoidance;
            return (
              <div
                key={node.id}
                className="absolute rounded-xl text-white text-center shadow-md"
                style={{
                  left: pos.x,
                  top: pos.y,
                  width: pos.w,
                  height: pos.h,
                  backgroundColor: colors.bg,
                  boxShadow: `0 2px 8px ${colors.bg}40`
                }}
                data-testid={`tree-node-${node.id}`}
              >
                {/* Status dot */}
                <div
                  className="absolute -top-1 -left-1 w-3.5 h-3.5 rounded-full border-2 border-white"
                  style={{ backgroundColor: node.decision === 'Allowed' ? '#4ade80' : '#f87171' }}
                />
                <div className="px-2 py-1.5">
                  <p className="text-[11px] font-semibold truncate">
                    {node.action?.slice(0, 18) || 'No action'}
                  </p>
                  <p className="text-[9px] opacity-80 mt-0.5">
                    {node.time} | {valueLabels[node.value_tag] || node.value_tag}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Stats */}
      <div className="mt-3 pt-3 border-t border-violet-200 grid grid-cols-3 gap-2 text-xs text-center">
        <div>
          <p className="text-muted-foreground">Roots</p>
          <p className="font-semibold">{roots.length}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Nodes</p>
          <p className="font-semibold">{flatNodes.length}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Links</p>
          <p className="font-semibold">{totalEdges}</p>
        </div>
      </div>
    </section>
  );
}
