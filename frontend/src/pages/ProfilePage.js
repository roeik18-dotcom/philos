import { Activity, Heart, Brain, TrendingUp, Users } from 'lucide-react';

export default function ProfilePage({ history }) {
  const totalHelped = history.filter(t => t.status === 'completed').length;
  const totalStarted = history.filter(t => t.status === 'partial').length;
  
  const bodyHelped = history.filter(t => t.category === 'body' && t.status === 'completed').length;
  const emotionHelped = history.filter(t => t.category === 'emotion' && t.status === 'completed').length;
  const mindHelped = history.filter(t => t.category === 'mind' && t.status === 'completed').length;
  
  const totalMinutes = history
    .filter(t => t.status === 'completed')
    .reduce((sum, t) => sum + t.minutes, 0);

  const categoryStats = [
    { label: 'גוף', count: bodyHelped, icon: Activity, color: '#A7C4BC' },
    { label: 'רגש', count: emotionHelped, icon: Heart, color: '#D4A5A5' },
    { label: 'מחשבה', count: mindHelped, icon: Brain, color: '#A0C1D1' },
  ];

  return (
    <div data-testid="profile-page" className="flex-1 px-6 py-8 pb-24 flex flex-col gap-6">
      <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-foreground">
        הפרופיל שלי
      </h1>

      <div className="bg-white/50 backdrop-blur-sm border border-white/60 shadow-lg rounded-3xl p-6 flex flex-col items-center gap-4">
        <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center">
          <Users className="w-10 h-10 text-primary" />
        </div>
        <h2 className="text-2xl font-semibold text-foreground">הסטטיסטיקות שלי</h2>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white/50 backdrop-blur-sm border border-white/60 shadow-sm rounded-3xl p-6 flex flex-col items-center gap-2">
          <span className="text-4xl font-bold text-foreground">{totalHelped}</span>
          <span className="text-base text-muted-foreground text-center">אנשים שעזרתי</span>
        </div>

        <div className="bg-white/50 backdrop-blur-sm border border-white/60 shadow-sm rounded-3xl p-6 flex flex-col items-center gap-2">
          <span className="text-4xl font-bold text-foreground">{totalMinutes}</span>
          <span className="text-base text-muted-foreground text-center">דקות תרומה</span>
        </div>
      </div>

      <div className="bg-white/50 backdrop-blur-sm border border-white/60 shadow-sm rounded-3xl p-6 flex flex-col gap-4">
        <div className="flex items-center gap-3">
          <TrendingUp className="w-6 h-6 text-primary" />
          <h3 className="text-xl font-medium text-foreground">התפלגות לפי תחומים</h3>
        </div>

        <div className="flex flex-col gap-3">
          {categoryStats.map(stat => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="flex items-center justify-between p-4 rounded-2xl bg-background/50">
                <div className="flex items-center gap-3">
                  <div 
                    className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ backgroundColor: `${stat.color}30` }}
                  >
                    <Icon className="w-5 h-5" style={{ color: stat.color }} />
                  </div>
                  <span className="text-lg text-foreground">{stat.label}</span>
                </div>
                <span className="text-2xl font-bold text-foreground">{stat.count}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
