export default function DecisionDisplay({ decision }) {
  const isBlocked = decision.result.status === 'blocked';

  return (
    <div className="space-y-4">
      {/* Status */}
      <div className="flex items-center gap-3">
        <span className="text-sm font-medium text-muted-foreground">Status:</span>
        <span
          className={`px-4 py-2 rounded-full font-medium ${
            isBlocked
              ? 'bg-destructive/10 text-destructive'
              : 'bg-green-500/10 text-green-700'
          }`}
        >
          {decision.result.status.toUpperCase()}
        </span>
      </div>

      {/* Constraints */}
      <div>
        <h3 className="text-sm font-medium text-muted-foreground mb-2">Constraints:</h3>
        <div className="flex items-center gap-2">
          <span
            className={`w-3 h-3 rounded-full ${
              decision.constraints.pass ? 'bg-green-500' : 'bg-destructive'
            }`}
          />
          <span className="text-foreground">
            {decision.constraints.pass ? 'All constraints passed' : 'Constraints failed'}
          </span>
        </div>
        {!decision.constraints.pass && decision.constraints.reason.length > 0 && (
          <ul className="mt-2 space-y-1">
            {decision.constraints.reason.map((reason, idx) => (
              <li key={idx} className="text-sm text-destructive bg-destructive/5 px-3 py-2 rounded-lg">
                {reason}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Recommendation */}
      <div className="p-4 bg-primary/5 border border-primary/20 rounded-2xl">
        <h3 className="text-sm font-medium text-muted-foreground mb-2">Recommended Action:</h3>
        <p className="text-foreground font-medium">{decision.recommended_action}</p>
      </div>
    </div>
  );
}
