import { useState } from 'react';
import DecisionMap from '../components/philos/DecisionMap';

export default function PhilosDashboard() {
  const [state, setState] = useState({
    physical_capacity: 50,
    chaos_order: 0,
    ego_collective: 0,
    gap_type: 'energy'
  });
  const [actionText, setActionText] = useState("");
  const [decisionResult, setDecisionResult] = useState(null);

  const evaluateAction = () => {
    if (!actionText) {
      alert('יש להזין פעולה');
      return;
    }

    let decision = "Allowed";

    // Evaluate based on gap type and capacity
    if (state.gap_type === "energy" && state.physical_capacity < 30) {
      decision = "Blocked";
    }

    // Calculate new projection values based on action
    // Move toward order when taking structured action
    // Move toward collective when action benefits others
    const actionLower = actionText.toLowerCase();
    
    let newChaosOrder = state.chaos_order;
    let newEgoCollective = state.ego_collective;

    // Actions that increase order
    if (actionLower.includes('walk') || actionLower.includes('exercise') || actionLower.includes('organize')) {
      newChaosOrder = Math.min(100, state.chaos_order + 20);
    }
    
    // Actions that increase collective orientation
    if (actionLower.includes('help') || actionLower.includes('share') || actionLower.includes('call')) {
      newEgoCollective = Math.min(100, state.ego_collective + 20);
    }

    // Actions that increase chaos/spontaneity  
    if (actionLower.includes('rest') || actionLower.includes('sleep') || actionLower.includes('relax')) {
      newChaosOrder = Math.max(-100, state.chaos_order - 15);
    }

    // Actions that increase ego focus
    if (actionLower.includes('meditate') || actionLower.includes('journal') || actionLower.includes('think')) {
      newEgoCollective = Math.max(-100, state.ego_collective - 15);
    }

    // Update state with new projection values
    setState(prev => ({
      ...prev,
      chaos_order: newChaosOrder,
      ego_collective: newEgoCollective
    }));

    setDecisionResult({
      decision,
      projection: {
        chaos_order: newChaosOrder,
        ego_collective: newEgoCollective
      }
    });
  };

  const handleReset = () => {
    setState({
      physical_capacity: 50,
      chaos_order: 0,
      ego_collective: 0,
      gap_type: 'energy'
    });
    setActionText("");
    setDecisionResult(null);
  };

  return (
    <div className="min-h-screen bg-background p-6 pb-24">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground">Philos Orientation</h1>
        </div>

        {/* State Sliders */}
        <section className="bg-white rounded-3xl p-6 shadow-sm border border-border space-y-4">
          
          {/* Gap Type */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Gap Type</label>
            <select
              value={state.gap_type}
              onChange={(e) => setState({ ...state, gap_type: e.target.value })}
              className="w-full px-4 py-2 border border-border rounded-xl"
            >
              <option value="energy">energy</option>
              <option value="clarity">clarity</option>
              <option value="order">order</option>
              <option value="relation">relation</option>
            </select>
          </div>

          {/* Physical Capacity */}
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-foreground">Physical Capacity</label>
              <span className="text-sm font-bold">{state.physical_capacity}</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={state.physical_capacity}
              onChange={(e) => setState({ ...state, physical_capacity: parseInt(e.target.value) })}
              className="w-full"
            />
          </div>

          {/* Chaos ↔ Order */}
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-foreground">chaos ←→ order</label>
              <span className="text-sm font-bold">{state.chaos_order}</span>
            </div>
            <input
              type="range"
              min="-100"
              max="100"
              value={state.chaos_order}
              onChange={(e) => setState({ ...state, chaos_order: parseInt(e.target.value) })}
              className="w-full"
            />
          </div>

          {/* Ego ↔ Collective */}
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-foreground">ego ←→ collective</label>
              <span className="text-sm font-bold">{state.ego_collective}</span>
            </div>
            <input
              type="range"
              min="-100"
              max="100"
              value={state.ego_collective}
              onChange={(e) => setState({ ...state, ego_collective: parseInt(e.target.value) })}
              className="w-full"
            />
          </div>
        </section>

        {/* Action Evaluation */}
        <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
          <h3 className="text-xl font-semibold text-foreground mb-4">Action Evaluation</h3>
          
          <input
            type="text"
            placeholder="Enter action..."
            value={actionText}
            onChange={(e) => setActionText(e.target.value)}
            className="w-full px-4 py-3 border border-border rounded-xl text-lg mb-4"
          />
          
          <button
            onClick={evaluateAction}
            className="w-full px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:bg-primary/90 transition-all"
          >
            Evaluate Decision
          </button>

          {decisionResult && (
            <div className="mt-6 p-4 bg-muted/30 rounded-2xl space-y-2">
              <p className="text-foreground">
                <span className="text-muted-foreground">Decision:</span>{' '}
                <span className={`font-bold ${decisionResult.decision === 'Allowed' ? 'text-green-600' : 'text-red-600'}`}>
                  {decisionResult.decision}
                </span>
              </p>
              <p className="text-foreground">
                <span className="text-muted-foreground">Projection → chaos/order:</span>{' '}
                {decisionResult.projection.chaos_order}
              </p>
              <p className="text-foreground">
                <span className="text-muted-foreground">Projection → ego/collective:</span>{' '}
                {decisionResult.projection.ego_collective}
              </p>
            </div>
          )}
        </section>

        {/* Decision Map */}
        <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
          <DecisionMap 
            state={state}
            decisionState={decisionResult ? { result: { status: decisionResult.decision.toLowerCase() } } : null}
            gapType={state.gap_type}
          />
        </section>

      </div>
    </div>
  );
}
