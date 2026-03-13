#!/usr/bin/env python3
"""Final pass: Fix all remaining Hebrew by replacing line-level patterns."""
import re, glob, subprocess

# Full line-level replacements for remaining broken strings (old_line -> new_line)  
LINE_FIXES = {
    # CreateRequestModal.js
    "setError('נא להזין Name פרטי');": "setError('Please enter your name');",
    "setError('נא להזין Description העזרה');": "setError('Please describe what help you need');",
    "setError('נא להזין Time משוער');": "setError('Please enter estimated time');",
    "צריך עזרה?": "Need help?",
    "Name פרטי": "Your Name",
    'placeholder="לדוגמה: דוד"': 'placeholder="e.g., David"',
    "סוג עזרה": "Help type",
    'placeholder="לדוגמה: Guidance להליכה בפארק"': 'placeholder="e.g., Help with a walk in the park"',
    "Time משוער (minutes)": "Estimated time (minutes)",
    "מרחק (אופציונלי)": "Distance (optional)",
    "Send בקשה": "Submit request",
    
    # DailySummary.js
    "סיכום Today": "Today's Summary",
    "התחלתי": "Started",
    "בקשה נוספת": "Another request",
    
    # RequestCard.js
    "אAccept": "Accept",
    
    # TaskCard.js
    "התחל": "Start",
    
    # Timer.js
    "עוזר ל": "Helping ",
    "סיום": "Finish",
    
    # ActionEvaluationForm.js
    "רווח Personal": "Personal gain",
    "רווח Collective": "Collective gain",
    "הגדר הערכה": "Set evaluation",
    
    # DecisionMap.js
    "הגדר ערכי מצב כדי See מיקום במפת ההחלטה": "Set state values to see position in the decision map",
    
    # FeedbackButton.js
    "תודה!": "Thank you!",
    "הFeedback your התAccept": "Your feedback was received",
    "{ id: 'confusion', label: 'בלבול', color: 'orange' }": "{ id: 'confusion', label: 'Confusion', color: 'orange' }",
    "{ id: 'improvement', label: 'הצעת שיפור', color: 'blue' }": "{ id: 'improvement', label: 'Suggestion', color: 'blue' }",
    "{ id: 'bug', label: 'באג', color: 'red' }": "{ id: 'bug', label: 'Bug', color: 'red' }",
    'placeholder="ספר לנו מה קרה..."': 'placeholder="Tell us what happened..."',
    
    # OnboardingHint.js
    "לתת, לעזור, Strengthen אחרים": "Give, help, strengthen others",
    "להיטען, לשקם, Rest": "Recharge, restore, rest",
    "לגלות, ללמוד, לנסות חדw": "Discover, learn, try new things'",
    "בחר את הDirection הfirst your": "Choose your first direction",
    "מה הכי מושך אותך Now?": "What attracts you most right now?",
    "הנקודה הראDifferent your נוספה לField הגלובלי": "Your first point was added to the global field",
    "Send את הנקודה הראDifferent your": "Send your first point",
    "לחץ כדי לhisח את הפrising הראDifferent your לגלובוס ולJoin לField האנושי.": "Click to send your first action to the globe and join the human field.",
    "Send לגלובוס": "Send to Globe",
    
    # OrientationMap.js
    "מציאות": "Reality",
    "מי אני Today": "Who am I today",
    "ניגוד": "Opposition",
    "בין אילו כוחות": "Between which forces",
    "בLiveרה": "Choice",
    "פrising": "Action",
    "מה עשיתי": "What I did",
    "מה השתנה": "What changed",
    
    # QuickDecisionButton.js
    "לתת": "Give",
    "להיטען": "Recharge",
    "לגלות": "Discover",
    "פrising מהירה": "Quick Action",
    "בחר Direction — הנקודה Sentת לגלובוס מיד": "Choose a direction — your point is sent to the globe immediately",
    "צפה ברשומה your": "View your record",
    
    # CollectiveTrajectorySection.js
    "מגמה over": "Trend over",
    
    # ContinuePreviousSessionSection.js
    "המשך מהמפגש Previous": "Continue from previous session",
    "ההחלטה האחרונה your הייתה:": "Your last decision was:",
    "דפוס שולט:": "Dominant pattern:",
    "ניתן Continue מאותה נקודה בדיוק": "You can continue from that exact point",
    "המשך מכאן": "Continue from here",
    
    # DailyDecisionPromptSection.js
    "איך הגבת למצב unexpected Today?": "How did you react to an unexpected situation today?",
    "הייתה תגובה Emotionalת שהיית רוצה לנתח?": "Was there an emotional reaction you'd like to analyze?",
    "הfelt... ואז...": "I felt... and then...",
    "Add החלטה": "Add decision",
    
    # DailyOrientationLoopSection.js
    "Add מעט סדר לRecovery": "Add a bit of order to recovery",
    "לפתוח לDirection של תרומה": "Open up to a contribution direction",
    "Perform פrising קטנה של תרומה": "Perform a small act of contribution",
    "להתLiveל עם פעולת Recovery": "Start with a recovery action",
    "Today מתLiveל מחזור new של decisions.": "Today begins a new cycle of decisions.",
    "התחל את Today": "Start your day",
    "הOrientation היומית עוזרת Create מחזור התנהגותי Positive": "Daily orientation helps create a positive behavioral cycle",
    
    # DecisionHistorySection.js
    "Add המשך": "Add continuation",
    "החלטת המשך": "Continuation decision",
    "מספר continuations": "Number of continuations",
    
    # DecisionPathEngineSection.js
    "להפסיק וRest 5 minutes": "Stop and rest for 5 minutes",
    "להתמקד בTask אחת": "Focus on one task",
    "לhisח הודעה positive לחבר": "Send a positive message to a friend",
    "להקשיב למThere isהו": "Listen to someone",
    "לShare badיון": "Share an idea",
    "להתקשר למThere isהו": "Call someone",
    "לhisח הודעה כועסת": "Send an angry message",
    "להתעלם מהבעיה": "Ignore the problem",
    "לגלול ברשתות Socialות": "Scroll through social media",
    "לדחות את ההחלטה": "Postpone the decision",
    "מrising": "Excellent",
    "חלw": "Weak",
    "מסוYes": "Risky",
    "מנוע Decision Paths": "Decision Path Engine",
    "3 Paths ofם מוצעים עם תחזיות": "3 suggested paths with predictions",
    "מסוYes": "Risky",
    "recovery stability Predictedה": "Predicted recovery stability",
    "בחר Path זה": "Choose this path",
    "מקרא:": "Legend:",
    "משפר סדר/Recovery/תרומה": "Improves order/recovery/contribution",
    "מעלה Harm/הימנעות": "Increases harm/avoidance",
    
    # DecisionPathSection.js
    "מrising! המשך הNoah.": "Excellent! Keep going.",
    
    # DecisionPathsSection.js
    "להתעלם וContinue הNoah": "Ignore and move on",
    "לShare מThere isהו קרוב": "Share with someone close",
    "כתיבה ביומן (No לhisח)": "Write in a journal (don't send)",
    "להביע את הEmotion בConversation": "Express the emotion in conversation",
    "מנוחה shortה של 20 minutes": "Short 20-minute rest",
    "שתיית מים וחטיף בריא": "Drink water and have a healthy snack",
    "Continue לעבוד בall זאת": "Continue working anyway",
    "Act לgoodת אחרים": "Act for the benefit of others",
    "לקחת רגע לRecovery": "Take a moment for recovery",
    "כעס|עצבני|מתוסall|רוגז": "כעס|עצבני|מתוסכל|רוגז",
    "לחץ|מתח": "לחץ|מתח",
    "קונפליקט|ויכוח": "קונפליקט|ויכוח",
    "החלטה|Choose": "החלטה|Choose",
    "עייף|עייפות": "עייף|עייפות",
    "עמוס": "עמוס",
    "דילמה": "דילמה",
    "מריבה": "מריבה",
    "מותש": "מותש",
    "הזן הקשר או אירוע לAcceptת Paths ofם אפשריים": "Enter a context or event to get possible paths",
    'placeholder="לדוגמה: אני מרגThere is לחץ בעבודה..."': 'placeholder="e.g., I feel stressed at work..."',
    "הצג Paths ofם אפשריים": "Show possible paths",
    "3 Paths ofם אפשריים:": "3 possible paths:",
    "Order Drift צפוי": "Expected order drift",
    "סחף Social צפוי": "Expected social drift",
    "סיכון Harm": "Harm risk",
    "Support בRecovery": "Recovery support",
    "הזן הקשר או מצב כדי לAccept Decision Paths": "Enter a context or situation to get decision paths",
    "לחץ בעבודה": "Stress at work",
    "ויכוח עם חבר": "Argument with a friend",
    "עייפות": "Fatigue",
    "החלטה קשה": "Tough decision",
    "label: ['א׳', 'ב׳', 'ג׳']": "label: ['A', 'B', 'C']",
    
    # DecisionReplaySection.js
    "פrising שמכוונת לתת ולתרום others": "Action aimed at giving and contributing to others",
    "פrising שעלולה לגרום Harm": "Action that may cause harm",
    "להתעלם מהסיטואציה": "Ignore the situation",
    "פrising של הימנעות או דLiveיה": "Action of avoidance or postponement",
    "הPath החלופי היה עשוי להוביל balance High יותר": "The alternative path could have led to higher balance",
    "הPath שבחרת הוביל balance good יותר מהחלופה.": "The path you chose led to better balance than the alternative.",
    "אם היית בוחר בRecovery Path, לחץ הHarm היה Low יותר.": "If you had chosen the recovery path, harm pressure would have been lower.",
    "הPath החלופי היה עשוי להוביל ליותר סדר וLess הימנעות.": "The alternative path could have led to more order and less avoidance.",
    "Contribution Path היה מstrong את הDirection הCollective.": "A contribution path would have strengthened the collective direction.",
    "שני הPaths ofם היו Leadingים לתוצאות דומות.": "Both paths would have led to similar results.",
    "הבLiveרה your הייתה מתאימה למצב.": "Your choice was appropriate for the situation.",
    "הפעלה חוזרת של החלטה": "Decision Replay",
    "Check מה היה קורה אם היית בוחר אחרת": "See what would have happened if you chose differently",
    "ההחלטה המקורית": "The original decision",
    "Paths ofם חלופיים אפשריים": "Possible alternative paths",
    "לחץ על Path חלופי כדי See את הInsight": "Click on an alternative path to see the insight",
    "סדר צפוי:": "Expected order:",
    "Collective צפוי:": "Expected collective:",
    
    # DecisionTreeSection.js
    "עץ decisions": "Decision Tree",
    "Paths of Your decisions כstructure מסועף": "Your decision paths as a branching structure",
    
    # DirectionExplanationsSection.js
    "Symbolic Meaning, התנהגות אנושית, Impact on the field": "Symbolic meaning, human behavior, impact on the field",
    "Impact on the field הCollective": "Impact on the collective field",
    
    # DirectionHistorySection.js
    "תנועה בין directions over Time": "Movement between directions over time",
    "מעברים אחרונים": "Recent transitions",
    "אין מספיק נתונים להצגת היסטוריה.": "Not enough data to display history.",
    "בצע מספר actions כדי See Patterns.": "Perform several actions to see patterns.",
    "סדר": "Order",
    "תרומה": "Contribution",
    "חקירה": "Exploration",
    
    # FeedCard.js
    "שאלה לOrientation": "Orientation Question",
    
    # FieldGlobeSection.js
    "No data זמינים": "No data available",
    
    # FieldImpactLayer.js
    "all פrising שYou עושה Added to the field האנושי הגלובלי.": "Every action you take is added to the global human field.",
    "עבור למערכת כדי See את הגלובוס המNo": "Go to the system to see the full globe",
    
    # GlobalFieldSection.js
    "אזור הRecovery strong.": "The recovery zone is strong.",
    "מצב מתוח": "Tense state",
    "מצב בריא": "Healthy state",
    "מצב מאורגן": "Organized state",
    "מצב Balanced": "Balanced state",
    "מפת הערכים הCollectiveת הLiveה": "Live collective value map",
    "all הנתונים מוצגים באופן אנונימי": "All data is displayed anonymously",
    
    # GlobalTrendSection.js
    "Order Drift falling - שים לב balance.": "Order Drift falling — pay attention to balance.",
    "Recovery Stability נweakת - Add actions Recovery.": "Recovery Stability weakening — add recovery actions.",
    "המגמות stability - המשך בPath הנוכLive.": "Trends are stable — continue on the current path.",
    "מגמות over Time": "Trends Over Time",
    "גרף מגמות": "Trend chart",
    "סחף Social": "Social drift",
    "There isן": "None",
    
    # GlobalValueFieldSection.js
    "Total decisions (all הsessions)": "Total decisions (all sessions)",
    "Order Drift גלובלי": "Global order drift",
    "(סדר + Recovery) - (Harm + הימנעות)": "(Order + Recovery) - (Harm + Avoidance)",
    "סחף Social גלובלי": "Global social drift",
    "תרומה - Harm": "Contribution - Harm",
    "Harm Pressure long טווח": "Long-term Harm Pressure",
    "Recovery Stability long טווח": "Long-term Recovery Stability",
    "אשכול ערכים דומיננטי": "Dominant value cluster",
    "מallל הdecisions": "of all decisions",
    "התפלגות ערכים גלובלית": "Global value distribution",
    
    # HomeNavigationSection.js
    "מצב נוכLive": "Current state",
    "תאר את הפrising שעשית או שYou מתכנן לעשות. לדוגמה:": "Describe the action you did or plan to do. For example:",
    "יצאתי להליכה shortה": "I went for a short walk",
    
    # InviteSection.js
    "Invite לField": "Invite to Field",
    "Share קThere isור וInvite מThere isהו לJoin": "Share a link and invite someone to join",
    "אין קודים active": "No active codes",
    "Invites Redeemed בSuccess": "Invites redeemed successfully",
    
    # InviteTrackingSection.js
    "דוח המרת Invites": "Invite Conversion Report",
    
    # Various remaining patterns in many files
    "Decision Paths": "Decision Paths",
}

def translate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Apply longest-first line fixes
    for old, new in sorted(LINE_FIXES.items(), key=lambda x: len(x[0]), reverse=True):
        content = content.replace(old, new)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

files = []
for ext in ['*.js', '*.jsx']:
    files.extend(glob.glob(f'/app/frontend/src/**/{ext}', recursive=True))

changed = 0
for f in sorted(files):
    if translate_file(f):
        changed += 1
        print(f'Fixed: {f}')

print(f'\nDone. {changed} files fixed.')

# Count remaining
result = subprocess.run(
    ['grep', '-Prl', '[\u0590-\u05FF]', '/app/frontend/src/', '--include=*.js', '--include=*.jsx'],
    capture_output=True, text=True
)
remaining = result.stdout.strip().split('\n') if result.stdout.strip() else []
print(f'Files still containing Hebrew: {len(remaining)}')

# Total chars
total_chars = 0
for f in remaining:
    r = subprocess.run(['grep', '-Poc', '[\u0590-\u05FF]', f], capture_output=True, text=True)
    chars = int(r.stdout.strip()) if r.stdout.strip() else 0
    total_chars += chars
print(f'Total remaining Hebrew characters: {total_chars}')
