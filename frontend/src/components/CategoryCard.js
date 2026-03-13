import { Activity, Heart, Brain } from 'lucide-react';

const CATEGORY_CONFIG = {
  body: {
    label: 'Body',
    icon: Activity,
    bgColor: '#E8F0ED',
    textColor: '#2C4A40',
    accentColor: '#A7C4BC',
    image: 'https://images.unsplash.com/photo-1593068415562-8b5db003f219?q=80&w=800&auto=format&fit=crop',
  },
  emotion: {
    label: 'Emotion',
    icon: Heart,
    bgColor: '#F7EBEB',
    textColor: '#5A3A3A',
    accentColor: '#D4A5A5',
    image: 'https://images.unsplash.com/photo-1648993880088-37d4a048e6d5?q=80&w=800&auto=format&fit=crop',
  },
  mind: {
    label: 'Mind',
    icon: Brain,
    bgColor: '#EBF4F8',
    textColor: '#2A4550',
    accentColor: '#A0C1D1',
    image: 'https://images.unsplash.com/photo-1761468720849-5abc8533343c?q=80&w=800&auto=format&fit=crop',
  },
};

export default function CategoryCard({ category, onClick }) {
  const config = CATEGORY_CONFIG[category];
  const Icon = config.icon;

  return (
    <button
      data-testid={`category-${category}-button`}
      onClick={onClick}
      className="relative overflow-hidden rounded-3xl aspect-[4/3] flex flex-col justify-end p-6 shadow-sm hover:shadow-md transition-all active:scale-[0.98] group cursor-pointer border border-border/50 w-full"
      style={{ backgroundColor: config.bgColor }}
    >
      <div 
        className="absolute inset-0 bg-cover bg-center opacity-10 group-hover:opacity-15 transition-opacity"
        style={{ backgroundImage: `url(${config.image})` }}
      />
      <div className="relative z-10 flex items-center gap-3">
        <div 
          className="w-12 h-12 rounded-2xl flex items-center justify-center shadow-sm"
          style={{ backgroundColor: config.accentColor }}
        >
          <Icon className="w-6 h-6" style={{ color: config.textColor }} />
        </div>
        <h2 
          className="text-2xl font-semibold tracking-tight"
          style={{ color: config.textColor }}
        >
          {config.label}
        </h2>
      </div>
    </button>
  );
}
