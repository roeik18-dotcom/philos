import {
  FieldGlobeSection,
  OrientationIndexPage,
  MetricsDashboardSection,
  ReferralLeaderboardSection,
  InviteTrackingSection,
  RecommendationCalibrationSection,
  ReplayAdaptiveEffectSection,
  CollectiveMirrorSection,
  CollectiveTrajectorySection,
  CollectiveLayerSection,
  CollectiveTrendsSection,
  GlobalFieldSection,
  ValueConstellationSection,
  PersonalMapSection,
  CollectiveValueMapSection
} from '../../components/philos/sections';
import { analyzePersonalMap } from '../../hooks/usePhilosState';

export default function SystemTab({
  history,
  learningHistory,
  replayInsights,
  replayAdaptiveAdjustments,
  adaptiveScores
}) {
  return (
    <div className="space-y-5">
      {/* Global Field Globe - 3D Visualization */}
      <FieldGlobeSection />

      {/* Orientation Index - Global Public View */}
      <OrientationIndexPage />

      {/* Metrics Dashboard - Admin Panel */}
      <MetricsDashboardSection />

      {/* Referral Leaderboard */}
      <ReferralLeaderboardSection />

      {/* Invite Tracking Report */}
      <InviteTrackingSection />

      {/* Recommendation Calibration */}
      <RecommendationCalibrationSection history={history} />

      {/* Replay Adaptive Effect */}
      <ReplayAdaptiveEffectSection 
        adjustments={replayAdaptiveAdjustments}
        adaptiveScores={adaptiveScores}
        replayInsights={replayInsights}
      />

      {/* Collective Mirror */}
      <CollectiveMirrorSection
        history={history}
        learningHistory={learningHistory}
        replayInsights={replayInsights}
      />

      {/* Collective Trajectory */}
      <CollectiveTrajectorySection history={history} />

      {/* Collective Layer */}
      <CollectiveLayerSection />

      {/* Collective Trends */}
      <CollectiveTrendsSection />

      {/* Global Field */}
      <GlobalFieldSection />

      {/* Value Constellation */}
      <ValueConstellationSection history={history} />

      {/* Personal Map */}
      <PersonalMapSection
        history={history}
        analyzePersonalMap={analyzePersonalMap}
      />

      {/* Collective Value Map */}
      <CollectiveValueMapSection history={history} />
    </div>
  );
}
