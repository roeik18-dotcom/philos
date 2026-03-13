import { useState } from 'react';
import { Share2, ChevronDown, ChevronUp, Users } from 'lucide-react';
import {
  EntryLayer,
  DailyOpeningSection,
  OppositionLayer,
  DailyOrientationQuestion,
  FieldImpactLayer,
  ClosingLayer,
  FieldMissionSection,
  OrientationFeedSection,
  CommunityStreakSection,
  InviteSection,
  DecisionPathSection,
  GlobalFieldDashboard,
  CompassAISection,
  FieldGlobeSection,
  DailyBaseSelection,
  RetentionNudges
} from '../../components/philos/sections';
import TrustChangeCard from '../../components/philos/sections/TrustChangeCard';
import InlineInviteCard from '../../components/philos/sections/InlineInviteCard';

export default function HomeTab({
  user,
  history,
  state,
  actionText,
  setActionText,
  evaluateAction,
  recommendationMetadata,
  onClearRecommendation,
  onFollowRecommendation,
  decisionResult,
  adaptiveScores,
  replayInsights,
  missionContributed,
  setMissionContributed,
  setShowShareCard,
  setActiveTab
}) {
  const [showCommunity, setShowCommunity] = useState(false);
  const [actionCompleted, setActionCompleted] = useState(false);
  const [actionDirection, setActionDirection] = useState(null);
  const [baseSelected, setBaseSelected] = useState(false);
  const [showAtmosphere, setShowAtmosphere] = useState(false);

  return (
    <div className="space-y-4">

      {/* ═══ BRIEF CONTEXT ═══ */}
      <EntryLayer userId={user?.id} />

      {/* ═══ CORE ACTION PATH — Base + Daily Action ═══ */}
      <DailyBaseSelection userId={user?.id} onBaseSelected={() => setBaseSelected(true)} />

      {baseSelected ? (
        <DailyOrientationQuestion
          userId={user?.id}
          onActionRecorded={(actionData) => {
            setActionCompleted(true);
            setActionDirection(actionData?.direction || actionData?.suggested_direction || null);
            if (actionData?.mission_contributed) setMissionContributed(true);
          }}
        />
      ) : (
        <div className="rounded-2xl border border-dashed border-gray-200 p-4 text-center" data-testid="base-gate">
          <p className="text-xs text-gray-400">Select a daily base to continue</p>
        </div>
      )}

      {/* ═══ POST-ACTION: Trust Change + Invite ═══ */}
      {actionCompleted && (
        <div className="space-y-3 animate-fadeIn">
          <TrustChangeCard userId={user?.id} />
          <InlineInviteCard />
        </div>
      )}

      {/* ═══ RETENTION NUDGES ═══ */}
      <RetentionNudges
        visible={actionCompleted}
        onNavigate={(target) => {
          if (target === 'community') setShowCommunity(true);
        }}
      />

      {/* ═══ FIELD IMPACT ═══ */}
      <FieldImpactLayer
        userId={user?.id}
        actionCompleted={actionCompleted}
        actionDirection={actionDirection}
      />

      {/* ─── Atmosphere: globe, opening, opposition, closing ─── */}
      <div className="pt-1">
        <button
          onClick={() => setShowAtmosphere(!showAtmosphere)}
          className="w-full flex items-center justify-center gap-2 py-2 text-[10px] text-gray-300 hover:text-gray-500 transition-colors"
          data-testid="toggle-atmosphere-section"
        >
          <span>{showAtmosphere ? 'Hide field & observation' : 'Global field & observation'}</span>
          {showAtmosphere ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      {showAtmosphere && (
        <div className="space-y-4 animate-fadeIn">
          <GlobalFieldDashboard />
          <FieldGlobeSection />
          <DailyOpeningSection userId={user?.id} />
          <OppositionLayer userId={user?.id} />
          <ClosingLayer userId={user?.id} />
          <CompassAISection userId={user?.id} />
        </div>
      )}

      {/* ─── Community ─── */}
      <div className="pt-2">
        <button
          onClick={() => setShowCommunity(!showCommunity)}
          className="w-full flex items-center justify-center gap-2 py-2.5 text-xs text-gray-400 hover:text-gray-600 transition-colors"
          data-testid="toggle-community-section"
        >
          <Users className="w-3.5 h-3.5" />
          <span>{showCommunity ? 'Hide community' : 'Community & shared field'}</span>
          {showCommunity ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {showCommunity && (
        <div className="space-y-4 animate-fadeIn">
          <FieldMissionSection missionContributed={missionContributed} />
          <OrientationFeedSection />
          <CommunityStreakSection />
          <InviteSection userId={user?.id} />

          <button
            onClick={() => setShowShareCard(true)}
            className="w-full py-3 px-4 bg-white rounded-2xl shadow-sm border border-border flex items-center justify-center gap-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:shadow-md active:scale-[0.98] transition-all duration-300"
            data-testid="open-share-card-btn"
          >
            <Share2 className="w-4 h-4" />
            <span>Share your orientation</span>
          </button>

          <DecisionPathSection
            userId={user?.id}
            onActionFollowed={() => {}}
          />
        </div>
      )}
    </div>
  );
}
