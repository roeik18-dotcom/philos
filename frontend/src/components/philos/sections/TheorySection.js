import { useMemo } from 'react';

// Direction definitions with Hebrew labels
const directions = [
  {
    id: 'recovery',
    name: 'Recovery',
    nameEn: 'Recovery',
    description: 'Restoring balance after pressure or harm',
    color: 'bg-blue-100 text-blue-700 border-blue-300',
    position: { x: 25, y: 75 } // Lower-left
  },
  {
    id: 'order',
    name: 'Order',
    nameEn: 'Order',
    description: 'Creating structure, organization, and clarity',
    color: 'bg-indigo-100 text-indigo-700 border-indigo-300',
    position: { x: 25, y: 25 } // Upper-left/center
  },
  {
    id: 'contribution',
    name: 'Contribution',
    nameEn: 'Contribution',
    description: 'Action for the benefit of others and the collective',
    color: 'bg-green-100 text-green-700 border-green-300',
    position: { x: 75, y: 25 } // Upper-right
  },
  {
    id: 'exploration',
    name: 'Exploration',
    nameEn: 'Exploration',
    description: 'Openness, flexibility, and forward movement',
    color: 'bg-amber-100 text-amber-700 border-amber-300',
    position: { x: 75, y: 75 } // Right side
  }
];

// Tension axes
const tensions = [
  {
    id: 'chaos-order',
    axis: 'vertical',
    poles: ['Chaos', 'Order'],
    polesEn: ['Chaos', 'Order'],
    description: 'The axis between spontaneity and structure'
  },
  {
    id: 'ego-collective',
    axis: 'horizontal',
    poles: ['Ego', 'Collective'],
    polesEn: ['Ego', 'Collective'],
    description: 'The axis between self-focus and focus on others'
  }
];

// Path relationships - the theoretical balancing logic
const pathRelationships = [
  {
    from: 'harm',
    fromLabel: 'Harm',
    to: 'recovery',
    toLabel: 'Recovery',
    explanation: 'actions Harm requires balance through recovery'
  },
  {
    from: 'avoidance',
    fromLabel: 'Avoidance',
    to: 'order',
    toLabel: 'Order',
    explanation: 'Avoidance balanced by creating order and structure'
  },
  {
    from: 'isolation',
    fromLabel: 'Isolation / self-focus',
    to: 'contribution',
    toLabel: 'Contribution',
    explanation: 'Self-focus balanced by contribution others'
  },
  {
    from: 'rigidity',
    fromLabel: 'rigidity / stagnation',
    to: 'exploration',
    toLabel: 'Exploration',
    explanation: 'Stagnation balanced by openness and exploration'
  }
];

export default function TheorySection() {
  return (
    <div className="space-y-6" data-testid="theory-section">
      {/* Header */}
      <section className="bg-gradient-to-br from-slate-50 to-gray-50 rounded-3xl p-6 shadow-sm border border-slate-200">
        <h2 className="text-xl font-bold text-foreground mb-3">The Descriptive Model</h2>
        <p className="text-muted-foreground leading-relaxed">
          Philos Orientation is a system that identifies the direction of your actions, learns your patterns, and suggests a balancing direction to continue.
        </p>
      </section>

      {/* Four Directions */}
      <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
        <h3 className="text-lg font-semibold text-foreground mb-4">The Four Directions</h3>
        <div className="grid grid-cols-2 gap-4">
          {directions.map((dir) => (
            <div
              key={dir.id}
              className={`p-4 rounded-xl border ${dir.color}`}
              data-testid={`direction-${dir.id}`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold">{dir.name}</span>
                <span className="text-xs opacity-70">{dir.nameEn}</span>
              </div>
              <p className="text-sm opacity-80">{dir.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Two Tensions */}
      <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
        <h3 className="text-lg font-semibold text-foreground mb-4">Two Tension Axes</h3>
        <div className="space-y-4">
          {tensions.map((tension) => (
            <div
              key={tension.id}
              className="p-4 rounded-xl bg-gray-50 border border-gray-200"
              data-testid={`tension-${tension.id}`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                  <span className="font-bold text-gray-700">{tension.poles[0]}</span>
                  <span className="text-gray-400">↔</span>
                  <span className="font-bold text-gray-700">{tension.poles[1]}</span>
                </div>
                <span className="text-xs text-gray-500">
                  {tension.polesEn[0]} ↔ {tension.polesEn[1]}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">{tension.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Decision Logic */}
      <section className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-3xl p-6 shadow-sm border border-emerald-200">
        <h3 className="text-lg font-semibold text-foreground mb-4">Decision Logic</h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-white/60 rounded-xl">
            <div className="w-8 h-8 rounded-full bg-emerald-200 flex items-center justify-center text-emerald-700 font-bold">1</div>
            <p className="text-sm text-gray-700">Actions create direction</p>
          </div>
          <div className="flex items-center gap-3 p-3 bg-white/60 rounded-xl">
            <div className="w-8 h-8 rounded-full bg-emerald-200 flex items-center justify-center text-emerald-700 font-bold">2</div>
            <p className="text-sm text-gray-700">Recurring directions create patterns</p>
          </div>
          <div className="flex items-center gap-3 p-3 bg-white/60 rounded-xl">
            <div className="w-8 h-8 rounded-full bg-emerald-200 flex items-center justify-center text-emerald-700 font-bold">3</div>
            <p className="text-sm text-gray-700">Patterns shape orientation</p>
          </div>
        </div>
      </section>

      {/* Path Relationships - Balancing Logic */}
      <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
        <h3 className="text-lg font-semibold text-foreground mb-2">Paths of Balance</h3>
        <p className="text-sm text-muted-foreground mb-4">
          When the current direction is negative, the system suggests a balancing direction:
        </p>
        <div className="space-y-3">
          {pathRelationships.map((path, idx) => (
            <div
              key={idx}
              className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 border border-gray-200"
              data-testid={`path-${path.from}-${path.to}`}
            >
              <span className="px-3 py-1 rounded-lg bg-red-100 text-red-700 text-sm font-medium">
                {path.fromLabel}
              </span>
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
              <span className="px-3 py-1 rounded-lg bg-green-100 text-green-700 text-sm font-medium">
                {path.toLabel}
              </span>
            </div>
          ))}
        </div>
        <p className="text-xs text-muted-foreground mt-4 p-3 bg-blue-50 rounded-xl border border-blue-100">
          💡 If the current direction is already positive, the system will suggest strengthening or balancing it instead of reversing it.
        </p>
      </section>

      {/* Example */}
      <section className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-3xl p-6 shadow-sm border border-amber-200">
        <h3 className="text-lg font-semibold text-foreground mb-3">Example</h3>
        <div className="space-y-3 text-sm text-gray-700">
          <p className="p-3 bg-white/60 rounded-xl">
            • If an action stems from <span className="font-bold text-red-600">Avoidance</span>, the recommended direction may be <span className="font-bold text-indigo-600">Order</span>.
          </p>
          <p className="p-3 bg-white/60 rounded-xl">
            • If an action stems from <span className="font-bold text-red-600">Harm</span>, the recommended direction may be <span className="font-bold text-blue-600">Recovery</span>.
          </p>
        </div>
      </section>

      {/* Visual Quadrant Preview */}
      <section className="bg-white rounded-3xl p-6 shadow-sm border border-border">
        <h3 className="text-lg font-semibold text-foreground mb-4">Direction Map</h3>
        <div className="relative w-full aspect-square max-w-sm mx-auto bg-gray-50 rounded-xl border border-gray-200 overflow-hidden">
          {/* Axes */}
          <div className="absolute top-1/2 left-0 right-0 h-px bg-gray-300"></div>
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-300"></div>
          
          {/* Axis Labels */}
          <span className="absolute top-2 left-1/2 -translate-x-1/2 text-xs text-gray-500 font-medium">Order</span>
          <span className="absolute bottom-2 left-1/2 -translate-x-1/2 text-xs text-gray-500 font-medium">Chaos</span>
          <span className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-500 font-medium">Collective</span>
          <span className="absolute left-2 top-1/2 -translate-y-1/2 text-xs text-gray-500 font-medium">Ego</span>
          
          {/* Direction Labels in Quadrants */}
          <div className="absolute top-[20%] left-[20%] text-center">
            <span className="px-2 py-1 rounded bg-indigo-100 text-indigo-700 text-xs font-medium">Order</span>
          </div>
          <div className="absolute top-[20%] right-[20%] text-center">
            <span className="px-2 py-1 rounded bg-green-100 text-green-700 text-xs font-medium">Contribution</span>
          </div>
          <div className="absolute bottom-[20%] left-[20%] text-center">
            <span className="px-2 py-1 rounded bg-blue-100 text-blue-700 text-xs font-medium">Recovery</span>
          </div>
          <div className="absolute bottom-[20%] right-[20%] text-center">
            <span className="px-2 py-1 rounded bg-amber-100 text-amber-700 text-xs font-medium">Exploration</span>
          </div>
        </div>
        <p className="text-xs text-muted-foreground text-center mt-3">
          A visual map of the four directions on the tension axes
        </p>
      </section>
    </div>
  );
}
