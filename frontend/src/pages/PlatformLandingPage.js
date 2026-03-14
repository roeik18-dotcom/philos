import { useEffect, useRef, useState } from 'react';
import { ArrowRight, ChevronRight, Zap, Target, Globe, Layers, Eye, Compass, Activity } from 'lucide-react';
import './platform.css';

/* ═══════════════════════════════════════════════════
   SYSTEM CHAIN — The 13-stage model
   ═══════════════════════════════════════════════════ */
const CHAIN = [
  { id: 'cosmos',      label: 'Cosmos',      tier: 'cosmos', tip: 'The total field of existence' },
  { id: 'space',       label: 'Space',       tier: 'cosmos', tip: 'The dimension that holds structure' },
  { id: 'matter',      label: 'Matter',      tier: 'cosmos', tip: 'The substance of reality' },
  { id: 'energy',      label: 'Energy',      tier: 'life',   tip: 'The capacity to act and transform' },
  { id: 'motion',      label: 'Motion',      tier: 'life',   tip: 'Change across time' },
  { id: 'life',        label: 'Life',        tier: 'life',   tip: 'Self-organizing complexity' },
  { id: 'human',       label: 'Human',       tier: 'human',  tip: 'The agent of meaning' },
  { id: 'forces',      label: 'Forces',      tier: 'human',  tip: 'Internal drives and tensions' },
  { id: 'conflict',    label: 'Conflict',    tier: 'human',  tip: 'The collision of opposing forces' },
  { id: 'orientation', label: 'Orientation', tier: 'action', tip: 'Where you stand in the field' },
  { id: 'decision',    label: 'Decision',    tier: 'action', tip: 'The moment of commitment' },
  { id: 'action',      label: 'Action',      tier: 'action', tip: 'Force applied to reality' },
  { id: 'impact',      label: 'Impact',      tier: 'action', tip: 'The change left in the field' },
];

const FORCES = [
  { name: 'Contribution', color: 'var(--pl-emerald)', opposite: 'Harm' },
  { name: 'Recovery', color: 'var(--pl-cyan)', opposite: 'Avoidance' },
  { name: 'Order', color: 'var(--pl-violet)', opposite: 'Chaos' },
  { name: 'Exploration', color: 'var(--pl-amber)', opposite: 'Rigidity' },
];

const CONTRADICTIONS = [
  { left: 'Individual', right: 'Collective', desc: 'Self-interest vs. shared good' },
  { left: 'Stability', right: 'Change', desc: 'Preservation vs. transformation' },
  { left: 'Control', right: 'Freedom', desc: 'Structure vs. emergence' },
];

/* ═══════════════════════════════════════════════════
   SECTION COMPONENTS
   ═══════════════════════════════════════════════════ */

function SystemChain() {
  return (
    <div className="chain-container" data-testid="system-chain">
      {CHAIN.map((node, i) => (
        <div key={node.id} style={{ display: 'flex', alignItems: 'center' }}>
          <div className="chain-node hover-tooltip">
            <div className={`node-dot ${node.tier}`} />
            <span className="node-label">{node.label}</span>
            <span className="tooltip-text">{node.tip}</span>
          </div>
          {i < CHAIN.length - 1 && <div className="chain-connector" style={{ animationDelay: `${i * 0.15}s` }} />}
        </div>
      ))}
    </div>
  );
}

function GlobeVisualization() {
  return (
    <div className="globe-vis" data-testid="globe-visualization">
      <div className="globe-ring cosmos">
        <span className="globe-label cosmos-label">Cosmos</span>
      </div>
      <div className="globe-ring life">
        <span className="globe-label life-label">Life</span>
      </div>
      <div className="globe-ring human">
        <span className="globe-label human-label">Human</span>
      </div>
      <div className="globe-center">
        <div className="globe-center-dot" />
      </div>
    </div>
  );
}

function ForcesFlow() {
  return (
    <div className="flow-card" data-testid="forces-flow">
      <div className="flex items-center gap-2 mb-4">
        <Zap className="w-4 h-4" style={{ color: 'var(--pl-cyan)' }} />
        <span className="text-xs uppercase tracking-widest" style={{ color: 'var(--pl-cyan)' }}>Directional Forces</span>
      </div>
      <div className="flex flex-wrap gap-3">
        {FORCES.map(f => (
          <div key={f.name} className="flow-node-sm" style={{ borderColor: f.color + '33' }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: f.color, display: 'inline-block' }} />
            <span style={{ color: 'var(--pl-text)' }}>{f.name}</span>
            <span className="flow-arrow">&harr;</span>
            <span style={{ color: 'var(--pl-muted)' }}>{f.opposite}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ContradictionsFlow() {
  return (
    <div className="flow-card" data-testid="contradictions-flow">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-4 h-4" style={{ color: 'var(--pl-rose)' }} />
        <span className="text-xs uppercase tracking-widest" style={{ color: 'var(--pl-rose)' }}>Fundamental Contradictions</span>
      </div>
      <div className="space-y-3">
        {CONTRADICTIONS.map(c => (
          <div key={c.left} className="flex items-center gap-3">
            <span className="flow-node-sm" style={{ borderColor: 'var(--pl-violet)33' }}>
              {c.left}
            </span>
            <div className="flex-1 h-px" style={{ background: 'linear-gradient(90deg, var(--pl-violet), transparent, var(--pl-rose))' }} />
            <span className="flow-node-sm" style={{ borderColor: 'var(--pl-rose)33' }}>
              {c.right}
            </span>
          </div>
        ))}
      </div>
      <p className="text-xs mt-3" style={{ color: 'var(--pl-dim)' }}>These tensions are not bugs. They are the engine of orientation.</p>
    </div>
  );
}

function OrientationEngine() {
  const nodes = [
    { label: 'Sense', angle: -90, color: 'var(--pl-cyan)' },
    { label: 'Orient', angle: -30, color: 'var(--pl-emerald)' },
    { label: 'Decide', angle: 30, color: 'var(--pl-violet)' },
    { label: 'Act', angle: 90, color: 'var(--pl-amber)' },
    { label: 'Reflect', angle: 150, color: 'var(--pl-rose)' },
    { label: 'Adapt', angle: 210, color: 'var(--pl-dim)' },
  ];
  return (
    <div className="flow-card flex flex-col items-center" data-testid="orientation-engine">
      <div className="flex items-center gap-2 mb-6 self-start">
        <Compass className="w-4 h-4" style={{ color: 'var(--pl-emerald)' }} />
        <span className="text-xs uppercase tracking-widest" style={{ color: 'var(--pl-emerald)' }}>Orientation Engine</span>
      </div>
      <div className="engine-ring">
        <div className="engine-center-label">Orientation<br/>Loop</div>
        {nodes.map(n => {
          const rad = (n.angle * Math.PI) / 180;
          const r = 96;
          const x = Math.cos(rad) * r;
          const y = Math.sin(rad) * r;
          return (
            <div
              key={n.label}
              className="engine-node"
              style={{
                top: `calc(50% + ${y}px - 14px)`,
                left: `calc(50% + ${x}px - 26px)`,
                borderColor: n.color + '44',
                color: n.color,
              }}
            >
              {n.label}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   SECTION WRAPPER with reveal animation
   ═══════════════════════════════════════════════════ */
function Section({ children, className = '', id }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setVisible(true); },
      { threshold: 0.12 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={ref}
      id={id}
      className={`reveal-section ${visible ? 'visible' : ''} ${className}`}
    >
      {children}
    </section>
  );
}

/* ═══════════════════════════════════════════════════
   MAIN PAGE
   ═══════════════════════════════════════════════════ */
export default function PlatformLandingPage({ onEnterApp }) {
  return (
    <div className="platform-landing min-h-screen" data-testid="platform-landing">

      {/* ── HERO ── */}
      <div className="bg-grid min-h-screen flex flex-col justify-center items-center px-4 relative">
        <div className="absolute inset-0 pointer-events-none" style={{
          background: 'radial-gradient(ellipse 60% 40% at 50% 40%, rgba(0,212,255,0.06), transparent)'
        }} />

        <div className="text-center max-w-3xl mx-auto relative z-10" data-testid="hero-section">
          <p className="text-xs uppercase tracking-[0.25em] mb-6" style={{ color: 'var(--pl-muted)' }}>
            Philos Orientation System
          </p>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight mb-6 glow-cyan" style={{ letterSpacing: '-0.03em' }}>
            A computational model<br />of human orientation
          </h1>
          <p className="text-base sm:text-lg mb-10" style={{ color: 'var(--pl-muted)', maxWidth: '520px', margin: '0 auto 40px' }}>
            From cosmos to action. A system that maps how humans navigate
            forces, resolve conflict, and produce impact in the world.
          </p>

          <SystemChain />

          <div className="flex items-center justify-center gap-4 mt-10">
            <button className="cta-btn cta-btn-primary" onClick={onEnterApp} data-testid="cta-enter-app">
              Enter the system <ArrowRight className="w-4 h-4" />
            </button>
            <a href="#model" className="cta-btn cta-btn-ghost">
              Explore the model <ChevronRight className="w-4 h-4" />
            </a>
          </div>
        </div>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2">
          <div className="w-px h-8" style={{ background: 'linear-gradient(to bottom, var(--pl-dim), transparent)' }} />
        </div>
      </div>

      {/* ── PROBLEM ── */}
      <Section id="problem" className="py-24 sm:py-32 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-xs uppercase tracking-[0.2em] mb-4" style={{ color: 'var(--pl-rose)' }}>The Problem</p>
          <div className="section-divider mb-8" />
          <h2 className="text-lg sm:text-xl font-semibold mb-6" style={{ lineHeight: 1.5 }}>
            Humans act without orientation.
          </h2>
          <p className="text-sm leading-relaxed mb-8" style={{ color: 'var(--pl-muted)', maxWidth: '480px', margin: '0 auto' }}>
            Every day, billions of decisions are made without a model of the forces at play.
            Trust erodes. Value is destroyed. Conflict escalates.
            Not because people are bad — but because they lack a system
            to understand where they stand in the field.
          </p>
          <div className="grid grid-cols-3 gap-6 max-w-md mx-auto mt-10">
            <div className="inv-stat">
              <div className="inv-stat-number">73%</div>
              <div className="inv-stat-label">Trust deficit</div>
            </div>
            <div className="inv-stat">
              <div className="inv-stat-number">4.2B</div>
              <div className="inv-stat-label">Daily decisions</div>
            </div>
            <div className="inv-stat">
              <div className="inv-stat-number">0</div>
              <div className="inv-stat-label">Systems for it</div>
            </div>
          </div>
        </div>
      </Section>

      {/* ── MODEL ── */}
      <Section id="model" className="py-24 sm:py-32 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-xs uppercase tracking-[0.2em] mb-4" style={{ color: 'var(--pl-cyan)' }}>The Model</p>
            <div className="section-divider mb-8" />
            <h2 className="text-lg sm:text-xl font-semibold mb-4">
              Orientation is computable.
            </h2>
            <p className="text-sm" style={{ color: 'var(--pl-muted)', maxWidth: '440px', margin: '0 auto' }}>
              The Philos model traces reality from its most fundamental layer
              to the point where a human produces impact.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 items-center">
            <GlobeVisualization />
            <div className="space-y-6">
              <div className="flex items-start gap-3">
                <Globe className="w-4 h-4 mt-1 shrink-0" style={{ color: 'var(--pl-cyan)' }} />
                <div>
                  <p className="text-sm font-medium mb-1">Cosmos Layer</p>
                  <p className="text-xs" style={{ color: 'var(--pl-muted)' }}>
                    Space, matter, and energy — the substrate on which everything operates.
                    The field that contains all possibility.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Layers className="w-4 h-4 mt-1 shrink-0" style={{ color: 'var(--pl-emerald)' }} />
                <div>
                  <p className="text-sm font-medium mb-1">Life Layer</p>
                  <p className="text-xs" style={{ color: 'var(--pl-muted)' }}>
                    Energy becomes motion. Motion becomes life.
                    Self-organizing systems that persist and adapt.
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Eye className="w-4 h-4 mt-1 shrink-0" style={{ color: 'var(--pl-violet)' }} />
                <div>
                  <p className="text-sm font-medium mb-1">Human Forces Layer</p>
                  <p className="text-xs" style={{ color: 'var(--pl-muted)' }}>
                    Internal drives, external pressures, and the conflict between them.
                    This is where orientation begins.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Section>

      {/* ── SYSTEM ENGINE ── */}
      <Section id="engine" className="py-24 sm:py-32 px-4" style={{ background: 'rgba(255,255,255,0.01)' }}>
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-xs uppercase tracking-[0.2em] mb-4" style={{ color: 'var(--pl-emerald)' }}>System Engine</p>
            <div className="section-divider mb-8" />
            <h2 className="text-lg sm:text-xl font-semibold mb-4">
              Forces. Contradictions. Orientation.
            </h2>
            <p className="text-sm" style={{ color: 'var(--pl-muted)', maxWidth: '440px', margin: '0 auto' }}>
              The engine that computes human position in the field.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <ForcesFlow />
            <ContradictionsFlow />
          </div>
          <OrientationEngine />
        </div>
      </Section>

      {/* ── APPLICATION ── */}
      <Section id="application" className="py-24 sm:py-32 px-4">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-xs uppercase tracking-[0.2em] mb-4" style={{ color: 'var(--pl-violet)' }}>Application</p>
            <div className="section-divider mb-8" />
            <h2 className="text-lg sm:text-xl font-semibold mb-4">
              A live system, not a theory.
            </h2>
            <p className="text-sm" style={{ color: 'var(--pl-muted)', maxWidth: '440px', margin: '0 auto' }}>
              Philos is running. Users enter the system, make decisions,
              and produce measurable impact on the collective field.
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <div className="flow-card text-center">
              <Target className="w-5 h-5 mx-auto mb-3" style={{ color: 'var(--pl-cyan)' }} />
              <p className="text-sm font-medium mb-1">Trust Test</p>
              <p className="text-xs" style={{ color: 'var(--pl-muted)' }}>
                Measure your trust state with a single question.
              </p>
            </div>
            <div className="flow-card text-center">
              <Compass className="w-5 h-5 mx-auto mb-3" style={{ color: 'var(--pl-emerald)' }} />
              <p className="text-sm font-medium mb-1">Orientation Map</p>
              <p className="text-xs" style={{ color: 'var(--pl-muted)' }}>
                See where you stand in the directional field.
              </p>
            </div>
            <div className="flow-card text-center">
              <Activity className="w-5 h-5 mx-auto mb-3" style={{ color: 'var(--pl-violet)' }} />
              <p className="text-sm font-medium mb-1">Collective Field</p>
              <p className="text-xs" style={{ color: 'var(--pl-muted)' }}>
                Watch the global field shift in real time.
              </p>
            </div>
          </div>

          <div className="flex justify-center mt-10">
            <button className="cta-btn cta-btn-primary" onClick={onEnterApp} data-testid="cta-trust-test">
              Take the trust test <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </Section>

      {/* ── VISION ── */}
      <Section id="vision" className="py-24 sm:py-32 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-xs uppercase tracking-[0.2em] mb-4" style={{ color: 'var(--pl-amber)' }}>Vision</p>
          <div className="section-divider mb-8" />
          <h2 className="text-lg sm:text-xl font-semibold mb-6" style={{ lineHeight: 1.5 }}>
            Build the orientation layer<br />for human decision-making.
          </h2>
          <p className="text-sm leading-relaxed mb-10" style={{ color: 'var(--pl-muted)', maxWidth: '480px', margin: '0 auto' }}>
            Every decision platform — from social networks to financial systems —
            operates without a model of human orientation. Philos provides
            that missing layer. A computational system that maps forces,
            resolves contradictions, and produces trust.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-lg mx-auto mb-12">
            <div className="inv-stat">
              <div className="inv-stat-number">V+R+T</div>
              <div className="inv-stat-label">Engine</div>
            </div>
            <div className="inv-stat">
              <div className="inv-stat-number">4</div>
              <div className="inv-stat-label">Directions</div>
            </div>
            <div className="inv-stat">
              <div className="inv-stat-number">13</div>
              <div className="inv-stat-label">System layers</div>
            </div>
            <div className="inv-stat">
              <div className="inv-stat-number">1</div>
              <div className="inv-stat-label">Mission</div>
            </div>
          </div>

          <div className="flex items-center justify-center gap-4">
            <button className="cta-btn cta-btn-primary" onClick={onEnterApp} data-testid="cta-enter-system">
              Enter the system <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </Section>

      {/* ── FOOTER ── */}
      <footer className="py-12 px-4 text-center" style={{ borderTop: '1px solid var(--pl-border)' }}>
        <p className="text-xs" style={{ color: 'var(--pl-dim)' }}>
          Philos Orientation System &middot; Mapping human forces since 2024
        </p>
      </footer>
    </div>
  );
}
