import { useState } from 'react';
import { useLocalStorage } from './hooks/useLocalStorage';
import HomePage from './pages/HomePage';
import HistoryPage from './pages/HistoryPage';
import ProfilePage from './pages/ProfilePage';
import BottomNav from './components/BottomNav';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [history, setHistory] = useLocalStorage('community-help-history', []);

  const getTodayRequests = () => {
    const today = new Date().toISOString().split('T')[0];
    return history.filter(request => {
      const requestDate = new Date(request.startedAt || request.completedAt).toISOString().split('T')[0];
      return requestDate === today;
    });
  };

  const handleSaveRequest = (request) => {
    setHistory(prev => {
      const existingRequestIndex = prev.findIndex(r => 
        r.id === request.id && 
        new Date(r.startedAt).toISOString().split('T')[0] === new Date().toISOString().split('T')[0]
      );

      if (existingRequestIndex >= 0) {
        const updated = [...prev];
        updated[existingRequestIndex] = {
          ...updated[existingRequestIndex],
          ...request,
        };
        return updated;
      } else {
        return [...prev, request];
      }
    });
  };

  return (
    <div className="max-w-md mx-auto min-h-screen flex flex-col relative overflow-hidden bg-background">
      {currentPage === 'home' && (
        <HomePage 
          todayRequests={getTodayRequests()} 
          onSaveRequest={handleSaveRequest}
        />
      )}
      {currentPage === 'history' && <HistoryPage history={history} />}
      {currentPage === 'profile' && <ProfilePage history={history} />}
      
      <BottomNav currentPage={currentPage} onNavigate={setCurrentPage} />
    </div>
  );
}

export default App;
