import { useState } from 'react';
import CategoryCard from '../components/CategoryCard';
import TaskCard from '../components/TaskCard';
import Timer from '../components/Timer';
import DailySummary from '../components/DailySummary';
import { getRandomTaskByCategory } from '../data/tasks';
import { ChevronRight } from 'lucide-react';

export default function HomePage({ todayTasks, onSaveTask }) {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [currentTask, setCurrentTask] = useState(null);
  const [timerActive, setTimerActive] = useState(false);
  const [showSummary, setShowSummary] = useState(false);

  const handleCategorySelect = (category) => {
    const task = getRandomTaskByCategory(category);
    setSelectedCategory(category);
    setCurrentTask(task);
    setTimerActive(false);
    setShowSummary(false);
  };

  const handleStartTask = () => {
    setTimerActive(true);
    onSaveTask({
      ...currentTask,
      status: 'partial',
      startedAt: new Date().toISOString(),
    });
  };

  const handleFinishTask = () => {
    onSaveTask({
      ...currentTask,
      status: 'completed',
      completedAt: new Date().toISOString(),
    });
    setTimerActive(false);
    setShowSummary(true);
  };

  const handleNewTask = () => {
    setSelectedCategory(null);
    setCurrentTask(null);
    setTimerActive(false);
    setShowSummary(false);
  };

  const handleBack = () => {
    if (timerActive) {
      const confirmed = window.confirm('האם אתה בטוח? התקדמותך תישמר כחלקית');
      if (!confirmed) return;
    }
    handleNewTask();
  };

  return (
    <div className="flex-1 px-6 py-8 pb-24 flex flex-col gap-6">
      {!selectedCategory && (
        <>
          <div className="text-center mb-6">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight leading-none text-foreground mb-3">
              המקלט היומי
            </h1>
            <p className="text-base md:text-lg text-muted-foreground leading-relaxed">
              בחר תחום לתרגול היום
            </p>
          </div>
          
          <div className="flex flex-col gap-4" data-testid="category-selection">
            <CategoryCard category="body" onClick={() => handleCategorySelect('body')} />
            <CategoryCard category="emotion" onClick={() => handleCategorySelect('emotion')} />
            <CategoryCard category="mind" onClick={() => handleCategorySelect('mind')} />
          </div>
        </>
      )}

      {selectedCategory && !timerActive && !showSummary && (
        <>
          <div className="flex items-center gap-4 mb-4">
            <button
              data-testid="back-button"
              onClick={handleBack}
              className="rounded-full hover:bg-muted text-muted-foreground hover:text-foreground h-10 w-10 p-0 flex items-center justify-center transition-all"
            >
              <ChevronRight className="w-6 h-6" />
            </button>
            <h2 className="text-2xl font-semibold text-foreground">המשימה שלך</h2>
          </div>
          <TaskCard task={currentTask} onStart={handleStartTask} />
        </>
      )}

      {timerActive && !showSummary && (
        <>
          <div className="flex items-center gap-4 mb-4">
            <button
              data-testid="back-button-timer"
              onClick={handleBack}
              className="rounded-full hover:bg-muted text-muted-foreground hover:text-foreground h-10 w-10 p-0 flex items-center justify-center transition-all"
            >
              <ChevronRight className="w-6 h-6" />
            </button>
            <h2 className="text-2xl font-semibold text-foreground">תרגול פעיל</h2>
          </div>
          <Timer task={currentTask} onFinish={handleFinishTask} />
        </>
      )}

      {showSummary && (
        <DailySummary todayTasks={todayTasks} onNewTask={handleNewTask} />
      )}
    </div>
  );
}
