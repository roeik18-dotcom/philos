import { useState, useEffect, useCallback } from 'react';
import { List, PlusCircle, Map, User, BarChart3, LogOut, Menu, X, Home } from 'lucide-react';
import ActionFeed from './app/ActionFeed';
import PostAction from './app/PostAction';
import ImpactMap from './app/ImpactMap';
import ProductProfile from './app/ProductProfile';
import DailyDashboard from './app/DailyDashboard';
import AuthScreen from '../components/auth/AuthScreen';
import './app.css';

const NAV_ITEMS = [
  { id: 'feed', label: 'Feed', icon: List, path: '/app/feed', auth: false },
  { id: 'post', label: 'Post', icon: PlusCircle, path: '/app/post', auth: true },
  { id: 'map', label: 'Map', icon: Map, path: '/app/map', auth: false },
  { id: 'profile', label: 'Profile', icon: User, path: '/app/profile', auth: true },
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3, path: '/app/dashboard', auth: true },
];

function getActiveTab() {
  const p = window.location.pathname;
  if (p.startsWith('/app/post')) return 'post';
  if (p.startsWith('/app/map')) return 'map';
  if (p.startsWith('/app/profile')) return 'profile';
  if (p.startsWith('/app/dashboard')) return 'dashboard';
  return 'feed';
}

export default function ProductApp({ user, onLogout, onAuthSuccess }) {
  const [tab, setTab] = useState(getActiveTab);
  const [showAuth, setShowAuth] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);

  const navigate = useCallback((id) => {
    const item = NAV_ITEMS.find(n => n.id === id);
    if (item?.auth && !user) {
      setShowAuth(true);
      return;
    }
    setTab(id);
    window.history.pushState({}, '', item?.path || '/app/feed');
    setMobileNav(false);
  }, [user]);

  useEffect(() => {
    const onPop = () => setTab(getActiveTab());
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  if (showAuth) {
    return (
      <AuthScreen
        onAuthSuccess={(u) => { onAuthSuccess(u); setShowAuth(false); }}
        onSkip={() => setShowAuth(false)}
      />
    );
  }

  const renderPage = () => {
    switch (tab) {
      case 'post': return <PostAction user={user} onPosted={() => navigate('feed')} />;
      case 'map': return <ImpactMap />;
      case 'profile': return <ProductProfile user={user} />;
      case 'dashboard': return <DailyDashboard user={user} />;
      default: return <ActionFeed user={user} />;
    }
  };

  return (
    <div className="product-app" data-testid="product-app">
      {/* Top bar */}
      <header className="app-topbar" data-testid="app-topbar">
        <div className="app-topbar-inner">
          <a href="/" className="app-logo" data-testid="app-logo">
            <Home className="w-4 h-4" />
            <span>Philos</span>
          </a>

          {/* Desktop nav */}
          <nav className="app-nav-desktop" data-testid="app-nav-desktop">
            {NAV_ITEMS.map(item => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  className={`app-nav-btn ${tab === item.id ? 'active' : ''}`}
                  onClick={() => navigate(item.id)}
                  data-testid={`nav-${item.id}`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          <div className="app-topbar-right">
            {user ? (
              <div className="app-user-area">
                <span className="app-user-name" data-testid="app-user-name">{user.name || user.email}</span>
                <button className="app-logout-btn" onClick={onLogout} data-testid="app-logout-btn">
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button className="app-login-btn" onClick={() => setShowAuth(true)} data-testid="app-login-btn">
                Sign in
              </button>
            )}
            <button className="app-mobile-toggle" onClick={() => setMobileNav(!mobileNav)} data-testid="mobile-nav-toggle">
              {mobileNav ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile nav drawer */}
      {mobileNav && (
        <div className="app-mobile-nav" data-testid="mobile-nav-drawer">
          {NAV_ITEMS.map(item => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={`app-mobile-nav-btn ${tab === item.id ? 'active' : ''}`}
                onClick={() => navigate(item.id)}
                data-testid={`mobile-nav-${item.id}`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Page content */}
      <main className="app-main">
        {renderPage()}
      </main>

      {/* Bottom tab bar (mobile) */}
      <nav className="app-bottom-bar" data-testid="app-bottom-bar">
        {NAV_ITEMS.map(item => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              className={`app-bottom-btn ${tab === item.id ? 'active' : ''}`}
              onClick={() => navigate(item.id)}
              data-testid={`bottom-nav-${item.id}`}
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
