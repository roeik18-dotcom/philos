import { useState } from 'react';
import {
  MissionsSection,
  CirclesSection,
  LeadersSection,
  CircleDetailView
} from '../../components/philos/sections';

export default function CommunityTab({ user }) {
  const userId = user?.id || localStorage.getItem('philos_user_id');
  const [selectedCircle, setSelectedCircle] = useState(null);

  if (selectedCircle) {
    return (
      <CircleDetailView
        circleId={selectedCircle}
        userId={userId}
        onBack={() => setSelectedCircle(null)}
      />
    );
  }

  return (
    <div className="space-y-5" data-testid="community-tab">
      {/* Field Missions */}
      <MissionsSection userId={userId} />

      {/* Value Circles */}
      <CirclesSection userId={userId} onViewCircle={setSelectedCircle} />

      {/* Value Leaders */}
      <LeadersSection />
    </div>
  );
}
