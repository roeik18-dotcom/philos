import { useState, useEffect } from 'react';
import PlatformLandingPage from './pages/PlatformLandingPage';
import ProductApp from './pages/ProductApp';
import PhilosDashboard from './pages/PhilosDashboard';
import TrustTestPage from './pages/TrustTestPage';
import InvitePage from './pages/InvitePage';
import AdminPage from './pages/AdminPage';
import ProfilePage from './pages/ProfilePage';
import AuthScreen from './components/auth/AuthScreen';
import { getUserId } from './services/cloudSync';
import { BackendReadyProvider, useBackendReady } from './hooks/useBackendReady';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function AppInner() {
  const [user, setUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [showAuth, setShowAuth] = useState(false);
  const [inviteCode, setInviteCode] = useState(null);
  const { isReady } = useBackendReady();

  // Initialize persistent user ID + check invite route
  useEffect(() => {
    const persistentUserId = getUserId();
    console.log('Persistent User ID:', persistentUserId);

    const path = window.location.pathname;
    const match = path.match(/^\/invite\/([a-zA-Z0-9-]+)$/);
    if (match) {
      setInviteCode(match[1]);
    } else if (path === '/join') {
      const params = new URLSearchParams(window.location.search);
      const code = params.get('invite');
      if (code) setInviteCode(code);
    }
  }, []);

  // Check auth ONLY when backend is ready
  useEffect(() => {
    if (!isReady || authChecked) return;

    const checkAuth = async () => {
      const token = localStorage.getItem('philos_auth_token');
      const savedUser = localStorage.getItem('philos_user');

      if (token && savedUser) {
        try {
          const response = await fetch(`${API_URL}/api/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` },
          });
          const data = await response.json();
          if (data.success && data.user) {
            setUser(data.user);
          } else {
            localStorage.removeItem('philos_auth_token');
            localStorage.removeItem('philos_user');
          }
        } catch {
          // Network error — token might still be valid, keep user from localStorage
          try {
            const parsed = JSON.parse(savedUser);
            if (parsed && parsed.id) setUser(parsed);
          } catch {}
        }
      }
      setAuthChecked(true);
    };

    checkAuth();
  }, [isReady, authChecked]);

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setShowAuth(false);
  };
  const handleSkip = () => setShowAuth(false);
  const handleLogout = () => {
    localStorage.removeItem('philos_auth_token');
    localStorage.removeItem('philos_user');
    setUser(null);
  };
  const handleShowAuth = () => setShowAuth(true);

  // Minimal branded loading — no technical messages, no spinners
  if (!authChecked) {
    return (
      <div className="app-wake-screen" data-testid="app-wake-screen">
        <span className="app-wake-logo">Philos</span>
      </div>
    );
  }

  if (window.location.pathname === '/admin') return <AdminPage />;

  if (window.location.pathname.startsWith('/app')) {
    return (
      <ProductApp
        user={user}
        onLogout={handleLogout}
        onAuthSuccess={handleAuthSuccess}
      />
    );
  }

  if (window.location.pathname.startsWith('/profile/')) return <ProfilePage />;

  if (window.location.pathname === '/trust-test') {
    if (showAuth) return <AuthScreen onAuthSuccess={handleAuthSuccess} onSkip={handleSkip} />;
    return <TrustTestPage user={user} onLogout={handleLogout} onShowAuth={handleShowAuth} />;
  }

  if (inviteCode) {
    return (
      <InvitePage
        code={inviteCode}
        onEnter={() => { setInviteCode(null); window.history.pushState({}, '', '/'); }}
      />
    );
  }

  if (showAuth) return <AuthScreen onAuthSuccess={handleAuthSuccess} onSkip={handleSkip} />;

  if (window.location.pathname === '/dashboard') {
    return (
      <div className="min-h-screen bg-background">
        <PhilosDashboard user={user} onLogout={handleLogout} onShowAuth={handleShowAuth} />
      </div>
    );
  }

  return <PlatformLandingPage onEnterApp={() => { window.location.href = '/trust-test'; }} />;
}

function App() {
  return (
    <BackendReadyProvider>
      <AppInner />
    </BackendReadyProvider>
  );
}

export default App;
