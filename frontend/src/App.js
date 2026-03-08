import { useState, useEffect } from 'react';
import PhilosDashboard from './pages/PhilosDashboard';
import AuthScreen from './components/auth/AuthScreen';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAuth, setShowAuth] = useState(false);

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
          <p className="text-gray-600">טוען...</p>
        </div>
      </div>
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
