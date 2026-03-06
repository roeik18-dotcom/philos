import { useState } from 'react';
import DecisionMap from '../components/philos/DecisionMap';

// Optimal zone definition
const OPTIMAL_ZONE = {
  order: { min: 20, max: 60 },
  collective: { min: 10, max: 50 }
};

// Calculate suggested vector toward optimal zone
const calculateSuggestedVector = (chaosOrder, egoCollective) => {
  let suggestedOrder = 0;
  let suggestedCollective = 0;
  let suggestions = [];
  let reasons = [];

  // Check order axis (chaos_order)
  if (chaosOrder < OPTIMAL_ZONE.order.min) {
    suggestedOrder = Math.min(20, OPTIMAL_ZONE.order.min - chaosOrder);
    suggestions.push("Take a short walk");
    suggestions.push("Organize something small");
    reasons.push("moves toward order");
    reasons.push("reduces chaos");
  } else if (chaosOrder > OPTIMAL_ZONE.order.max) {
    suggestedOrder = -Math.min(15, chaosOrder - OPTIMAL_ZONE.order.max);
    suggestions.push("Rest for a moment");
    suggestions.push("Let go of control");
    reasons.push("allows flexibility");
    reasons.push("reduces rigidity");
  }

  // Check collective axis (ego_collective)
  if (egoCollective < OPTIMAL_ZONE.collective.min) {
    suggestedCollective = Math.min(20, OPTIMAL_ZONE.collective.min - egoCollective);
    suggestions.push("Help someone nearby");
    suggestions.push("Share an idea");
    reasons.push("increases collective balance");
  } else if (egoCollective > OPTIMAL_ZONE.collective.max) {
    suggestedCollective = -Math.min(15, egoCollective - OPTIMAL_ZONE.collective.max);
    suggestions.push("Take time for yourself");
    suggestions.push("Reflect quietly");
    reasons.push("restores personal balance");
  }

  // Check if in optimal zone
  const inOptimalZone = 
    chaosOrder >= OPTIMAL_ZONE.order.min && 
    chaosOrder <= OPTIMAL_ZONE.order.max &&
    egoCollective >= OPTIMAL_ZONE.collective.min && 
    egoCollective <= OPTIMAL_ZONE.collective.max;

  if (inOptimalZone) {
    suggestions = ["Maintain current balance"];
    reasons = ["You are in the optimal zone"];
  }

  return {
    suggestedOrder,
    suggestedCollective,
    suggestions: suggestions.slice(0, 2),
    reasons: reasons.slice(0, 3),
    inOptimalZone
  };
};

export default function PhilosDashboard() {
  const [state, setState] = useState({
    physical_capacity: 50,
    chaos_order: 0,
    ego_collective: 0,
    gap_type: 'energy'
  });
  const [actionText, setActionText] = useState("");
  const [decisionResult, setDecisionResult] = useState(null);
  const [history, setHistory] = useState([]);

  const evaluateAction = () => {
    if (!actionText) {
      alert('יש להזין פעולה');
      return;
    }

    let decision = "Allowed";
    let reasons = [];

    // Evaluate based on gap type and capacity
    if (state.gap_type === "energy" && state.physical_capacity < 30) {
      decision = "Blocked";
      reasons.push("Energy gap blocks action - physical capacity too low");
    } else {
      reasons.push("Energy gap allows the action");
    }

    // Calculate new projection values based on action
    const actionLower = actionText.toLowerCase();
    
    let newChaosOrder = state.chaos_order;
    let newEgoCollective = state.ego_collective;

    // Actions that increase order
    if (actionLower.includes('walk') || actionLower.includes('exercise') || actionLower.includes('organize')) {
      newChaosOrder = Math.min(100, state.chaos_order + 20);
      reasons.push("The action increases order and structure");
    }
    
    // Actions that increase collective orientation
    if (actionLower.includes('help') || actionLower.includes('share') || actionLower.includes('call')) {
      newEgoCollective = Math.min(100, state.ego_collective + 20);
      reasons.push("The action increases collective orientation");
    }

    // Actions that increase chaos/spontaneity  
    if (actionLower.includes('rest') || actionLower.includes('sleep') || actionLower.includes('relax')) {
      newChaosOrder = Math.max(-100, state.chaos_order - 15);
      reasons.push("The action allows for spontaneity and rest");
    }

    // Actions that increase ego focus
    if (actionLower.includes('meditate') || actionLower.includes('journal') || actionLower.includes('think')) {
      newEgoCollective = Math.max(-100, state.ego_collective - 15);
      reasons.push("The action focuses on self-reflection");
    }

    // Default reason if no specific match
    if (reasons.length === 1) {
      reasons.push("Action maintains current orientation balance");
    }

    // Update state with new projection values
    setState(prev => ({
      ...prev,
      chaos_order: newChaosOrder,
      ego_collective: newEgoCollective
    }));

    const newResult = {
      decision,
      action: actionText,
      reasons,
      projection: {
        chaos_order: newChaosOrder,
        ego_collective: newEgoCollective
      }
    };

    setDecisionResult(newResult);

    // Add to history (limit to last 5)
    setHistory(prev => [
      {
        action: actionText,
        decision: decision,
        chaos_order: newChaosOrder,
        ego_collective: newEgoCollective,
        time: new Date().toLocaleTimeString('he-IL', { hour: '2-digit', minute: '2-digit' })
      },
      ...prev
    ].slice(0, 5));
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
    setHistory([]);
  };

  // Calculate trajectory direction
  const getTrajectoryDirection = () => {
    if (history.length < 2) return 'starting';
    const latest = history[0];
    const previous = history[1];
    const orderDelta = latest.chaos_order - previous.chaos_order;
    const collectiveDelta = latest.ego_collective - previous.ego_collective;
    
    if (orderDelta > 0) return 'toward order';
    if (orderDelta < 0) return 'toward chaos';
    if (collectiveDelta > 0) return 'toward collective';
    if (collectiveDelta < 0) return 'toward ego';
    return 'stable';
  };

  // Export session data
  const exportSession = () => {
    const sessionData = {
      timestamp: new Date().toISOString(),
      state: state,
      history: history,
      balanceScore: 100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective)),
      trajectory: getTrajectoryDirection(),
      totalActions: history.length
    };
    const blob = new Blob([JSON.stringify(sessionData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `philos-session-${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-background p-6 pb-24">
      <div className="max-w-2xl mx-auto space-y-6">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground">Philos Orientation</h1>
          <p className="text-lg text-primary font-medium mt-1">Mental Navigation System</p>
          <p className="text-sm text-muted-foreground mt-1">Navigate your decisions in real time</p>
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

        {/* How do you feel right now? */}
        <section className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-3xl p-4 shadow-sm border border-purple-200">
          <h3 className="text-sm font-medium text-foreground mb-3">How do you feel right now?</h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setState(prev => ({ ...prev, chaos_order: Math.min(100, prev.chaos_order + 20) }))}
              className="px-4 py-2 text-sm bg-green-100 hover:bg-green-200 text-green-700 rounded-lg transition-all"
            >
              😌 Calm
            </button>
            <button
              onClick={() => setState(prev => ({ ...prev, chaos_order: Math.max(-100, prev.chaos_order - 20) }))}
              className="px-4 py-2 text-sm bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-all"
            >
              😰 Stressed
            </button>
            <button
              onClick={() => setState(prev => ({ ...prev, chaos_order: Math.max(-100, prev.chaos_order - 10) }))}
              className="px-4 py-2 text-sm bg-orange-100 hover:bg-orange-200 text-orange-700 rounded-lg transition-all"
            >
              😕 Confused
            </button>
          </div>
        </section>

        {/* Micro Actions */}
        <section className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-3xl p-4 shadow-sm border border-blue-200">
          <h3 className="text-sm font-medium text-foreground mb-3">Micro Actions</h3>
          <div className="flex flex-wrap gap-2">
            {[
              { text: 'Drink water', icon: '💧' },
              { text: 'Take 5 deep breaths', icon: '🌬️' },
              { text: 'Stand up and stretch', icon: '🧘' },
              { text: 'Send a positive message', icon: '💬' }
            ].map((action) => (
              <button
                key={action.text}
                onClick={() => setActionText(action.text)}
                className="px-3 py-2 text-sm bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-lg transition-all"
              >
                {action.icon} {action.text}
              </button>
            ))}
          </div>
        </section>

        {/* Quick Actions */}
        <section className="bg-white rounded-3xl p-4 shadow-sm border border-border">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Quick Actions</h3>
          <div className="flex flex-wrap gap-2">
            {[
              'Help a friend',
              'Take a walk',
              'Send angry message',
              'Ignore someone',
              'Organize your desk'
            ].map((action) => (
              <button
                key={action}
                onClick={() => setActionText(action)}
                className="px-3 py-2 text-sm bg-muted/50 hover:bg-muted text-foreground rounded-lg transition-all"
              >
                {action}
              </button>
            ))}
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

          {/* Decision Explanation */}
          {decisionResult && (
            <div className="mt-4 p-4 bg-white border border-border rounded-2xl">
              <h4 className="text-lg font-semibold text-foreground mb-3">Decision Explanation</h4>
              
              <div className="space-y-2 text-sm">
                <p className="text-foreground">
                  <span className="text-muted-foreground">Action:</span>{' '}
                  <span className="font-medium">{decisionResult.action}</span>
                </p>
                
                <p className="text-foreground">
                  <span className="text-muted-foreground">Decision:</span>{' '}
                  <span className={`font-bold ${decisionResult.decision === 'Allowed' ? 'text-green-600' : 'text-red-600'}`}>
                    {decisionResult.decision}
                  </span>
                </p>
                
                <div className="mt-3 pt-3 border-t border-border">
                  <p className="text-muted-foreground mb-2">Explanation:</p>
                  <ul className="space-y-1">
                    {decisionResult.reasons.map((reason, idx) => (
                      <li key={idx} className="text-foreground">• {reason}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Vector Suggestion Engine */}
          {(() => {
            const suggestion = calculateSuggestedVector(state.chaos_order, state.ego_collective);
            return (
              <div className="mt-4 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl">
                <h4 className="text-lg font-semibold text-foreground mb-3">Suggested Next Action</h4>
                
                {suggestion.inOptimalZone ? (
                  <div className="text-center py-2">
                    <p className="text-green-600 font-medium">✓ You are in the optimal zone</p>
                    <p className="text-sm text-muted-foreground mt-1">Maintain current balance</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Suggestions */}
                    <div>
                      <p className="text-sm text-muted-foreground mb-2">Suggestion:</p>
                      <div className="space-y-1">
                        {suggestion.suggestions.map((s, idx) => (
                          <p key={idx} className="text-foreground font-medium">
                            {idx === 0 ? '' : 'or '}{s}
                          </p>
                        ))}
                      </div>
                    </div>

                    {/* Reasons */}
                    <div className="pt-2 border-t border-blue-200">
                      <p className="text-sm text-muted-foreground mb-1">Reason:</p>
                      <ul className="text-sm text-foreground">
                        {suggestion.reasons.map((r, idx) => (
                          <li key={idx}>• {r}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Suggested Vector */}
                    <div className="pt-2 border-t border-blue-200">
                      <p className="text-sm text-muted-foreground mb-1">Suggested Vector:</p>
                      <div className="flex gap-4 text-sm font-mono">
                        {suggestion.suggestedOrder !== 0 && (
                          <span className="text-foreground">
                            → order {suggestion.suggestedOrder > 0 ? '+' : ''}{suggestion.suggestedOrder}
                          </span>
                        )}
                        {suggestion.suggestedCollective !== 0 && (
                          <span className="text-foreground">
                            → collective {suggestion.suggestedCollective > 0 ? '+' : ''}{suggestion.suggestedCollective}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })()}
        </section>

        {/* Orientation Status Panel */}
        <section className="bg-white rounded-3xl p-4 shadow-sm border border-border">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-foreground">Orientation Status</h3>
            <button
              onClick={handleReset}
              className="px-4 py-2 text-sm bg-muted hover:bg-muted/80 text-foreground rounded-xl transition-all"
            >
              Start New Session
            </button>
          </div>
          
          <div className="grid grid-cols-3 gap-3">
            {/* Order */}
            <div className="text-center p-3 bg-muted/20 rounded-xl">
              <p className="text-xs text-muted-foreground mb-1">Order</p>
              <p className={`text-2xl font-bold ${state.chaos_order >= 0 ? 'text-blue-600' : 'text-orange-500'}`}>
                {state.chaos_order >= 0 ? '+' : ''}{state.chaos_order}
              </p>
            </div>
            
            {/* Collective */}
            <div className="text-center p-3 bg-muted/20 rounded-xl">
              <p className="text-xs text-muted-foreground mb-1">Collective</p>
              <p className={`text-2xl font-bold ${state.ego_collective >= 0 ? 'text-green-600' : 'text-purple-500'}`}>
                {state.ego_collective >= 0 ? '+' : ''}{state.ego_collective}
              </p>
            </div>
            
            {/* Energy Gap */}
            <div className="text-center p-3 bg-muted/20 rounded-xl">
              <p className="text-xs text-muted-foreground mb-1">Energy</p>
              <p className={`text-2xl font-bold ${state.physical_capacity >= 30 ? 'text-green-600' : 'text-red-500'}`}>
                {state.physical_capacity}%
              </p>
            </div>
          </div>

          {/* Balance Score */}
          {(() => {
            const balanceScore = 100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective));
            const scoreColor = balanceScore >= 70 ? 'text-green-600' : balanceScore >= 40 ? 'text-yellow-500' : 'text-red-500';
            const scoreBg = balanceScore >= 70 ? 'bg-green-100' : balanceScore >= 40 ? 'bg-yellow-100' : 'bg-red-100';
            const scoreLabel = balanceScore >= 70 ? 'Balanced' : balanceScore >= 40 ? 'Unstable' : 'Conflict';
            return (
              <div className={`mt-3 p-3 ${scoreBg} rounded-xl text-center`}>
                <p className="text-xs text-muted-foreground mb-1">Balance Score</p>
                <p className={`text-3xl font-bold ${scoreColor}`}>{balanceScore}</p>
                <p className={`text-sm font-medium ${scoreColor}`}>{scoreLabel}</p>
              </div>
            );
          })()}

          {/* Suggested Stabilizing Action - show when balance < 30 */}
          {(() => {
            const balanceScore = 100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective));
            if (balanceScore >= 30) return null;
            return (
              <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-xl">
                <p className="text-sm font-semibold text-red-700 mb-2">⚠️ Suggested Stabilizing Action</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    'Take a short walk',
                    'Drink water',
                    'Write it but don\'t send',
                    'Pause for 2 minutes'
                  ].map(action => (
                    <button
                      key={action}
                      onClick={() => setActionText(action)}
                      className="px-2 py-1 text-xs bg-red-100 hover:bg-red-200 text-red-700 rounded-lg transition-all"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              </div>
            );
          })()}
        </section>

        {/* Recover Energy */}
        <section className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-3xl p-4 shadow-sm border border-emerald-200">
          <h3 className="text-sm font-medium text-foreground mb-2">Recover Energy (+10)</h3>
          <div className="flex flex-wrap gap-2">
            {[
              { text: 'Deep breathing', icon: '🌬️' },
              { text: 'Short walk', icon: '🚶' },
              { text: 'Stretch', icon: '🧘' },
              { text: 'Drink water', icon: '💧' }
            ].map(action => (
              <button
                key={action.text}
                onClick={() => {
                  setActionText(action.text);
                  setState(prev => ({ ...prev, physical_capacity: Math.min(100, prev.physical_capacity + 10) }));
                }}
                className="px-3 py-2 text-sm bg-emerald-100 hover:bg-emerald-200 text-emerald-700 rounded-lg transition-all"
              >
                {action.icon} {action.text}
              </button>
            ))}
          </div>
        </section>

        {/* Daily Loop */}
        <section className="bg-gradient-to-br from-slate-50 to-gray-100 rounded-3xl p-4 shadow-sm border border-slate-200">
          <h3 className="text-sm font-medium text-foreground mb-3">Daily Loop</h3>
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-1">
              <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold">1</span>
              <span className="text-muted-foreground">Check state</span>
            </div>
            <span className="text-muted-foreground">→</span>
            <div className="flex items-center gap-1">
              <span className="w-6 h-6 rounded-full bg-green-100 text-green-600 flex items-center justify-center font-bold">2</span>
              <span className="text-muted-foreground">Take action</span>
            </div>
            <span className="text-muted-foreground">→</span>
            <div className="flex items-center gap-1">
              <span className="w-6 h-6 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold">3</span>
              <span className="text-muted-foreground">Evaluate</span>
            </div>
            <span className="text-muted-foreground">→</span>
            <div className="flex items-center gap-1">
              <span className="w-6 h-6 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center font-bold">4</span>
              <span className="text-muted-foreground">Repeat</span>
            </div>
          </div>
        </section>

        {/* Decision Map */}
        <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
          <DecisionMap 
            state={state}
            decisionState={decisionResult ? { result: { status: decisionResult.decision.toLowerCase() } } : null}
            gapType={state.gap_type}
            history={history}
            suggestion={calculateSuggestedVector(state.chaos_order, state.ego_collective)}
          />
        </section>

        {/* Decision History */}
        {history.length > 0 && (
          <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
            <h3 className="text-xl font-semibold text-foreground mb-4">Decision History</h3>
            
            <div className="space-y-3">
              {history.map((item, idx) => (
                <div 
                  key={idx} 
                  className="p-3 bg-muted/20 rounded-xl border border-border/50"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm text-muted-foreground">{item.time}</span>
                    <span className={`text-sm font-bold ${item.decision === 'Allowed' ? 'text-green-600' : 'text-red-600'}`}>
                      {item.decision}
                    </span>
                  </div>
                  <p className="font-medium text-foreground mb-1">{item.action}</p>
                  <p className="text-sm text-muted-foreground">
                    {item.chaos_order !== 0 && (
                      <span>order {item.chaos_order > 0 ? '+' : ''}{item.chaos_order} </span>
                    )}
                    {item.ego_collective !== 0 && (
                      <span>| collective {item.ego_collective > 0 ? '+' : ''}{item.ego_collective}</span>
                    )}
                    {item.chaos_order === 0 && item.ego_collective === 0 && (
                      <span>balanced</span>
                    )}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Session Summary */}
        <section className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-3xl p-5 shadow-sm border border-indigo-200">
          <h3 className="text-lg font-semibold text-foreground mb-4">Session Summary</h3>
          
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-white/60 rounded-xl p-3 text-center">
              <p className="text-xs text-muted-foreground">Actions</p>
              <p className="text-2xl font-bold text-indigo-600">{history.length}</p>
            </div>
            <div className="bg-white/60 rounded-xl p-3 text-center">
              <p className="text-xs text-muted-foreground">Balance Score</p>
              <p className={`text-2xl font-bold ${
                100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective)) >= 70 
                  ? 'text-green-600' 
                  : 100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective)) >= 40 
                    ? 'text-yellow-500' 
                    : 'text-red-500'
              }`}>
                {100 - (Math.abs(state.chaos_order) + Math.abs(state.ego_collective))}
              </p>
            </div>
            <div className="bg-white/60 rounded-xl p-3 text-center">
              <p className="text-xs text-muted-foreground">Trajectory</p>
              <p className="text-sm font-bold text-purple-600">{getTrajectoryDirection()}</p>
            </div>
            <div className="bg-white/60 rounded-xl p-3 text-center">
              <p className="text-xs text-muted-foreground">Energy</p>
              <p className={`text-sm font-bold ${state.physical_capacity >= 50 ? 'text-green-600' : state.physical_capacity >= 30 ? 'text-yellow-500' : 'text-red-500'}`}>
                {state.physical_capacity >= 50 ? 'stable' : state.physical_capacity >= 30 ? 'low' : 'critical'}
              </p>
            </div>
          </div>

          {/* Export Button */}
          <button
            onClick={exportSession}
            className="w-full px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium transition-all flex items-center justify-center gap-2"
          >
            <span>📥</span> Export Session (JSON)
          </button>
        </section>

        {/* Footer */}
        <div className="text-center text-xs text-muted-foreground pt-4">
          <p>Interactive Decision Engine</p>
          <p className="mt-1">Deploy → test with real decisions</p>
        </div>

      </div>
    </div>
  );
}
