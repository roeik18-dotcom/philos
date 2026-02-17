import { useState, useEffect, useRef } from 'react';
import { Check, Clock } from 'lucide-react';

export default function Timer({ request, onFinish, onMount }) {
  const [secondsLeft, setSecondsLeft] = useState(request.minutes * 60);
  const [isRunning, setIsRunning] = useState(true);
  const intervalRef = useRef(null);
  const hasShownAlertRef = useRef(false);
  const hasMountedRef = useRef(false);

  useEffect(() => {
    // Call onMount only once when component first mounts
    if (!hasMountedRef.current && onMount) {
      onMount();
      hasMountedRef.current = true;
    }
  }, [onMount]);

  useEffect(() => {
    if (isRunning && secondsLeft > 0) {
      intervalRef.current = setInterval(() => {
        setSecondsLeft(prev => {
          if (prev <= 1) {
            setIsRunning(false);
            if (!hasShownAlertRef.current) {
              hasShownAlertRef.current = true;
              setTimeout(() => {
                alert('הזמן הסתיים! 🎉');
              }, 100);
            }
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRunning, secondsLeft]);

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;
  const progress = ((request.minutes * 60 - secondsLeft) / (request.minutes * 60)) * 100;

  const getCategoryColor = (category) => {
    const colors = {
      body: { accent: '#A7C4BC', text: '#2C4A40' },
      emotion: { accent: '#D4A5A5', text: '#5A3A3A' },
      mind: { accent: '#A0C1D1', text: '#2A4550' },
    };
    return colors[category] || colors.body;
  };

  const colors = getCategoryColor(request.category);

  return (
    <div 
      data-testid="timer-active"
      className="bg-white/50 backdrop-blur-sm border border-white/60 shadow-lg rounded-[2rem] p-8 flex flex-col items-center gap-6"
    >
      <div className="text-center">
        <h3 className="text-xl font-medium text-foreground mb-2">
          עוזר ל{request.name}
        </h3>
        <p className="text-base text-muted-foreground">{request.need}</p>
      </div>

      <div className="relative w-48 h-48 flex items-center justify-center">
        <svg className="absolute inset-0 w-full h-full transform -rotate-90">
          <circle
            cx="96"
            cy="96"
            r="88"
            stroke="#E6E2DD"
            strokeWidth="8"
            fill="none"
          />
          <circle
            cx="96"
            cy="96"
            r="88"
            stroke={colors.accent}
            strokeWidth="8"
            fill="none"
            strokeDasharray={`${2 * Math.PI * 88}`}
            strokeDashoffset={`${2 * Math.PI * 88 * (1 - progress / 100)}`}
            className="transition-all duration-1000 ease-linear"
            strokeLinecap="round"
          />
        </svg>
        <div className="flex flex-col items-center gap-1">
          <Clock className="w-6 h-6 text-muted-foreground" />
          <div className="text-5xl font-bold" style={{ color: colors.text }}>
            {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
          </div>
        </div>
      </div>

      <button
        data-testid="finish-task-button"
        onClick={onFinish}
        className="mt-4 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 h-14 px-10 shadow-md hover:shadow-lg transition-all active:scale-95 flex items-center gap-3 text-lg font-medium tracking-wide"
      >
        <Check className="w-5 h-5" />
        <span>סיום</span>
      </button>
    </div>
  );
}
