#!/usr/bin/env python3
"""Bulk translate Hebrew strings to English across all frontend files."""
import re, os, glob

# Common Hebrew -> English translation map
TRANSLATIONS = {
    # Direction labels (common across many files)
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
    
    # Department labels
    "'ראש'": "'Mind'",
    "'גוף'": "'Body'",
    '"ראש"': '"Mind"',
    '"גוף"': '"Body"',
    
    # Navigation/Tab labels  
    "'בית'": "'Home'",
    "'פיד'": "'Feed'",
    "'קהילה'": "'Community'",
    "'תובנות'": "'Insights'",
    "'תיאוריה'": "'Theory'",
    "'היסטוריה'": "'History'",
    "'מובילים'": "'Leaders'",
    "'משימות'": "'Missions'",
    
    # Common UI strings
    'טוען...': 'Loading...',
    'טוען נתונים': 'Loading data',
    'טוען': 'Loading',
    'מעבד...': 'Processing...',
    'מעדכן...': 'Updating...',
    'שגיאה': 'Error',
    'הצלחה': 'Success',
    'אישור': 'Confirm',
    'ביטול': 'Cancel',
    'סגור': 'Close',
    'שמור': 'Save',
    'מחק': 'Delete',
    'ערוך': 'Edit',
    'הוסף': 'Add',
    'חזרה': 'Back',
    'הבא': 'Next',
    'הקודם': 'Previous',
    'חיפוש': 'Search',
    'סינון': 'Filter',
    'הכל': 'All',
    'ללא': 'None',
    'כן': 'Yes',
    'לא': 'No',
    
    # Auth / Account
    'התחבר': 'Sign In',
    'התחברות': 'Sign In',
    'הרשמה': 'Sign Up',
    'הרשם': 'Sign Up',
    'אימייל': 'Email',
    'סיסמה': 'Password',
    'התנתק': 'Sign Out',
    'חשבון': 'Account',
    
    # Status labels
    'מסונכרן': 'Synced',
    'לא מקוון': 'Offline',
    'פעיל': 'Active',
    'לא פעיל': 'Inactive',
    'הושלם': 'Completed',
    'ממתין': 'Waiting',
    'בתהליך': 'In Progress',
    
    # Common descriptive text patterns
    'שגיאה בטעינת נתונים': 'Error loading data',
    'שגיאה בחיבור לשרת': 'Error connecting to server',
    'שגיאה בטעינת': 'Error loading',
    'נתונים אנונימיים מכלל המשתמשים': 'Anonymous data from all users',
    'כל הנתונים מוצגים באופן אנונימי ומצטבר': 'All data is displayed anonymously and in aggregate',
    'משתמשים פעילים היום': 'active users today',
    'ברצף': 'on a streak',
    'משתמשים': 'users',
    'החלטות': 'decisions',
    'פעולות': 'actions',
    'חברים': 'members',
    'ימים': 'days',
    'דקות': 'minutes',
    'שבועות': 'weeks',
    'ימים רצופים': 'consecutive days',
    'נקודות': 'points',
    'נקודות ערך': 'value points',
    'פעילים': 'active',
    
    # Section titles
    'שדה קולקטיבי': 'Collective Field',
    'מראה קולקטיבית': 'Collective Mirror',
    'מסלול קולקטיבי': 'Collective Trajectory',
    'מגמות קולקטיביות': 'Collective Trends',
    'רצף קהילתי': 'Community Streak',
    'מעגלי ערך': 'Value Circles',
    'תובנות שרשרת': 'Chain Insights',
    'למידה אדפטיבית': 'Adaptive Learning',
    'התמצאות יומית': 'Daily Orientation',
    'שרשרת השפעה': 'Influence Chain',
    'היסטוריית שדה': 'Field History',
    'התפלגות כיוונים': 'Direction Distribution',
    'ציר הניגודים': 'Opposition Axes',
    'רשומת פעולות': 'Action Record',
    'אמון שדה': 'Field Trust',
    'ערך שדה': 'Field Value',
    'סיכון שדה': 'Field Risk',
    'מצב אמון': 'Trust Status',
    'תרומה לשדה': 'Field Contribution',
    'השפעה': 'Impact',
    'רצף': 'Streak',
    'תרומה קולקטיבית': 'Collective Contribution',
    'חקירת מסלולים': 'Path Exploration',
    'לחץ נזק': 'Harm Pressure',
    'מגמת סדר': 'Order Trend',
    'יציבות התאוששות': 'Recovery Stability',
    'סחף סדר': 'Order Drift',
    'סחף קולקטיבי': 'Collective Drift',
    'התפלגות ערכים קולקטיבית': 'Collective Value Distribution',
    'סחף סדר ממוצע': 'Average Order Drift',
    'סחף קולקטיבי ממוצע': 'Average Collective Drift',
    'לחץ נזק ממוצע': 'Average Harm Pressure',
    'יציבות התאוששות': 'Recovery Stability',
    
    # Detailed strings from sections
    'הפעולה הזו נובעת מהכיוון המומלץ': 'This action follows the recommended direction',
    'בטל קישור להמלצה': 'Unlink from recommendation',
    'בטל קישור': 'Unlink',
    'השוואת הדפוסים שלך לשדה הקולקטיבי': 'Comparing your patterns to the collective field',
    'ההחלטות שלך': 'Your decisions',
    'אתה': 'You',
    'ממוצע קולקטיבי': 'Collective average',
    'תובנות השוואה': 'Comparison insights',
    'תובנות מגמה': 'Trend insights',
    'תובנות מגמתיות': 'Trend insights',
    'תובנות אדפטיביות': 'Adaptive insights',
    'תובנות קולקטיביות': 'Collective insights',
    
    # Closing layer
    'מה השתנה היום?': 'What changed today?',
    'הבסיס שבחרת היום': 'Your chosen base today',
    'הכי פעיל': 'Most active',
    'מועדף': 'Preferred',
    'מוזנח': 'Neglected',
    'הכיוון הדומיננטי של הפעולות שלך היום': 'The dominant direction of your actions today',
    'מבט למחר': 'Looking ahead to tomorrow',
    'מתח עולה': 'Rising tension',
    'השדה ממשיך להשתנות': 'The field keeps changing',
    'שינוי בשדה הגלובלי': 'Change in the global field',
    
    # AdaptiveLearningSection
    'התאמת דירוג מסלולים לפי ביצועים': 'Adjusting path ranking by performance',
    'צריך לפחות 2 החלטות עם בחירת מסלול כדי להתחיל ללמוד': 'Need at least 2 decisions with path selection to start learning',
    'בחר מסלולים והערך אותם כדי לבנות היסטוריית למידה': 'Select paths and evaluate them to build learning history',
    'התאמות דירוג נוכחיות': 'Current ranking adjustments',
    'רמת אמון לפי סוג מסלול': 'Trust level by path type',
    'דיוק התחזיות הכללי': 'Overall prediction accuracy',
    'למידות': 'learnings',
    'דיוק התחזיות גבוה - המערכת לומדת היטב': 'Prediction accuracy is high — the system is learning well',
    'דיוק התחזיות בינוני - המערכת מתכווננת': 'Prediction accuracy is moderate — the system is adjusting',
    
    # ChainInsightsSection
    'ניתוח דפוסים התנהגותיים מהמסלולים שלך': 'Analyzing behavioral patterns from your paths',
    'מסלול התאוששות': 'Recovery Path',
    'מסלול סיכון': 'Risk Path',
    'מסלול צמיחה': 'Growth Path',
    'תיקון באמצע המסלול': 'Mid-path Correction',
    'שרשרת עקבית של החלטות חיוביות': 'Consistent chain of positive decisions',
    'שרשרת של החלטות בעייתיות - שקול לשנות כיוון': 'Chain of problematic decisions — consider changing direction',
    'דפוס חוזר': 'Repeating Pattern',
    'דפוס תיקון רגשי': 'Emotional Correction Pattern',
    'התראה': 'Warning',
    'מסלולי התאוששות': 'Recovery paths',
    'התראות': 'Warnings',
    'תיקונים': 'Corrections',
    'דפוסים': 'Patterns',
    
    # CircleDetailView
    'טוען מעגל...': 'Loading circle...',
    'חזרה למעגלים': 'Back to circles',
    'עזוב': 'Leave',
    'הצטרף': 'Join',
    'אין פעולות עדיין': 'No actions yet',
    'אין מובילים עדיין': 'No leaders yet',
    'אין משימות פעילות': 'No active missions',
    'קהילות לפי כיוון ונישה': 'Communities by direction and niche',
    
    # CollectiveLayerSection
    'טוען נתונים קולקטיביים...': 'Loading collective data...',
    
    # CollectiveTrajectorySection  
    'תנועת הדפוסים שלך ביחס לשדה הקולקטיבי לאורך זמן': 'Your pattern movement relative to the collective field over time',
    'המשך להוסיף החלטות כדי לראות מגמות לאורך זמן': 'Keep adding decisions to see trends over time',
    'נתוני השבוע הנוכחי ביחס לקולקטיב': "This week's data relative to the collective",
    'מתקרב לממוצע': 'Converging to average',
    'מעל ומתרחק': 'Above and diverging',
    'מתחת ומתרחק': 'Below and diverging',
    'יציב': 'Stable',
    'עכשיו': 'Now',
    
    # CollectiveTrendsSection
    'השוואת 7 ימים אחרונים מול תקופה קודמת': 'Comparing last 7 days vs. previous period',
    'מגמות 7 ימים אחרונים': 'Last 7 days trends',
    'השוואת תקופות': 'Period comparison',
    'תקופה קודמת': 'Previous period',
    'תקופה נוכחית': 'Current period',
    'שינוי סחף סדר': 'Order drift change',
    'שינוי סחף קולקטיבי': 'Collective drift change',
    'שינוי לחץ נזק': 'Harm pressure change',
    'שינוי יציבות': 'Stability change',
    'שינוי בפעילות': 'Activity change',
    'טוען נתוני מגמות...': 'Loading trend data...',
    
    # CommunityStreakSection
    'אנשים נמצאים ברצף היום': 'people are on a streak today',
    'רצף הארוך ביותר': 'Longest streak',
    
    # Compass AI
    'מצפן AI': 'AI Compass',
    
    # OnboardingHint, FeedbackButton, etc.
    'ברוך הבא': 'Welcome',
    'משוב': 'Feedback',
    'שלח': 'Send',
    'שלח משוב': 'Send Feedback',
    
    # EntryLayer
    'מערכת התמצאות': 'Orientation System',
    
    # FieldMissionSection
    'משימת שדה': 'Field Mission',
    'משימה יומית': 'Daily Mission',
    
    # Globe
    'שלח נקודה': 'Send Point',
    'נשלח': 'Sent',
    'גלובוס שדה': 'Field Globe',
    
    # InviteSection
    'הזמנות': 'Invites',
    'הזמן': 'Invite',
    'העתק': 'Copy',
    'הועתק': 'Copied',
    'העתק קישור': 'Copy Link',
    
    # FieldImpactLayer
    'השפעת שדה': 'Field Impact',
    
    # Subscription
    'מנוי': 'Subscription',
    'שדרג': 'Upgrade',
    
    # Theory
    'תיאוריה': 'Theory',
    
    # Weekly/Monthly reports
    'סיכום שבועי': 'Weekly Summary',
    'דוח שבועי': 'Weekly Report',
    'דוח חודשי': 'Monthly Report',
    'דוח רבעוני': 'Quarterly Review',
    'תובנה שבועית': 'Weekly Insight',
    
    # Decision path
    'מסלול החלטות': 'Decision Path',
    'מסלולי החלטה': 'Decision Paths',
    'מנוע מסלולים': 'Path Engine',
    'היסטוריית החלטות': 'Decision History',
    'החלטה מהירה': 'Quick Decision',
    
    # Data files
    'עזרה ברגע קשה': 'Help in a tough moment',
    'שיחה': 'Conversation',
    'ליווי': 'Guidance',
    'תמיכה': 'Support',
    'הקשבה': 'Listening',
    'עידוד': 'Encouragement',
    
    # Categories
    'גוף': 'Body',
    'רגש': 'Emotion',
    'מחשבה': 'Mind',
    
    # Hooks
    'דעיכה יומית': 'Daily Decay',
    
    # Send to Globe
    'סמן נוכחות בשדה': 'Mark presence in the field',
    
    # Various common inline text
    'הוזמן על ידי': 'Invited by',
    'הוזמנת על ידי': 'Invited by',
    'הביא לשדה': 'Brought to the field',
    'אנשים לשדה': 'people to the field',
    'כבר הצטרפו': 'already joined',
    'מוגבל': 'Restricted',
    'שביר': 'Fragile',
    'בבנייה': 'Building',
    'ראשוני': 'Initial',
    'התחלה': 'Starting',
    
    # OrientationShareCard
    'שתף': 'Share',
    'הורד תמונה': 'Download Image',
    'לחץ בחוץ לסגירה': 'Click outside to close',
    
    # Orientation
    'התמצאות': 'Orientation',
    'התמצאות יומית': 'Daily Orientation',
    
    # Various text patterns
    'צעד קטן אחד יכול לשנות את הכיוון': 'One small step can change your direction',
    'מצוין! הפעולה נרשמה': 'Great! Action recorded',
    'הושלם היום': 'Completed today',
    'עשיתי את זה': 'I did it',
    'צפה בפרופיל': 'View Profile',
    'צפה ברשומת הפעולות שלך': 'View your action record',
    'שתף את ההתמצאות שלך': 'Share your orientation',
    'מאיזה מרכז אתה פועל היום?': 'What center are you operating from today?',
    'המרכז שלך היום': 'Your center today',
    'הקצאות אפשריות היום': 'Possible allocations today',
    'בחר בסיס יומי כדי להמשיך לפעולה': 'Select a daily base to continue',
    'הזמן מישהו לשדה': 'Invite someone to the field',
    'מה עכשיו?': "What's next?",
    
    # Closing layer narrative strings
    'מחר, שקול אם יש מקום גם להתאוששות — נתינה מתמדת דורשת הטענה.': 'Tomorrow, consider if there\'s room for recovery — constant giving requires recharging.',
    'מחר, כשתרגיש מוכן, נסה לצאת החוצה — פעולה קטנה של תרומה או חקירה.': 'Tomorrow, when you feel ready, try going outward — a small act of contribution or exploration.',
    'מחר, אחרי שבנית מבנה, תן לעצמך רגע של חקירה — גילוי דברים חדשים.': 'Tomorrow, after building structure, allow yourself a moment of exploration — discovering new things.',
    'מחר, נסה לתת מבנה למה שגילית — סדר עוזר לעגן את החקירה.': 'Tomorrow, try giving structure to what you discovered — order helps anchor exploration.',
    
    # Tension narratives
    'כוח ההתאוששות עולה ברקע. השדה מאזן: כשהנתינה חזקה, הצורך במנוחה גובר.': 'Recovery force is rising in the background. The field balances: when giving is strong, the need for rest grows.',
    'כוח התרומה מתעורר. ההטענה שלך יוצרת אנרגיה — מחר היא תחפש כיוון.': 'The force of contribution awakens. Your recharging creates energy — tomorrow it will seek direction.',
    'כוח החקירה מתרחב בצד. ככל שהסדר מתחזק, הפיתוי לגלות חדש גדל.': 'The force of exploration expands on the side. As order strengthens, the urge to discover grows.',
    'כוח הסדר מתגבש. מה שגילית היום צריך מסגרת — וזה ימשוך אותך מחר.': 'The force of order solidifies. What you discovered today needs a framework — and it will draw you tomorrow.',
    
    # Return cues
    'מישהו עשוי להמשיך מה שהתחלת. חזור כדי לראות.': 'Someone may continue what you started. Come back to see.',
    'האנרגיה שטענת תהפוך לפעולה. חזור כדי לכוון אותה.': 'The energy you charged will turn into action. Come back to direct it.',
    'המבנה שבנית ישפיע על השדה. חזור כדי לראות איך.': 'The structure you built will affect the field. Come back to see how.',
    'מה שגילית עוד לא נגמר. חזור כדי להמשיך.': 'What you discovered is not over yet. Come back to continue.',
    
    # CollectiveMirrorSection detailed
    'התאוששות אצלך גבוהה מהממוצע הקולקטיבי': 'Your recovery is above the collective average',
    'מסלולי התאוששות נבחרים פחות מהממוצע': 'Recovery paths are chosen less than average',
    'לחץ הנזק אצלך השבוע נמוך מהממוצע': 'Your harm pressure this week is below average',
    'לחץ הנזק אצלך גבוה מהממוצע הקולקטיבי': 'Your harm pressure is above the collective average',
    'מגמת הסדר אצלך חזקה מהממוצע': 'Your order trend is stronger than average',
    'מסלולי סדר נבחרים פחות מהממוצע': 'Order paths are chosen less than average',
    'התרומה הקולקטיבית שלך גבוהה מהממוצע': 'Your collective contribution is above average',
    'אתה חוקר יותר מסלולים חלופיים מהממוצע': 'You explore more alternative paths than average',
    'הדפוסים שלך דומים לממוצע הקולקטיבי': 'Your patterns are similar to the collective average',
    'שגיאה בטעינת נתונים קולקטיביים': 'Error loading collective data',
    
    # CollectiveTrajectorySection detailed
    'אתה מתקרב בהדרגה למגמת ההתאוששות הקולקטיבית': 'You are gradually converging with the collective recovery trend',
    'ההתאוששות שלך נעה מעל הממוצע הקולקטיבי לאורך זמן': 'Your recovery moves above the collective average over time',
    'נראה ריחוק גובר ממגמת הסדר הקולקטיבית': 'There appears to be growing divergence from the collective order trend',
    'מגמת הסדר שלך מתקרבת לממוצע הקולקטיבי': 'Your order trend is converging with the collective average',
    'תרומתך נעה מעל הממוצע הקולקטיבי לאורך זמן': 'Your contribution moves above the collective average over time',
    'רמת התרומה שלך מתקרבת לממוצע הקולקטיבי': 'Your contribution level is converging with the collective average',
    'לחץ הנזק שלך יורד מתחת לממוצע הקולקטיבי': 'Your harm pressure is dropping below the collective average',
    'לחץ הנזק שלך מתרחק מעלה מהממוצע הקולקטיבי': 'Your harm pressure is diverging above the collective average',
    'המגמות שלך יציבות ביחס לשדה הקולקטיבי': 'Your trends are stable relative to the collective field',
    
    # AdaptiveLearningSection detailed patterns (with template vars)
}

# RTL direction removal
DIR_RTL_PATTERN = re.compile(r'\s+dir="rtl"')
# Hebrew locale patterns
HE_LOCALE_PATTERNS = [
    ("'he-IL'", "'en-US'"),
    ('"he-IL"', '"en-US"'),
    ("{ locale: he }", ""),
    (", { locale: he }", ""),
]

def translate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Apply direct translations (longest first to avoid partial matches)
    sorted_translations = sorted(TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True)
    for hebrew, english in sorted_translations:
        content = content.replace(hebrew, english)
    
    # Remove dir="rtl" 
    content = DIR_RTL_PATTERN.sub('', content)
    
    # Replace Hebrew locale references
    for old, new in HE_LOCALE_PATTERNS:
        content = content.replace(old, new)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Find all JS/JSX files with Hebrew
files = []
for ext in ['*.js', '*.jsx', '*.ts', '*.tsx']:
    files.extend(glob.glob(f'/app/frontend/src/**/{ext}', recursive=True))

changed = 0
for f in sorted(files):
    if translate_file(f):
        changed += 1
        print(f'Translated: {f}')

print(f'\nDone. {changed} files modified.')

# Check remaining Hebrew
import subprocess
result = subprocess.run(
    ['grep', '-Prl', '[\u0590-\u05FF]', '/app/frontend/src/', '--include=*.js', '--include=*.jsx'],
    capture_output=True, text=True
)
remaining = result.stdout.strip().split('\n') if result.stdout.strip() else []
print(f'Files still containing Hebrew: {len(remaining)}')
for f in remaining:
    print(f'  {f}')
