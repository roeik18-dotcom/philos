#!/usr/bin/env python3
"""Second pass: Translate remaining Hebrew strings to English."""
import re, os, glob

# Extended translation map for remaining Hebrew
TRANSLATIONS = {
    # Compass AI Section
    'המצפן שלך': 'Your Compass',
    'כיוון דומיננטי': 'Dominant direction',
    'כיוון חלש': 'Weak direction',
    'איזון כיוונים': 'Direction balance',
    'פעולה מוצעת': 'Suggested action',
    'כיוון מומלץ': 'Recommended direction',
    'כיוון מוביל': 'Leading direction',
    
    # ClosingLayer
    'נעת בכיוון': 'You moved in the direction of',
    'chosenHe': 'chosenEn',
    
    # CollectiveLayerSection
    'ערך דומיננטי': 'Dominant value',
    'כיוון': 'Direction',
    'קולקטיבי': 'Collective',
    'אגו': 'Ego',
    'כאוס': 'Chaos',
    'מאוזן': 'Balanced',
    
    # CollectiveMirrorSection
    'הנתונים מבוססים על': 'Data is based on',
    'מ-': 'from ',
    
    # CollectiveTrajectorySection
    'מגמה לאורך': 'Trend over',
    'לפני': 'ago',
    "ש'": 'w',
    
    # ContinuePreviousSessionSection
    'לפני רגע': 'Just now',
    'שעות': 'hours',
    'חודשים': 'months',
    'אתמול': 'Yesterday',
    'המשך מהמפגש הקודם': 'Continue from previous session',
    'המערכת זיהתה שכבר התחלת תהליך קודם': 'The system detected that you already started a previous process',
    'היום': 'Today',
    
    # DailyDecisionPromptSection
    'מה הייתה החלטה קטנה שקיבלת היום?': 'What small decision did you make today?',
    'איך הגבת למצב לא צפוי היום?': 'How did you react to an unexpected situation today?',
    'הייתה תגובה רגשית שהיית רוצה לנתח?': 'Was there an emotional reaction you\'d like to analyze?',
    'איזו החלטה השפיעה על היום שלך?': 'What decision influenced your day?',
    'מה עשית כדי להתקדם היום?': 'What did you do to move forward today?',
    'האם נמנעת ממשהו היום?': 'Did you avoid something today?',
    'איך עזרת למישהו היום?': 'How did you help someone today?',
    'החלטתי ל...': 'I decided to...',
    'כשקרה... הגבתי ב...': 'When ... happened, I reacted by...',
    'הרגשתי... ואז...': 'I felt... and then...',
    'ההחלטה ל... השפיעה...': 'The decision to... affected...',
    'עשיתי צעד קדימה כש...': 'I took a step forward when...',
    'נמנעתי מ...': 'I avoided...',
    'עזרתי ל... ב...': 'I helped ... with...',
    'שאלת היום': 'Question of the day',
    'הוסף החלטה': 'Add decision',
    
    # DailyOpeningSection
    'פתיחת יום': 'Daily Opening',
    'הכוח הדומיננטי שלך': 'Your dominant force',
    'הכיוון המוצע להיום': 'Suggested direction for today',
    
    # DailyOrientationLoopSection
    'מומנטום חיובי של תרומה': 'Positive contribution momentum',
    'איזון של התאוששות': 'Recovery balance',
    'מיקוד בסדר וארגון': 'Focus on order and organization',
    'דפוס של לחץ ונזק': 'Pattern of pressure and harm',
    'דפוס של הימנעות': 'Pattern of avoidance',
    'מערכת מאוזנת': 'Balanced system',
    'אין נתונים': 'No data',
    'לבצע פעולת התאוששות קטנה': 'Perform a small recovery action',
    'לבחור פעולה קטנה של סדר': 'Choose a small order action',
    'להמשיך במומנטום החיובי': 'Continue with the positive momentum',
    
    # DailySummarySection
    'קוגניטיבי': 'Cognitive',
    'רגשי': 'Emotional',
    'פיזי': 'Physical',
    'אישי': 'Personal',
    'חברתי': 'Social',
    'דחפים': 'Drives',
    'פנימי': 'Internal',
    'חיצוני': 'External',
    'סיכום יומי': 'Daily Summary',
    'פרופיל כוחות': 'Forces Profile',
    'וקטורי ערך': 'Value Vectors',
    
    # DaySummarySection
    'סיכום סוף יום': 'End of Day Summary',
    'על השדה': 'on the field',
    'על השדה הגלובלי': 'on the global field',
    
    # DecisionHistorySection
    'בסשן': 'in session',
    'המשך ל': 'Continue to',
    'המשכים': 'continuations',
    'מאושר': 'Allowed',
    'נחסם': 'Blocked',
    'סדר/כאוס': 'Order/Chaos',
    'אגו/קולקטיב': 'Ego/Collective',
    'איזון': 'Balance',
    'פחות': 'Less',
    'עוד': 'More',
    'הוסף המשך': 'Add continuation',
    'בדוק מסלול חלופי': 'Check alternative path',
    
    # DecisionPathEngineSection
    'ניטרלי': 'Neutral',
    'לנשום עמוק 5 פעמים': 'Take 5 deep breaths',
    'לשתות כוס מים': 'Drink a glass of water',
    'לצאת להליכה קצרה': 'Go for a short walk',
    'לעשות מתיחות': 'Do stretches',
    'להפסיק ולנוח 5 דקות': 'Stop and rest for 5 minutes',
    'לארגן את השולחן': 'Organize the desk',
    'לכתוב רשימת משימות': 'Write a task list',
    'לסדר תיקיות במחשב': 'Organize computer folders',
    'לתכנן את שאר היום': 'Plan the rest of the day',
    
    # DecisionPathSection
    'בוצע': 'Done',
    'מעולה! המשך הלאה.': 'Great! Keep going.',
    'קבל המלצה חדשה': 'Get new recommendation',
    'למה זה מומלץ?': 'Why is this recommended?',
    
    # DecisionPathsSection
    'שיחה פתוחה ורגועה': 'Open and calm conversation',
    'לקחת הפסקה לפני תגובה': 'Take a break before reacting',
    'להתעלם ולהמשיך הלאה': 'Ignore and move on',
    'תרגיל נשימות עמוקות': 'Deep breathing exercise',
    'לארגן את סביבת העבודה': 'Organize the work environment',
    'לשתף מישהו קרוב': 'Share with someone close',
    'לרשום יתרונות וחסרונות': 'Write pros and cons',
    'להתייעץ עם מישהו מנוסה': 'Consult with someone experienced',
    'לדחות את ההחלטה ליום': 'Postpone the decision for a day',
    'הליכה קצרה בחוץ': 'Short walk outside',
    
    # DecisionReplaySection
    'לעזור למישהו': 'Help someone',
    'מסלול תרומה': 'Contribution Path',
    'פעולה שמכוונת לתת ולתרום לאחרים': 'Action aimed at giving and contributing to others',
    'לקחת הפסקה קצרה': 'Take a short break',
    'פעולה שמאפשרת התאוששות ומנוחה': 'Action that allows recovery and rest',
    'לארגן משהו קטן': 'Organize something small',
    'מסלול סדר': 'Order Path',
    'פעולה שמגבירה סדר ומבנה': 'Action that increases order and structure',
    'להגיב באגרסיביות': 'React aggressively',
    'מסלול נזק': 'Harm Path',
    
    # DecisionTreeSection
    'עץ החלטות': 'Decision Tree',
    'מסלולי החלטות כמבנה מסועף': 'Decision paths as a branching structure',
    'שורשים': 'Roots',
    'צמתים': 'Nodes',
    'קשרים': 'Links',
    
    # DirectionExplanationsSection
    'ארבעת הכיוונים': 'The Four Directions',
    'משמעות סמלית, התנהגות אנושית, השפעה על השדה': 'Symbolic meaning, human behavior, impact on the field',
    'משמעות סמלית': 'Symbolic Meaning',
    'דוגמה להתנהגות': 'Behavior Example',
    'השפעה על השדה הקולקטיבי': 'Impact on the Collective Field',
    
    # DirectionHistorySection
    'היסטוריית כיוונים': 'Direction History',
    'תנועה בין כיוונים לאורך זמן': 'Movement between directions over time',
    'נוטה לנוע לכיוון': 'tends to move towards',
    'יש חזרתיות ב': 'There is recurrence in',
    'ואחריה': 'followed by',
    'נראה מעבר מתמשך לכיוון חיובי.': 'A consistent shift towards a positive direction is observed.',
    'זוהה דפוס של נטייה שלילית. מומלץ לשקול כיוון מאזן.': 'A negative tendency pattern was detected. Consider a balancing direction.',
    
    # EntryLayer
    'בחר כיוון ופעל': 'Choose a direction and act',
    'התחל פעולה': 'Start Action',
    'בחר כיוון. פעל. השפע.': 'Choose a direction. Act. Impact.',
    
    # FeedCard
    'ראה על הגלובוס': 'View on globe',
    'שאלה להתמצאות': 'Orientation Question',
    'תובנה מהשדה': 'Field Insight',
    'מוביל שדה': 'Field Leader',
    'ערך': 'Value',
    
    # FieldGlobeSection
    'ישראל': 'Israel',
    'צרפת': 'France',
    'ארה"ב': 'USA',
    'בריטניה': 'UK',
    'יפן': 'Japan',
    'גרמניה': 'Germany',
    'דרום אפריקה': 'South Africa',
    'ברזיל': 'Brazil',
    'מצב השדה': 'Field Status',
    'טעינת שדה...': 'Loading field...',
    
    # FieldImpactLayer
    'איך הפעולה שלך משפיעה על העולם?': 'How does your action impact the world?',
    'כל פעולה שאתה עושה נוספת לשדה האנושי הגלובלי.': 'Every action you take is added to the global human field.',
    'השדה הוא הסכום של כל הבחירות — שלך ושל אחרים.': 'The field is the sum of all choices — yours and others.',
    'הפעולה שלך': 'Your action',
    'נוספת לשדה': 'Added to the field',
    'בשדה היום': 'in the field today',
    'מוביל': 'Leading',
    'עבור למערכת כדי לראות את הגלובוס המלא': 'Go to the system to see the full globe',
    'השדה מחכה לפעולה הראשונה של היום': 'The field awaits your first action of today',
    
    # FieldMissionSection
    'אנשים כבר השתתפו': 'people already participated',
    'יעד': 'Target',
    'הפעולה שלך תרמה למשימת היום': 'Your action contributed to today\'s mission',
    
    # GlobalFieldSection
    'קולקטיב': 'Collective',
    'התאוששות': 'Recovery',
    'נזק': 'Harm',
    'השדה העולמי נוטה לכיוון סדר ומבנה.': 'The global field leans towards order and structure.',
    'השדה העולמי נוטה לכיוון קולקטיבי.': 'The global field leans towards the collective.',
    'השדה העולמי מאוזן יחסית.': 'The global field is relatively balanced.',
    'אזור הנזק חלש - מצב בריא.': 'Harm zone is weak — a healthy state.',
    
    # GlobalTrendSection
    'עולה': 'rising',
    'יורד': 'falling',
    'מתקדם לכיוון יציבות.': 'moving towards stability.',
    'שים לב לאיזון.': 'pay attention to balance.',
    'שיפור חיובי!': 'positive improvement!',
    'כדאי להתמקד בהתאוששות.': 'consider focusing on recovery.',
    'מתחזקת.': 'strengthening.',
    'נחלשת - הוסף פעולות התאוששות.': 'weakening — add recovery actions.',
    'מגמה חיובית לכיוון תרומה חברתית.': 'Positive trend towards social contribution.',
    'המגמות יציבות - המשך במסלול הנוכחי.': 'Trends are stable — continue on the current path.',
    'מגמות לאורך זמן': 'Trends Over Time',
    'סשנים אחרונים': 'recent sessions',
    'סשנים': 'sessions',
    
    # GlobalValueFieldSection
    'חיובי': 'Positive',
    'שלילי': 'Negative',
    'גבוה': 'High',
    'בינוני': 'Moderate',
    'נמוך': 'Low',
    'שדה ערכים גלובלי': 'Global Value Field',
    'איפוס': 'Reset',
    'ניתוח ארוך טווח מכל הסשנים': 'Long-term analysis from all sessions',
    'סה״כ': 'Total',
    'סה"כ': 'Total',
    
    # HighlightedRecords
    'אנשים בשדה': 'People in the field',
    
    # HomeNavigationSection
    'מצב היום': 'Today\'s Status',
    'הפעולה נובעת מהכיוון המומלץ': 'The action follows the recommended direction',
    'הזן פעולה לבדיקה...': 'Enter an action to check...',
    'פעל לפי ההמלצה': 'Act on the recommendation',
    'בדוק': 'Check',
    
    # InviteSection
    'כדי לקבל קודי הזמנה': 'to get invite codes',
    'הזמנה לשדה': 'Invite to the field',
    'שתף קישור והזמן מישהו להצטרף': 'Share a link and invite someone to join',
    'נוצלו': 'Redeemed',
    'אין קודים פעילים': 'No active codes',
    'צור קודי הזמנה': 'Generate invite codes',
    'הזמנות נוצלו בהצלחה': 'Invites redeemed successfully',
    'צור עוד קוד': 'Generate another code',
    
    # InviteTrackingSection
    'נשלחו': 'Sent',
    'נפתחו': 'Opened',
    'התקבלו': 'Accepted',
    'דוח המרת הזמנות': 'Invite Conversion Report',
    'פתיחה': 'Open rate',
    'קבלה': 'Accept rate',
    'המרה כוללת': 'Total conversion',
    
    # LeadersSection
    'מובילי שדה': 'Field Leaders',
    'המשפיעים הגדולים ביותר': 'The biggest influencers',
    
    # MetricsDashboardSection
    'השלמת שאלה יומית': 'Daily question completion',
    'שימור יום 2': 'Day 2 retention',
    'השתתפות במשימה': 'Mission participation',
    'ממוצע': 'Average',
    'המרת הזמנות': 'Invite conversions',
    'סקירת שימור': 'Retention Overview',
    
    # MissionsSection
    'משימות שדה': 'Field Missions',
    'הצטרף למאמץ הקולקטיבי': 'Join the collective effort',
    'פעילה היום': 'Active today',
    
    # MonthlyOrientationSection / MonthlyProgressReportSection
    'סיכום חודשי': 'Monthly Summary',
    'דוח התקדמות חודשי': 'Monthly Progress Report',
    'לעומת תחילת החודש': 'compared to the start of the month',
    'צמיחה': 'Growth',
    'שבוע': 'Week',
    'חודש': 'Month',
    
    # NextBestDirectionSection
    'כיוון הבא': 'Next Direction',
    'מומלץ': 'Recommended',
    
    # OppositionLayer
    'ציר הניגודים': 'Opposition Axis',
    'קיפאון מאוזן על ידי פתיחות וחקירה': 'Stagnation balanced by openness and exploration',
    'נזק דורשות איזון דרך התאוששות': 'Harm requires balance through recovery',
    'מיקוד עצמי מאוזן על ידי תרומה': 'Self-focus balanced by contribution',
    'הימנעות מאוזנת על ידי יצירת סדר ומבנה': 'Avoidance balanced by creating order and structure',
    
    # OrientationCirclesSection
    'מעגלי התמצאות': 'Orientation Circles',
    
    # OrientationCompassSection
    'מצפן התמצאות': 'Orientation Compass',
    
    # OrientationFeedSection
    'פיד התמצאות': 'Orientation Feed',
    
    # OrientationFieldToday
    'שדה ההתמצאות היום': 'Orientation Field Today',
    
    # OrientationIdentitySection
    'זהות התמצאות': 'Orientation Identity',
    
    # OrientationIndexPage
    'דף אינדקס התמצאות': 'Orientation Index',
    
    # OrientationShareCard
    'כרטיס שיתוף': 'Share Card',
    
    # PathLearningSection
    'למידת מסלולים': 'Path Learning',
    
    # QuarterlyReviewSection
    'סקירה רבעונית': 'Quarterly Review',
    
    # RecommendationCalibrationSection
    'כיול המלצות': 'Recommendation Calibration',
    
    # RecommendationFollowThroughSection
    'מעקב המלצות': 'Recommendation Follow-Through',
    
    # ReferralLeaderboardSection
    'טבלת מזמינים': 'Referral Leaderboard',
    
    # RelativeScoreSection
    'ציון יחסי': 'Relative Score',
    
    # ReplayAdaptiveEffectSection
    'השפעה אדפטיבית': 'Adaptive Effect',
    
    # ReplayInsightsSummarySection
    'סיכום תובנות': 'Insights Summary',
    
    # SendToGlobeButton
    'סמן נוכחות בשדה': 'Mark presence in the field',
    'שולח לגלובוס...': 'Sending to globe...',
    'נשלח לגלובוס': 'Sent to globe',
    
    # SessionComparisonSection
    'השוואת סשנים': 'Session Comparison',
    'סשן א\' מראה': 'Session A shows',
    'סשן ב\' מראה': 'Session B shows',
    
    # SessionLibrarySection
    'ספריית סשנים': 'Session Library',
    
    # SubscriptionSection
    'שדרג את החוויה': 'Upgrade your experience',
    
    # TheorySection
    'תיאוריית השדה': 'Field Theory',
    
    # ValueConstellationSection
    'קונסטלציית ערכים': 'Value Constellation',
    
    # ValueProfileSection
    'פרופיל ערכים': 'Value Profile',
    
    # WeeklyBehavioralReportSection
    'דוח התנהגותי שבועי': 'Weekly Behavioral Report',
    'מגמות התנהגותיות מ': 'Behavioral trends from',
    
    # WeeklyInsightSection
    'תובנות שבועיות': 'Weekly Insights',
    
    # WeeklyOrientationSummarySection
    'סיכום התמצאות שבועי': 'Weekly Orientation Summary',
    
    # WeeklyReportSection
    'דו"ח שבועי': 'Weekly Report',
    
    # WeeklySummarySection
    'סיכום שבועי': 'Weekly Summary',
    
    # FeedTab / HistoryTab
    'אין פריטים': 'No items',
    'פיד': 'Feed',
    
    # Hooks
    'סשן חדש': 'New Session',
    'שגיאה בשמירה': 'Error saving',
    'שגיאה בטעינה': 'Error loading',
    
    # Various common patterns
    'פעמים': 'times',
    'שרשראות': 'chains',
    'לאורך זמן': 'over time',
    'מבוסס על': 'Based on',
    'האחרונים': 'recent',
    'הפעלות חוזרות': 'repeat activations',
    'חזוי': 'Predicted',
    'בפועל': 'Actual',
    'עוצמה': 'Strength',
    'משקל': 'Weight',
    'רמה': 'Level',
    'תובנה': 'Insight',
    'התאמה': 'Match',
    'אזהרה': 'Warning',
    'תיקון': 'Correction',
    'יש': 'There is',
    'מסלול': 'Path',
    'מסלולי': 'Paths of',
    'צריך לפחות': 'Need at least',
    'מה קורה': 'What\'s happening',
    'שדה עולמי': 'Global Field',
    'שדה': 'Field',
    'נסחף': 'drifting',
    'נוקשות': 'rigidity',
    'מתייצב': 'stabilizing',
    'משתנה': 'changing',
    'נראה': 'appears',
    'נראה פער מתמשך בכיוון': 'A persistent gap in direction appears',
    'סקירה קוגניטיבית של': 'Cognitive review of',
    'יש עלייה בדפוסי נזק - שים לב': 'There is an increase in harm patterns — pay attention',
    'חי': 'Live',
    
    # Subscription
    'חודשי': 'Monthly',
    'שנתי': 'Annual',
    'בסיסי': 'Basic',
    'מתקדם': 'Advanced',
    'פרימיום': 'Premium',
    
    # Admin Page
    'ניהול': 'Admin',
    'לוח בקרה': 'Dashboard',
    
    # ActionEvaluationForm
    'הערך את הפעולה': 'Evaluate the action',
    'שלח הערכה': 'Submit evaluation',
    
    # OnboardingHint
    'ברוך הבא למערכת': 'Welcome to the system',
    'צעד ראשון': 'First step',
    'בואו נתחיל': 'Let\'s begin',
    'הבנתי': 'Got it',
    
    # FeedbackButton
    'שלח משוב': 'Send Feedback',
    'תודה על המשוב!': 'Thanks for the feedback!',
    
    # Various formatting/misc
    'ק"מ': 'km',
    'לפני ': 'ago ',
}

# Template literal patterns that need contextual translation
REGEX_REPLACEMENTS = [
    # Hebrew template strings with variables
    (r'מסלולי \$\{valueLabels\[topBoosted\]\} מקבלים כעת עדיפות גבוהה יותר', '${valueLabels[topBoosted]} paths now receive higher priority'),
    (r'מסלולים עם נטיית \$\{valueLabels\[topPenalized\]\} מקבלים הפחתת משקל', 'Paths with ${valueLabels[topPenalized]} tendency receive reduced weight'),
    (r'השרשרת הזו מראה תיקון כיוון מ\$\{valueLabels\[firstValue\]\} ל\$\{valueLabels\[lastValue\]\}', 'This chain shows direction correction from ${valueLabels[firstValue]} to ${valueLabels[lastValue]}'),
    (r'שרשרת זו מראה ירידה מ\$\{valueLabels\[firstValue\]\} ל\$\{valueLabels\[lastValue\]\}', 'This chain shows decline from ${valueLabels[firstValue]} to ${valueLabels[lastValue]}'),
    (r'נמצא תיקון: מ\$\{valueLabels\[values\[i\]\]\} ל\$\{valueLabels\[values\[i \+ 1\]\]\}', 'Correction found: from ${valueLabels[values[i]]} to ${valueLabels[values[i + 1]]}'),
    (r'יש Repeating Pattern \(\$\{count\} פעמים\): \$\{patternLabels\}', 'Repeating pattern (${count} times): ${patternLabels}'),
    (r'יש Repeating Pattern של תגובה שלילית ואחריה תיקון \(\$\{emotionalCorrections\.length\} פעמים\)', 'Repeating pattern of negative reaction followed by correction (${emotionalCorrections.length} times)'),
    (r'You נוטה לנוע לכיוון', 'You tend to move towards'),
    (r'יש חזרתיות ב\$\{directionLabels\[from\] \|\| from\} ו?אחריה \$\{directionLabels\[to\] \|\| to\}', 'There is recurrence in ${directionLabels[from] || from} followed by ${directionLabels[to] || to}'),
    # he-IL locale patterns
    (r"toLocaleString\('he-IL'\)", "toLocaleString('en-US')"),
    (r"toLocaleDateString\('he-IL'", "toLocaleDateString('en-US'"),
    (r"toLocaleTimeString\('he-IL'", "toLocaleTimeString('en-US'"),
    # Remove Hebrew locale import
    (r"import \{ he \} from 'date-fns/locale';?\n?", ""),
]

import re, glob

def translate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Apply regex replacements first
    for pattern, replacement in REGEX_REPLACEMENTS:
        content = re.sub(pattern, replacement, content)
    
    # Apply direct translations (longest first)
    sorted_translations = sorted(TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True)
    for hebrew, english in sorted_translations:
        content = content.replace(hebrew, english)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

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
