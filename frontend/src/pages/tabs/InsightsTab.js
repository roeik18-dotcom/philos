import {
  WeeklyInsightSection,
  WeeklyReportSection,
  ChainInsightsSection,
  RecommendationFollowThroughSection,
  WeeklyBehavioralReportSection,
  MonthlyProgressReportSection,
  QuarterlyReviewSection,
  ReplayInsightsSummarySection,
  DecisionPathEngineSection,
  PathLearningSection,
  AdaptiveLearningSection
} from '../../components/philos/sections';

export default function InsightsTab({
  user,
  history,
  state,
  decisionResult,
  handlePathSelection,
  adaptiveScores,
  selectedPathData,
  learningHistory,
  replayHistory
}) {
  return (
    <div className="space-y-5">
      {/* Weekly Orientation Insight */}
      <WeeklyInsightSection userId={user?.id} />

      {/* Weekly Report */}
      <WeeklyReportSection userId={user?.id} />

      {/* Chain Insights */}
      <ChainInsightsSection history={history} />

      {/* Recommendation Follow-Through Analytics */}
      <RecommendationFollowThroughSection history={history} />

      {/* Weekly Behavioral Report */}
      <WeeklyBehavioralReportSection history={history} user={user} />

      {/* Monthly Progress Report */}
      <MonthlyProgressReportSection history={history} />

      {/* Quarterly Review */}
      <QuarterlyReviewSection history={history} />

      {/* Replay Insights Summary */}
      <ReplayInsightsSummarySection user={user} replayCount={replayHistory?.length || 0} />

      {/* Decision Path Engine */}
      <DecisionPathEngineSection
        state={state}
        history={history}
        onSelectPath={handlePathSelection}
        adaptiveScores={adaptiveScores}
      />

      {/* Path Learning */}
      <PathLearningSection
        selectedPath={selectedPathData}
        actualOutcome={decisionResult}
      />

      {/* Adaptive Learning */}
      <AdaptiveLearningSection
        learningHistory={learningHistory}
        adaptiveScores={adaptiveScores}
      />
    </div>
  );
}
