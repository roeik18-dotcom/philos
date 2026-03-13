#!/usr/bin/env python3
"""Final comprehensive cleanup of all remaining Hebrew."""
import re, glob, subprocess

FIXES = {
    # philos/index.js
    "רצפה מוסרית: Harm High מדי": "Moral floor: Harm too high",
    "קריסת אנרגיה: capacity Low מדי": "Energy collapse: capacity too low",
    "ניצול: Personal gain High מדי ביחס לCollective": "Exploitation: Personal gain too high relative to Collective",
    "אפשר Continue לAction מדודה": "Allow continuing with measured action",
    "מוסרית": "moral",
    "אנרגיה": "energy",
    "עצור וCheck Action עם Less Harm": "Stop and check action with less harm",
    "צמצם היקף וחזור כשThere is יותר capacity": "Reduce scope and return when there is more capacity",
    "שנה את הAction כך שתועיל יותר לCollective": "Change the action so it benefits the collective more",
    "הפער דורש החזרת קיבולת דרך Action גופנית": "The gap requires restoring capacity through physical action",
    "בצע Action גופנית shortה שמחזירה capacity": "Perform a short physical action that restores capacity",
    "הפער דורש בהירות והגדרה מדויקת": "The gap requires clarity and precise definition",
    "כתוב את הבעיה במשפט אחד ברור": "Write the problem in one clear sentence",
    "הפער דורש ארגון של מרכיב קיים בReality": "The gap requires organizing an existing component in reality",
    "Order מרכיב אחד small בReality": "Organize one small component in reality",
    "הפער דורש מגע There isיר עם גורם אנושי רלוונטי": "The gap requires direct contact with a relevant person",
    "צור קשר There isיר עם person אחד רלוונטי": "Reach out directly to one relevant person",
    "הפער דורש Action שיוצרת Value ליותר מperson אחד": "The gap requires action that creates value for more than one person",
    "בצע Action אחת שמועילה ליותר מperson אחד": "Perform one action that benefits more than one person",

    # services/recommendationService.js
    "Continue בRecovery או Add Order": "Continue with recovery or add order",
    "Strengthen את הOrder או לפתוח לContribution": "Strengthen order or open to contribution",
    "Continue בContribution או לפתוח לExploration": "Continue contribution or open to exploration",
    "Continue בExploration או Noזן עם Recovery": "Continue exploration or balance with recovery",
    "בידוד": "Isolation",
    "Action קטנה של עזרה למThere isהו": "A small act of helping someone",
    "לShare משהו שלמדת": "Share something you learned",
    "להציע סיוע לחבר": "Offer help to a friend",
    "הפסקה shortה ומודעת": "Short mindful break",
    "נשימות עמוקות לכמה minutes": "Deep breathing for a few minutes",
    "Action קטנה של Order": "A small act of order",
    "לסיים Task פתוחה אחת": "Finish one open task",
    "לנסות משהו חדw": "Try something new'",
    "לשאול שאלה פתוחה": "Ask an open question",
    "לצאת מאזור הנוחות": "Step out of your comfort zone",
    "Stop וBreathe ago תגובה": "Stop and breathe before reacting",
    "לזהות את הEmotion וGive לו מקום": "Identify the emotion and give it space",
    "Choose בתגובה מתונה": "Choose a measured response",
    "Perform החלטה קטנה במקום דLiveיה": "Make a small decision instead of postponing",
    "לקחת First step small": "Take a small first step",
    "להתמודד עם משהו אחד small": "Deal with one small thing",
    "קיבלו reinforcement בעקבות Match High לתוצאות Actual": "received reinforcement following high match to actual results",
    "מAcceptים כרגע Weight Low יותר עקב פער בין המלצה לתוצאה": "currently receive lower weight due to gap between recommendation and result",
    "הכיול הנוכLive מעדיף": "Current calibration favors",
    "על פני": "over",
    "אין מספיק נתונים. Recommended להתLiveל עם Recovery.": "Not enough data. Recommended to start with recovery.",
    "הימנעות → Order": "Avoidance → Order",
    "בידוד → Contribution": "Isolation → Contribution",
    "הBalanced system.": "The system is balanced.",

    # services/analyticsService.js
    "אין מספיק נתונים לניתוח.": "Not enough data for analysis.",
    "appears דפוס Positive עם דגש על": "A positive pattern appears with emphasis on",
    "זוהה דפוס של": "A pattern was detected of",
    ". Recommended לשקול actions Recovery.": ". Consider recovery actions.",
    "הBalanced system. Continue toעקוב אחר הPatterns.": "The system is balanced. Continue monitoring the patterns.",

    # FeedTab.js
    "בשבילך": "For You",
    "מותאם ל": "Tailored to ",
    "כרטיסים": "cards",
    "אין still תוYes בFeed your": "No content in your feed yet",

    # TheorySection.js
    "Back balance after לחץ או Harm": "Restoring balance after pressure or harm",
    "יצירת structure, ארגון ובהירות": "Creating structure, organization, and clarity",
    "Action לgoodת אחרים והCollective": "Action for the benefit of others and the collective",
    "פתיחות, גמThere isות ותנועה קדימה": "Openness, flexibility, and forward movement",
    "הציר בין ספונטניות לבין structure": "The axis between spontaneity and structure",
    "הציר בין מיקוד עצמי לבין מיקוד באחרים": "The axis between self-focus and focus on others",
    "בידוד / מיקוד עצמי": "Isolation / self-focus",
    "המודל הDescriptionטי": "The Descriptive Model",
    "פילוס אוריינטציה היא מערכת שמזהה את הDirection של הactions your, לומדת את הPatterns your, ומציעה Direction מאזן להמשך.": "Philos Orientation is a system that identifies the direction of your actions, learns your patterns, and suggests a balancing direction to continue.",
    "שני צירי המתח": "Two Tension Axes",
    "לוגיקת ההחלטה": "Decision Logic",
    "actions יוצרות Direction": "Actions create direction",
    "directions חוזרים יוצרים Patterns": "Recurring directions create patterns",
    "Patterns מעצבים את הOrientation": "Patterns shape orientation",
    "כאשר הDirection הנוכLive Negative, המערכת מציעה Direction מאזן:": "When the current direction is negative, the system suggests a balancing direction:",
    "אם הDirection הנוכLive כבר Positive, המערכת תציע Strengthen אותו או Noזן אותו במקום להפוך אותו.": "If the current direction is already positive, the system will suggest strengthening or balancing it instead of reversing it.",
    "דוגמה": "Example",
    "אם Action נובעת מ": "If an action stems from ",
    ", הDirection הRecommended עשוי להיות ": ", the recommended direction may be ",
    "מפת הdirections": "Direction Map",
    "מפה ויזואלית של The Four Directions על צירי המתח": "A visual map of the four directions on the tension axes",

    # WeeklySummarySection.js
    "התמקדות עצמית": "Self-focus",
    "הWeek נע לDirection": "This week moved towards",
    " ו": " and ",
    "הValue השולט הWeek:": "Dominant value this week:",
    "Cognitive review of 7 הdays recent": "Cognitive review of the last 7 days",
    "אין מספיק נתונים לWeekly Summary": "Not enough data for weekly summary",
    "Continue toהשתמש באפליקציה כדי לצבור נתונים": "Continue using the app to accumulate data",
    "Averageים Weekיים": "Weekly Averages",
    "מגמות הWeek": "Weekly Trends",
    "התפלגות ערכים Weekית": "Weekly Value Distribution",

    # WeeklyBehavioralReportSection.js
    "הWeek בלטו יותר": "This week stood out more",
    "נמצאו": "Found",
    "Corrections באמצע Paths ofם": "corrections in the middle of paths",
    "נמצאו chains problematic - שקול לשנות Direction": "Problematic chains found — consider changing direction",
    "הWeek נבדקו שוב ושוב Paths of": "This week repeatedly checked paths of",
    "שNo נבחרו בTime אמת": "that were not chosen in real time",
    "בלטו יותר בrepeat activations מאשר בdecisions Actual": "stood out more in replays than in actual decisions",
    "appears פער עקבי בין הבLiveרות Actual לבין העדפות הבדיקה החוזרת": "A consistent gap appears between actual choices and replay preferences",
    "times בדקת מעבר מ": "times you checked a shift from ",
    "ל": "to ",
    "סיכום מגמות from 7 הdays recent": "Trend summary from the last 7 days",
    "התפלגות סוגי chains": "Chain type distribution",
    "אין מספיק נתונים להצגה": "Not enough data to display",
    "דפוס דומיננטי הWeek": "Dominant pattern this week",
    "תנועה positive strongה": "Strong positive movement",
    "תנועה Negative strongה": "Strong negative movement",
    "התפלגות יחסית": "Relative distribution",
    "השוואה לrepeat activations": "Comparison to replays",
    "repeat activations | ": "replays | ",
    "הWeek": "this week",
    "בLiveרות Actual vs repeat activations": "Actual choices vs replays",
    "הפעלה חוזרת": "Replay",
    "פער": "Gap",
    "הכי נבדק": "Most checked",
    "הוחמץ": "Missed",
    "נמנע": "Avoided",
    "Paths of סיכון": "Risk paths",
    "פער זוהה": "Gap detected",
    "נבדק יותר (+": "checked more (+",
    "%) מאשר נבחר Actual": "%) than actually chosen",
    "נבחר יותר Actual מאשר נבדק בrepeat activations": "actually chosen more than checked in replays",
    "תובנות הפעלה חוזרת": "Replay insights",

    # WeeklyOrientationSummarySection.js
    "לחץ וHarm": "Pressure and Harm",
    "זה הDirection הRecommended לWeek הקרוב.": "This is the recommended direction for the coming week.",
    "Week שעבר בלט דפוס של": "Last week showed a pattern of",
    ". הWeek Recommended Continue במומנטום.": ". This week it is recommended to continue the momentum.",
    "הWeek Recommended Strengthen Direction של Contribution.": "This week it is recommended to strengthen a contribution direction.",
    "הWeek הnew מתLiveל מתוך הדפוס של הWeek שעבר.": "The new week starts from last week's pattern.",
    "Week שעבר": "Last week",
    "No הייתה Activeות בWeek שעבר.": "There was no activity last week.",
    "בלט דפוס של": "A pattern stood out of",
    "decisions בWeek שעבר": "decisions last week",
    "הWeek": "This week",
    "Start את הWeek": "Start the week",
    "הסיכום הWeekי Helping בנות Direction התנהגותי long טווח": "The weekly summary helps build long-term behavioral direction",

    # MonthlyOrientationSection.js
    "זה הDirection הRecommended לMonth הקרוב.": "This is the recommended direction for the coming month.",
    "Month שעבר בלט דפוס של": "Last month showed a pattern of",
    ". הMonth Recommended Continue במומנטום.": ". This month it is recommended to continue the momentum.",
    "הMonth Recommended Strengthen Direction של Contribution.": "This month it is recommended to strengthen a contribution direction.",
    "הMonth הnew מתLiveל מתוך הדפוס של הMonth שעבר.": "The new month starts from last month's pattern.",
    "Orientation Monthlyת": "Monthly Orientation",
    "No הייתה Activeות בMonth שעבר.": "There was no activity last month.",
    "decisions בMonth שעבר": "decisions last month",
    "הMonth": "This month",
    "Start את הMonth": "Start the month",
    "הOrientation הMonthlyת עוזרת לבנות Direction התנהגותי long טווח": "Monthly orientation helps build long-term behavioral direction",

    # MonthlyProgressReportSection.js
    "בMonth הlast ניכרת עלייה בchains Recovery": "Last month showed an increase in recovery chains",
    "נרשמה ירידה בchains Recovery": "A decrease in recovery chains was recorded",
    "appears ירידה עקבית בדפוסי Harm": "A consistent decrease in harm patterns appears",
    "דפוסי Correction נעשו תכופים יותר over הMonth": "Correction patterns became more frequent over the month",
    "There is עלייה ברצפי Growth Positiveים": "There is an increase in positive growth streaks",
    "There is יותר chains Warning - Recommended להתייחס": "There are more warning chains — recommended to address",
    "Less chains Warning מאשר בתLiveלת הMonth - התקדמות!": "Fewer warning chains than at the start of the month — progress!",
    "מגמה allלית positive הMonth 📈": "Overall positive trend this month",
    "מגמה Negative הMonth - הזדמנות לשינוי": "Negative trend this month — opportunity for change",
    "Behavioral trends from-4 הweeks recent": "Behavioral trends from the last 4 weeks",
    "מגמה Weekית": "Weekly trend",
    "דפוס דומיננטי הMonth": "Dominant pattern this month",
    "שיפור strong": "Strong improvement",
    "נקודת סיכון": "Risk point",
    "עלייה קבועה over הרבעון": "Consistent increase over the quarter",
    "עלייה קבועה - Recommended להתייחס": "Consistent increase — recommended to address",
    "תובנות Monthlyות": "Monthly insights",
    "מגמה allלית": "Overall trend",

    # QuarterlyReviewSection.js
    "ברבעון הlast נבנתה Recovery Stability עקבית": "Last quarter saw consistent recovery stability built",
    "דפוסי Recovery הולכים ומתstrongים": "Recovery patterns are getting stronger",
    "ניכרת ירידה מתמשכת בדפוסי Harm": "A continued decrease in harm patterns is observed",
    "There is עלייה בדפוסי Harm over הרבעון - נקודה לתשומת לב": "There is an increase in harm patterns over the quarter — a point of attention",
    "דפוסי Correction הפכו לחלק Stable מההתנהגות": "Correction patterns have become a stable part of behavior",
    "רצפי Growth הפכו תכופים יותר": "Growth streaks have become more frequent",
    "הרבעון מסתיים במגמה positive ברורה 🌟": "The quarter ends with a clear positive trend",
    "Behavioral trends from-3 הmonths recent": "Behavioral trends from the last 3 months",
    "עקביות": "Consistency",
    "מגמה Monthlyת": "Monthly trend",
    "דפוס דומיננטי": "Dominant pattern",
    "משתפרת": "Improving",
    "שיפור עקבי": "Consistent improvement",
    "נקודת סיכון": "Risk point",
    "Recommended להתייחס": "Recommended to address",
    "עקביות Correction": "Correction consistency",
    "תובנות רבעוניות": "Quarterly insights",
    "מגמה רבעונית allלית": "Overall quarterly trend",

    # NextBestDirectionSection.js
    "ניווט התנהגותי מבוסס Patterns": "Behavioral navigation based on patterns",
    "Recommended direction לToday:": "Recommended direction for today:",
    "Path Descriptionטי:": "Descriptive path:",
    "המלצה Initialת": "Initial recommendation",
    "המלצה allלית": "General recommendation",

    # OppositionLayer.js
    "הChaos מושך אותך — חופש וגילוי בראw": "Chaos attracts you — freedom and discovery at the forefront'",
    "You בין Order לChaos — בשני העולמות": "You are between order and chaos — in both worlds",
    "הנתינה דומיננטית — You פועל עבור אחרים": "Giving is dominant — you act for others",
    "מתח בין פנים לחוץ — שניהם Liveים בך": "Tension between inside and outside — both live in you",
    "הExploration מושכת אותך — Discover דברים newים": "Exploration attracts you — discover new things",
    "בין הRoots למסע — שני הכוחות שווים": "Between roots and journey — both forces are equal",
    "בין אילו קטבים You נע": "Between which poles you move",

    # OrientationCompassSection.js
    "המיקום your קרוב לcenter הField הCollective.": "Your position is close to the collective field center.",
    "מצפן Orientation": "Orientation Compass",
    "המיקום your מול הField הCollective": "Your position vs. the collective field",
    "center הField הCollective": "Collective field center",
    "מיקום your": "Your position",
    "מומנטום": "Momentum",
    "מגמת הField (4 weeks)": "Field trend (4 weeks)",
    "נע ל": "Moving towards ",
    "המיקום your הWeek": "Your position this week",
    "התפלגות הWeek your:": "Your weekly distribution:",
    "Match לField": "Match to field",
    "הDirection הנוכLive: ": "Current direction: ",
    "Based on": "Based on",
    " actions ב-7 days אחרונים": " actions in the last 7 days",
    "Direction מאזן Recommended: ": "Recommended balancing direction: ",
    "הField הCollective Based on": "The collective field based on",
    " users": " users",
    "אין מספיק נתונים להצגת מיקום.": "Not enough data to display position.",
    "בצע Action ראDifferent כדי להתLiveל.": "Perform your first action to get started.",

    # OrientationIdentitySection.js
    "זה בOrder להרגThere is ככה": "It's okay to feel this way",
    "הימנעות היא תגובה טבעית. הצעד הfirst הוא להכיר בזה. הצעד Next - Create structure small אחד.": "Avoidance is a natural response. The first step is to recognize it. The next step — create one small structure.",
    "הסתר פירוט": "Hide details",
    "הצג פירוט": "Show details",
    "התפלגות הactions your:": "Your actions distribution:",
    "יחס הימנעות:": "Avoidance ratio:",

    # PathLearningSection.js
    "נמוכה": "Low",
    "הPath שנבחר אYes הוביל ל": "The chosen path did lead to ",
    "התחזית הייתה": "The prediction was",
    ", אך התוצאה הייתה": ", but the result was",
    "סחף הOrder עלה כמצופה.": "Order drift increased as expected.",
    "סחף הOrder ירד כמצופה.": "Order drift decreased as expected.",
    "סחף הOrder התנהג אחרת מהתחזית.": "Order drift behaved differently from the prediction.",
    "הContribution הSocial עלתה כמצופה.": "Social contribution increased as expected.",
    "לחץ הHarm ירד - תוצאה positive!": "Harm pressure decreased — positive result!",
    "לחץ הHarm עלה למרות התחזית.": "Harm pressure increased despite the prediction.",
    "התחזית הייתה מדויקת ברובה.": "The prediction was mostly accurate.",
    "התחזית הייתה חלקית בלבד.": "The prediction was only partial.",
    "התחזית No התאימה לתוצאה Actual.": "The prediction did not match the actual result.",
    "השוואה בין תחזית לתוצאה Actual": "Comparison between prediction and actual result",
    "Path שנבחר:": "Chosen path:",
    "נבחר ב-": "Chosen at ",
    "תחזית": "Prediction",
    "תוצאה Actual": "Actual Result",
    "איכות Match:": "Match quality:",
    "תובנות:": "Insights:",

    # RecommendationCalibrationSection.js
    "התאמת Weightים בהתבסס על תוצאות Actual": "Adjusting weights based on actual results",
    "Weightים מכוילים": "Calibrated Weights",
    "הweakה": "Weakened",
    "בסיס": "Baseline",
    "הכי מחוזק": "Most boosted",
    "מופחת": "Reduced",
    "הכיול מתבצע אוטומטית בהתבסס על ביצועי ההמלצות": "Calibration is performed automatically based on recommendation performance",

    # RecommendationFollowThroughSection.js
    "דפוס הימנעות": "Avoidance pattern",
    "פער Collective": "Collective gap",
    "נקודה עיוורת": "Blind spot",
    "מומנטום Contribution": "Contribution momentum",
    "העדפת הפעלה חוזרת": "Replay preference",
    "חוסר Balance": "Balance deficit",
    "ברירת מחדל": "Default",
    "זוכים לשיעור המעקב הHigh ביותר": "have the highest follow-through rate",
    "ההמלצות Leadingות לתוצאות תואמות ב-": "Recommendations lead to matching results in ",
    "% מהמקרים": "% of cases",
    "There is פער משמעותי בין ההמלצות לתוצאות Actual": "There is a significant gap between recommendations and actual results",
    "% Match": "% match",
    "הובילו Actual לתוצאות תואמות ברוב המקרים": "actually led to matching results in most cases",
    "There is פער בין המלצות": "There is a gap between recommendations for",
    "לבין הactions Actual": "and the actual actions",
    "מעקב אחר המלצות": "Recommendation Follow-Through",
    "ניתוח יעילות מנוע ההמלצות": "Analysis of recommendation engine effectiveness",
    "שיעור מעקב": "Follow-through rate",
    "התאמת תוצאות": "Result alignment",
    "המלצה ↔ פועל": "Recommendation ↔ Action",
    "הכי נעקב": "Most followed",
    "התפלגות מעקב לפי Direction": "Follow-through distribution by direction",
    "הכי אפקטיבי": "Most effective",
    "דורש שיפור": "Needs improvement",
    "decisions שנבעו מהמלצות": "decisions that stemmed from recommendations",

    # ReplayAdaptiveEffectSection.js
    "השפעת הפעלה חוזרת על Paths ofם": "Impact of replays on paths",
    "התאמות אוטומטיות בהתבסס על": "Automatic adjustments based on",
    "directions מחוזקים": "Boosted directions",
    "directions מוweakים": "Weakened directions",
    "תובנות Match": "Match Insights",

    # ReplayInsightsSummarySection.js
    "Insights Summary הפעלה חוזרת": "Replay Insights Summary",
    "בWeek הlast": "this week",
    "Loading תובנות...": "Loading insights...",
    "הPaths ofם החלופיים הנבדקים ביותר": "The most checked alternative paths",
    "דפוסי מעבר נפוצים": "Common transition patterns",
    "points עיוורות אפשריות": "Possible blind spots",
    "מWorld No בדקת Path": "You never checked a path of",
    "אחרי החלטת": "after a decision of",
    "תובנות התנהגותיות": "Behavioral insights",
    "Total הפעלות": "Total replays",
    "דפוסי מעבר": "Transition patterns",
    "points עיוורות": "Blind spots",

    # SendToGlobeButton.js
    "Your action נוספה לField האנושי": "Your action was added to the human field",
    "הנקודה your בגלובוס": "Your point on the globe",
    "Send Point לגלובוס": "Send Point to Globe",

    # SessionComparisonSection.js
    "סשן ב׳ מראה Recovery Stability High יותר.": "Session B shows higher recovery stability.",
    "סשן א׳ מראה Recovery Stability High יותר.": "Session A shows higher recovery stability.",
    "סשן ב׳ מראה Harm Pressure Low יותר.": "Session B shows lower harm pressure.",
    "סשן א׳ מראה Harm Pressure Low יותר.": "Session A shows lower harm pressure.",
    "סשן ב׳ נוטה יותר לDirection Order.": "Session B leans more towards order direction.",
    "סשן א׳ נוטה יותר לDirection Order.": "Session A leans more towards order direction.",
    "סשן ב׳ מראה נטייה Social strongה יותר.": "Session B shows stronger social tendency.",
    "סשן א׳ מראה נטייה Social strongה יותר.": "Session A shows stronger social tendency.",
    "סשן ב׳ כולל יותר decisions.": "Session B has more decisions.",
    "סשן א׳ כולל יותר decisions.": "Session A has more decisions.",
    "שני הsessions דומים במדדים העיקריים.": "Both sessions are similar in key metrics.",
    "א׳": "A",
    "ב׳": "B",
    "השווה בין שני sessions Saveים": "Compare two saved sessions",
    "Need at least 2 sessions Saveים להשוואה": "Need at least 2 saved sessions for comparison",
    "Save More sessions בספריית הsessions": "Save more sessions in the session library",
    "סשן א׳": "Session A",
    "סשן ב׳": "Session B",
    "בחר סשן...": "Select session...",
    "Loading השוואה...": "Loading comparison...",
    "Dominant value א׳": "Dominant value A",
    "Dominant value ב׳": "Dominant value B",
    "השוואת מדדים": "Metrics Comparison",
    "מספר decisions": "Number of decisions",
    "בחר שני sessions להשוואה": "Select two sessions for comparison",

    # SessionLibrarySection.js
    "הסשן נשמר בSuccess!": "Session saved successfully!",
    "למחוק את הסשן הזה?": "Delete this session?",
    "sessions Saveים": "saved sessions",
    "טען sessions קודמים": "Load previous sessions",
    "שומר...": "Saving...",
    "Save סשן נוכLive": "Save current session",
    "Need at least 3 decisions כדי לSave": "Need at least 3 decisions to save",
    "אין sessions Saveים": "No saved sessions",
    "Save את הסשן הנוכLive כדי להתLiveל": "Save the current session to get started",
    "פתח סשן": "Open session",
    "badנן רשימה": "Refresh list",

    # ValueConstellationSection.js
    "מפת Value Constellation": "Value Constellation Map",
    "structure מרחבי של decisions לפי ערכים": "Spatial structure of decisions by values",
    "מעברים": "Transitions",
    "Links בין ערכים": "Links between values",
    "התפלגות ערכים": "Value Distribution",

    # ValueProfileSection.js
    "פרופיל Value": "Value Profile",
    "Value כולל": "Total Value",
    "הנThere isה Nextה:": "Next niche:",
    "תגים": "Tags",

    # DecisionPathsSection regex patterns - leave Hebrew in regex patterns alone but translate UI text
    "הזן הקשר": "Enter context",
}

def translate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    for old, new in sorted(FIXES.items(), key=lambda x: len(x[0]), reverse=True):
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

print(f'Fixed {changed} files.')

# Count remaining
result = subprocess.run(
    ['grep', '-Prl', '[\u0590-\u05FF]', '/app/frontend/src/', '--include=*.js', '--include=*.jsx'],
    capture_output=True, text=True
)
remaining = result.stdout.strip().split('\n') if result.stdout.strip() else []
total = 0
for f in remaining:
    r = subprocess.run(['grep', '-Poc', '[\u0590-\u05FF]', f], capture_output=True, text=True)
    c = int(r.stdout.strip()) if r.stdout.strip() else 0
    total += c
    if c > 2:
        print(f'  {f.replace("/app/frontend/src/","")} ({c} chars)')
print(f'\nRemaining: {len(remaining)} files, {total} Hebrew chars')
