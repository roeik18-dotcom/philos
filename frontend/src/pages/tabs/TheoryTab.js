import {
  DirectionExplanationsSection,
  TheorySection,
  DirectionHistorySection
} from '../../components/philos/sections';

export default function TheoryTab({ history }) {
  return (
    <div className="space-y-5">
      {/* Direction Explanations - Four Directions Deep Dive */}
      <DirectionExplanationsSection />

      {/* Theoretical Framework */}
      <TheorySection />

      {/* Direction History with Patterns */}
      <DirectionHistorySection history={history} />
    </div>
  );
}
