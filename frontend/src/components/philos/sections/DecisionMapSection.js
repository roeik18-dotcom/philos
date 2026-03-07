import DecisionMap from '../DecisionMap';

export default function DecisionMapSection({ state, decisionResult, history, calculateSuggestedVector }) {
  return (
    <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
      <DecisionMap 
        state={state}
        decisionState={decisionResult ? { result: { status: decisionResult.decision.toLowerCase() } } : null}
        gapType={state.gap_type}
        history={history}
        suggestion={calculateSuggestedVector(state.chaos_order, state.ego_collective)}
      />
    </section>
  );
}
