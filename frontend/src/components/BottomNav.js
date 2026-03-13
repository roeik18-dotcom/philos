import { Home, Calendar, User, FileText } from 'lucide-react';

export default function BottomNav({ currentPage, onNavigate }) {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'my-requests', label: 'My Requests', icon: FileText },
    { id: 'history', label: 'History', icon: Calendar },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  return (
    <nav 
      data-testid="bottom-nav"
      className="fixed bottom-0 left-0 right-0 h-20 bg-white/80 backdrop-blur-lg border-t border-white/20 flex items-center justify-around pb-4 pt-2 shadow-[0_-4px_20px_rgba(0,0,0,0.02)]"
      style={{ zIndex: 9999 }}
    >
      {navItems.map(item => {
        const Icon = item.icon;
        const isActive = currentPage === item.id;
        
        return (
          <button
            key={item.id}
            data-testid={`nav-${item.id}-button`}
            onClick={() => onNavigate(item.id)}
            className="flex flex-col items-center gap-1 px-3 py-2 rounded-2xl transition-all active:scale-95"
            style={{
              backgroundColor: isActive ? '#E6E2DD' : 'transparent',
            }}
          >
            <Icon 
              className="w-5 h-5" 
              style={{ color: isActive ? '#4A4238' : '#8C867D' }}
            />
            <span 
              className="text-xs font-medium"
              style={{ color: isActive ? '#4A4238' : '#8C867D' }}
            >
              {item.label}
            </span>
          </button>
        );
      })}
    </nav>
  );
}
