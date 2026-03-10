// Lightweight loading skeleton components for Philos Orientation
// Provides visual feedback during async data loading

/**
 * Basic skeleton pulse animation
 */
const pulseClass = "animate-pulse bg-gray-200 rounded";

/**
 * Section skeleton - for full section loading
 */
export function SectionSkeleton({ lines = 3, showHeader = true }) {
  return (
    <div className="bg-white rounded-3xl p-6 shadow-sm border border-border" dir="rtl">
      {showHeader && (
        <div className={`h-5 w-32 ${pulseClass} mb-4`}></div>
      )}
      <div className="space-y-3">
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i} className={`h-4 ${pulseClass}`} style={{ width: `${85 - i * 15}%` }}></div>
        ))}
      </div>
    </div>
  );
}

/**
 * Card skeleton - for smaller card-like content
 */
export function CardSkeleton({ showBadge = false }) {
  return (
    <div className="p-4 rounded-xl bg-gray-50 border border-gray-200" dir="rtl">
      {showBadge && (
        <div className={`h-6 w-20 ${pulseClass} mb-3`}></div>
      )}
      <div className={`h-5 w-3/4 ${pulseClass} mb-2`}></div>
      <div className={`h-4 w-1/2 ${pulseClass}`}></div>
    </div>
  );
}

/**
 * Stats skeleton - for statistics display
 */
export function StatsSkeleton({ count = 3 }) {
  return (
    <div className="grid grid-cols-3 gap-4" dir="rtl">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="text-center p-3">
          <div className={`h-8 w-12 ${pulseClass} mx-auto mb-2`}></div>
          <div className={`h-4 w-16 ${pulseClass} mx-auto`}></div>
        </div>
      ))}
    </div>
  );
}

/**
 * Chart skeleton - for chart placeholders
 */
export function ChartSkeleton({ height = 120 }) {
  return (
    <div 
      className={`${pulseClass} w-full`} 
      style={{ height: `${height}px` }}
      dir="rtl"
    >
      <div className="flex items-end justify-around h-full p-4">
        {[40, 65, 50, 80, 55, 70, 45].map((h, i) => (
          <div 
            key={i} 
            className="bg-gray-300 rounded-t w-6"
            style={{ height: `${h}%` }}
          ></div>
        ))}
      </div>
    </div>
  );
}

/**
 * List skeleton - for list items
 */
export function ListSkeleton({ items = 3 }) {
  return (
    <div className="space-y-3" dir="rtl">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className={`h-3 w-3 rounded-full ${pulseClass}`}></div>
          <div className={`h-4 flex-1 ${pulseClass}`} style={{ maxWidth: `${90 - i * 10}%` }}></div>
        </div>
      ))}
    </div>
  );
}

/**
 * Inline loading indicator - minimal text replacement
 */
export function InlineLoader({ width = "w-24" }) {
  return <span className={`inline-block h-4 ${width} ${pulseClass}`}></span>;
}

/**
 * Collective section skeleton - specific for mirror/trajectory
 */
export function CollectiveSkeleton() {
  return (
    <div className="bg-white rounded-3xl p-6 shadow-sm border border-border" dir="rtl">
      <div className={`h-5 w-40 ${pulseClass} mb-4`}></div>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="p-4 rounded-xl bg-gray-50">
          <div className={`h-4 w-16 ${pulseClass} mb-2`}></div>
          <div className={`h-6 w-20 ${pulseClass}`}></div>
        </div>
        <div className="p-4 rounded-xl bg-gray-50">
          <div className={`h-4 w-16 ${pulseClass} mb-2`}></div>
          <div className={`h-6 w-20 ${pulseClass}`}></div>
        </div>
      </div>
      <ChartSkeleton height={100} />
    </div>
  );
}

/**
 * Replay insights skeleton
 */
export function ReplaySkeleton() {
  return (
    <div className="bg-white rounded-3xl p-6 shadow-sm border border-border" dir="rtl">
      <div className={`h-5 w-36 ${pulseClass} mb-4`}></div>
      <StatsSkeleton count={3} />
      <div className="mt-4 pt-4 border-t">
        <ListSkeleton items={2} />
      </div>
    </div>
  );
}
