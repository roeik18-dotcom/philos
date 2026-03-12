import {
  MissionsSection,
  CirclesSection,
  LeadersSection
} from '../../components/philos/sections';

export default function CommunityTab({ user }) {
  const userId = user?.id || localStorage.getItem('philos_user_id');

  return (
    <div className="space-y-5" data-testid="community-tab">
      {/* Field Missions */}
      <MissionsSection userId={userId} />

      {/* Value Circles */}
      <CirclesSection userId={userId} />

      {/* Value Leaders */}
      <LeadersSection />
    </div>
  );
}
