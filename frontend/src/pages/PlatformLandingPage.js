import { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { ArrowRight, ArrowDown } from 'lucide-react';
import Globe from 'react-globe.gl';
import './platform.css';

/* ═══════════════════════════════════════════════════
   GLOBE BACKGROUND — layer 1
   ═══════════════════════════════════════════════════ */
function GlobeBackground() {
  const globeRef = useRef();
  const containerRef = useRef();
  const [dim, setDim] = useState(700);

  const points = useMemo(() => {
    const pts = [];
    for (let i = 0; i < 50; i++) {
      pts.push({
        lat: (Math.random() - 0.5) * 140,
        lng: (Math.random() - 0.5) * 340,
        size: 0.3 + Math.random() * 0.7,
        color: ['#00d4ff', '#10b981', '#7c3aed', '#f59e0b'][Math.floor(Math.random() * 4)],
      });
    }
    return pts;
  }, []);

  const arcs = useMemo(() => {
    const a = [];
    for (let i = 0; i < 14; i++) {
      a.push({
        startLat: (Math.random() - 0.5) * 140,
        startLng: (Math.random() - 0.5) * 340,
        endLat: (Math.random() - 0.5) * 140,
        endLng: (Math.random() - 0.5) * 340,
        color: ['rgba(0,212,255,0.2)', 'rgba(16,185,129,0.2)', 'rgba(124,58,237,0.2)'][i % 3],
      });
    }
    return a;
  }, []);

  const rings = useMemo(() => [
    { lat: 32.08, lng: 34.78, maxR: 4, propagationSpeed: 2, repeatPeriod: 2000, color: () => 'rgba(0,212,255,0.25)' },
    { lat: 40.71, lng: -74.01, maxR: 3, propagationSpeed: 1.5, repeatPeriod: 2500, color: () => 'rgba(16,185,129,0.25)' },
    { lat: -33.87, lng: 151.21, maxR: 3, propagationSpeed: 1.8, repeatPeriod: 3000, color: () => 'rgba(124,58,237,0.25)' },
  ], []);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      setDim(Math.min(entry.contentRect.width, entry.contentRect.height, 800));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const g = globeRef.current;
    if (!g) return;
    g.controls().autoRotate = true;
    g.controls().autoRotateSpeed = 0.4;
    g.controls().enableZoom = false;
    g.controls().enablePan = false;
    g.controls().enableRotate = false;
    g.pointOfView({ altitude: 2.4 });
  }, []);

  const globeImg = useCallback(() => '//unpkg.com/three-globe/example/img/earth-dark.jpg', []);
  const bumpImg = useCallback(() => '//unpkg.com/three-globe/example/img/earth-topology.png', []);

  return (
    <div ref={containerRef} className="entrance-globe" data-testid="entrance-globe">
      <Globe
        ref={globeRef}
        width={dim}
        height={dim}
        globeImageUrl={globeImg()}
        bumpImageUrl={bumpImg()}
        backgroundColor="rgba(0,0,0,0)"
        atmosphereColor="#00d4ff"
        atmosphereAltitude={0.15}
        pointsData={points}
        pointLat="lat" pointLng="lng"
        pointAltitude={d => d.size * 0.03}
        pointRadius={d => d.size * 0.25}
        pointColor="color"
        arcsData={arcs}
        arcStartLat="startLat" arcStartLng="startLng"
        arcEndLat="endLat" arcEndLng="endLng"
        arcColor="color" arcStroke={0.3}
        arcDashLength={0.4} arcDashGap={0.2} arcDashAnimateTime={4000}
        arcAltitudeAutoScale={0.25}
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
   COMPASS GEOMETRY — layer 2 (pure CSS)
   ═══════════════════════════════════════════════════ */
function CompassGeometry() {
  return (
    <div className="entrance-compass" aria-hidden="true">
      <div className="compass-ring compass-ring-1" />
      <div className="compass-ring compass-ring-2" />
      <div className="compass-ring compass-ring-3" />
      <div className="compass-crosshair compass-h" />
      <div className="compass-crosshair compass-v" />
      <div className="compass-tick tick-n" />
      <div className="compass-tick tick-e" />
      <div className="compass-tick tick-s" />
      <div className="compass-tick tick-w" />
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   ENTRANCE LAYER PAGE
   ═══════════════════════════════════════════════════ */
export default function PlatformLandingPage() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const enterApp = () => { window.location.href = '/app/feed'; };

  return (
    <div className="entrance-page" data-testid="entrance-page">

      {/* ═══ HERO — full screen ═══ */}
      <section className="entrance-hero" data-testid="entrance-hero">
        {/* Background layers */}
        <div className="entrance-bg" style={{ transform: `translateY(${scrollY * 0.15}px)` }}>
          <GlobeBackground />
          <CompassGeometry />
          <div className="entrance-gradient-top" />
          <div className="entrance-gradient-bottom" />
        </div>

        {/* Content */}
        <div className="entrance-content">
          <h1 className="entrance-headline" data-testid="entrance-headline">
            <span className="entrance-line entrance-line-1">Actions build trust.</span>
            <span className="entrance-line entrance-line-2">Trust shapes opportunity.</span>
          </h1>

          <button className="entrance-cta" onClick={enterApp} data-testid="entrance-cta">
            Enter the App <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        <div className="entrance-scroll-hint">
          <ArrowDown className="w-4 h-4" />
        </div>
      </section>

      {/* ═══ MICRO-MESSAGES ═══ */}
      <section className="entrance-ideas" data-testid="entrance-ideas">
        <MicroMessage
          index={0}
          label="Action"
          arrow="Trust"
          text="Real actions build measurable trust."
          color="#00d4ff"
        />
        <MicroMessage
          index={1}
          label="Trust"
          arrow="Visibility"
          text="Trust increases influence in the network."
          color="#f59e0b"
        />
        <MicroMessage
          index={2}
          label="Visibility"
          arrow="Opportunity"
          text="Influence creates real opportunity."
          color="#10b981"
        />
      </section>

      {/* ═══ BOTTOM CTA ═══ */}
      <section className="entrance-bottom" data-testid="entrance-bottom-cta">
        <button className="entrance-cta entrance-cta-bottom" onClick={enterApp} data-testid="entrance-cta-bottom">
          Enter the App <ArrowRight className="w-5 h-5" />
        </button>
      </section>

      {/* ═══ FOOTER ═══ */}
      <footer className="entrance-footer" data-testid="entrance-footer">
        Philos
      </footer>
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   MICRO-MESSAGE BLOCK
   ═══════════════════════════════════════════════════ */
function MicroMessage({ label, arrow, text, color, index }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setVisible(true); },
      { threshold: 0.3 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`micro-msg ${visible ? 'micro-visible' : ''}`}
      style={{ transitionDelay: `${index * 120}ms` }}
      data-testid={`micro-msg-${index}`}
    >
      <div className="micro-label" style={{ color }}>
        {label} <span className="micro-arrow">&#x2192;</span> {arrow}
      </div>
      <p className="micro-text">{text}</p>
    </div>
  );
}
