#!/usr/bin/env python3
"""Translate all Hebrew strings in backend Python files."""
import re, glob, subprocess

BACKEND_TRANSLATIONS = {
    # Auth messages
    "כתובת האימייל כבר קיימת במערכת": "Email address already exists",
    "קוד ההזמנה אינו תקף": "Invalid invite code",
    "ההרשמה הצליחה!": "Registration successful!",
    "אימייל או סיסמה שגויים": "Invalid email or password",
    "התחברת בהצלחה!": "Login successful!",
    "התנתקת בהצלחה": "Logged out successfully",
    "לא מחובר": "Not logged in",
    "הנתונים הועברו בהצלחה לחשבון שלך": "Data migrated successfully to your account",
    "הגעת למגבלת קודי ההזמנה": "You have reached the invite code limit",
    
    # Admin messages
    "תודה על המשוב!": "Thank you for your feedback!",
    "הפעולה הראשונה שלך נשלחה לשדה!": "Your first action was sent to the field!",
    
    # Direction labels
    "'תרומה'": "'Contribution'",
    "'התאוששות'": "'Recovery'",
    "'סדר'": "'Order'",
    "'חקירה'": "'Exploration'",
    "'נזק'": "'Harm'",
    "'הימנעות'": "'Avoidance'",
    '"תרומה"': '"Contribution"',
    '"התאוששות"': '"Recovery"',
    '"סדר"': '"Order"',
    '"חקירה"': '"Exploration"',
    '"נזק"': '"Harm"',
    '"הימנעות"': '"Avoidance"',
    
    # Direction labels in f-strings and dicts
    'תרומה': 'Contribution',
    'התאוששות': 'Recovery',
    'סדר': 'Order',
    'חקירה': 'Exploration',
    'נזק': 'Harm',
    'הימנעות': 'Avoidance',
    
    # Insight strings - Field/Collective
    'השדה הקולקטיבי נוטה כעת ל': 'The collective field currently leans towards ',
    'השדה הקולקטיבי מראה נטייה חזקה ל': 'The collective field shows a strong tendency towards ',
    'השדה הקולקטיבי נוטה ל': 'The collective field leans towards ',
    'השדה הקולקטיבי נע השבוע יותר לכיוון': 'The collective field moved this week more towards',
    'השדה הקולקטיבי מתייצב בשבועות האחרונים.': 'The collective field is stabilizing in recent weeks.',
    'השדה הקולקטיבי נסחף מהאיזון בשבועות האחרונים.': 'The collective field has drifted from balance in recent weeks.',
    'השדה הקולקטיבי נסחף מהאיזון בימים האחרונים.': 'The collective field has drifted from balance in recent days.',
    'השדה הקולקטיבי נע בהדרגה לכיוון': 'The collective field is gradually moving towards',
    'השדה הקולקטיבי יציב ומאוזן בשבועות האחרונים.': 'The collective field is stable and balanced in recent weeks.',
    'השדה הקולקטיבי יציב ומאוזן.': 'The collective field is stable and balanced.',
    'השדה הקולקטיבי מתייצב ונע לכיוון איזון חיובי.': 'The collective field is stabilizing and moving towards positive balance.',
    'השדה הקולקטיבי יציב יחסית לתקופה הקודמת.': 'The collective field is relatively stable compared to the previous period.',
    'השדה הקולקטיבי נע לכיוון תרומה וסדר בשבועות האחרונים.': 'The collective field is moving towards contribution and order in recent weeks.',
    'השדה הקולקטיבי נע לכיוון סדר בשבועות האחרונים.': 'The collective field is moving towards order in recent weeks.',
    'השדה הקולקטיבי נע לכיוון חקירה בשבועות האחרונים.': 'The collective field is moving towards exploration in recent weeks.',
    'השדה הקולקטיבי נע לכיוון התאוששות בשבועות האחרונים.': 'The collective field is moving towards recovery in recent weeks.',
    'אין מספיק נתונים היסטוריים לזיהוי מגמה.': 'Not enough historical data to identify a trend.',
    'השדה מאוזן היום.': 'The field is balanced today.',
    'היום השדה נוטה לכיוון': 'Today the field leans towards',
    
    # Collective insights
    'לחץ הנזק הממוצע נמוך.': 'Average harm pressure is low.',
    'לחץ הנזק הממוצע גבוה יחסית.': 'Average harm pressure is relatively high.',
    'לחץ הנזק הממוצע בינוני.': 'Average harm pressure is moderate.',
    'לחץ הנזק ירד ביחס לתקופה הקודמת.': 'Harm pressure decreased relative to the previous period.',
    'לחץ הנזק עלה ביחס לתקופה הקודמת.': 'Harm pressure increased relative to the previous period.',
    'יש עלייה קלה בכיוון סדר.': 'There is a slight increase towards order.',
    'יש עלייה קלה בכיוון קולקטיבי.': 'There is a slight increase in the collective direction.',
    'הכיוון הממוצע מאוזן.': 'The average direction is balanced.',
    'יציבות ההתאוששות הקולקטיבית גבוהה.': 'Collective recovery stability is high.',
    'יש עלייה בהתאוששות הקולקטיבית.': 'There is an increase in collective recovery.',
    'יש ירידה בהתאוששות הקולקטיבית.': 'There is a decrease in collective recovery.',
    'הכיוון הקולקטיבי מתחזק.': 'The collective direction is strengthening.',
    'יש ירידה בכיוון הקולקטיבי.': 'There is a decrease in the collective direction.',
    'פעילות גבוהה יותר השבוע.': 'Higher activity this week.',
    'פעילות נמוכה יותר השבוע.': 'Lower activity this week.',
    
    # Compass insights
    'אתה מיושר היטב עם השדה הקולקטיבי.': 'You are well aligned with the collective field.',
    'המיקום שלך קרוב למרכז השדה הקולקטיבי.': 'Your position is close to the collective field center.',
    'אתה רחוק ממרכז השדה הקולקטיבי.': 'You are far from the collective field center.',
    'יש מרחק בין המיקום שלך לבין מרכז השדה הקולקטיבי.': 'There is a distance between your position and the collective field center.',
    'נראה סחף לכיוון כאוס. מומלץ לשקול פעולת התאוששות או סדר.': 'Drift towards chaos detected. Consider a recovery or order action.',
    'יש נטייה לבידוד. כדאי לשקול פעולת תרומה.': 'Tendency towards isolation detected. Consider a contribution action.',
    'אתה מתייצב לכיוון סדר.': 'You are stabilizing towards order.',
    'יש תנועה חיובית לכיוון תרומה.': 'There is positive movement towards contribution.',
    'אתה במצב התאוששות.': 'You are in a recovery state.',
    'המומנטום שלך חיובי לכיוון': 'Your momentum is positive towards',
    'המומנטום מראה סחף מהאיזון.': 'Momentum shows drift from balance.',
    
    # Pattern insights
    'אין מספיק נתונים לזיהוי דפוס. המשך לבצע פעולות.': 'Not enough data to identify a pattern. Keep performing actions.',
    'זוהה סחף לכיוון נזק. מומלץ לאזן עם התאוששות.': 'Drift towards harm detected. Recommend balancing with recovery.',
    'זוהה סחף לכיוון הימנעות. מומלץ לאזן עם סדר.': 'Drift towards avoidance detected. Recommend balancing with order.',
    'זוהה דפוס של בידוד (סדר ללא תרומה). מומלץ לפתוח לכיוון תרומה.': 'Isolation pattern detected (order without contribution). Consider opening towards contribution.',
    'נראה דפוס של התייצבות חיובית. המשך בכיוון זה.': 'Positive stabilization pattern detected. Continue in this direction.',
    'הדפוס הנוכחי מאוזן יחסית.': 'The current pattern is relatively balanced.',
    
    # Comparison insights
    'אתה בין ה-': 'You are in the top ',
    '% המובילים במיקוד על': '% focused on',
    'אתה מעל הממוצע במיקוד על': 'You are above average in focus on',
    'הכיוון המוביל שלך השבוע הוא': 'Your leading direction this week is',
    'המיקוד שלך מאוזן בין הכיוונים. זהו סימן טוב לאיזון.': 'Your focus is balanced between directions. This is a good sign of balance.',
    'אין מספיק נתונים השבוע. בצע פעולות כדי להשוות את עצמך לאחרים.': 'Not enough data this week. Perform actions to compare yourself with others.',
    
    # Next best direction
    'הצעד הבא: התאוששות. חזור לאיזון.': 'Next step: Recovery. Return to balance.',
    'הצעד הבא: ליצור מבנה וסדר.': 'Next step: Create structure and order.',
    'הצעד הבא: לתרום לאחרים.': 'Next step: Contribute to others.',
    'הצעד הבא: להיפתח לחדש.': 'Next step: Open up to new things.',
    'יצאת מהמסלול.': 'You went off track.',
    'נסחפת להימנעות.': 'You drifted into avoidance.',
    'מיקוד עצמי גבוה.': 'High self-focus.',
    'יש קיפאון.': 'There is stagnation.',
    'אתה על המסלול הנכון.': 'You are on the right track.',
    'ברוך הבא למסע.': 'Welcome to the journey.',
    'התחל עם פעולת התאוששות.': 'Start with a recovery action.',
    'התאוששות היא נקודת הפתיחה הטובה ביותר.': 'Recovery is the best starting point.',
    'המשך קדימה.': 'Keep moving forward.',
    'לאיזון מלא, נסה גם': 'For full balance, also try',
    'איזון בין הכיוונים מחזק את ההתמצאות.': 'Balance between directions strengthens orientation.',
    
    # Theory basis
    'נזק → התאוששות: כשיש נזק, הדרך חזרה היא דרך התאוששות.': 'Harm → Recovery: When there is harm, the way back is through recovery.',
    'הימנעות → סדר: הימנעות מאוזנת על ידי יצירת מבנה.': 'Avoidance → Order: Avoidance is balanced by creating structure.',
    'בידוד → תרומה: מיקוד עצמי מאוזן על ידי תרומה לאחרים.': 'Isolation → Contribution: Self-focus is balanced by contributing to others.',
    'נוקשות → חקירה: קיפאון מאוזן על ידי פתיחות וחקירה.': 'Rigidity → Exploration: Stagnation is balanced by openness and exploration.',
    
    # Loop state labels
    'לולאת הימנעות': 'Avoidance Loop',
    'ממוקד בהתאוששות': 'Focused on Recovery',
    'בונה סדר': 'Building Order',
    'מכוון לתרומה': 'Directed at Contribution',
    'מונע מחקירה': 'Driven by Exploration',
    'מעבר מהתאוששות לתרומה': 'Transition from Recovery to Contribution',
    'סחף מסדר': 'Drift from Order',
    'מאוזן': 'Balanced',
    'מתחיל מסע': 'Starting the Journey',
    
    # Loop descriptions  
    'נראה שאתה בדפוס של הימנעות. זה בסדר - זיהוי זה הצעד הראשון לשינוי.': "It seems you're in an avoidance pattern. That's okay — recognition is the first step to change.",
    'אתה בתהליך התאוששות פעיל. זה זמן חשוב לריפוי ואיזון.': 'You are in an active recovery process. This is an important time for healing and balance.',
    'אתה יוצר מבנה וסדר בחיים שלך. זה סימן של התקדמות.': 'You are creating structure and order in your life. This is a sign of progress.',
    'אתה ממוקד בתרומה לאחרים. זה מעשיר אותך ואת הסביבה.': 'You are focused on contributing to others. This enriches you and your environment.',
    'אתה פתוח לחדש ולחקירה. זה מרחיב את האופקים שלך.': 'You are open to new things and exploration. This expands your horizons.',
    'אתה עובר מהתאוששות לתרומה. זה מסע חיובי מאוד.': 'You are transitioning from recovery to contribution. This is a very positive journey.',
    'היית ממוקד בסדר אבל יש סחף. זה הזדמנות לבדוק מה השתנה.': 'You were focused on order but there is drift. This is an opportunity to check what changed.',
    'אתה מפזר את הפעולות שלך בין הכיוונים. זה מצב בריא.': 'You spread your actions between directions. This is a healthy state.',
    'ברוך הבא! אתה בתחילת המסע שלך.': 'Welcome! You are at the beginning of your journey.',
    
    # Loop insights
    'הימנעות היא תגובה טבעית. הצעד הבא הוא ליצור מבנה קטן.': 'Avoidance is a natural response. The next step is to create a small structure.',
    'התאוששות היא בסיס חיוני. כשתרגיש מוכן, נסה גם פעולות סדר.': 'Recovery is an essential foundation. When you feel ready, also try order actions.',
    'סדר מאפשר יציבות. השלב הבא יכול להיות תרומה לאחרים.': 'Order enables stability. The next step can be contributing to others.',
    'תרומה מחברת אותך לאחרים. זכור גם לדאוג לעצמך.': 'Contribution connects you to others. Remember to also take care of yourself.',
    'חקירה מביאה צמיחה. לפעמים כדאי גם לעצור וליצור סדר.': 'Exploration brings growth. Sometimes it is also worth stopping and creating order.',
    'המעבר הזה מראה התקדמות משמעותית. המשך בקצב שלך.': 'This transition shows significant progress. Continue at your pace.',
    'סחף הוא טבעי. חזור ליצור מבנה קטן אחד.': 'Drift is natural. Return to create one small structure.',
    'איזון הוא מטרה טובה. המשך לשמור על מגוון.': 'Balance is a good goal. Keep maintaining variety.',
    'כל מסע מתחיל בצעד אחד. התחל עם פעולת התאוששות.': 'Every journey begins with one step. Start with a recovery action.',
    
    # Questions
    'מה הדבר הקטן ביותר שאתה יכול לעשות עכשיו כדי ליצור סדר?': 'What is the smallest thing you can do right now to create order?',
    'איזו משימה קטנה אתה יכול להשלים ב-5 דקות הקרובות?': 'What small task can you complete in the next 5 minutes?',
    'מה הצעד הראשון שתוכל לעשות היום לקראת משהו שדחית?': 'What is the first step you can take today towards something you postponed?',
    'מה הדבר הקטן שאתה יכול לעשות היום עבור מישהו אחר?': 'What small thing can you do today for someone else?',
    'איך תוכל לתרום למישהו קרוב אליך היום?': 'How can you contribute to someone close to you today?',
    'מה תוכל לשתף עם אחרים מהניסיון שלך?': 'What can you share with others from your experience?',
    'מה משהו חדש שתוכל לנסות היום?': 'What is something new you can try today?',
    'איזו שאלה חדשה תוכל לשאול היום?': 'What new question can you ask today?',
    'מה הדבר שתמיד רצית לחקור אבל לא הספקת?': 'What is something you always wanted to explore but never got to?',
    'מה תעשה היום כדי לדאוג לעצמך?': 'What will you do today to take care of yourself?',
    'איזו הפסקה קטנה מגיעה לך היום?': 'What small break do you deserve today?',
    'מה יעזור לך להתאושש ולהטען מחדש?': 'What will help you recover and recharge?',
    'איזו משימה תוכל לסיים היום כדי ליצור סדר?': 'What task can you finish today to create order?',
    'מה הדבר שצריך ארגון בחיים שלך עכשיו?': 'What needs organizing in your life right now?',
    'איך תוכל ליצור מבנה קטן שיתמוך בך?': 'How can you create a small structure to support you?',
    'מה הצעד הבא שתעשה היום בכיוון של תרומה?': 'What is the next step you will take today towards contribution?',
    'איך תוכל להמשיך את המומנטום החיובי שלך?': 'How can you continue your positive momentum?',
    'מה תוכל לעשות היום שירחיב את המעגל שלך?': 'What can you do today to expand your circle?',
    'מה המבנה הקטן שתוכל ליצור מחדש היום?': 'What small structure can you recreate today?',
    'איזו הרגל טובה תוכל לחזור אליה?': 'What good habit can you return to?',
    'מה יעזור לך להרגיש יותר מאורגן?': 'What will help you feel more organized?',
    'מה הכיוון שהכי מושך אותך היום?': 'What direction attracts you most today?',
    'באיזה תחום תרצה להתמקד היום?': 'What area would you like to focus on today?',
    'מה יהפוך את היום הזה למשמעותי עבורך?': 'What would make this day meaningful for you?',
    'מה הדבר הראשון שתעשה היום לטובת עצמך?': 'What is the first thing you will do today for yourself?',
    'איך תרצה להתחיל את המסע שלך?': 'How would you like to start your journey?',
    'מה יגרום לך להרגיש טוב היום?': 'What will make you feel good today?',
    
    # Reflections / Suggestions
    'עשה פעולה פיזית קטנה שמסדרת משהו סביבך.': 'Do a small physical action that organizes something around you.',
    'הזז את הגוף היום — אפילו הליכה קצרה.': 'Move your body today — even a short walk.',
    'סדר פינה אחת בסביבה שלך.': 'Organize one corner in your environment.',
    'עשה משהו מעשי שדחית.': 'Do something practical that you postponed.',
    'שלח מילה טובה למישהו שלא ציפה לזה.': 'Send a kind word to someone who does not expect it.',
    'הקשב למישהו היום — באמת הקשב.': 'Listen to someone today — really listen.',
    'עשה משהו קטן עבור מישהו קרוב.': 'Do something small for someone close.',
    'תן לעצמך רגע של חמלה היום.': 'Give yourself a moment of compassion today.',
    'מצא דבר אחד חדש שלא שמת לב אליו קודם.': 'Find one new thing you have not noticed before.',
    'ארגן רעיון אחד שמסתובב לך בראש.': 'Organize one idea that has been going through your mind.',
    'למד משהו קטן שלא ידעת.': 'Learn something small you did not know.',
    'קבל החלטה אחת שדחית.': 'Make one decision you postponed.',
    
    # Actions for compass
    'קח הפסקה של 5 דקות ונשום עמוק.': 'Take a 5-minute break and breathe deeply.',
    'שתה כוס מים ושב בשקט לרגע.': 'Drink a glass of water and sit quietly for a moment.',
    'צא להליכה קצרה של 10 דקות.': 'Go for a short 10-minute walk.',
    'כתוב 3 דברים שאתה אסיר תודה עליהם.': 'Write down 3 things you are grateful for.',
    'האזן לשיר אחד שאתה אוהב.': 'Listen to one song you love.',
    'בחר משימה קטנה אחת והשלם אותה עכשיו.': 'Choose one small task and complete it now.',
    'סדר פינה אחת בחדר שלך.': 'Organize one corner of your room.',
    'כתוב רשימה של 3 דברים לעשות היום.': 'Write a list of 3 things to do today.',
    'קבע זמן קבוע למשימה שדחית.': 'Set a fixed time for a task you postponed.',
    'מחק 5 הודעות ישנות מהטלפון.': 'Delete 5 old messages from your phone.',
    'שלח הודעה חיובית למישהו שאכפת לך ממנו.': 'Send a positive message to someone you care about.',
    'הצע עזרה קטנה למישהו קרוב.': 'Offer a small help to someone close.',
    'הקשב למישהו במשך 5 דקות בלי להפריע.': 'Listen to someone for 5 minutes without interrupting.',
    'שתף משהו מועיל עם אחרים.': 'Share something useful with others.',
    'תן מחמאה כנה למישהו.': 'Give a sincere compliment to someone.',
    'נסה משהו חדש שלא עשית קודם.': 'Try something new you have not done before.',
    'קרא מאמר על נושא שמעניין אותך.': 'Read an article about a topic that interests you.',
    'שאל שאלה שלא שאלת קודם.': 'Ask a question you have not asked before.',
    'לך בדרך אחרת מהרגיל.': 'Take a different path than usual.',
    'התחל שיחה עם מישהו חדש.': 'Start a conversation with someone new.',
    'בצע את הפעולה הראשונה שלך כדי לקבל ניתוח מצפן.': 'Perform your first action to receive a compass analysis.',
    'המשך בכיוון שלך.': 'Continue in your direction.',
    
    # Weekly insights
    'שבוע מאוזן! פעלת במגוון כיוונים.': 'Balanced week! You acted in a variety of directions.',
    'כדאי לשקול גיוון.': 'Consider diversifying.',
    'אך רוב הפעולות היום נעו לכיוון ה': 'but most actions today moved towards ',
    'והפעולות שלך היום תאמו את הבחירה.': 'and your actions today matched the choice.',
    
    # Greetings
    'בוקר טוב': 'Good morning',
    'צהריים טובים': 'Good afternoon',
    'ערב טוב': 'Good evening',
    
    # Time labels  
    'עכשיו': 'now',
    'שבוע ': 'Week ',
    'השבוע': 'This week',
    
    # Status labels
    'עולה': 'rising',
    'יורד': 'falling',
    'יציב': 'stable',
    'חדש': 'new',
    'שקט': 'quiet',
    'איזון': 'Balance',
    'עליון 10%': 'Top 10%',
    'עליון 25%': 'Top 25%',
    'מעל הממוצע': 'Above average',
    'פעיל': 'Active',
    
    # Various
    'הפעולה שלך חיזקה היום את שדה ה': 'Your action today strengthened the field of ',
    'הפעולה שלך נוספה לשדה האנושי': 'Your action was added to the human field',
    'השלמתי את השאלה היומית': 'I completed the daily question',
    'הפעולה הראשונה שלך העניקה נקודת ערך ל': 'Your first action awarded a value point to ',
    'אין מספיק נתונים. בצע פעולות כדי לראות את המיקום שלך.': 'Not enough data. Perform actions to see your position.',
    'אין עדיין נתוני הפעלה חוזרת. התחל לבדוק מסלולים חלופיים כדי לקבל תובנות.': 'No replay data yet. Start checking alternative paths to get insights.',
    'אין מספיק נתונים השבוע. התחל עם פעולה אחת.': 'Not enough data this week. Start with one action.',
    'שבוע שקט. כדאי להוסיף עוד פעולות.': 'Quiet week. Consider adding more actions.',
    'אין מספיק נתונים השבוע. נסה לענות על השאלה היומית כל יום.': 'Not enough data this week. Try answering the daily question every day.',
    'השבוע הייתה לך פעילות מאוזנת בכל הכיוונים.': 'This week you had balanced activity across all directions.',
    'עוד לא ביצעת פעולות היום. התחל את היום עם השאלה היומית.': 'You have not performed actions today. Start the day with the daily question.',
    'היום עוד לא ביצעת פעולות. מחר יום חדש.': 'You have not performed actions today. Tomorrow is a new day.',
    'אין מספיק נתונים לחישוב מומנטום.': 'Not enough data to calculate momentum.',
    'ומתייצב.': 'and is stabilizing.',
    'אך יש סחף מהאיזון.': 'but there is drift from balance.',
    'ומשנה כיוון.': 'and is changing direction.',
    
    # Social routes
    'הצטרפת למשימה!': 'You joined the mission!',
    'כבר חבר במעגל': 'Already a member of the circle',
    'הצטרפת למעגל!': 'You joined the circle!',
    'לא חבר במעגל': 'Not a member of the circle',
    'עזבת את המעגל': 'You left the circle',
    'חזק את הקשר': 'Strengthen the connection',
    'שקם את הבסיס': 'Restore the foundation',
    'שחזר סדר': 'Restore order',
    'הרחב את השדה': 'Expand the field',
    'עשה פעולה אחת של נתינה היום': 'Do one act of giving today',
    'קח זמן אחד להתאוששות': 'Take one moment for recovery',
    'ארגן דבר אחד בסביבה שלך': 'Organize one thing in your environment',
    'נסה דבר חדש אחד היום': 'Try one new thing today',
    'משימה': 'Mission',
    'משימת מעגל': 'Circle mission',
    'פעולה ראשונה': 'First Action',
    '10 פעולות': '10 Actions',
    '50 פעולות': '50 Actions',
    '100 פעולות': '100 Actions',
    'שבוע רצוף': 'Weekly Streak',
    
    # Helpers
    'השדה שקט. ממתין לפעולה ראשונה.': 'The field is quiet. Awaiting the first action.',
    'המסלול החלופי הנבדק ביותר הוא': 'The most checked alternative path is',
    'מההפעלות החוזרות': 'of the replays',
    'אתה נוטה לבדוק מסלולי': 'You tend to check paths of',
    'כשאתה בוחר ב': 'when you choose',
    'זה מצביע על מודעות לחלופות חיוביות': 'This indicates awareness of positive alternatives',
    'פעמים': 'times',
    'הדפוס הנפוץ ביותר': 'The most common pattern',
    'אתה מרבה לבדוק חלופות להחלטות מסוג': 'You frequently check alternatives for decisions of type',
    'נקודה עיוורת: מעולם לא בדקת מסלול': 'Blind spot: you never checked a path of',
    'אחרי החלטת': 'after a decision of',
    'יש לך נטייה לבדוק מסלולי התאוששות - ייתכן שאתה מרגיש צורך במנוחה שלא מתממש.': 'You tend to check recovery paths — you may feel a need for rest that is not being met.',
    'אתה נמנע מלבדוק מסלולי נזק בהפעלות חוזרות - סימן חיובי למודעות ערכית.': 'You avoid checking harm paths in replays — a positive sign of value awareness.',
    
    # Country names
    'ברזיל': 'Brazil', 'הודו': 'India', 'גרמניה': 'Germany', 'ארה"ב': 'USA',
    'יפן': 'Japan', 'ניגריה': 'Nigeria', 'ישראל': 'Israel', 'צרפת': 'France',
    'אוסטרליה': 'Australia', 'דרום קוריאה': 'South Korea', 'מקסיקו': 'Mexico',
    'בריטניה': 'UK', 'קנדה': 'Canada', 'איטליה': 'Italy', 'ספרד': 'Spain',
    'ארגנטינה': 'Argentina', 'טורקיה': 'Turkey', 'תאילנד': 'Thailand',
    'פולין': 'Poland', 'הולנד': 'Netherlands',
    
    # Base/Department labels
    'לב': 'Connection',
    'ראש': 'Mind',
    'גוף': 'Body',
    'מאיזה מרכז אתה פועל היום?': 'What center are you operating from today?',
    'קשרים ומערכות יחסים': 'Relationships & Connections',
    'אמפתיה והקשבה': 'Empathy & Listening',
    'תרומה ונתינה': 'Giving & Contributing',
    'תיקון רגשי': 'Emotional Healing',
    'סדר ותכנון': 'Order & Planning',
    'למידה וחקירה': 'Learning & Inquiry',
    'קבלת החלטות': 'Decision Making',
    'חשיבה אסטרטגית': 'Strategic Thinking',
    'תנועה ובריאות': 'Movement & Health',
    'פעולה מעשית': 'Practical Action',
    'משמעת ומחויבות': 'Discipline & Commitment',
    'סדר פיזי': 'Physical Order',
    
    # Misc labels
    'חדש': 'new',
    'מוביל': 'Leading',
    'משתמש חדש': 'New User',
    'באוריינטציית': 'in orientation of',
    'מדד ההתמצאות היום': 'Orientation Index today',
    'מובילה': 'is leading',
    'אתמול': 'yesterday',
    
    # Daily summary
    'היום ביצעת': 'Today you performed',
    'פעמים, בעיקר בכיוון': 'times, mainly towards',
    'ההשפעה שלך על השדה': 'Your impact on the field',
    'בחרת לפעול מה': 'You chose to act from the ',
    'הכוח הדומיננטי': 'Dominant force',
    'הכיוון המוביל': 'Leading direction',
    'השבוע התמקדת מאוד ב': 'This week you focused heavily on ',
    'השבוע עברת מהתאוששות לפעולה. כיוון מוביל': 'This week you moved from recovery to action. Leading direction',
    'הכיוון המוביל שלך השבוע': 'Your leading direction this week',
    
    # Mission descriptions
    'משימת היום: תרומה': 'Mission of the Day: Contribution',
    'עשה פעולה קטנה שתעזור למישהו אחר היום': 'Do a small action to help someone else today',
    'משימת היום: התאוששות': 'Mission of the Day: Recovery',
    'קח רגע של מנוחה והטענה עצמית היום': 'Take a moment of rest and self-recharging today',
    'משימת היום: סדר': 'Mission of the Day: Order',
    'ארגן דבר אחד קטן בסביבה שלך היום': 'Organize one small thing in your environment today',
    'משימת היום: חקירה': 'Mission of the Day: Exploration',
    'נסה משהו חדש או למד דבר אחד חדש היום': 'Try something new or learn one new thing today',
    
    # Narrative helpers
    'השדה נוטה ל': 'The field leans towards ',
    'התנועה מתחזקת': 'Movement is strengthening',
    'גל של': 'A wave of',
    'עובר בשדה': 'passes through the field',
    'פעילות': 'Activity',
    'עולה ברחבי השדה': 'rising across the field',
    'השדה נרגע': 'The field is calming down',
    'עדיין מוביל': 'still leads',
    'התנועה מאטה': 'Movement is slowing',
    'שומר על נוכחות': 'maintaining presence',
    'השדה שוקע לשקט, עם נטייה ל': 'The field settles into quiet, leaning towards ',
    'שולט בשדה היום': 'dominates the field today',
    'כוח ה': 'The force of ',
    'דומיננטי בשדה': 'is dominant in the field',
    'השדה מתפצל בין': 'The field splits between',
    'מתח בין': 'Tension between',
    'מושכים את השדה לכיוונים שונים': 'pulling the field in different directions',
    'מתייצב במספר אזורים': 'stabilizing in several regions',
    'השדה פעיל ברחבי העולם': 'The field is active around the world',
    'מתפשטת בין אזורים': 'spreading between regions',
    'תנועת': 'Movement of',
    'נמשכת בשדה': 'continues in the field',
    
    # Time
    'ד': 'm',  # minutes abbreviation
    'ש': 'h',  # hours abbreviation
}

def translate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    for old, new in sorted(BACKEND_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True):
        content = content.replace(old, new)
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Process backend Python files
backend_files = glob.glob('/app/backend/**/*.py', recursive=True)
backend_files = [f for f in backend_files if '__pycache__' not in f and 'tests/' not in f]

changed = 0
for f in sorted(backend_files):
    if translate_file(f):
        changed += 1
        print(f'Translated: {f}')

print(f'\nDone. {changed} backend files modified.')

# Check remaining
result = subprocess.run(
    ['grep', '-Prln', '[\u0590-\u05FF]'] + backend_files,
    capture_output=True, text=True
)
remaining = [f for f in result.stdout.strip().split('\n') if f and 'test' not in f.lower()]
print(f'Files still with Hebrew (excl. tests): {len(remaining)}')
for f in remaining:
    r = subprocess.run(['grep', '-Poc', '[\u0590-\u05FF]', f], capture_output=True, text=True)
    print(f'  {f} ({r.stdout.strip()} chars)')
