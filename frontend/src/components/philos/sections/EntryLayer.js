import { Compass } from 'lucide-react';

export default function EntryLayer() {
  return (
    <section
      className="relative rounded-3xl overflow-hidden bg-[#0a0a1a] text-white p-6 pb-7"
      dir="rtl"
      data-testid="entry-layer"
    >
      {/* Subtle radial glow */}
      <div className="absolute inset-0 pointer-events-none" style={{
        background: 'radial-gradient(ellipse at 50% 80%, rgba(99,102,241,0.12) 0%, transparent 60%)'
      }} />

      <div className="relative z-10">
        <div className="flex items-center gap-2 mb-4 opacity-60">
          <Compass className="w-4 h-4" />
          <span className="text-xs tracking-wide">Philos Orientation</span>
        </div>

        <h2 className="text-lg font-bold leading-relaxed mb-3">
          העולם מושך אותך לכיוונים מנוגדים.
        </h2>

        <p className="text-sm leading-relaxed text-gray-300 mb-2">
          בכל יום אתה עומד בין כוחות — בין סדר לכאוס, בין נתינה לשימור,
          בין חקירה להתבצרות.
        </p>

        <p className="text-sm leading-relaxed text-gray-300 mb-4">
          פילוס עוזר לך להתמצא בתוך הכוחות האלה.
          <br />
          כל יום, פעולה אחת קטנה — וכך אתה משנה את הכיוון של השדה האנושי.
        </p>

        <div className="flex items-center gap-2 pt-2 border-t border-white/10">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
          <span className="text-xs text-gray-400">בחר כיוון. פעל. השפע.</span>
        </div>
      </div>
    </section>
  );
}
