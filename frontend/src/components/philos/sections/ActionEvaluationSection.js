export default function ActionEvaluationSection({ 
  actionText, 
  setActionText, 
  evaluateAction, 
  decisionResult,
  state,
  calculateSuggestedVector 
}) {
  return (
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
          <p className="text-foreground">
            <span className="text-muted-foreground">Value Tag:</span>{' '}
            <span className={`px-2 py-0.5 rounded-full text-sm font-medium ${
              decisionResult.value_tag === 'contribution' ? 'bg-green-100 text-green-700' :
              decisionResult.value_tag === 'recovery' ? 'bg-blue-100 text-blue-700' :
              decisionResult.value_tag === 'order' ? 'bg-indigo-100 text-indigo-700' :
              decisionResult.value_tag === 'harm' ? 'bg-red-100 text-red-700' :
              decisionResult.value_tag === 'avoidance' ? 'bg-gray-100 text-gray-700' :
              'bg-gray-100 text-gray-600'
            }`}>
              {decisionResult.value_tag}
            </span>
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
  );
}
