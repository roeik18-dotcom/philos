import { MapPin, Clock, User } from 'lucide-react';

export default function RequestCard({ request, onAccept }) {
  if (!request) return null;

  const getCategoryColor = (category) => {
    const colors = {
      body: { bg: '#E8F0ED', accent: '#A7C4BC', text: '#2C4A40' },
      emotion: { bg: '#F7EBEB', accent: '#D4A5A5', text: '#5A3A3A' },
      mind: { bg: '#EBF4F8', accent: '#A0C1D1', text: '#2A4550' },
    };
    return colors[category] || colors.body;
  };

  const colors = getCategoryColor(request.category);

  return (
    <div 
      data-testid="request-card"
      className="bg-white/50 backdrop-blur-sm border border-white/60 shadow-lg rounded-[2rem] p-8 flex flex-col gap-6"
    >
      <div className="flex items-center gap-4">
        <div 
          className="w-14 h-14 rounded-full flex items-center justify-center shadow-md"
          style={{ backgroundColor: colors.accent }}
        >
          <User className="w-7 h-7" style={{ color: colors.text }} />
        </div>
        <div>
          <h3 className="text-2xl font-medium text-foreground">{request.name}</h3>
          <div className="flex items-center gap-2 text-muted-foreground mt-1">
            <MapPin className="w-4 h-4" />
            <span className="text-sm">{request.distance}</span>
          </div>
        </div>
      </div>

      <div className="bg-background/30 rounded-2xl p-5">
        <p className="text-lg text-foreground leading-relaxed text-center">
          {request.need}
        </p>
      </div>
      
      <div className="flex items-center justify-center gap-2 text-muted-foreground">
        <Clock className="w-5 h-5" />
        <span className="text-lg">{request.minutes} דקות</span>
      </div>

      <button
        data-testid="accept-request-button"
        onClick={onAccept}
        className="mt-2 rounded-full h-14 px-10 shadow-md hover:shadow-lg transition-all active:scale-95 flex items-center justify-center gap-3 text-lg font-medium tracking-wide"
        style={{ 
          backgroundColor: colors.accent,
          color: colors.text 
        }}
      >
        <span>אקבל</span>
      </button>
    </div>
  );
}
