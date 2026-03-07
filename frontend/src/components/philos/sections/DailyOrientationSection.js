export default function DailyOrientationSection() {
  return (
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
  );
}
