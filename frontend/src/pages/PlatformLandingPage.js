import { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { ArrowRight, ChevronRight, Zap, Target, Layers, Eye, Compass, Activity, ArrowDown, Flame, Users, MapPin, ShieldCheck } from 'lucide-react';
import Globe from 'react-globe.gl';
import './platform.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/* ═══════════════════════════════════════════════════
   3D GLOBE — hero visual
   ═══════════════════════════════════════════════════ */
function PhilosGlobe() {
  const globeRef = useRef();
  const containerRef = useRef();
  const [dim, setDim] = useState(500);

  const points = useMemo(() => {
    const pts = [];
    for (let i = 0; i < 60; i++) {
      pts.push({
        lat: (Math.random() - 0.5) * 140,
        lng: (Math.random() - 0.5) * 340,
        size: 0.3 + Math.random() * 0.8,
        color: ['#00d4ff', '#10b981', '#7c3aed', '#f59e0b'][Math.floor(Math.random() * 4)],
      });
    }
    return pts;
  }, []);

  const arcs = useMemo(() => {
    const a = [];
    for (let i = 0; i < 18; i++) {
      a.push({
        startLat: (Math.random() - 0.5) * 140,
        startLng: (Math.random() - 0.5) * 340,
        endLat: (Math.random() - 0.5) * 140,
        endLng: (Math.random() - 0.5) * 340,
        color: ['rgba(0,212,255,0.25)', 'rgba(16,185,129,0.25)', 'rgba(124,58,237,0.25)'][i % 3],
      });
    }
    return a;
  }, []);

  const rings = useMemo(() => [
    { lat: 32.08, lng: 34.78, maxR: 4, propagationSpeed: 2, repeatPeriod: 2000, color: () => 'rgba(0,212,255,0.3)' },
    { lat: 40.71, lng: -74.01, maxR: 3, propagationSpeed: 1.5, repeatPeriod: 2500, color: () => 'rgba(16,185,129,0.3)' },
    { lat: 51.51, lng: -0.13, maxR: 3, propagationSpeed: 1.8, repeatPeriod: 3000, color: () => 'rgba(124,58,237,0.3)' },
  ], []);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      setDim(Math.min(entry.contentRect.width, entry.contentRect.height, 600));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const g = globeRef.current;
    if (!g) return;
    g.controls().autoRotate = true;
    g.controls().autoRotateSpeed = 0.6;
    g.controls().enableZoom = false;
    g.pointOfView({ altitude: 2.2 });
  }, []);

  const globeImg = useCallback(() => '//unpkg.com/three-globe/example/img/earth-dark.jpg', []);
  const bumpImg = useCallback(() => '//unpkg.com/three-globe/example/img/earth-topology.png', []);

  return (
    <div ref={containerRef} className="globe-3d-container" data-testid="globe-3d">
      <Globe
        ref={globeRef}
        width={dim}
        height={dim}
        globeImageUrl={globeImg()}
        bumpImageUrl={bumpImg()}
        backgroundColor="rgba(0,0,0,0)"
        atmosphereColor="#00d4ff"
        atmosphereAltitude={0.18}
        pointsData={points}
        pointLat="lat" pointLng="lng"
        pointAltitude={d => d.size * 0.04}
        pointRadius={d => d.size * 0.3}
        pointColor="color"
        arcsData={arcs}
        arcStartLat="startLat" arcStartLng="startLng"
        arcEndLat="endLat" arcEndLng="endLng"
        arcColor="color" arcStroke={0.4}
        arcDashLength={0.4} arcDashGap={0.2} arcDashAnimateTime={3000}
        arcAltitudeAutoScale={0.3}
        ringsData={rings}
        ringLat="lat" ringLng="lng"
        ringMaxRadius="maxR"
        ringPropagationSpeed="propagationSpeed"
        ringRepeatPeriod="repeatPeriod"
        ringColor="color"
      />
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   LIVE STATS BAR
   ═══════════════════════════════════════════════════ */
function LiveStats() {
  const [stats, setStats] = useState({ actions: 0, users: 0, communities: 0, trust: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [feedRes, lbRes, cfRes] = await Promise.all([
          fetch(`${API_URL}/api/actions/feed?limit=50`),
          fetch(`${API_URL}/api/leaderboard`),
          fetch(`${API_URL}/api/community-funds`),
        ]);
        const feed = await feedRes.json();
        const lb = await lbRes.json();
        const cf = await cfRes.json();
        const totalTrust = (lb.leaders || []).reduce((s, l) => s + l.trust_score, 0);
        setStats({
          actions: (feed.actions || []).length,
          users: (lb.leaders || []).length,
          communities: (cf.funds || []).length,
          trust: Math.round(totalTrust),
        });
      } catch (e) { /* silent */ }
    };
    fetchStats();
  }, []);

  return (
    <div className="live-stats" data-testid="live-stats">
      <div className="live-stat">
        <Zap className="w-3.5 h-3.5" style={{ color: '#00d4ff' }} />
        <span className="live-stat-num">{stats.actions}</span>
        <span className="live-stat-label">Actions</span>
      </div>
      <div className="live-stat-sep" />
      <div className="live-stat">
        <Users className="w-3.5 h-3.5" style={{ color: '#10b981' }} />
        <span className="live-stat-num">{stats.users}</span>
        <span className="live-stat-label">Contributors</span>
      </div>
      <div className="live-stat-sep" />
      <div className="live-stat">
        <MapPin className="w-3.5 h-3.5" style={{ color: '#7c3aed' }} />
        <span className="live-stat-num">{stats.communities}</span>
        <span className="live-stat-label">Communities</span>
      </div>
      <div className="live-stat-sep" />
      <div className="live-stat">
        <Flame className="w-3.5 h-3.5" style={{ color: '#f59e0b' }} />
        <span className="live-stat-num">{stats.trust}</span>
        <span className="live-stat-label">Trust Generated</span>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   SCROLL-REVEAL SECTION
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
   ARCHITECTURE LAYER (deep scroll)
   ═══════════════════════════════════════════════════ */
const ARCHITECTURE = [
  { num: '01', id: 'foundation', title: 'Foundation', color: '#00d4ff', lead: 'Before anything moves, something must exist.', body: 'The universe begins with a substrate — space, time, and the potential for structure.', principle: 'Existence precedes function.' },
  { num: '02', id: 'physical-laws', title: 'Physical Laws', color: '#0ea5e9', lead: 'Reality is not arbitrary. It follows rules.', body: 'Gravity, thermodynamics, entropy — constraints that shape what can and cannot happen.', principle: 'Constraints define possibility.' },
  { num: '03', id: 'life', title: 'Life', color: '#10b981', lead: 'Matter organizes itself. Complexity emerges.', body: 'Systems begin to self-replicate, adapt, and persist. Life is organized resistance to decay.', principle: 'Life is organized resistance to decay.' },
  { num: '04', id: 'human-structure', title: 'Human Structure', color: '#34d399', lead: 'The human is a specific architecture of life.', body: 'A nervous system that models the world. A body that acts on it. A social layer that connects.', principle: 'Structure determines range of motion.' },
  { num: '05', id: 'forces', title: 'Forces', color: '#7c3aed', lead: 'The human is not still. Forces are always acting.', body: 'Contribution vs. harm. Recovery vs. avoidance. Order vs. chaos. Exploration vs. rigidity.', principle: 'No neutrality. Only direction.' },
  { num: '06', id: 'contradictions', title: 'Contradictions', color: '#8b5cf6', lead: 'Forces collide. Contradictions are structural.', body: 'Individual vs. collective. Stability vs. change. Control vs. freedom.', principle: 'Contradiction is the engine of orientation.' },
  { num: '07', id: 'orientation', title: 'Orientation', color: '#f59e0b', lead: 'The system computes a position.', body: 'Given forces and contradictions, orientation is where you stand in the field.', principle: 'Position is computable.' },
  { num: '08', id: 'decision', title: 'Decision', color: '#f97316', lead: 'Orientation becomes commitment.', body: 'The moment of decision collapses possibility into action.', principle: 'Decision is the collapse of the field.' },
  { num: '09', id: 'action', title: 'Action', color: '#f43f5e', lead: 'Force is applied to reality.', body: 'Action is not random. It is the output of the entire chain. It changes the field.', principle: 'Action is directed force.' },
  { num: '10', id: 'impact', title: 'Impact', color: '#ec4899', lead: 'The field has changed.', body: 'Trust shifts. Reputation updates. The collective field absorbs the new data.', principle: 'Impact is the delta on the field.' },
];

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

  return (
    <div ref={ref} className={`arch-layer ${visible ? 'arch-visible' : ''}`} data-testid={`arch-layer-${layer.id}`}>
      <div className="arch-layer-inner" style={{ '--arch-color': layer.color }}>
        <div className="arch-num" style={{ color: layer.color }}>{layer.num}</div>
        <div className="arch-content">
          <div className="arch-text">
            <h3 className="arch-title" style={{ color: layer.color }}>{layer.title}</h3>
            <p className="arch-lead">{layer.lead}</p>
            <p className="arch-body">{layer.body}</p>
            <div className="arch-principle">
              <span className="arch-principle-marker" style={{ background: layer.color }} />
              <span>{layer.principle}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   MAIN PAGE — Product First
   ═══════════════════════════════════════════════════ */
export default function PlatformLandingPage({ onEnterApp }) {
  return (
    <div className="platform-landing min-h-screen" data-testid="platform-landing">

      {/* ═══ HERO — Globe + Product Message ═══ */}
      <div className="hero-section bg-grid" data-testid="hero-section">
        <div className="hero-glow" />

        <div className="hero-globe-layout">
          <div className="hero-text-col">
            <div className="hero-badge-live">
              <span className="hero-badge-dot" />
              Live Network
            </div>

            <h1 className="hero-title glow-cyan">
              Your actions build trust.<br />Trust unlocks opportunity.
            </h1>

            <p className="hero-subtitle">
              Philos is a live network where real actions produce measurable trust.
              Contribute to your community, earn a Trust Score,
              and unlock opportunities others can't see.
            </p>

            <button className="cta-btn cta-btn-primary hero-cta-main" onClick={onEnterApp} data-testid="cta-enter-app">
              Start contributing <ArrowRight className="w-4 h-4" />
            </button>

            <LiveStats />
          </div>

          <div className="hero-globe-col">
            <PhilosGlobe />
          </div>
        </div>

        <div className="hero-scroll-hint">
          <ArrowDown className="w-4 h-4" style={{ color: 'rgba(255,255,255,0.2)' }} />
        </div>
      </div>

      {/* ═══ HOW IT WORKS — 3-step loop ═══ */}
      <Section id="how-it-works" className="py-24 sm:py-32 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <div className="section-label" style={{ color: '#00d4ff' }}>How It Works</div>
            <div className="section-divider mb-8" />
            <h2 className="section-heading">Three steps. One loop.</h2>
            <p className="section-body-sm">Every action feeds the system. Every reaction builds trust. Every threshold unlocks something real.</p>
          </div>

          <div className="loop-grid">
            <div className="loop-card">
              <div className="loop-card-num">1</div>
              <div className="loop-card-icon" style={{ background: 'rgba(0,212,255,0.08)', borderColor: 'rgba(0,212,255,0.2)' }}>
                <Zap className="w-6 h-6" style={{ color: '#00d4ff' }} />
              </div>
              <h3 className="loop-card-title">Post an Action</h3>
              <p className="loop-card-desc">Share something real you did for your community. Education, environment, health — any category.</p>
            </div>
            <div className="loop-connector"><ChevronRight className="w-5 h-5" style={{ color: 'rgba(255,255,255,0.1)' }} /></div>
            <div className="loop-card">
              <div className="loop-card-num">2</div>
              <div className="loop-card-icon" style={{ background: 'rgba(245,158,11,0.08)', borderColor: 'rgba(245,158,11,0.2)' }}>
                <Flame className="w-6 h-6" style={{ color: '#f59e0b' }} />
              </div>
              <h3 className="loop-card-title">Earn Trust</h3>
              <p className="loop-card-desc">Others react — Support, Useful, Verified. Each reaction adds to your Trust Score. Verified actions multiply it.</p>
            </div>
            <div className="loop-connector"><ChevronRight className="w-5 h-5" style={{ color: 'rgba(255,255,255,0.1)' }} /></div>
            <div className="loop-card">
              <div className="loop-card-num">3</div>
              <div className="loop-card-icon" style={{ background: 'rgba(16,185,129,0.08)', borderColor: 'rgba(16,185,129,0.2)' }}>
                <ShieldCheck className="w-6 h-6" style={{ color: '#10b981' }} />
              </div>
              <h3 className="loop-card-title">Unlock Opportunities</h3>
              <p className="loop-card-desc">Grants, jobs, collaborations — all gated by Trust Score. Higher trust means more access.</p>
            </div>
          </div>
        </div>
      </Section>

      {/* ═══ WHAT YOU GET — product features ═══ */}
      <Section id="features" className="py-24 sm:py-32 px-4" style={{ background: 'rgba(255,255,255,0.01)' }}>
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <div className="section-label" style={{ color: '#10b981' }}>The Platform</div>
            <div className="section-divider mb-8" />
            <h2 className="section-heading">Everything you need to build trust.</h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { icon: Zap, color: '#00d4ff', title: 'Action Feed', desc: 'A live stream of verified community actions.' },
              { icon: Flame, color: '#f59e0b', title: 'Trust Score', desc: 'Earned through reactions. Decays if you stop contributing.' },
              { icon: Target, color: '#10b981', title: 'Opportunities', desc: 'Jobs, grants, and collabs gated by your Trust Score.' },
              { icon: MapPin, color: '#7c3aed', title: 'Impact Map', desc: 'See actions visualized by location on a live map.' },
              { icon: Users, color: '#ec4899', title: 'Community Funds', desc: 'Transparent financial visibility for every community.' },
              { icon: ShieldCheck, color: '#0ea5e9', title: 'Trust Integrity', desc: 'Anti-spam, verification levels, and decay prevent gaming.' },
            ].map(f => {
              const Icon = f.icon;
              return (
                <div key={f.title} className="flow-card feature-card">
                  <Icon className="w-5 h-5 mb-3" style={{ color: f.color }} />
                  <p className="text-sm font-medium mb-1">{f.title}</p>
                  <p className="text-xs" style={{ color: 'var(--pl-muted)' }}>{f.desc}</p>
                </div>
              );
            })}
          </div>

          <div className="flex justify-center mt-10">
            <button className="cta-btn cta-btn-primary" onClick={onEnterApp} data-testid="cta-explore-platform">
              Explore the platform <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </Section>

      {/* ═══ THE MODEL — theory (moved lower) ═══ */}
      <Section id="model" className="py-24 sm:py-32 px-4">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <div className="section-label" style={{ color: '#7c3aed' }}>The Model</div>
            <div className="section-divider mb-8" />
            <h2 className="section-heading">Built on a computational model of human orientation.</h2>
            <p className="section-body-sm">
              Philos isn't just a platform. It's built on a formal model that traces how humans
              navigate forces, resolve conflict, and produce impact.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {[
              { icon: Layers, color: '#00d4ff', title: 'Cosmos to Action', desc: 'A 13-stage chain from the substrate of reality to measurable human impact.' },
              { icon: Zap, color: '#10b981', title: 'Directional Forces', desc: 'Contribution vs. harm, recovery vs. avoidance, order vs. chaos, exploration vs. rigidity.' },
              { icon: Activity, color: '#f43f5e', title: 'Contradictions', desc: 'Individual vs. collective, stability vs. change, control vs. freedom.' },
              { icon: Compass, color: '#f59e0b', title: 'V+R+T Engine', desc: 'Value, Risk, and Trust — the three-variable engine that computes orientation.' },
            ].map(m => {
              const Icon = m.icon;
              return (
                <div key={m.title} className="layer-card">
                  <Icon className="w-4 h-4 shrink-0" style={{ color: m.color }} />
                  <div>
                    <p className="layer-card-title">{m.title}</p>
                    <p className="layer-card-desc">{m.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex justify-center mt-10">
            <a href="#architecture" className="cta-btn cta-btn-ghost">
              Read the full architecture <ChevronRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </Section>

      {/* ═══ ARCHITECTURE — 10 deep layers (investor depth) ═══ */}
      <section id="architecture" className="arch-section" data-testid="architecture-section">
        <div className="arch-header">
          <div className="section-label" style={{ color: '#00d4ff' }}>Deep Dive</div>
          <div className="section-divider mb-8" />
          <h2 className="section-heading">10 layers. From substrate to system.</h2>
          <p className="section-body-sm">
            The complete architecture of the Philos model.
          </p>
        </div>
        <div className="arch-layers">
          {ARCHITECTURE.map((layer, i) => (
            <ArchitectureLayer key={layer.id} layer={layer} index={i} />
          ))}
        </div>
      </section>

      {/* ═══ FINAL CTA ═══ */}
      <Section id="cta" className="py-24 sm:py-32 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="section-heading" style={{ lineHeight: 1.5 }}>
            Ready to turn your actions<br />into measurable trust?
          </h2>
          <p className="section-body" style={{ maxWidth: '480px', margin: '0 auto 2rem' }}>
            Join a network where what you do matters. Post actions, earn trust,
            and unlock opportunities that match your impact.
          </p>
          <button className="cta-btn cta-btn-primary" onClick={onEnterApp} data-testid="cta-enter-system">
            Enter the network <ArrowRight className="w-4 h-4" />
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
