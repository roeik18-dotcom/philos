import { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { ArrowRight, ChevronRight, Zap, Target, Layers, Eye, Compass, Activity, ArrowDown } from 'lucide-react';
import Globe from 'react-globe.gl';
import './platform.css';

/* ═══════════════════════════════════════════════════
   DATA
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

const TIER_COLORS = { cosmos: '#00d4ff', life: '#10b981', human: '#7c3aed', action: '#f59e0b' };

const FORCES = [
  { name: 'Contribution', color: '#10b981', opposite: 'Harm', desc: 'Giving vs. taking' },
  { name: 'Recovery', color: '#00d4ff', opposite: 'Avoidance', desc: 'Healing vs. escaping' },
  { name: 'Order', color: '#7c3aed', opposite: 'Chaos', desc: 'Structure vs. entropy' },
  { name: 'Exploration', color: '#f59e0b', opposite: 'Rigidity', desc: 'Growth vs. stagnation' },
];

const CONTRADICTIONS = [
  { left: 'Individual', right: 'Collective', desc: 'Self-interest vs. shared good' },
  { left: 'Stability', right: 'Change', desc: 'Preservation vs. transformation' },
  { left: 'Control', right: 'Freedom', desc: 'Structure vs. emergence' },
];

const FLOW_STEPS = [
  { label: 'Forces', icon: Zap, color: '#00d4ff', desc: 'Internal drives and tensions push the human into motion.' },
  { label: 'Conflict', icon: Activity, color: '#f43f5e', desc: 'Opposing forces collide. The human is caught between poles.' },
  { label: 'Orientation', icon: Compass, color: '#10b981', desc: 'The system computes position in the field of forces.' },
  { label: 'Decision', icon: Target, color: '#7c3aed', desc: 'The moment of commitment. One direction is chosen.' },
  { label: 'Action', icon: Zap, color: '#f59e0b', desc: 'Force is applied to reality. The field changes.' },
  { label: 'Impact', icon: Layers, color: '#00d4ff', desc: 'The change left in the collective field. Trust shifts.' },
];

/* ═══════════════════════════════════════════════════
   ARCHITECTURE — 10 layers of the Philos model
   ═══════════════════════════════════════════════════ */
const ARCHITECTURE = [
  {
    num: '01', id: 'foundation', title: 'Foundation',
    color: '#00d4ff',
    lead: 'Before anything moves, something must exist.',
    body: 'The universe begins with a substrate — space, time, and the potential for structure. Foundation is not a thing. It is the condition that makes things possible. Every system, every organism, every decision rests on a layer it cannot see.',
    principle: 'Existence precedes function.',
  },
  {
    num: '02', id: 'physical-laws', title: 'Physical Laws',
    color: '#0ea5e9',
    lead: 'Reality is not arbitrary. It follows rules.',
    body: 'Gravity, thermodynamics, entropy — these are not suggestions. They are constraints that shape what can and cannot happen. Any model of human behavior that ignores the physical substrate is building on sand.',
    principle: 'Constraints define possibility.',
  },
  {
    num: '03', id: 'life', title: 'Life',
    color: '#10b981',
    lead: 'Matter organizes itself. Complexity emerges.',
    body: 'At some threshold, chemistry becomes biology. Systems begin to self-replicate, adapt, and persist. Life is not a property — it is a pattern. A pattern that resists entropy by consuming energy and producing order.',
    principle: 'Life is organized resistance to decay.',
  },
  {
    num: '04', id: 'human-structure', title: 'Human Structure',
    color: '#34d399',
    lead: 'The human is a specific architecture of life.',
    body: 'A nervous system that models the world. A body that acts on it. A social layer that connects individuals into groups. The human is not a blank slate — it is a structure with built-in capacities, limits, and biases.',
    principle: 'Structure determines range of motion.',
  },
  {
    num: '05', id: 'psychological-systems', title: 'Psychological Systems',
    color: '#7c3aed',
    lead: 'Inside the structure, systems compete.',
    body: 'Cognition, emotion, drives, memory — these are not one system. They are many systems running in parallel, often in contradiction. The human does not have a single will. It has a parliament of impulses negotiating in real time.',
    principle: 'The mind is a system of systems.',
  },
  {
    num: '06', id: 'conflict-engine', title: 'Conflict Engine',
    color: '#f43f5e',
    lead: 'Where opposing forces collide, orientation is born.',
    body: 'Contribution vs. harm. Order vs. chaos. Individual vs. collective. These are not problems to solve — they are permanent tensions. The human exists at the intersection of forces that pull in different directions. Conflict is not a bug. It is the engine.',
    principle: 'Tension is the source of movement.',
  },
  {
    num: '07', id: 'action-model', title: 'Action Model',
    color: '#f59e0b',
    lead: 'Orientation becomes decision. Decision becomes force.',
    body: 'The human senses, orients, decides, and acts. Each action carries a direction — toward contribution or harm, toward order or chaos. The action model maps the path from internal state to external impact.',
    principle: 'Every action has a directional signature.',
  },
  {
    num: '08', id: 'social-system', title: 'Social System',
    color: '#ec4899',
    lead: 'No human acts alone. The field is collective.',
    body: 'Actions propagate. Trust forms networks. Reputation creates asymmetry. The social system is the medium through which individual orientation becomes collective reality. What one person does changes the field for everyone.',
    principle: 'The field is shared.',
  },
  {
    num: '09', id: 'philos-engine', title: 'Philos Engine',
    color: '#00d4ff',
    lead: 'The computational layer that ties it all together.',
    body: 'Value, Risk, and Trust — computed in real time. The Philos engine takes the raw signal of human action, maps it against the directional forces, and produces a trust score. Not a judgment. A measurement. A position in the field.',
    principle: 'V + R + T = Orientation.',
  },
  {
    num: '10', id: 'investor-layer', title: 'Investor Layer',
    color: '#f59e0b',
    lead: 'A system this deep has surface applications.',
    body: 'Trust scoring for platforms. Orientation analytics for organizations. Conflict resolution engines for communities. The Philos model is not an app — it is an infrastructure layer for any system that involves human decision-making.',
    principle: 'Infrastructure scales. Features do not.',
  },
];

/* ═══════════════════════════════════════════════════
   GLOBE — 3D with particle layers
   ═══════════════════════════════════════════════════ */
function generatePoints(count, tier) {
  const color = TIER_COLORS[tier];
  const points = [];
  for (let i = 0; i < count; i++) {
    points.push({
      lat: (Math.random() - 0.5) * 160,
      lng: (Math.random() - 0.5) * 360,
      size: Math.random() * 0.4 + 0.1,
      color,
      tier,
    });
  }
  return points;
}

function generateArcs(count, tier) {
  const color = TIER_COLORS[tier];
  const arcs = [];
  for (let i = 0; i < count; i++) {
    arcs.push({
      startLat: (Math.random() - 0.5) * 120,
      startLng: (Math.random() - 0.5) * 360,
      endLat: (Math.random() - 0.5) * 120,
      endLng: (Math.random() - 0.5) * 360,
      color,
      tier,
    });
  }
  return arcs;
}

function PhilosGlobe() {
  const globeRef = useRef();
  const containerRef = useRef();
  const [dim, setDim] = useState(420);

  const points = useMemo(() => [
    ...generatePoints(40, 'cosmos'),
    ...generatePoints(30, 'life'),
    ...generatePoints(20, 'human'),
    ...generatePoints(15, 'action'),
  ], []);

  const arcs = useMemo(() => [
    ...generateArcs(8, 'cosmos'),
    ...generateArcs(6, 'life'),
    ...generateArcs(5, 'human'),
    ...generateArcs(4, 'action'),
  ], []);

  const rings = useMemo(() => [
    { lat: 30, lng: 60, maxR: 6, propagationSpeed: 2, repeatPeriod: 1200, color: '#00d4ff' },
    { lat: -20, lng: -100, maxR: 5, propagationSpeed: 2, repeatPeriod: 1400, color: '#10b981' },
    { lat: 50, lng: -30, maxR: 4, propagationSpeed: 3, repeatPeriod: 1000, color: '#7c3aed' },
    { lat: -40, lng: 120, maxR: 5, propagationSpeed: 2, repeatPeriod: 1600, color: '#f59e0b' },
  ], []);

  useEffect(() => {
    if (!containerRef.current) return;
    const update = () => {
      const w = containerRef.current?.offsetWidth || 420;
      setDim(Math.min(w, 500));
    };
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, []);

  useEffect(() => {
    const g = globeRef.current;
    if (!g) return;
    g.controls().autoRotate = true;
    g.controls().autoRotateSpeed = 0.8;
    g.controls().enableZoom = false;
    g.pointOfView({ altitude: 2.2 });
  }, []);

  const globeImageUrl = useCallback(() =>
    '//unpkg.com/three-globe/example/img/earth-dark.jpg', []);
  const bumpImageUrl = useCallback(() =>
    '//unpkg.com/three-globe/example/img/earth-topology.png', []);

  return (
    <div ref={containerRef} className="globe-3d-container" data-testid="globe-3d">
      <Globe
        ref={globeRef}
        width={dim}
        height={dim}
        globeImageUrl={globeImageUrl()}
        bumpImageUrl={bumpImageUrl()}
        backgroundColor="rgba(0,0,0,0)"
        atmosphereColor="#00d4ff"
        atmosphereAltitude={0.18}
        pointsData={points}
        pointLat="lat"
        pointLng="lng"
        pointAltitude={d => d.size * 0.04}
        pointRadius={d => d.size * 0.3}
        pointColor="color"
        arcsData={arcs}
        arcStartLat="startLat"
        arcStartLng="startLng"
        arcEndLat="endLat"
        arcEndLng="endLng"
        arcColor="color"
        arcStroke={0.4}
        arcDashLength={0.4}
        arcDashGap={0.2}
        arcDashAnimateTime={3000}
        arcAltitudeAutoScale={0.3}
        ringsData={rings}
        ringLat="lat"
        ringLng="lng"
        ringMaxRadius="maxR"
        ringPropagationSpeed="propagationSpeed"
        ringRepeatPeriod="repeatPeriod"
        ringColor="color"
      />
      {/* Layer legend */}
      <div className="globe-legend">
        {Object.entries(TIER_COLORS).map(([tier, color]) => (
          <div key={tier} className="globe-legend-item">
            <span className="globe-legend-dot" style={{ background: color }} />
            <span>{tier.charAt(0).toUpperCase() + tier.slice(1)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   SYSTEM CHAIN — animated node line
   ═══════════════════════════════════════════════════ */
function SystemChain() {
  const [activeNode, setActiveNode] = useState(null);

  return (
    <div data-testid="system-chain">
      <div className="chain-container">
        {CHAIN.map((node, i) => (
          <div key={node.id} style={{ display: 'flex', alignItems: 'center' }}>
            <div
              className="chain-node"
              onMouseEnter={() => setActiveNode(i)}
              onMouseLeave={() => setActiveNode(null)}
            >
              <div
                className="node-dot"
                style={{
                  background: TIER_COLORS[node.tier],
                  boxShadow: activeNode === i
                    ? `0 0 20px ${TIER_COLORS[node.tier]}, 0 0 40px ${TIER_COLORS[node.tier]}50`
                    : `0 0 8px ${TIER_COLORS[node.tier]}80`,
                  transform: activeNode === i ? 'scale(1.6)' : 'scale(1)',
                  transition: 'all 0.3s ease',
                }}
              />
              <span className="node-label" style={{
                color: activeNode === i ? '#fff' : undefined,
              }}>{node.label}</span>
            </div>
            {i < CHAIN.length - 1 && (
              <div className="chain-connector" style={{ animationDelay: `${i * 0.15}s` }} />
            )}
          </div>
        ))}
      </div>
      {activeNode !== null && (
        <p className="text-center text-xs mt-2 animate-fadeIn" style={{ color: TIER_COLORS[CHAIN[activeNode].tier] }}>
          {CHAIN[activeNode].tip}
        </p>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   INTERACTIVE SYSTEM MAP — layered model
   ═══════════════════════════════════════════════════ */
function SystemMap() {
  const [expandedTier, setExpandedTier] = useState(null);

  const tiers = [
    {
      id: 'cosmos', label: 'Cosmos Layer', color: '#00d4ff',
      nodes: CHAIN.filter(c => c.tier === 'cosmos'),
      desc: 'The foundational substrate. Space, matter, and energy define the field of all possibility.',
    },
    {
      id: 'life', label: 'Life Layer', color: '#10b981',
      nodes: CHAIN.filter(c => c.tier === 'life'),
      desc: 'Energy becomes motion. Motion becomes life. Self-organizing systems emerge and persist.',
    },
    {
      id: 'human', label: 'Human Layer', color: '#7c3aed',
      nodes: CHAIN.filter(c => c.tier === 'human'),
      desc: 'The agent of meaning. Internal forces, external pressures, and the conflict between them.',
    },
    {
      id: 'action', label: 'Action Layer', color: '#f59e0b',
      nodes: CHAIN.filter(c => c.tier === 'action'),
      desc: 'Orientation crystallizes into decision, decision into action, action into impact on the field.',
    },
  ];

  return (
    <div className="system-map" data-testid="system-map">
      {tiers.map((tier, ti) => (
        <div key={tier.id}>
          <button
            className="system-map-tier"
            onClick={() => setExpandedTier(expandedTier === tier.id ? null : tier.id)}
            style={{ '--tier-color': tier.color }}
            data-testid={`tier-${tier.id}`}
          >
            <div className="system-map-tier-header">
              <span className="system-map-tier-dot" style={{ background: tier.color }} />
              <span className="system-map-tier-label">{tier.label}</span>
              <span className="system-map-tier-count">{tier.nodes.length} stages</span>
            </div>
            <div className="system-map-tier-nodes">
              {tier.nodes.map(n => (
                <span key={n.id} className="system-map-node" style={{ borderColor: tier.color + '44' }}>
                  {n.label}
                </span>
              ))}
            </div>
            {expandedTier === tier.id && (
              <p className="system-map-tier-desc animate-fadeIn">{tier.desc}</p>
            )}
          </button>
          {ti < tiers.length - 1 && (
            <div className="system-map-connector">
              <ArrowDown className="w-3 h-3" style={{ color: 'rgba(255,255,255,0.15)' }} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   FLOW DIAGRAM — Forces → Impact
   ═══════════════════════════════════════════════════ */
function ActionFlow() {
  const [activeStep, setActiveStep] = useState(null);

  return (
    <div className="action-flow" data-testid="action-flow">
      <div className="action-flow-steps">
        {FLOW_STEPS.map((step, i) => {
          const Icon = step.icon;
          const isActive = activeStep === i;
          return (
            <div key={step.label} className="action-flow-step-wrapper">
              <button
                className={`action-flow-step ${isActive ? 'active' : ''}`}
                onMouseEnter={() => setActiveStep(i)}
                onMouseLeave={() => setActiveStep(null)}
                style={{ '--step-color': step.color }}
              >
                <div className="action-flow-icon" style={{
                  background: isActive ? step.color + '20' : 'transparent',
                  borderColor: step.color + (isActive ? '66' : '33'),
                }}>
                  <Icon className="w-4 h-4" style={{ color: step.color }} />
                </div>
                <span className="action-flow-label">{step.label}</span>
                {isActive && (
                  <p className="action-flow-desc animate-fadeIn">{step.desc}</p>
                )}
              </button>
              {i < FLOW_STEPS.length - 1 && (
                <div className="action-flow-connector">
                  <ChevronRight className="w-3 h-3" style={{ color: 'rgba(255,255,255,0.12)' }} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   ARCHITECTURE — vertical deep-dive
   ═══════════════════════════════════════════════════ */
function ArchitectureLayer({ layer, index }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setVisible(true); },
      { threshold: 0.15 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const isEven = index % 2 === 0;

  return (
    <div
      ref={ref}
      className={`arch-layer ${visible ? 'arch-visible' : ''}`}
      data-testid={`arch-layer-${layer.id}`}
    >
      <div className="arch-layer-inner" style={{ '--arch-color': layer.color }}>
        <div className="arch-num" style={{ color: layer.color }}>{layer.num}</div>
        <div className={`arch-content ${isEven ? '' : 'arch-content-right'}`}>
          <div className="arch-text">
            <h3 className="arch-title" style={{ color: layer.color }}>{layer.title}</h3>
            <p className="arch-lead">{layer.lead}</p>
            <p className="arch-body">{layer.body}</p>
            <div className="arch-principle">
              <span className="arch-principle-marker" style={{ background: layer.color }} />
              <span>{layer.principle}</span>
            </div>
          </div>
          <div className="arch-line" style={{ background: `linear-gradient(to bottom, ${layer.color}22, transparent)` }} />
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   SECTION WRAPPER — reveal on scroll
   ═══════════════════════════════════════════════════ */
function Section({ children, className = '', id, style }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setVisible(true); },
      { threshold: 0.08 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <section ref={ref} id={id} style={style}
      className={`reveal-section ${visible ? 'visible' : ''} ${className}`}>
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

      {/* ═══ HERO ═══ */}
      <div className="hero-section bg-grid" data-testid="hero-section">
        <div className="hero-glow" />

        <div className="hero-content">
          <div className="hero-badge">Philos Orientation System</div>

          <h1 className="hero-title glow-cyan">
            The computational model<br />of human orientation
          </h1>

          <p className="hero-subtitle">
            From cosmos to action. A system that maps how humans navigate forces,
            resolve conflict, and produce measurable impact in the world.
          </p>

          <SystemChain />

          <div className="hero-cta">
            <button className="cta-btn cta-btn-primary" onClick={onEnterApp} data-testid="cta-enter-app">
              Enter the system <ArrowRight className="w-4 h-4" />
            </button>
            <a href="#model" className="cta-btn cta-btn-ghost">
              Explore the model <ChevronRight className="w-4 h-4" />
            </a>
          </div>
        </div>

        <div className="hero-scroll-hint">
          <ArrowDown className="w-4 h-4" style={{ color: 'rgba(255,255,255,0.2)' }} />
        </div>
      </div>

      {/* ═══ PROBLEM ═══ */}
      <Section id="problem" className="py-24 sm:py-32 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <div className="section-label" style={{ color: 'var(--pl-rose)' }}>The Problem</div>
          <div className="section-divider mb-8" />
          <h2 className="section-heading">
            Humans act without orientation.
          </h2>
          <p className="section-body">
            Every day, billions of decisions are made without a model of the forces at play.
            Trust erodes. Value is destroyed. Conflict escalates.
            Not because people are bad — but because they lack a system
            to understand where they stand in the field.
          </p>
          <div className="grid grid-cols-3 gap-6 max-w-md mx-auto mt-12">
            <div className="inv-stat"><div className="inv-stat-number">73%</div><div className="inv-stat-label">Trust deficit</div></div>
            <div className="inv-stat"><div className="inv-stat-number">4.2B</div><div className="inv-stat-label">Daily decisions</div></div>
            <div className="inv-stat"><div className="inv-stat-number">0</div><div className="inv-stat-label">Systems for it</div></div>
          </div>
        </div>
      </Section>

      {/* ═══ MODEL — 3D Globe ═══ */}
      <Section id="model" className="py-24 sm:py-32 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <div className="section-label" style={{ color: 'var(--pl-cyan)' }}>The Model</div>
            <div className="section-divider mb-8" />
            <h2 className="section-heading">Orientation is computable.</h2>
            <p className="section-body-sm">
              The Philos model traces reality from its most fundamental layer
              to the point where a human produces impact.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 items-center">
            <PhilosGlobe />
            <div className="space-y-6">
              <div className="layer-card">
                <Layers className="w-4 h-4 shrink-0" style={{ color: '#00d4ff' }} />
                <div>
                  <p className="layer-card-title">Cosmos Layer</p>
                  <p className="layer-card-desc">
                    Space, matter, and energy — the substrate on which everything operates.
                    The field that contains all possibility.
                  </p>
                </div>
              </div>
              <div className="layer-card">
                <Layers className="w-4 h-4 shrink-0" style={{ color: '#10b981' }} />
                <div>
                  <p className="layer-card-title">Life Layer</p>
                  <p className="layer-card-desc">
                    Energy becomes motion. Motion becomes life.
                    Self-organizing systems that persist and adapt.
                  </p>
                </div>
              </div>
              <div className="layer-card">
                <Eye className="w-4 h-4 shrink-0" style={{ color: '#7c3aed' }} />
                <div>
                  <p className="layer-card-title">Human Forces Layer</p>
                  <p className="layer-card-desc">
                    Internal drives, external pressures, and the conflict between them.
                    This is where orientation begins.
                  </p>
                </div>
              </div>
              <div className="layer-card">
                <Zap className="w-4 h-4 shrink-0" style={{ color: '#f59e0b' }} />
                <div>
                  <p className="layer-card-title">Action Layer</p>
                  <p className="layer-card-desc">
                    Decision, action, impact. Force is applied to reality
                    and the collective field shifts.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Section>

      {/* ═══ PHILOS ARCHITECTURE — 10 deep layers ═══ */}
      <section id="architecture" className="arch-section" data-testid="architecture-section">
        <div className="arch-header">
          <div className="section-label" style={{ color: 'var(--pl-cyan)' }}>Philos Architecture</div>
          <div className="section-divider mb-8" />
          <h2 className="section-heading">10 layers. From substrate to system.</h2>
          <p className="section-body-sm">
            The complete architecture of the Philos model — from the physical
            foundation of reality to the application layer.
          </p>
        </div>
        <div className="arch-layers">
          {ARCHITECTURE.map((layer, i) => (
            <ArchitectureLayer key={layer.id} layer={layer} index={i} />
          ))}
        </div>
      </section>

      {/* ═══ SYSTEM MAP — Interactive layers ═══ */}
      <Section id="system-map" className="py-24 sm:py-32 px-4" style={{ background: 'rgba(255,255,255,0.01)' }}>
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <div className="section-label" style={{ color: 'var(--pl-violet)' }}>System Map</div>
            <div className="section-divider mb-8" />
            <h2 className="section-heading">13 stages. 4 layers. 1 system.</h2>
            <p className="section-body-sm">
              Click each layer to explore the stages within.
            </p>
          </div>
          <SystemMap />
        </div>
      </Section>

      {/* ═══ SYSTEM ENGINE — Forces + Contradictions ═══ */}
      <Section id="engine" className="py-24 sm:py-32 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <div className="section-label" style={{ color: 'var(--pl-emerald)' }}>System Engine</div>
            <div className="section-divider mb-8" />
            <h2 className="section-heading">Forces. Contradictions. Orientation.</h2>
            <p className="section-body-sm">
              The engine that computes human position in the field.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Forces */}
            <div className="flow-card" data-testid="forces-flow">
              <div className="flow-card-header">
                <Zap className="w-4 h-4" style={{ color: '#00d4ff' }} />
                <span style={{ color: '#00d4ff' }}>Directional Forces</span>
              </div>
              <div className="space-y-3">
                {FORCES.map(f => (
                  <div key={f.name} className="force-row">
                    <div className="force-dot" style={{ background: f.color }} />
                    <span className="force-name">{f.name}</span>
                    <div className="force-line" style={{ background: `linear-gradient(90deg, ${f.color}44, ${f.color}11)` }} />
                    <span className="force-opposite">{f.opposite}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Contradictions */}
            <div className="flow-card" data-testid="contradictions-flow">
              <div className="flow-card-header">
                <Activity className="w-4 h-4" style={{ color: '#f43f5e' }} />
                <span style={{ color: '#f43f5e' }}>Fundamental Contradictions</span>
              </div>
              <div className="space-y-3">
                {CONTRADICTIONS.map(c => (
                  <div key={c.left} className="contradiction-row">
                    <span className="contradiction-pole">{c.left}</span>
                    <div className="contradiction-line" />
                    <span className="contradiction-pole">{c.right}</span>
                  </div>
                ))}
              </div>
              <p className="text-xs mt-4" style={{ color: 'rgba(255,255,255,0.2)' }}>
                These tensions are not bugs. They are the engine of orientation.
              </p>
            </div>
          </div>

          {/* Action Flow */}
          <div className="flow-card" data-testid="action-flow-section">
            <div className="flow-card-header mb-6">
              <Compass className="w-4 h-4" style={{ color: '#10b981' }} />
              <span style={{ color: '#10b981' }}>Forces &rarr; Conflict &rarr; Orientation &rarr; Decision &rarr; Action &rarr; Impact</span>
            </div>
            <ActionFlow />
          </div>
        </div>
      </Section>

      {/* ═══ APPLICATION ═══ */}
      <Section id="application" className="py-24 sm:py-32 px-4" style={{ background: 'rgba(255,255,255,0.01)' }}>
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <div className="section-label" style={{ color: '#7c3aed' }}>Application</div>
            <div className="section-divider mb-8" />
            <h2 className="section-heading">A live system, not a theory.</h2>
            <p className="section-body-sm">
              Philos is running. Users enter the system, make decisions,
              and produce measurable impact on the collective field.
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <div className="flow-card text-center">
              <Target className="w-5 h-5 mx-auto mb-3" style={{ color: '#00d4ff' }} />
              <p className="text-sm font-medium mb-1">Trust Test</p>
              <p className="text-xs" style={{ color: 'var(--pl-muted)' }}>Measure your trust state with a single question.</p>
            </div>
            <div className="flow-card text-center">
              <Compass className="w-5 h-5 mx-auto mb-3" style={{ color: '#10b981' }} />
              <p className="text-sm font-medium mb-1">Orientation Map</p>
              <p className="text-xs" style={{ color: 'var(--pl-muted)' }}>See where you stand in the directional field.</p>
            </div>
            <div className="flow-card text-center">
              <Activity className="w-5 h-5 mx-auto mb-3" style={{ color: '#7c3aed' }} />
              <p className="text-sm font-medium mb-1">Collective Field</p>
              <p className="text-xs" style={{ color: 'var(--pl-muted)' }}>Watch the global field shift in real time.</p>
            </div>
          </div>

          <div className="flex justify-center mt-10">
            <button className="cta-btn cta-btn-primary" onClick={onEnterApp} data-testid="cta-trust-test">
              Take the trust test <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </Section>

      {/* ═══ VISION ═══ */}
      <Section id="vision" className="py-24 sm:py-32 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <div className="section-label" style={{ color: '#f59e0b' }}>Vision</div>
          <div className="section-divider mb-8" />
          <h2 className="section-heading" style={{ lineHeight: 1.5 }}>
            Build the orientation layer<br />for human decision-making.
          </h2>
          <p className="section-body">
            Every decision platform — from social networks to financial systems —
            operates without a model of human orientation. Philos provides
            that missing layer. A computational system that maps forces,
            resolves contradictions, and produces trust.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-lg mx-auto mt-12 mb-12">
            <div className="inv-stat"><div className="inv-stat-number">V+R+T</div><div className="inv-stat-label">Engine</div></div>
            <div className="inv-stat"><div className="inv-stat-number">4</div><div className="inv-stat-label">Directions</div></div>
            <div className="inv-stat"><div className="inv-stat-number">13</div><div className="inv-stat-label">System layers</div></div>
            <div className="inv-stat"><div className="inv-stat-number">1</div><div className="inv-stat-label">Mission</div></div>
          </div>

          <button className="cta-btn cta-btn-primary" onClick={onEnterApp} data-testid="cta-enter-system">
            Enter the system <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </Section>

      {/* ═══ FOOTER ═══ */}
      <footer className="py-12 px-4 text-center" style={{ borderTop: '1px solid var(--pl-border)' }}>
        <p className="text-xs" style={{ color: 'var(--pl-dim)' }}>
          Philos Orientation System &middot; Mapping human forces since 2024
        </p>
      </footer>
    </div>
  );
}
