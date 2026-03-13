import { useState, useEffect } from 'react';
import PhilosDashboard from './pages/PhilosDashboard';
import TrustTestPage from './pages/TrustTestPage';
import InvitePage from './pages/InvitePage';
import AdminPage from './pages/AdminPage';
import ProfilePage from './pages/ProfilePage';
import AuthScreen from './components/auth/AuthScreen';
import { getUserId } from './services/cloudSync';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAuth, setShowAuth] = useState(false);
  const [inviteCode, setInviteCode] = useState(null);

  // Initialize persistent user ID on app load + check for invite route
  useEffect(() => {
    const persistentUserId = getUserId();
    console.log('Persistent User ID:', persistentUserId);

    // Check if we're on an invite page (both /invite/CODE and /join?invite=CODE)
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

  // Check for existing auth on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('philos_auth_token');
      const savedUser = localStorage.getItem('philos_user');
      
      if (token && savedUser) {
        try {
          // Verify token is still valid
          const response = await fetch(`${API_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });
          const data = await response.json();
          
          if (data.success && data.user) {
            setUser(data.user);
          } else {
            // Token invalid, clear storage
            localStorage.removeItem('philos_auth_token');
            localStorage.removeItem('philos_user');
          }
        } catch (error) {
          console.error('Auth check error:', error);
        }
      }
      
      setLoading(false);
    };
    
    checkAuth();
  }, []);

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setShowAuth(false);
  };

  const handleSkip = () => {
    setShowAuth(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('philos_auth_token');
    localStorage.removeItem('philos_user');
    setUser(null);
  };

  const handleShowAuth = () => {
    setShowAuth(true);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-10 w-10 border-4 border-amber-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Admin page
  if (window.location.pathname === '/admin') {
    return <AdminPage />;
  }

  // Profile page
  if (window.location.pathname.startsWith('/profile/')) {
    return <ProfilePage />;
  }

  // Trust test public page
  if (window.location.pathname === '/trust-test') {
    if (showAuth) {
      return <AuthScreen onAuthSuccess={handleAuthSuccess} onSkip={handleSkip} />;
    }
    return <TrustTestPage user={user} onLogout={handleLogout} onShowAuth={handleShowAuth} />;
  }

  // Invite page
  if (inviteCode) {
    return (
      <InvitePage
        code={inviteCode}
        onEnter={() => {
          setInviteCode(null);
          window.history.pushState({}, '', '/');
        }}
      />
    );
  }

  if (showAuth) {
    return (
      <AuthScreen 
        onAuthSuccess={handleAuthSuccess}
        onSkip={handleSkip}
      />
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <PhilosDashboard 
        user={user}
        onLogout={handleLogout}
        onShowAuth={handleShowAuth}
      />
    </div>
  );
}

export default App;
