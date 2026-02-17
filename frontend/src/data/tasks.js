export const TASKS_LIBRARY = {
  body: [
    { id: 'body-1', title: 'מתיחות בוקר עדינות', minutes: 5, category: 'body' },
    { id: 'body-2', title: 'הליכה קצרה באוויר הצח', minutes: 10, category: 'body' },
    { id: 'body-3', title: 'תרגול נשימה עמוקה', minutes: 3, category: 'body' },
    { id: 'body-4', title: 'מתיחות יוגה פשוטות', minutes: 8, category: 'body' },
    { id: 'body-5', title: 'שתיית מים והזדקפות', minutes: 2, category: 'body' },
  ],
  emotion: [
    { id: 'emotion-1', title: 'כתיבת שלושה דברים שאני אסיר תודה עליהם', minutes: 3, category: 'emotion' },
    { id: 'emotion-2', title: 'שיחה קצרה עם אדם אהוב', minutes: 5, category: 'emotion' },
    { id: 'emotion-3', title: 'האזנה למוזיקה מרגיעה', minutes: 7, category: 'emotion' },
    { id: 'emotion-4', title: 'כתיבה חופשית ביומן', minutes: 10, category: 'emotion' },
    { id: 'emotion-5', title: 'חיבוק עצמי ומילות עידוד', minutes: 2, category: 'emotion' },
  ],
  mind: [
    { id: 'mind-1', title: 'מדיטציה מודרכת קצרה', minutes: 5, category: 'mind' },
    { id: 'mind-2', title: 'קריאת עמוד ספר מעורר השראה', minutes: 10, category: 'mind' },
    { id: 'mind-3', title: 'תרגול מיינדפולנס', minutes: 7, category: 'mind' },
    { id: 'mind-4', title: 'כתיבת מטרה אחת ליום', minutes: 3, category: 'mind' },
    { id: 'mind-5', title: 'הרהור שקט ללא מסכים', minutes: 8, category: 'mind' },
  ],
};

export function getRandomTaskByCategory(category) {
  const tasks = TASKS_LIBRARY[category] || [];
  if (tasks.length === 0) return null;
  const randomIndex = Math.floor(Math.random() * tasks.length);
  return tasks[randomIndex];
}
