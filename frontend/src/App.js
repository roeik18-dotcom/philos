import { useState, useEffect } from 'react';
import { useLocalStorage } from './hooks/useLocalStorage';
import HomePage from './pages/HomePage';
import HistoryPage from './pages/HistoryPage';
import ProfilePage from './pages/ProfilePage';
import BottomNav from './components/BottomNav';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [history, setHistory] = useLocalStorage('task-history', []);

  const getTodayTasks = () => {
    const today = new Date().toISOString().split('T')[0];
    return history.filter(task => {
      const taskDate = new Date(task.startedAt || task.completedAt).toISOString().split('T')[0];
      return taskDate === today;
    });
  };

  const handleSaveTask = (task) => {
    setHistory(prev => {
      const existingTaskIndex = prev.findIndex(t => 
        t.id === task.id && 
        new Date(t.startedAt).toISOString().split('T')[0] === new Date().toISOString().split('T')[0]
      );

      if (existingTaskIndex >= 0) {
        const updated = [...prev];
        updated[existingTaskIndex] = {
          ...updated[existingTaskIndex],
          ...task,
        };
        return updated;
      } else {
        return [...prev, task];
      }
    });
  };

  return (
    <div className="max-w-md mx-auto min-h-screen flex flex-col relative overflow-hidden bg-background">
      {currentPage === 'home' && (
        <HomePage 
          todayTasks={getTodayTasks()} 
          onSaveTask={handleSaveTask}
        />
      )}
      {currentPage === 'history' && <HistoryPage history={history} />}
      {currentPage === 'profile' && <ProfilePage history={history} />}
      
      <BottomNav currentPage={currentPage} onNavigate={setCurrentPage} />
    </div>
  );
}

export default App;
