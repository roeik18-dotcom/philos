#!/usr/bin/env python3
"""Third pass: Fix broken mixed-language strings and translate remaining Hebrew."""
import re, glob

# Fix broken No-prefix patterns (לא was incorrectly replaced with No inside words)
NO_FIXES = {
    'Noרגן את השולחן': 'Organize the desk',
    'Noרגן את סביבת העבודה': 'Organize the work environment', 
    'Noרגן משהו קטן בסביבה': 'Organize something small in your environment',
    'Noרגן משהו קטן': 'Organize something small',
    'Noרגן, לתכנן, לייצב': 'Organize, plan, stabilize',
    'Noרגן ולתכנן': 'Organize and plan',
    'Noרגן': 'Organize',
    'Noורך': 'over',
    'Noיזון': 'balance',
    'Noחרים': 'others',
    'Noחר': 'after',
    'Noן לפנות': 'Where to turn',
    'No צפוי': 'unexpected',
    'Noה': 'Noah',
    'Noירוע': 'event',
}

# Fix broken replacements from other short Hebrew words
BROKEN_FIXES = {
    # 'יש' → 'There is' broke other words
    'Emotionי': 'Emotional',
    'Emotionתי': 'felt',
    'Socialת': 'Social',
    'Positiveות': 'positive',
    'Positiveת': 'positive',
    'Negativeת': 'Negative',
    'Moderateת': 'Moderate',
    'Highה': 'High',
    'Stableה': 'Stable',
    'Stableות': 'stability',
    'Liveזוק': 'reinforcement',
    'Liveנם': 'Synchronize',
    'Liveקת': 'loading',
    'Sentו': 'Sent',
    
    # Fix remaining complete Hebrew strings and sentences
    'Based on נתונים היסטוריים': 'Based on historical data',
    'Based on Path הBalance התיאורטי': 'Based on theoretical balance path',
    'Based on Liveזוק Direction Positive': 'Based on positive direction reinforcement',
    'Error loading הסשן': 'Error loading session',
    'Error loading תובנות': 'Error loading insights',
    'Error במLiveקת הסשן': 'Error loading session',
    'Error בסנכרון': 'Error syncing',
    'Error בשמירת הסשן': 'Error saving session',
    'Loading data מהענן...': 'Loading data from cloud...',
    'Synced בין מכשירים': 'Synced across devices',
    'Invite הסתיים! 🎉': 'Invite completed! 🎉',
    
    'There is Harm Pressure High בField.': 'There is high harm pressure in the field.',
    'There is Streak של decisions Positiveות - המשך כך!': 'There is a streak of positive decisions — keep going!',
    'There is להזין פrising': 'There is a need to enter an action',
    'There is מקום לשיפור - הרבעון Next יכול להיות טוב יותר': 'There is room for improvement — the next quarter can be better',
    'There is מרחק בין המיקום שלך לבין מרכז הField.': 'There is a distance between your position and the field center.',
    'There is עלייה בדפוסי Harm Noורך הרבעון - נקודה לתשומת לב': 'There is an increase in harm patterns over the quarter — a point of attention',
    'There is עלייה בדפוסי Recovery': 'There is an increase in recovery patterns',
    
    'Balance טוב של Recovery.': 'Good balance of recovery.',
    'Balance כללי': 'General Balance',
    'Back Noיזון Noחר לחץ או Harm': 'Balance after pressure or harm',
    
    'Growth - Streak של decisions Positiveות': 'Growth — a streak of positive decisions',
    'Harm - מעבר לDirection Negative': 'Harm — shift to negative direction',
    'Warning - Streak של decisions בעייתיות': 'Warning — a streak of problematic decisions',
    'Recovery - מעבר מהימנעות לRecovery': 'Recovery — shift from avoidance to recovery',
    'Correction - זיהוי וMid-path Correction': 'Correction — detection and mid-path correction',
    'Patterns חוזרים': 'Repeating patterns',
    
    'Week Balanced - המשך בPath.': 'Balanced week — continue on the path.',
    
    'You מחפש בסיס Stable — Roots ago תנועה': 'You seek a stable base — root before movement',
    'You מיושר היטב עם הField הCollective.': 'You are well aligned with the collective field.',
    'You מתמקד בעצמך — שיקום Internal קודם': 'You are focusing on yourself — internal recovery first',
    'You נוטה לסדר — מבנה וביטחון Leadingים אותך': 'You lean towards order — structure and security lead you',
    'You רחוק ממרכז הField הCollective.': 'You are far from the collective field center.',
    
    'Order Drift rising - You Advanced לDirection Stableות.': 'Order Drift rising — you are advancing towards stability.',
    'Order Drift falling - שים לב Noיזון.': 'Order Drift falling — pay attention to balance.',
    'Harm Pressure ירד - מגמה Positiveת!': 'Harm Pressure decreased — positive trend!',
    'Harm Pressure עלה - שים לב לRecovery.': 'Harm Pressure increased — pay attention to recovery.',
    'Recovery Stability התחזקה.': 'Recovery Stability strengthened.',
    'Recovery Stability נחלשה.': 'Recovery Stability weakened.',
    'Recovery היא תמיד בLiveרה טובה': 'Recovery is always a good choice',
    
    'Impact Socialת No התממשה.': 'Social impact was not realized.',
    'Help someone קרוב': 'Help someone close',
    'Need at least 3 decisions כדי לSave סשן': 'Need at least 3 decisions to save a session',
    'No data עדיין': 'No data yet',
    'No הייתה Activeות.': 'There was no activity.',
    'No צוין': 'Not noted',
    'No Stableה': 'Not stable',
    
    'Self-focus balanced by contribution Noחרים.': 'Self-focus balanced by contribution to others.',
    'Self-focus balanced by contribution Noחרים': 'Self-focus balanced by contribution to others',
    'Conversation פתוחה ורגועה': 'Open and calm conversation',
    
    'appears Repeating Pattern של תגובה followed by Correction': 'Repeating pattern of reaction followed by correction appears',
    'appears דפוס הימנעות בMonth שעבר. הMonth Recommended לחזק Direction של סדר.': 'An avoidance pattern appears from last month. This month, consider strengthening the direction of order.',
    'appears דפוס הימנעות בWeek שעבר. הWeek Recommended לחזק Direction של סדר.': 'An avoidance pattern appears from last week. This week, consider strengthening the direction of order.',
    'appears לחץ בMonth שעבר. הMonth Recommended לחזק Direction של Recovery.': 'Pressure appears from last month. This month, consider strengthening the direction of recovery.',
    'appears לחץ בWeek שעבר. הWeek Recommended לחזק Direction של Recovery.': 'Pressure appears from last week. This week, consider strengthening the direction of recovery.',
    
    'Path הימנעות': 'Avoidance Path',
    'Path קשר': 'Connection Path',
    'rigidity / קיפאון': 'rigidity / stagnation',
    'rigidity → חקירה': 'rigidity → exploration',
    
    # InviteSection remaining
    'Active היום': 'Active today',
    
    # Feed tab
    'Conversation קצרה עם אדם אהוב': 'Short call with a loved one',
    
    # Session comparison
    'סשן א\' מראה': 'Session A shows',
    'סשן ב\' מראה': 'Session B shows',
    "Session A shows": "Session A shows",
    
    # Timer / RequestCard / DailySummary
    'עזרתי': 'Helped',
    'מקבל עזרה': 'Getting help',
    'עוד קצת': 'A bit more',
    'סיימתי': 'I\'m done',
    'כל הכבוד!': 'Great job!',
    'תודה רבה': 'Thank you',
    'עזרת ל': 'You helped',
    'בסך הכל עזרת ל': 'In total you helped',
    'אנשים היום': 'people today',
    'בקשה חדשה': 'New request',
    'קבל': 'Accept',
    
    # CreateRequestModal
    'צור בקשת עזרה': 'Create Help Request',
    'שם': 'Name',
    'תיאור הבקשה': 'Request description',
    'כמה זמן צריך?': 'How long will it take?',
    'כתובת / מרחק': 'Address / distance',
    'שליחה': 'Submit',
    'תחום': 'Category',
    
    # TaskCard
    'משימה': 'Task',
    
    # DecisionMap
    'מפת החלטות': 'Decision Map',
    
    # QuickDecisionButton
    'החלטה מהירה': 'Quick Decision',
    
    # OnboardingHint
    'הבנתי': 'Got it',
    'צעד ראשון': 'First step',
    
    # FeedbackButton
    'שלח': 'Send',
    'תודה על המשוב!': 'Thanks for your feedback!',
}

# Remaining Hebrew word-level translations
REMAINING_HEBREW = {
    'אדם': 'person',
    'אוגוסט': 'August',
    'ינואר': 'January',
    'פברואר': 'February', 
    'מרץ': 'March',
    'אפריל': 'April',
    'מאי': 'May',
    'יוני': 'June',
    'יולי': 'July',
    'ספטמבר': 'September',
    'אוקטובר': 'October',
    'נובמבר': 'November',
    'דצמבר': 'December',
    'שונה': 'Different',
    'זמן': 'Time',
    'עולם': 'World',
    'דומה': 'Similar',
    'בחירה': 'Choice',
    'בחירות': 'Choices',
    'ליצור': 'Create',
    'ליצירת': 'For creating',
    'להפחית': 'Reduce',
    'להגביר': 'Increase',
    'למצוא': 'Find',
    'לבצע': 'Perform',
    'לבחור': 'Choose',
    'להמשיך': 'Continue',
    'לחזק': 'Strengthen',
    'לשפר': 'Improve',
    'לראות': 'See',
    'להוסיף': 'Add',
    'לנוח': 'Rest',
    'לנשום': 'Breathe',
    'לעצור': 'Stop',
    'לחשוב': 'Think',
    'לפעול': 'Act',
    'פעולה': 'action',
    'פעולות': 'actions',
    'ממנה': 'from it',
    'שלך': 'your',
    'שלו': 'his',
    'כיוון': 'direction',
    'כיוונים': 'directions',
    'ורך': 'over',
    'חודשים': 'months',
    'בעייתיות': 'problematic',
    'פעולה שמכוונת': 'Action aimed at',
    'פעולה שמאפשרת': 'Action that allows',
    'פעולה שמגבירה': 'Action that increases',
    'פעולה שמובילה': 'Action that leads to',
    'לנזק ולהרס': 'damage and destruction',
    
    # Hebrew month names in date formatting
    'suggested_direction_he': 'suggested_direction_he',
    'מלא': 'full',
    'המלא': 'full',
    'תיאור': 'Description',
    'שרשרת': 'chain',
    'שיקום': 'rehabilitation',
    'מבנה': 'structure',
    'מרכז': 'center',
    'ממוצע': 'average',
    'מחר': 'tomorrow',
    'היום': 'today',
    'אתמול': 'yesterday',
    'עדיין': 'still',
    'חדש': 'new',
    'ישן': 'old',
    'קודם': 'previous',
    'הבא': 'next',
    'ראשון': 'first',
    'אחרון': 'last',
    'כל': 'all',
    'הכל': 'everything',
    'כולו': 'entire',
    'כולם': 'everyone',
    'עוד': 'more',
    'פחות': 'less',
    'קצר': 'short',
    'ארוך': 'long',
    'גדול': 'large',
    'קטן': 'small',
    'טוב': 'good',
    'רע': 'bad',
    'חזק': 'strong',
    'חלש': 'weak',
}

def translate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix broken No-prefix patterns first (longest first)
    for broken, fixed in sorted(NO_FIXES.items(), key=lambda x: len(x[0]), reverse=True):
        content = content.replace(broken, fixed)
    
    # Fix broken mixed-language patterns (longest first)
    for broken, fixed in sorted(BROKEN_FIXES.items(), key=lambda x: len(x[0]), reverse=True):
        content = content.replace(broken, fixed)
    
    # Apply remaining Hebrew word translations (longest first)
    for hebrew, english in sorted(REMAINING_HEBREW.items(), key=lambda x: len(x[0]), reverse=True):
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
        print(f'Fixed: {f}')

print(f'\nDone. {changed} files fixed.')

# Check remaining Hebrew
import subprocess
result = subprocess.run(
    ['grep', '-Prl', '[\u0590-\u05FF]', '/app/frontend/src/', '--include=*.js', '--include=*.jsx'],
    capture_output=True, text=True
)
remaining = result.stdout.strip().split('\n') if result.stdout.strip() else []
print(f'Files still containing Hebrew: {len(remaining)}')
for f in remaining:
    # Count Hebrew chars
    count = subprocess.run(['grep', '-Poc', '[\u0590-\u05FF]', f], capture_output=True, text=True)
    print(f'  {f} ({count.stdout.strip()} chars)')
