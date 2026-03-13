"""All domain constants used across the Philos Orientation system."""

ANONYMOUS_ALIASES = [
    "Explorer", "Builder", "Seeker", "Navigator", "Pioneer",
    "Guardian", "Visionary", "Pathfinder", "Strategist", "Catalyst",
    "Dreamer", "Architect", "Sentinel", "Wanderer", "Alchemist",
    "Sage", "Herald", "Beacon", "Anchor", "Voyager"
]

DIRECTION_FORCE_MAP = {
    'contribution': {'cognitive': 0.2, 'emotional': 0.4, 'physical': 0.1, 'personal': 0.1, 'social': 0.8, 'drives': 0.3},
    'recovery': {'cognitive': 0.3, 'emotional': 0.6, 'physical': 0.5, 'personal': 0.7, 'social': 0.1, 'drives': 0.2},
    'order': {'cognitive': 0.7, 'emotional': 0.2, 'physical': 0.3, 'personal': 0.4, 'social': 0.3, 'drives': 0.6},
    'exploration': {'cognitive': 0.8, 'emotional': 0.5, 'physical': 0.2, 'personal': 0.3, 'social': 0.4, 'drives': 0.7}
}

DIRECTION_VECTOR_MAP = {
    'contribution': {'internal': 0.2, 'external': 0.5, 'collective': 0.8},
    'recovery': {'internal': 0.8, 'external': 0.1, 'collective': 0.2},
    'order': {'internal': 0.5, 'external': 0.4, 'collective': 0.4},
    'exploration': {'internal': 0.4, 'external': 0.7, 'collective': 0.3}
}

FORCE_LABELS_HE = {
    'cognitive': 'קוגניטיבי', 'emotional': 'רגשי', 'physical': 'פיזי',
    'personal': 'אישי', 'social': 'חברתי', 'drives': 'דחפים'
}

VECTOR_LABELS_HE = {
    'internal': 'פנימי', 'external': 'חיצוני', 'collective': 'קולקטיבי'
}

DIRECTION_THEORY = {
    'contribution': {
        'label_he': 'תרומה', 'symbol': 'נתינה',
        'explanation_he': 'כיוון התרומה מבטא את הרצון לתת, לעזור ולהשפיע על הסביבה. זהו הכוח שמחבר בין הפרט לקולקטיב.',
        'meaning_he': 'כשאתה פועל בכיוון התרומה, אתה מחזק את השדה הקולקטיבי ויוצר ערך שחורג מגבולות העצמי.',
        'symbolic_meaning_he': 'הסמל של התרומה הוא הנתינה — הזרימה כלפי חוץ. כמו נהר שמזין את השדות סביבו, פעולת התרומה יוצרת ערך שמתפשט מעבר לגבולות האדם הפועל.',
        'behavior_example_he': 'לעזור לחבר שנמצא במשבר, להתנדב בקהילה, לשתף ידע עם עמית, להקשיב למישהו שצריך אוזן קשבת.',
        'field_effect_he': 'פעולות תרומה מחזקות את הקשר בין חלקי השדה. ככל שיותר אנשים פועלים בכיוון התרומה, השדה הקולקטיבי הופך מחובר ויציב יותר.'
    },
    'recovery': {
        'label_he': 'התאוששות', 'symbol': 'שיקום',
        'explanation_he': 'כיוון ההתאוששות מבטא את הצורך בהטענה, מנוחה ושיקום פנימי. זהו הכוח שמאפשר לחזור לאיזון.',
        'meaning_he': 'כשאתה פועל בכיוון ההתאוששות, אתה בונה את הבסיס הפנימי שממנו כל פעולה אחרת מתחילה.',
        'symbolic_meaning_he': 'הסמל של ההתאוששות הוא השיקום — התנועה פנימה. כמו עץ שמפיל עלים בסתיו כדי לשמור אנרגיה לאביב, ההתאוששות היא ההכנה לצמיחה הבאה.',
        'behavior_example_he': 'לקחת הפסקה אחרי יום עמוס, לישון כמו שצריך, לצאת לטיול בטבע, לשתות כוס תה בשקט, לסרב לבקשה כשאין כוח.',
        'field_effect_he': 'פעולות התאוששות מייצבות את הבסיס של השדה. כשאנשים מאפשרים לעצמם התאוששות, הם חוזרים לשדה עם יותר אנרגיה ובהירות.'
    },
    'order': {
        'label_he': 'סדר', 'symbol': 'מבנה',
        'explanation_he': 'כיוון הסדר מבטא את הרצון לארגן, לתכנן וליצור מבנה. זהו הכוח שמביא יציבות ובהירות.',
        'meaning_he': 'כשאתה פועל בכיוון הסדר, אתה יוצר מסגרת שמאפשרת לכל הכיוונים האחרים לפעול בצורה יעילה.',
        'symbolic_meaning_he': 'הסמל של הסדר הוא המבנה — השלד שמחזיק הכול. כמו אדריכל שמתכנן בניין, הסדר יוצר את התשתית שעליה כל דבר אחר נבנה.',
        'behavior_example_he': 'לארגן את הלוח זמנים, לתכנן את השבוע, לסדר את חדר העבודה, לכתוב רשימת משימות, להגדיר יעדים ברורים.',
        'field_effect_he': 'פעולות סדר יוצרות מבנה בשדה הקולקטיבי. כשיש סדר, כל הכיוונים האחרים פועלים בצורה יעילה יותר — השדה הופך ברור וניתן לניווט.'
    },
    'exploration': {
        'label_he': 'חקירה', 'symbol': 'גילוי',
        'explanation_he': 'כיוון החקירה מבטא את הסקרנות, הרצון ללמוד ולגלות. זהו הכוח שמניע שינוי וצמיחה.',
        'meaning_he': 'כשאתה פועל בכיוון החקירה, אתה פותח דלתות חדשות ומרחיב את גבולות ההכרה.',
        'symbolic_meaning_he': 'הסמל של החקירה הוא הגילוי — התנועה קדימה לעבר הלא נודע. כמו חוקר שמפליג לים הפתוח, החקירה דורשת אומץ ופתיחות.',
        'behavior_example_he': 'ללמוד נושא חדש, לנסות גישה שונה לבעיה, לשאול שאלות קשות, לצאת מאזור הנוחות, לפגוש אנשים חדשים.',
        'field_effect_he': 'פעולות חקירה מרחיבות את השדה. הן מוסיפות ממדים חדשים ואפשרויות שלא היו קיימות קודם — השדה הופך דינמי ומלא פוטנציאל.'
    }
}

GLOBE_COUNTRY_COORDS = {
    "BR": {"lat": -14.2, "lng": -51.9}, "IN": {"lat": 20.6, "lng": 78.9}, "DE": {"lat": 51.2, "lng": 10.5},
    "US": {"lat": 37.1, "lng": -95.7}, "JP": {"lat": 36.2, "lng": 138.3}, "NG": {"lat": 9.1, "lng": 8.7},
    "IL": {"lat": 31.1, "lng": 34.8}, "FR": {"lat": 46.2, "lng": 2.2}, "AU": {"lat": -25.3, "lng": 133.8},
    "KR": {"lat": 35.9, "lng": 127.8}, "MX": {"lat": 23.6, "lng": -102.6}, "GB": {"lat": 55.4, "lng": -3.4},
    "CA": {"lat": 56.1, "lng": -106.3}, "IT": {"lat": 41.9, "lng": 12.6}, "ES": {"lat": 40.5, "lng": -3.7},
    "AR": {"lat": -38.4, "lng": -63.6}, "TR": {"lat": 39.0, "lng": 35.2}, "TH": {"lat": 15.9, "lng": 100.5},
    "PL": {"lat": 51.9, "lng": 19.1}, "NL": {"lat": 52.1, "lng": 5.3}
}

GLOBE_COLOR_MAP = {
    'contribution': '#22c55e', 'recovery': '#3b82f6', 'order': '#6366f1', 'exploration': '#f59e0b'
}

GLOBE_DIR_LABELS = {'recovery': 'התאוששות', 'order': 'סדר', 'contribution': 'תרומה', 'exploration': 'חקירה'}

BASE_DEFINITIONS = {
    'heart': {
        'name_he': 'לב',
        'description_he': 'מאיזה מרכז אתה פועל היום?',
        'allocations_he': ['קשרים ומערכות יחסים', 'אמפתיה והקשבה', 'תרומה ונתינה', 'תיקון רגשי'],
        'allocations_keys': ['relationships', 'empathy', 'contribution', 'emotional_repair']
    },
    'head': {
        'name_he': 'ראש',
        'description_he': 'מאיזה מרכז אתה פועל היום?',
        'allocations_he': ['סדר ותכנון', 'למידה וחקירה', 'קבלת החלטות', 'חשיבה אסטרטגית'],
        'allocations_keys': ['order', 'learning', 'decision_making', 'strategic_thinking']
    },
    'body': {
        'name_he': 'גוף',
        'description_he': 'מאיזה מרכז אתה פועל היום?',
        'allocations_he': ['תנועה ובריאות', 'פעולה מעשית', 'משמעת ומחויבות', 'סדר פיזי'],
        'allocations_keys': ['movement', 'practical_action', 'discipline', 'physical_order']
    }
}

DIRECTION_TO_DEPT = {
    'contribution': 'heart', 'recovery': 'body', 'order': 'head', 'exploration': 'head'
}

DEPT_LABELS_HE = {'heart': 'לב', 'head': 'ראש', 'body': 'גוף'}

MISSION_DESCRIPTIONS = {
    'contribution': {'mission_he': 'משימת היום: תרומה', 'description_he': 'עשה פעולה קטנה שתעזור למישהו אחר היום'},
    'recovery': {'mission_he': 'משימת היום: התאוששות', 'description_he': 'קח רגע של מנוחה והטענה עצמית היום'},
    'order': {'mission_he': 'משימת היום: סדר', 'description_he': 'ארגן דבר אחד קטן בסביבה שלך היום'},
    'exploration': {'mission_he': 'משימת היום: חקירה', 'description_he': 'נסה משהו חדש או למד דבר אחד חדש היום'}
}

MISSION_TARGET = 5000
MAX_INVITE_CODES = 5

VALUE_NICHES = {
    'builder_of_order': {
        'label_he': 'בונה הסדר', 'description_he': 'אתה יוצר מבנה ויציבות. הפעולות שלך מארגנות את השדה.',
        'dominant_direction': 'order', 'threshold': 35,
        'strengthening_actions_he': ['לתכנן את השבוע', 'לסדר סדרי עדיפויות', 'לכתוב רשימת משימות']
    },
    'explorer': {
        'label_he': 'חוקר', 'description_he': 'אתה פותח דלתות חדשות. הסקרנות שלך מרחיבה את השדה.',
        'dominant_direction': 'exploration', 'threshold': 35,
        'strengthening_actions_he': ['ללמוד משהו חדש', 'לשאול שאלה קשה', 'לנסות גישה שונה']
    },
    'contributor': {
        'label_he': 'תורם', 'description_he': 'אתה נותן לעולם. הנתינה שלך מחזקת את הקשר בשדה.',
        'dominant_direction': 'contribution', 'threshold': 35,
        'strengthening_actions_he': ['לעזור למישהו', 'לשתף ידע', 'להקשיב לחבר']
    },
    'regenerator': {
        'label_he': 'משקם', 'description_he': 'אתה בונה את הבסיס הפנימי. ההתאוששות שלך מייצבת את השדה.',
        'dominant_direction': 'recovery', 'threshold': 35,
        'strengthening_actions_he': ['לקחת הפסקה', 'לישון כמו שצריך', 'לצאת לטיול']
    },
    'social_connector': {
        'label_he': 'מחבר חברתי', 'description_he': 'אתה מגשר בין אנשים וכיוונים. הנוכחות שלך מאחדת את השדה.',
        'dominant_direction': None, 'threshold': 20,
        'strengthening_actions_he': ['להזמין חבר', 'להשתתף במשימה קולקטיבית', 'לשתף את ההתמצאות']
    },
    'deep_thinker': {
        'label_he': 'הוגה עמוק', 'description_he': 'אתה מאזן בין כל הכיוונים. העומק שלך מעשיר את השדה.',
        'dominant_direction': None, 'threshold': 20,
        'strengthening_actions_he': ['לשקול את הצעדים', 'לחזור על החלטה ישנה', 'לרשום תובנה']
    }
}

BADGES = [
    {'id': 'first_action', 'label_he': 'צעד ראשון', 'desc_he': 'ביצעת את הפעולה הראשונה', 'condition': lambda p: p.get('total_actions', 0) >= 1},
    {'id': 'first_globe_point', 'label_he': 'נקודה בשדה', 'desc_he': 'שלחת נקודה לגלובוס', 'condition': lambda p: p.get('globe_points', 0) >= 1},
    {'id': 'streak_3', 'label_he': 'רצף 3 ימים', 'desc_he': 'שמרת על רצף של 3 ימים', 'condition': lambda p: p.get('current_streak', 0) >= 3},
    {'id': 'streak_7', 'label_he': 'נוכחות שבועית', 'desc_he': '7 ימים רצופים בשדה', 'condition': lambda p: p.get('current_streak', 0) >= 7},
    {'id': 'streak_30', 'label_he': 'נוכחות חודשית', 'desc_he': '30 ימים רצופים', 'condition': lambda p: p.get('current_streak', 0) >= 30},
    {'id': 'actions_10', 'label_he': 'פעיל', 'desc_he': '10 פעולות', 'condition': lambda p: p.get('total_actions', 0) >= 10},
    {'id': 'actions_50', 'label_he': 'מחויב', 'desc_he': '50 פעולות', 'condition': lambda p: p.get('total_actions', 0) >= 50},
    {'id': 'actions_100', 'label_he': 'תורם קבוע', 'desc_he': '100 פעולות', 'condition': lambda p: p.get('total_actions', 0) >= 100},
    {'id': 'all_directions', 'label_he': 'רב-כיווני', 'desc_he': 'פעלת בכל 4 הכיוונים', 'condition': lambda p: all(p.get('dir_counts', {}).get(d, 0) > 0 for d in ['contribution', 'recovery', 'order', 'exploration'])},
    {'id': 'niche_found', 'label_he': 'מצאת את הנישה', 'desc_he': 'הנישה שלך זוהתה', 'condition': lambda p: p.get('dominant_niche') is not None},
]

SUBSCRIPTION_PLANS = {
    'free': {'label_he': 'חופשי', 'price': 0.0, 'features_he': ['התמצאות יומית', 'מצפן בסיסי', 'גלובוס', 'קהילה'], 'limits': {'feed_cards': 5, 'value_detail': False, 'niche_insights': False, 'weekly_report': False, 'globe_regions': 3}},
    'plus': {'label_he': 'פלוס', 'price': 9.99, 'features_he': ['כל תכונות חופשי', 'פיד מותאם אישית מלא', 'אנליטיקת ערך מלאה', 'דוח שבועי מעמיק', 'תובנות נישה'], 'limits': {'feed_cards': 50, 'value_detail': True, 'niche_insights': True, 'weekly_report': True, 'globe_regions': 20}},
    'collective': {'label_he': 'קולקטיב', 'price': 24.99, 'features_he': ['כל תכונות פלוס', 'מעגלים פרטיים', 'תובנות גלובוס פרימיום', 'פרופיל מורחב', 'התקדמות נישה מלאה'], 'limits': {'feed_cards': -1, 'value_detail': True, 'niche_insights': True, 'weekly_report': True, 'globe_regions': -1}}
}

FEED_ACTIONS_HE = ['ארגנתי את סביבת העבודה', 'עזרתי לחבר', 'למדתי נושא חדש', 'לקחתי הפסקה', 'תכננתי את השבוע', 'שיתפתי ידע', 'ניסיתי גישה שונה', 'ישנתי 8 שעות', 'כתבתי רשימת יעדים', 'פגשתי אדם חדש', 'התנדבתי בקהילה', 'יצאתי לטיול בטבע', 'קראתי מאמר', 'הקשבתי למישהו', 'סידרתי סדרי עדיפויות']
FEED_QUESTIONS_HE = ['איזה כוח מנחה אותך היום?', 'מה הצעד הבא שלך?', 'מה למדת על עצמך השבוע?', 'איפה אתה מרגיש שאתה תקוע?', 'מה תרצה לשנות מחר?']
FEED_REFLECTIONS_HE = ['שמתי לב שהכיוון שלי היה בעיקר פנימי. צריך לאזן.', 'השדה הגלובלי נע לכיוון תרומה — אולי זה הזמן להצטרף.', 'גיליתי שסדר עוזר לי יותר ממה שחשבתי.', 'ההתאוששות הייתה הכי חשובה השבוע.']

CIRCLE_DEFS = {
    'builders_of_order': {'label_he': 'בוני הסדר', 'direction': 'order', 'color': '#6366f1', 'desc_he': 'קהילה של אנשים שיוצרים מבנה ויציבות בשדה.'},
    'explorers': {'label_he': 'חוקרים', 'direction': 'exploration', 'color': '#f59e0b', 'desc_he': 'קהילה של סקרנים שמרחיבים את גבולות השדה.'},
    'contributors': {'label_he': 'תורמים', 'direction': 'contribution', 'color': '#22c55e', 'desc_he': 'קהילה של נותנים שמחזקים את הקשר בשדה.'},
    'regenerators': {'label_he': 'משקמים', 'direction': 'recovery', 'color': '#3b82f6', 'desc_he': 'קהילה של אנשים שמייצבים את הבסיס הפנימי.'},
    'social_connectors': {'label_he': 'מחברים חברתיים', 'direction': None, 'color': '#ec4899', 'desc_he': 'קהילה של מגשרים שמאחדים כיוונים שונים.'},
    'deep_thinkers': {'label_he': 'הוגים עמוקים', 'direction': None, 'color': '#8b5cf6', 'desc_he': 'קהילה של אנשים שמאזנים בין כל הכיוונים.'}
}

COMPASS_SUGGESTIONS = {
    'order': {'weak': 'exploration', 'suggestion_he': 'נסה ללמוד משהו חדש לגמרי היום — לצאת מהמבנה הרגיל.'},
    'exploration': {'weak': 'order', 'suggestion_he': 'תן מבנה למה שגילית — כתוב רשימה או תכנן צעד הבא.'},
    'contribution': {'weak': 'recovery', 'suggestion_he': 'קח זמן לעצמך היום — גם נותנים צריכים להיטען.'},
    'recovery': {'weak': 'contribution', 'suggestion_he': 'עשה משהו קטן עבור מישהו אחר — נתינה מחזקת אחרי התאוששות.'}
}

ACTION_MEANINGS = {
    'contribution': {
        'personal_he': 'פעולה שמרחיבה את הנוכחות שלך מעבר לעצמך',
        'social_he': 'חיזוק הקשר החברתי — נתינה שמחברת בין אנשים',
        'value_he': 'ערך התרומה — העולם נבנה מפעולות של נתינה',
        'system_he': 'כוח תרומה בשדה — מגביר את הכיוון הקולקטיבי'
    },
    'recovery': {
        'personal_he': 'פעולה שמחזקת את הבסיס הפנימי שלך',
        'social_he': 'מודל של טיפול עצמי — מראה לאחרים שמותר לעצור',
        'value_he': 'ערך ההתאוששות — בנייה דורשת מנוחה',
        'system_he': 'כוח איזון בשדה — ייצוב פנימי שמקרין החוצה'
    },
    'order': {
        'personal_he': 'פעולה שיוצרת מבנה ובהירות בחיים שלך',
        'social_he': 'תרומה למסגרת — סדר אישי משפיע על הסביבה',
        'value_he': 'ערך הסדר — יציבות כבסיס לצמיחה',
        'system_he': 'כוח ארגון בשדה — מגביר את היציבות הגלובלית'
    },
    'exploration': {
        'personal_he': 'פעולה שפותחת דלתות חדשות בעולם שלך',
        'social_he': 'הרחבת אופקים — סקרנות שמזמינה אחרים לגלות',
        'value_he': 'ערך החקירה — גילוי כמנוע לשינוי',
        'system_he': 'כוח הרחבה בשדה — מגדיל את מפת האפשרויות'
    }
}

DEMO_COUNTRIES = [
    ("Brazil", "BR"), ("India", "IN"), ("Germany", "DE"), ("USA", "US"),
    ("Japan", "JP"), ("Nigeria", "NG"), ("Israel", "IL"), ("France", "FR"),
    ("Australia", "AU"), ("South Korea", "KR"), ("Mexico", "MX"), ("UK", "GB"),
    ("Canada", "CA"), ("Italy", "IT"), ("Spain", "ES"), ("Argentina", "AR"),
    ("Turkey", "TR"), ("Thailand", "TH"), ("Poland", "PL"), ("Netherlands", "NL")
]

DEMO_ALIASES = [
    "Atlas", "Nova", "Sage", "Drift", "Ember", "Coral", "Zenith", "Flux",
    "Prism", "Echo", "Nimbus", "Pulse", "Aether", "Crest", "Dusk", "Fern",
    "Glint", "Haven", "Iris", "Jade", "Kite", "Lumen", "Mist", "Nest",
    "Opal", "Pine", "Quill", "Reef", "Spark", "Thorn", "Ursa", "Vale",
    "Wren", "Zephyr", "Amber", "Brook", "Cedar", "Dawn", "Elm", "Frost",
    "Grove", "Haze", "Ivy", "Jet", "Kelp", "Lark", "Moss", "Nyx",
    "Orion", "Peak"
]

DIRECTIONS = ['contribution', 'recovery', 'order', 'exploration']
