export default function ActionPathDisplay({ actionPath }) {
  return (
    <div className="space-y-4">
      <div className="p-6 bg-gradient-to-br from-primary/5 to-primary/10 border border-primary/20 rounded-2xl">
        <h3 className="text-xl font-semibold text-foreground mb-2">
          {actionPath.path_name}
        </h3>
        <p className="text-muted-foreground mb-4">
          {actionPath.explanation}
        </p>
        <div className="p-4 bg-background border border-border rounded-xl">
          <p className="text-sm font-medium text-muted-foreground mb-1">First Action:</p>
          <p className="text-foreground font-medium">{actionPath.first_action}</p>
        </div>
      </div>
    </div>
  );
}
