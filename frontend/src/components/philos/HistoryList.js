export default function HistoryList({ history }) {
  if (history.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No history yet. Complete an evaluation to see history.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {history.map((item, idx) => (
        <div
          key={idx}
          className="p-4 border border-border rounded-2xl hover:bg-muted/30 transition-colors"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-muted-foreground">
                #{history.length - idx}
              </span>
              <span className="text-sm font-medium text-foreground">
                {item.gap_type}
              </span>
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${
                  item.decision_status === 'allowed'
                    ? 'bg-green-500/10 text-green-700'
                    : 'bg-destructive/10 text-destructive'
                }`}
              >
                {item.decision_status}
              </span>
            </div>
            <span className="text-xs text-muted-foreground">
              {new Date(item.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <div className="text-sm text-muted-foreground">
            <span className="font-medium">Path:</span>{' '}
            {item.action_path_name || 'N/A'}
          </div>
          {item.reasons.length > 0 && (
            <div className="mt-2 text-xs text-destructive">
              {item.reasons.join(', ')}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
