import { useState, useEffect } from 'react';

const STAGES = [
  { id: 'reality', label: 'Reality', desc: "What's happening now" },
  { id: 'human', label: 'Person', desc: 'Who am I today' },
  { id: 'opposition', label: 'Opposition', desc: 'Between which forces' },
  { id: 'choice', label: 'Choice', desc: 'Where to turn' },
  { id: 'action', label: 'Action', desc: 'What I did' },
  { id: 'field', label: 'Field', desc: 'What changed' }
];

export default function OrientationMap() {
  const [stage, setStage] = useState(0);
  const [transitioning, setTransitioning] = useState(false);

  useEffect(() => {
    const handleStageChange = (e) => {
      const newStage = STAGES.findIndex(s => s.id === e.detail?.stage);
      if (newStage >= 0 && newStage !== stage) {
        setTransitioning(true);
        setTimeout(() => {
          setStage(newStage);
          setTransitioning(false);
        }, 150);
      }
    };
    window.addEventListener('orientation-stage', handleStageChange);
    return () => window.removeEventListener('orientation-stage', handleStageChange);
  }, [stage]);

  // Auto-advance on page load: reality → human after 2s
  useEffect(() => {
    const timer = setTimeout(() => {
      window.dispatchEvent(new CustomEvent('orientation-stage', { detail: { stage: 'human' } }));
    }, 2000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="flex items-center gap-0 py-2 px-1 overflow-x-auto" data-testid="orientation-map">
      {STAGES.map((s, i) => {
        const isActive = i === stage;
        const isPast = i < stage;
        const isFuture = i > stage;

        return (
          <div key={s.id} className="flex items-center" style={{ flex: isActive ? '0 0 auto' : '0 0 auto' }}>
            {/* Stage node */}
            <div
              className={`flex flex-col items-center transition-all duration-500 ${transitioning ? 'opacity-80' : 'opacity-100'}`}
              data-testid={`stage-${s.id}`}
            >
              <div
                className={`relative flex items-center justify-center rounded-full transition-all duration-500 ${
                  isActive
                    ? 'w-8 h-8 bg-white shadow-lg ring-2 ring-indigo-400 ring-offset-1'
                    : isPast
                    ? 'w-5 h-5 bg-indigo-100'
                    : 'w-5 h-5 bg-gray-100'
                }`}
              >
                {isActive && <div className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse" />}
                {isPast && <div className="w-2 h-2 rounded-full bg-indigo-400" />}
                {isFuture && <div className="w-1.5 h-1.5 rounded-full bg-gray-300" />}
              </div>
              <span
                className={`mt-1 text-center leading-none transition-all duration-500 ${
                  isActive
                    ? 'text-[10px] font-bold text-indigo-600'
                    : isPast
                    ? 'text-[8px] text-indigo-400'
                    : 'text-[8px] text-gray-300'
                }`}
              >
                {s.label}
              </span>
            </div>

            {/* Connector line */}
            {i < STAGES.length - 1 && (
              <div className="flex items-center mx-0.5 mt-[-10px]">
                <div
                  className={`h-px transition-all duration-500 ${
                    i < stage ? 'w-4 bg-indigo-300' : 'w-4 bg-gray-200'
                  }`}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
