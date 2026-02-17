export const COMMUNITY_REQUESTS = {
  body: [
    { id: 'body-1', name: 'שרה', need: 'עזרה בהעברת רהיטים בבניין', minutes: 15, distance: '0.3 ק"מ', category: 'body' },
    { id: 'body-2', name: 'דוד', need: 'ליווי להליכה בפארק', minutes: 20, distance: '0.8 ק"מ', category: 'body' },
    { id: 'body-3', name: 'מרים', need: 'עזרה בגינה המשותפת', minutes: 25, distance: '0.5 ק"מ', category: 'body' },
    { id: 'body-4', name: 'יוסף', need: 'עזרה בנשיאת קניות', minutes: 10, distance: '0.2 ק"מ', category: 'body' },
    { id: 'body-5', name: 'רחל', need: 'עזרה בארגון מחסן', minutes: 30, distance: '1.2 ק"מ', category: 'body' },
  ],
  emotion: [
    { id: 'emotion-1', name: 'אבי', need: 'שיחה ידידותית על קפה', minutes: 20, distance: '0.6 ק"מ', category: 'emotion' },
    { id: 'emotion-2', name: 'נעמי', need: 'ליווי לאירוע משפחתי', minutes: 45, distance: '1.5 ק"מ', category: 'emotion' },
    { id: 'emotion-3', name: 'עומר', need: 'שיתוף ניסיון בנושא קריירה', minutes: 30, distance: '0.9 ק"מ', category: 'emotion' },
    { id: 'emotion-4', name: 'תמר', need: 'עזרה בהכנה לאירוע חגיגי', minutes: 40, distance: '1.1 ק"מ', category: 'emotion' },
    { id: 'emotion-5', name: 'גיא', need: 'שיחת עידוד והקשבה', minutes: 15, distance: '0.4 ק"מ', category: 'emotion' },
  ],
  mind: [
    { id: 'mind-1', name: 'לאה', need: 'עזרה בשיעורי בית של הילדים', minutes: 25, distance: '0.7 ק"מ', category: 'mind' },
    { id: 'mind-2', name: 'משה', need: 'הדרכה בטכנולוגיה בסיסית', minutes: 30, distance: '0.5 ק"מ', category: 'mind' },
    { id: 'mind-3', name: 'רות', need: 'עזרה במילוי טפסים ומסמכים', minutes: 20, distance: '0.3 ק"מ', category: 'mind' },
    { id: 'mind-4', name: 'אריאל', need: 'שיתוף ידע במקצוע מסוים', minutes: 35, distance: '1.0 ק"מ', category: 'mind' },
    { id: 'mind-5', name: 'הדס', need: 'ייעוץ בתכנון פיננסי בסיסי', minutes: 40, distance: '1.3 ק"מ', category: 'mind' },
  ],
};

export function getRandomRequestByCategory(category) {
  const requests = COMMUNITY_REQUESTS[category] || [];
  if (requests.length === 0) return null;
  const randomIndex = Math.floor(Math.random() * requests.length);
  return requests[randomIndex];
}
