export default function SessionSummarySection({ 
  history, 
  state, 
  getTrajectoryDirection, 
  exportSession, 
  setShowShareCard,
  decisionResult 
}) {
  return (
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

      {/* Share Decision Button */}
      <button
        onClick={() => setShowShareCard(true)}
        disabled={!decisionResult}
        className="w-full px-4 py-3 bg-pink-500 hover:bg-pink-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all flex items-center justify-center gap-2 mt-3"
      >
        <span>🔗</span> Share Decision
      </button>
    </section>
  );
}
