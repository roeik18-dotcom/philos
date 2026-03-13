#!/usr/bin/env python3
"""
Translate all Hebrew strings in backend files to English.
This script does exact string replacements to preserve code structure.
"""
import re

def translate_file(filepath, replacements):
    """Read file, apply all replacements, write back."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
        else:
            print(f"  WARNING: Not found in {filepath}: {old[:60]}...")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Translated {filepath}")


# ============================================================
# AUTH.PY
# ============================================================
print("=== Translating auth.py ===")
translate_file('/app/backend/routes/auth.py', [
    ('message="כתובת האימייל כבר קיימת במערכת"  # Email already exists',
     'message="This email address is already registered"'),
    ('message="קוד ההזמנה אינו תקף"',
     'message="Invalid invite code"'),
    ('message="ההרשמה הצליחה!"  # Registration successful',
     'message="Registration successful!"'),
    ('message="אימייל או סיסמה שגויים"  # Invalid email or password',
     'message="Invalid email or password"'),
    ('message="התחברת בהצלחה!"  # Login successful',
     'message="Logged in successfully!"'),
    ('"התנתקת בהצלחה"}  # Logged out successfully',
     '"Logged out successfully"}'),
    ('message="לא מחובר"  # Not logged in',
     'message="Not logged in"'),
    ('"הנתונים הועברו בהצלחה לחשבון שלך",  # Data migrated successfully',
     '"Data migrated successfully to your account",'),
])


# ============================================================
# ADMIN.PY
# ============================================================
print("=== Translating admin.py ===")
translate_file('/app/backend/routes/admin.py', [
    ("'message_he': 'תודה על המשוב!'",
     "'message': 'Thank you for your feedback!'"),
    ("'message_he': 'הפעולה הראשונה שלך נשלחה לשדה!',",
     "'message': 'Your first action has been sent to the field!',"),
])


# ============================================================
# PROFILE.PY
# ============================================================
print("=== Translating profile.py ===")
translate_file('/app/backend/routes/profile.py', [
    ('get("name", "ישראל")',
     'get("name", "Israel")'),
])


# ============================================================
# MEMORY.PY
# ============================================================
print("=== Translating memory.py ===")
translate_file('/app/backend/routes/memory.py', [
    ('insights=["אין עדיין נתוני הפעלה חוזרת. התחל לבדוק מסלולים חלופיים כדי לקבל תובנות."]',
     'insights=["No replay data yet. Start exploring alternative paths to gain insights."]'),
])


# ============================================================
# COLLECTIVE.PY
# ============================================================
print("=== Translating collective.py ===")
translate_file('/app/backend/routes/collective.py', [
    ("'contribution': 'תרומה',\n            'recovery': 'התאוששות',\n            'order': 'סדר',\n            'harm': 'נזק',\n            'avoidance': 'הימנעות'",
     "'contribution': 'Contribution',\n            'recovery': 'Recovery',\n            'order': 'Order',\n            'harm': 'Harm',\n            'avoidance': 'Avoidance'"),
    ('insights.append(f"השדה הקולקטיבי נוטה כעת ל{value_labels.get(top_values[0][0], \'\')} ו{value_labels.get(top_values[1][0], \'\')}.")',
     'insights.append(f"The collective field currently leans toward {value_labels.get(top_values[0][0], \'\')} and {value_labels.get(top_values[1][0], \'\')}.")'),
    ('insights.append(f"השדה הקולקטיבי נוטה כעת ל{value_labels.get(top_values[0][0], \'\')}.")',
     'insights.append(f"The collective field currently leans toward {value_labels.get(top_values[0][0], \'\')}.")'),
    ('insights.append("לחץ הנזק הממוצע נמוך.")',
     'insights.append("Average harm pressure is low.")'),
    ('insights.append("לחץ הנזק הממוצע גבוה יחסית.")',
     'insights.append("Average harm pressure is relatively high.")'),
    ('insights.append("לחץ הנזק הממוצע בינוני.")',
     'insights.append("Average harm pressure is moderate.")'),
    ('insights.append("יש עלייה קלה בכיוון סדר.")',
     'insights.append("There is a slight increase toward Order.")'),
    ('insights.append("יש עלייה קלה בכיוון קולקטיבי.")',
     'insights.append("There is a slight increase in collective direction.")'),
    ('insights.append("הכיוון הממוצע מאוזן.")',
     'insights.append("The average direction is balanced.")'),
    ('insights.append("יציבות ההתאוששות הקולקטיבית גבוהה.")',
     'insights.append("Collective recovery stability is high.")'),
    ('insights.append("השדה הקולקטיבי נע השבוע יותר לכיוון סדר.")',
     'insights.append("The collective field moved more toward Order this week.")'),
    ('insights.append("השדה הקולקטיבי נע השבוע יותר לכיוון כאוס.")',
     'insights.append("The collective field moved more toward chaos this week.")'),
    ('insights.append("לחץ הנזק ירד ביחס לתקופה הקודמת.")',
     'insights.append("Harm pressure has decreased compared to the previous period.")'),
    ('insights.append("לחץ הנזק עלה ביחס לתקופה הקודמת.")',
     'insights.append("Harm pressure has increased compared to the previous period.")'),
    ('insights.append("יש עלייה בהתאוששות הקולקטיבית.")',
     'insights.append("There is an increase in collective recovery.")'),
    ('insights.append("יש ירידה בהתאוששות הקולקטיבית.")',
     'insights.append("There is a decrease in collective recovery.")'),
    ('insights.append("הכיוון הקולקטיבי מתחזק.")',
     'insights.append("The collective direction is strengthening.")'),
    ('insights.append("יש ירידה בכיוון הקולקטיבי.")',
     'insights.append("There is a decrease in collective direction.")'),
    ('insights.append("פעילות גבוהה יותר השבוע.")',
     'insights.append("Higher activity this week.")'),
    ('insights.append("פעילות נמוכה יותר השבוע.")',
     'insights.append("Lower activity this week.")'),
    ('insights.append("השדה הקולקטיבי יציב יחסית לתקופה הקודמת.")',
     'insights.append("The collective field is relatively stable compared to the previous period.")'),
])


# ============================================================
# SOCIAL.PY
# ============================================================
print("=== Translating social.py ===")
translate_file('/app/backend/routes/social.py', [
    ("'country': 'ישראל'", "'country': 'Israel'"),
    ("'direction_he': 'תרומה'", "'direction_he': 'Contribution'"),
    ("'niche_tag': 'תורם'", "'niche_tag': 'Contributor'"),
    ("for label, thresh in [('פעולה ראשונה', 1), ('10 פעולות', 10), ('50 פעולות', 50), ('שבוע רצוף', None)]:",
     "for label, thresh in [('First action', 1), ('10 actions', 10), ('50 actions', 50), ('Consecutive week', None)]:"),
    ("'next_milestone_he': '10 פעולות' if profile['total_actions'] < 10 else '50 פעולות' if profile['total_actions'] < 50 else '100 פעולות'",
     "'next_milestone': '10 actions' if profile['total_actions'] < 10 else '50 actions' if profile['total_actions'] < 50 else '100 actions'"),
    ("momentum = 'עולה' if total_today > yesterday_events else ('יורד' if total_today < yesterday_events * 0.8 else 'יציב')",
     "momentum = 'rising' if total_today > yesterday_events else ('falling' if total_today < yesterday_events * 0.8 else 'stable')"),
    ("'title_he': {'contribution': 'חזק את הקשר', 'recovery': 'שקם את הבסיס', 'order': 'שחזר סדר', 'exploration': 'הרחב את השדה'}.get(d, ''),",
     "'title': {'contribution': 'Strengthen the bond', 'recovery': 'Rebuild the foundation', 'order': 'Restore order', 'exploration': 'Expand the field'}.get(d, ''),"),
    ("'description_he': {'contribution': 'עשה פעולה אחת של נתינה היום', 'recovery': 'קח זמן אחד להתאוששות', 'order': 'ארגן דבר אחד בסביבה שלך', 'exploration': 'נסה דבר חדש אחד היום'}.get(d, ''),",
     "'description': {'contribution': 'Do one act of giving today', 'recovery': 'Take a moment to recover', 'order': 'Organize one thing in your environment', 'exploration': 'Try one new thing today'}.get(d, ''),"),
    ("'message_he': 'הצטרפת למשימה!'",
     "'message': 'You have joined the mission!'"),
    ("'message_he': 'כבר חבר במעגל'",
     "'message': 'Already a member of the circle'"),
    ("'message_he': 'הצטרפת למעגל!'",
     "'message': 'You have joined the circle!'"),
    ("'title_he': {'contribution': 'חזק את הקשר', 'recovery': 'שקם את הבסיס', 'order': 'שחזר סדר', 'exploration': 'הרחב את השדה'}.get(d, 'משימה'),",
     "'title': {'contribution': 'Strengthen the bond', 'recovery': 'Rebuild the foundation', 'order': 'Restore order', 'exploration': 'Expand the field'}.get(d, 'Mission'),"),
    ("'description_he': f\"משימת מעגל: {cdef['label_he']}\",",
     "'description': f\"Circle mission: {cdef.get('label', cdef.get('label_he', ''))}\","),
    ("'message_he': 'לא חבר במעגל'", "'message': 'Not a member of the circle'"),
    ("'message_he': 'עזבת את המעגל'", "'message': 'You have left the circle'"),
    ("'suggestion_he': 'בצע את הפעולה הראשונה שלך כדי לקבל ניתוח מצפן.',",
     "'suggestion': 'Perform your first action to receive a compass analysis.',"),
    ("COMPASS_SUGGESTIONS.get(dominant, {}).get('suggestion_he', 'המשך בכיוון שלך.')",
     "COMPASS_SUGGESTIONS.get(dominant, {}).get('suggestion', 'Keep going in your direction.')"),
])


# ============================================================
# CONSTANTS.PY
# ============================================================
print("=== Translating constants.py ===")
translate_file('/app/backend/constants.py', [
    ("'cognitive': 'קוגניטיבי', 'emotional': 'רגשי', 'physical': 'פיזי',",
     "'cognitive': 'Cognitive', 'emotional': 'Emotional', 'physical': 'Physical',"),
    ("'personal': 'אישי', 'social': 'חברתי', 'drives': 'דחפים'",
     "'personal': 'Personal', 'social': 'Social', 'drives': 'Drives'"),
    ("'internal': 'פנימי', 'external': 'חיצוני', 'collective': 'קולקטיבי'",
     "'internal': 'Internal', 'external': 'External', 'collective': 'Collective'"),
    # Contribution
    ("'label_he': 'תרומה', 'symbol': 'נתינה',",
     "'label_he': 'Contribution', 'symbol': 'Giving',"),
    ("'explanation_he': 'כיוון התרומה מבטא את הרצון לתת, לעזור ולהשפיע על הסביבה. זהו הכוח שמחבר בין הפרט לקולקטיב.',",
     "'explanation_he': 'The Contribution direction expresses the desire to give, help, and impact your surroundings. It is the force that connects the individual to the collective.',"),
    ("'meaning_he': 'כשאתה פועל בכיוון התרומה, אתה מחזק את השדה הקולקטיבי ויוצר ערך שחורג מגבולות העצמי.',",
     "'meaning_he': 'When you act in the Contribution direction, you strengthen the collective field and create value beyond the boundaries of self.',"),
    ("'symbolic_meaning_he': 'הסמל של התרומה הוא הנתינה — הזרימה כלפי חוץ. כמו נהר שמזין את השדות סביבו, פעולת התרומה יוצרת ערך שמתפשט מעבר לגבולות האדם הפועל.',",
     "'symbolic_meaning_he': 'The symbol of Contribution is giving — an outward flow. Like a river nourishing the fields around it, Contribution creates value that spreads beyond the individual.',"),
    ("'behavior_example_he': 'לעזור לחבר שנמצא במשבר, להתנדב בקהילה, לשתף ידע עם עמית, להקשיב למישהו שצריך אוזן קשבת.',",
     "'behavior_example_he': 'Helping a friend in crisis, volunteering in the community, sharing knowledge with a colleague, listening to someone who needs a caring ear.',"),
    ("'field_effect_he': 'פעולות תרומה מחזקות את הקשר בין חלקי השדה. ככל שיותר אנשים פועלים בכיוון התרומה, השדה הקולקטיבי הופך מחובר ויציב יותר.'",
     "'field_effect_he': 'Contribution actions strengthen the bond between parts of the field. The more people act in the Contribution direction, the more connected and stable the collective field becomes.'"),
    # Recovery
    ("'label_he': 'התאוששות', 'symbol': 'שיקום',",
     "'label_he': 'Recovery', 'symbol': 'Restoration',"),
    ("'explanation_he': 'כיוון ההתאוששות מבטא את הצורך בהטענה, מנוחה ושיקום פנימי. זהו הכוח שמאפשר לחזור לאיזון.',",
     "'explanation_he': 'The Recovery direction expresses the need for recharging, rest, and inner restoration. It is the force that enables a return to balance.',"),
    ("'meaning_he': 'כשאתה פועל בכיוון ההתאוששות, אתה בונה את הבסיס הפנימי שממנו כל פעולה אחרת מתחילה.',",
     "'meaning_he': 'When you act in the Recovery direction, you build the inner foundation from which every other action begins.',"),
    ("'symbolic_meaning_he': 'הסמל של ההתאוששות הוא השיקום — התנועה פנימה. כמו עץ שמפיל עלים בסתיו כדי לשמור אנרגיה לאביב, ההתאוששות היא ההכנה לצמיחה הבאה.',",
     "'symbolic_meaning_he': 'The symbol of Recovery is restoration — the inward movement. Like a tree shedding leaves in autumn to conserve energy for spring, Recovery is the preparation for the next growth.',"),
    ("'behavior_example_he': 'לקחת הפסקה אחרי יום עמוס, לישון כמו שצריך, לצאת לטיול בטבע, לשתות כוס תה בשקט, לסרב לבקשה כשאין כוח.',",
     "'behavior_example_he': 'Taking a break after a busy day, getting proper sleep, going for a nature walk, quietly drinking a cup of tea, saying no when you are out of energy.',"),
    ("'field_effect_he': 'פעולות התאוששות מייצבות את הבסיס של השדה. כשאנשים מאפשרים לעצמם התאוששות, הם חוזרים לשדה עם יותר אנרגיה ובהירות.'",
     "'field_effect_he': 'Recovery actions stabilize the foundation of the field. When people allow themselves recovery, they return to the field with more energy and clarity.'"),
    # Order
    ("'label_he': 'סדר', 'symbol': 'מבנה',",
     "'label_he': 'Order', 'symbol': 'Structure',"),
    ("'explanation_he': 'כיוון הסדר מבטא את הרצון לארגן, לתכנן וליצור מבנה. זהו הכוח שמביא יציבות ובהירות.',",
     "'explanation_he': 'The Order direction expresses the desire to organize, plan, and create structure. It is the force that brings stability and clarity.',"),
    ("'meaning_he': 'כשאתה פועל בכיוון הסדר, אתה יוצר מסגרת שמאפשרת לכל הכיוונים האחרים לפעול בצורה יעילה.',",
     "'meaning_he': 'When you act in the Order direction, you create a framework that allows all other directions to function effectively.',"),
    ("'symbolic_meaning_he': 'הסמל של הסדר הוא המבנה — השלד שמחזיק הכול. כמו אדריכל שמתכנן בניין, הסדר יוצר את התשתית שעליה כל דבר אחר נבנה.',",
     "'symbolic_meaning_he': 'The symbol of Order is structure — the skeleton that holds everything together. Like an architect designing a building, Order creates the infrastructure on which everything else is built.',"),
    ("'behavior_example_he': 'לארגן את הלוח זמנים, לתכנן את השבוע, לסדר את חדר העבודה, לכתוב רשימת משימות, להגדיר יעדים ברורים.',",
     "'behavior_example_he': 'Organizing your schedule, planning your week, tidying your workspace, writing a to-do list, setting clear goals.',"),
    ("'field_effect_he': 'פעולות סדר יוצרות מבנה בשדה הקולקטיבי. כשיש סדר, כל הכיוונים האחרים פועלים בצורה יעילה יותר — השדה הופך ברור וניתן לניווט.'",
     "'field_effect_he': 'Order actions create structure in the collective field. When there is order, all other directions operate more effectively — the field becomes clear and navigable.'"),
    # Exploration
    ("'label_he': 'חקירה', 'symbol': 'גילוי',",
     "'label_he': 'Exploration', 'symbol': 'Discovery',"),
    ("'explanation_he': 'כיוון החקירה מבטא את הסקרנות, הרצון ללמוד ולגלות. זהו הכוח שמניע שינוי וצמיחה.',",
     "'explanation_he': 'The Exploration direction expresses curiosity, the desire to learn and discover. It is the force that drives change and growth.',"),
    ("'meaning_he': 'כשאתה פועל בכיוון החקירה, אתה פותח דלתות חדשות ומרחיב את גבולות ההכרה.',",
     "'meaning_he': 'When you act in the Exploration direction, you open new doors and expand the boundaries of awareness.',"),
    ("'symbolic_meaning_he': 'הסמל של החקירה הוא הגילוי — התנועה קדימה לעבר הלא נודע. כמו חוקר שמפליג לים הפתוח, החקירה דורשת אומץ ופתיחות.',",
     "'symbolic_meaning_he': 'The symbol of Exploration is discovery — the forward movement toward the unknown. Like an explorer setting sail for the open sea, Exploration requires courage and openness.',"),
    ("'behavior_example_he': 'ללמוד נושא חדש, לנסות גישה שונה לבעיה, לשאול שאלות קשות, לצאת מאזור הנוחות, לפגוש אנשים חדשים.',",
     "'behavior_example_he': 'Learning a new subject, trying a different approach to a problem, asking tough questions, stepping out of your comfort zone, meeting new people.',"),
    ("'field_effect_he': 'פעולות חקירה מרחיבות את השדה. הן מוסיפות ממדים חדשים ואפשרויות שלא היו קיימות קודם — השדה הופך דינמי ומלא פוטנציאל.'",
     "'field_effect_he': 'Exploration actions expand the field. They add new dimensions and possibilities that did not exist before — the field becomes dynamic and full of potential.'"),
])


# ============================================================
# SERVICES/HELPERS.PY
# ============================================================
print("=== Translating services/helpers.py ===")
translate_file('/app/backend/services/helpers.py', [
    ("'contribution': 'תרומה',\n         'recovery': 'התאוששות',\n         'order': 'סדר',\n         'harm': 'נזק',\n         'avoidance': 'הימנעות'",
     "'contribution': 'Contribution',\n         'recovery': 'Recovery',\n         'order': 'Order',\n         'harm': 'Harm',\n         'avoidance': 'Avoidance'"),
    # Replay insights
    ('f"המסלול החלופי הנבדק ביותר הוא {tag_labels.get(top_alt[0], top_alt[0])} ({percentage}% מההפעלות החוזרות)."',
     'f"The most explored alternative path is {tag_labels.get(top_alt[0], top_alt[0])} ({percentage}% of replays)."'),
    ('f"אתה נוטה לבדוק מסלולי {to_label} כשאתה בוחר ב{from_label}. "',
     'f"You tend to explore {to_label} paths when choosing {from_label}. "'),
    ('f"זה מצביע על מודעות לחלופות חיוביות ({count} פעמים)."',
     'f"This indicates awareness of positive alternatives ({count} times)."'),
    ('f"הדפוס הנפוץ ביותר: מ{from_label} ל{to_label} ({count} פעמים)."',
     'f"Most common pattern: from {from_label} to {to_label} ({count} times)."'),
    ('f"אתה מרבה לבדוק חלופות להחלטות מסוג {tag_labels.get(top_orig[0], top_orig[0])}."',
     'f"You frequently explore alternatives for {tag_labels.get(top_orig[0], top_orig[0])} decisions."'),
    ('f"נקודה עיוורת: מעולם לא בדקת מסלול {to_label} אחרי החלטת {from_label}."',
     'f"Blind spot: you have never explored a {to_label} path after a {from_label} decision."'),
    ('"יש לך נטייה לבדוק מסלולי התאוששות - ייתכן שאתה מרגיש צורך במנוחה שלא מתממש."',
     '"You tend to explore Recovery paths — you may feel a need for rest that is not being met."'),
    ('"אתה נמנע מלבדוק מסלולי נזק בהפעלות חוזרות - סימן חיובי למודעות ערכית."',
     '"You avoid exploring Harm paths in replays — a positive sign of value awareness."'),
    # Globe narrative
    ("return 'השדה שקט. ממתין לפעולה ראשונה.'",
     "return 'The field is quiet. Waiting for the first action.'"),
    ("if momentum == 'עולה' and dominant_pct > 0.4:",
     "if momentum == 'rising' and dominant_pct > 0.4:"),
    ("f'השדה נוטה ל{dir_he} — התנועה מתחזקת',",
     "f'The field leans toward {dir_he} — momentum is building',"),
    ("f'גל של {dir_he} עובר בשדה',",
     "f'A wave of {dir_he} is moving through the field',"),
    ("f'פעילות {dir_he} עולה ברחבי השדה',",
     "f'{dir_he} activity is rising across the field',"),
    ("elif momentum == 'יורד':",
     "elif momentum == 'falling':"),
    ("f'השדה נרגע — {dir_he} עדיין מוביל',",
     "f'The field is calming — {dir_he} still leads',"),
    ("f'התנועה מאטה, {dir_he} שומר על נוכחות',",
     "f'Movement is slowing, {dir_he} maintains presence',"),
    ("f'השדה שוקע לשקט, עם נטייה ל{dir_he}',",
     "f'The field is settling into stillness, leaning toward {dir_he}',"),
    ("f'השדה נוטה בבירור ל{dir_he}',",
     "f'The field clearly leans toward {dir_he}',"),
    ("f'{dir_he} שולט בשדה היום',",
     "f'{dir_he} dominates the field today',"),
    ("f'כוח ה{dir_he} דומיננטי בשדה',",
     "f'{dir_he} force is dominant in the field',"),
    ("f'השדה מתפצל בין {dir_he} ל{secondary_he}',",
     "f'The field is split between {dir_he} and {secondary_he}',"),
    ("f'מתח בין {dir_he} ל{secondary_he} — השדה בתנועה',",
     "f'Tension between {dir_he} and {secondary_he} — the field is in motion',"),
    ("f'{dir_he} ו{secondary_he} מושכים את השדה לכיוונים שונים',",
     "f'{dir_he} and {secondary_he} pull the field in different directions',"),
    ("f'{dir_he} מתייצב במספר אזורים',",
     "f'{dir_he} is stabilizing across multiple regions',"),
    ("f'השדה פעיל ברחבי העולם — {dir_he} מוביל',",
     "f'The field is active worldwide — {dir_he} leads',"),
    ("f'פעילות {dir_he} מתפשטת בין אזורים',",
     "f'{dir_he} activity is spreading across regions',"),
    ("f'השדה נוטה ל{dir_he} היום',",
     "f'The field leans toward {dir_he} today',"),
    ("f'תנועת {dir_he} נמשכת בשדה',",
     "f'{dir_he} movement continues in the field',"),
    ("f'השדה חי — {dir_he} מוביל את הכיוון',",
     "f'The field is alive — {dir_he} leads the way',"),
])


print("\n=== All small/medium files translated! ===")
print("=== Now translating orientation.py (largest file) ===")

# ============================================================
# ORIENTATION.PY - This is the biggest file with hundreds of Hebrew strings
# ============================================================

# Read the entire file
with open('/app/backend/routes/orientation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Direction labels (appears many times throughout the file)
# Each occurrence uses different indentation, so we replace the Hebrew values
replacements = [
    # Direction labels - common pattern throughout
    ("'recovery': 'התאוששות',", "'recovery': 'Recovery',"),
    ("'order': 'סדר',", "'order': 'Order',"),
    ("'contribution': 'תרומה',", "'contribution': 'Contribution',"),
    ("'exploration': 'חקירה'", "'exploration': 'Exploration'"),
    ("'harm': 'נזק',", "'harm': 'Harm',"),
    ("'avoidance': 'הימנעות'", "'avoidance': 'Avoidance'"),
    ("'contribution': 'תרומה'", "'contribution': 'Contribution'"),
    ("'recovery': 'התאוששות'", "'recovery': 'Recovery'"),
    ("'order': 'סדר'", "'order': 'Order'"),
    ("'harm': 'נזק'", "'harm': 'Harm'"),
    
    # Field today insight
    ('insight = f"היום השדה נוטה לכיוון {direction_labels.get(dominant_direction, dominant_direction)}."',
     'insight = f"Today the field leans toward {direction_labels.get(dominant_direction, dominant_direction)}."'),
    ('insight = "השדה מאוזן היום."',
     'insight = "The field is balanced today."'),
    
    # Momentum insights
    ('momentum_insight = "השדה הקולקטיבי מתייצב ונע לכיוון איזון חיובי."',
     'momentum_insight = "The collective field is stabilizing and moving toward positive balance."'),
    ('momentum_insight = "השדה הקולקטיבי נסחף מהאיזון בימים האחרונים."',
     'momentum_insight = "The collective field has been drifting from balance in recent days."'),
    ('momentum_insight = f"השדה הקולקטיבי נע בהדרגה לכיוון {direction_labels.get(momentum_direction, momentum_direction)}."',
     'momentum_insight = f"The collective field is gradually moving toward {direction_labels.get(momentum_direction, momentum_direction)}."'),
    ('momentum_insight = "השדה הקולקטיבי יציב ומאוזן."',
     'momentum_insight = "The collective field is stable and balanced."'),
    ('momentum_insight = "אין מספיק נתונים לחישוב מומנטום."',
     'momentum_insight = "Not enough data to calculate momentum."'),
    
    # Field insights
    ('field_insight = f"השדה הקולקטיבי מראה נטייה חזקה ל{direction_labels[dominant_direction]} ומתייצב."',
     'field_insight = f"The collective field shows a strong leaning toward {direction_labels[dominant_direction]} and is stabilizing."'),
    ('field_insight = f"השדה הקולקטיבי נוטה ל{direction_labels[dominant_direction]} אך יש סחף מהאיזון."',
     'field_insight = f"The collective field leans toward {direction_labels[dominant_direction]} but there is drift from balance."'),
    ('field_insight = f"השדה הקולקטיבי נוטה ל{direction_labels[dominant_direction]} ומשנה כיוון."',
     'field_insight = f"The collective field leans toward {direction_labels[dominant_direction]} and is shifting direction."'),
    ('field_insight = f"השדה הקולקטיבי מראה נטייה ל{direction_labels[dominant_direction]}."',
     'field_insight = f"The collective field shows a leaning toward {direction_labels[dominant_direction]}."'),
    
    # Week labels
    ("'label': f'שבוע {4 - i}' if i > 0 else 'השבוע'",
     "'label': f'Week {4 - i}' if i > 0 else 'This week'"),
    
    # Trend insights
    ('trend_insight = "השדה הקולקטיבי מתייצב בשבועות האחרונים."',
     'trend_insight = "The collective field has been stabilizing in recent weeks."'),
    ('trend_insight = "השדה הקולקטיבי נסחף מהאיזון בשבועות האחרונים."',
     'trend_insight = "The collective field has been drifting from balance in recent weeks."'),
    ('trend_insight = f"השדה הקולקטיבי נע בהדרגה לכיוון {direction_labels.get(consistent_direction, consistent_direction)} בשבועות האחרונים."',
     'trend_insight = f"The collective field has been gradually moving toward {direction_labels.get(consistent_direction, consistent_direction)} in recent weeks."'),
    ('trend_insight = "השדה הקולקטיבי יציב ומאוזן בשבועות האחרונים."',
     'trend_insight = "The collective field has been stable and balanced in recent weeks."'),
    ('trend_insight = "השדה הקולקטיבי נע לכיוון תרומה וסדר בשבועות האחרונים."',
     'trend_insight = "The collective field has been moving toward Contribution and Order in recent weeks."'),
    ('trend_insight = "השדה הקולקטיבי נע לכיוון סדר בשבועות האחרונים."',
     'trend_insight = "The collective field has been moving toward Order in recent weeks."'),
    ('trend_insight = "השדה הקולקטיבי נע לכיוון חקירה בשבועות האחרונים."',
     'trend_insight = "The collective field has been moving toward Exploration in recent weeks."'),
    ('trend_insight = "השדה הקולקטיבי נע לכיוון התאוששות בשבועות האחרונים."',
     'trend_insight = "The collective field has been moving toward Recovery in recent weeks."'),
    ('trend_insight = "אין מספיק נתונים היסטוריים לזיהוי מגמה."',
     'trend_insight = "Not enough historical data to identify a trend."'),
    
    # Comparison insights
    ('comparison_insight="אין מספיק נתונים השבוע. בצע פעולות כדי להשוות את עצמך לאחרים."',
     'comparison_insight="Not enough data this week. Perform actions to compare yourself with others."'),
    ('rank_label = "עליון 10%"', 'rank_label = "Top 10%"'),
    ('rank_label = "עליון 25%"', 'rank_label = "Top 25%"'),
    ('rank_label = "מעל הממוצע"', 'rank_label = "Above average"'),
    ('rank_label = "פעיל"', 'rank_label = "Active"'),
    ('comparison_insight = f"אתה בין ה-{100 - int(dominant_percentile)}% המובילים במיקוד על {direction_labels.get(dominant_direction, dominant_direction)} השבוע."',
     'comparison_insight = f"You are among the top {100 - int(dominant_percentile)}% focused on {direction_labels.get(dominant_direction, dominant_direction)} this week."'),
    ('comparison_insight = f"אתה מעל הממוצע במיקוד על {direction_labels.get(dominant_direction, dominant_direction)}."',
     'comparison_insight = f"You are above average in focus on {direction_labels.get(dominant_direction, dominant_direction)}."'),
    ('comparison_insight = f"הכיוון המוביל שלך השבוע הוא {direction_labels.get(dominant_direction, dominant_direction)}."',
     'comparison_insight = f"Your leading direction this week is {direction_labels.get(dominant_direction, dominant_direction)}."'),
    ('comparison_insight = "המיקוד שלך מאוזן בין הכיוונים. זהו סימן טוב לאיזון."',
     'comparison_insight = "Your focus is balanced across directions. This is a good sign of equilibrium."'),
    
    # Decision path docstring (comments, not user-facing but good to translate)
    ('- harm → recovery: "יצאת מהמסלול. הצעד הבא: התאוששות."',
     '- harm → recovery: "You went off track. Next step: Recovery."'),
    ('- avoidance → order: "נסחפת להימנעות. הצעד הבא: ליצור מבנה."',
     '- avoidance → order: "You drifted into avoidance. Next step: Create structure."'),
    ('- isolation → contribution: "מיקוד עצמי גבוה. הצעד הבא: לתרום לאחרים."',
     '- isolation → contribution: "High self-focus. Next step: Contribute to others."'),
    ('- rigidity → exploration: "יש קיפאון. הצעד הבא: לפתוח לחדש."',
     '- rigidity → exploration: "There is stagnation. Next step: Open to new things."'),
    
    # Recovery micro-actions
    ('"קח הפסקה של 5 דקות ונשום עמוק.",', '"Take a 5-minute break and breathe deeply.",'),
    ('"שתה כוס מים ושב בשקט לרגע.",', '"Drink a glass of water and sit quietly for a moment.",'),
    ('"צא להליכה קצרה של 10 דקות.",', '"Go for a short 10-minute walk.",'),
    ('"כתוב 3 דברים שאתה אסיר תודה עליהם.",', '"Write down 3 things you are grateful for.",'),
    ('"האזן לשיר אחד שאתה אוהב."', '"Listen to one song you love."'),
    
    # Order micro-actions
    ('"בחר משימה קטנה אחת והשלם אותה עכשיו.",', '"Pick one small task and complete it now.",'),
    ('"סדר פינה אחת בחדר שלך.",', '"Tidy up one corner of your room.",'),
    ('"כתוב רשימה של 3 דברים לעשות היום.",', '"Write a list of 3 things to do today.",'),
    ('"קבע זמן קבוע למשימה שדחית.",', '"Set a fixed time for a task you have been putting off.",'),
    ('"מחק 5 הודעות ישנות מהטלפון."', '"Delete 5 old messages from your phone."'),
    
    # Contribution micro-actions
    ('"שלח הודעה חיובית למישהו שאכפת לך ממנו.",', '"Send a positive message to someone you care about.",'),
    ('"הצע עזרה קטנה למישהו קרוב.",', '"Offer a small help to someone close to you.",'),
    ('"הקשב למישהו במשך 5 דקות בלי להפריע.",', '"Listen to someone for 5 minutes without interrupting.",'),
    ('"שתף משהו מועיל עם אחרים.",', '"Share something useful with others.",'),
    ('"תן מחמאה כנה למישהו."', '"Give a sincere compliment to someone."'),
    
    # Exploration micro-actions
    ('"נסה משהו חדש שלא עשית קודם.",', '"Try something new that you have not done before.",'),
    ('"קרא מאמר על נושא שמעניין אותך.",', '"Read an article on a topic that interests you.",'),
    ('"שאל שאלה שלא שאלת קודם.",', '"Ask a question you have not asked before.",'),
    ('"לך בדרך אחרת מהרגיל.",', '"Take a different route than usual.",'),
    ('"התחל שיחה עם מישהו חדש."', '"Start a conversation with someone new."'),
    
    # Recommended steps
    ("'harm': \"הצעד הבא: התאוששות. חזור לאיזון.\",",
     "'harm': \"Next step: Recovery. Return to balance.\","),
    ("'avoidance': \"הצעד הבא: ליצור מבנה וסדר.\",",
     "'avoidance': \"Next step: Create structure and order.\","),
    ("'isolation': \"הצעד הבא: לתרום לאחרים.\",",
     "'isolation': \"Next step: Contribute to others.\","),
    ("'rigidity': \"הצעד הבא: להיפתח לחדש.\"",
     "'rigidity': \"Next step: Open up to new things.\""),
    
    # Theory basis
    ("'harm': \"נזק → התאוששות: כשיש נזק, הדרך חזרה היא דרך התאוששות.\",",
     "'harm': \"Harm → Recovery: When there is harm, the way back is through recovery.\","),
    ("'avoidance': \"הימנעות → סדר: הימנעות מאוזנת על ידי יצירת מבנה.\",",
     "'avoidance': \"Avoidance → Order: Avoidance is balanced by creating structure.\","),
    ("'isolation': \"בידוד → תרומה: מיקוד עצמי מאוזן על ידי תרומה לאחרים.\",",
     "'isolation': \"Isolation → Contribution: Self-focus is balanced by contributing to others.\","),
    ("'rigidity': \"נוקשות → חקירה: קיפאון מאוזן על ידי פתיחות וחקירה.\"",
     "'rigidity': \"Rigidity → Exploration: Stagnation is balanced by openness and exploration.\""),
    
    # Headlines
    ("'harm': \"יצאת מהמסלול.\",",
     "'harm': \"You went off track.\","),
    ("'avoidance': \"נסחפת להימנעות.\",",
     "'avoidance': \"You drifted into avoidance.\","),
    ("'isolation': \"מיקוד עצמי גבוה.\",",
     "'isolation': \"High self-focus.\","),
    ("'rigidity': \"יש קיפאון.\",",
     "'rigidity': \"There is stagnation.\","),
    ("'positive': \"אתה על המסלול הנכון.\",",
     "'positive': \"You are on the right track.\","),
    ("'new_user': \"ברוך הבא למסע.\"",
     "'new_user': \"Welcome to the journey.\""),
    
    # New user decision path
    ('recommended_step="התחל עם פעולת התאוששות.",',
     'recommended_step="Start with a Recovery action.",'),
    ('theory_basis="התאוששות היא נקודת הפתיחה הטובה ביותר.",',
     'theory_basis="Recovery is the best starting point.",'),
    
    # Generic recommended steps
    ('recommended_step = recommended_steps.get(drift_type, "המשך קדימה.")',
     'recommended_step = recommended_steps.get(drift_type, "Keep moving forward.")'),
    ('recommended_step = f"לאיזון מלא, נסה גם {direction_labels.get(recommended_direction, recommended_direction)}."',
     'recommended_step = f"For full balance, also try {direction_labels.get(recommended_direction, recommended_direction)}."'),
    ('theory = "איזון בין הכיוונים מחזק את ההתמצאות."',
     'theory = "Balance between directions strengthens orientation."'),
    
    # Identity labels
    ("'label': 'לולאת הימנעות',", "'label': 'Avoidance loop',"),
    ("'description': 'נראה שאתה בדפוס של הימנעות. זה בסדר - זיהוי זה הצעד הראשון לשינוי.',",
     "'description': 'It seems you are in an avoidance pattern. That is okay — recognizing it is the first step to change.',"),
    ("'insight': 'הימנעות היא תגובה טבעית. הצעד הבא הוא ליצור מבנה קטן.'",
     "'insight': 'Avoidance is a natural response. The next step is to create a small structure.'"),
    
    ("'label': 'ממוקד בהתאוששות',", "'label': 'Focused on Recovery',"),
    ("'description': 'אתה בתהליך התאוששות פעיל. זה זמן חשוב לריפוי ואיזון.',",
     "'description': 'You are in an active recovery process. This is an important time for healing and balance.',"),
    ("'insight': 'התאוששות היא בסיס חיוני. כשתרגיש מוכן, נסה גם פעולות סדר.'",
     "'insight': 'Recovery is an essential foundation. When you feel ready, try some Order actions too.'"),
    
    ("'label': 'בונה סדר',", "'label': 'Building Order',"),
    ("'description': 'אתה יוצר מבנה וסדר בחיים שלך. זה סימן של התקדמות.',",
     "'description': 'You are creating structure and order in your life. This is a sign of progress.',"),
    ("'insight': 'סדר מאפשר יציבות. השלב הבא יכול להיות תרומה לאחרים.'",
     "'insight': 'Order enables stability. The next step could be contributing to others.'"),
    
    ("'label': 'מכוון לתרומה',", "'label': 'Oriented toward Contribution',"),
    ("'description': 'אתה ממוקד בתרומה לאחרים. זה מעשיר אותך ואת הסביבה.',",
     "'description': 'You are focused on contributing to others. This enriches you and your surroundings.',"),
    ("'insight': 'תרומה מחברת אותך לאחרים. זכור גם לדאוג לעצמך.'",
     "'insight': 'Contribution connects you to others. Remember to take care of yourself too.'"),
    
    ("'label': 'מונע מחקירה',", "'label': 'Driven by Exploration',"),
    ("'description': 'אתה פתוח לחדש ולחקירה. זה מרחיב את האופקים שלך.',",
     "'description': 'You are open to new things and exploration. This broadens your horizons.',"),
    ("'insight': 'חקירה מביאה צמיחה. לפעמים כדאי גם לעצור וליצור סדר.'",
     "'insight': 'Exploration brings growth. Sometimes it is also worth pausing to create order.'"),
    
    ("'label': 'מעבר מהתאוששות לתרומה',", "'label': 'Transitioning from Recovery to Contribution',"),
    ("'description': 'אתה עובר מהתאוששות לתרומה. זה מסע חיובי מאוד.',",
     "'description': 'You are moving from Recovery to Contribution. This is a very positive journey.',"),
    ("'insight': 'המעבר הזה מראה התקדמות משמעותית. המשך בקצב שלך.'",
     "'insight': 'This transition shows significant progress. Continue at your own pace.'"),
    
    ("'label': 'סחף מסדר',", "'label': 'Drifting from Order',"),
    ("'description': 'היית ממוקד בסדר אבל יש סחף. זה הזדמנות לבדוק מה השתנה.',",
     "'description': 'You were focused on Order but there is drift. This is an opportunity to check what has changed.',"),
    ("'insight': 'סחף הוא טבעי. חזור ליצור מבנה קטן אחד.'",
     "'insight': 'Drift is natural. Go back and create one small structure.'"),
    
    ("'label': 'מאוזן',", "'label': 'Balanced',"),
    ("'description': 'אתה מפזר את הפעולות שלך בין הכיוונים. זה מצב בריא.',",
     "'description': 'You are spreading your actions across directions. This is a healthy state.',"),
    ("'insight': 'איזון הוא מטרה טובה. המשך לשמור על מגוון.'",
     "'insight': 'Balance is a good goal. Keep maintaining variety.'"),
    
    ("'label': 'מתחיל מסע',", "'label': 'Starting the journey',"),
    ("'description': 'ברוך הבא! אתה בתחילת המסע שלך.',",
     "'description': 'Welcome! You are at the beginning of your journey.',"),
    ("'insight': 'כל מסע מתחיל בצעד אחד. התחל עם פעולת התאוששות.'",
     "'insight': 'Every journey begins with a single step. Start with a Recovery action.'"),
    
    # Daily orientation questions - ORDER
    ('"מה הדבר הקטן ביותר שאתה יכול לעשות עכשיו כדי ליצור סדר?",',
     '"What is the smallest thing you can do right now to create order?",'),
    ('"איזו משימה קטנה אתה יכול להשלים ב-5 דקות הקרובות?",',
     '"What small task can you complete in the next 5 minutes?",'),
    ('"מה הצעד הראשון שתוכל לעשות היום לקראת משהו שדחית?"',
     '"What is the first step you can take today toward something you have been putting off?"'),
    
    # Daily orientation questions - CONTRIBUTION
    ('"מה הדבר הקטן שאתה יכול לעשות היום עבור מישהו אחר?",',
     '"What small thing can you do today for someone else?",'),
    ('"איך תוכל לתרום למישהו קרוב אליך היום?",',
     '"How can you contribute to someone close to you today?",'),
    ('"מה תוכל לשתף עם אחרים מהניסיון שלך?"',
     '"What can you share with others from your experience?"'),
    
    # Daily orientation questions - EXPLORATION
    ('"מה משהו חדש שתוכל לנסות היום?",',
     '"What is something new you can try today?",'),
    ('"איזו שאלה חדשה תוכל לשאול היום?",',
     '"What new question can you ask today?",'),
    ('"מה הדבר שתמיד רצית לחקור אבל לא הספקת?"',
     '"What have you always wanted to explore but never had the time for?"'),
    
    # Daily orientation questions - RECOVERY
    ('"מה תעשה היום כדי לדאוג לעצמך?",',
     '"What will you do today to take care of yourself?",'),
    ('"איזו הפסקה קטנה מגיעה לך היום?",',
     '"What small break do you deserve today?",'),
    ('"מה יעזור לך להתאושש ולהטען מחדש?"',
     '"What will help you recover and recharge?"'),
    
    # Daily orientation questions - DRIFT_ORDER
    ('"איזו משימה תוכל לסיים היום כדי ליצור סדר?",',
     '"What task can you finish today to create order?",'),
    ('"מה הדבר שצריך ארגון בחיים שלך עכשיו?",',
     '"What needs organizing in your life right now?",'),
    ('"איך תוכל ליצור מבנה קטן שיתמוך בך?"',
     '"How can you create a small structure to support yourself?"'),
    
    # Daily orientation questions - DRIFT_CONTRIBUTION
    ('"מה הצעד הבא שתעשה היום בכיוון של תרומה?",',
     '"What is the next step you will take today toward contribution?",'),
    ('"איך תוכל להמשיך את המומנטום החיובי שלך?",',
     '"How can you continue your positive momentum?",'),
    ('"מה תוכל לעשות היום שירחיב את המעגל שלך?"',
     '"What can you do today that will expand your circle?"'),
    
    # Daily orientation questions - DRIFT_FROM_ORDER
    ('"מה המבנה הקטן שתוכל ליצור מחדש היום?",',
     '"What small structure can you recreate today?",'),
    ('"איזו הרגל טובה תוכל לחזור אליה?",',
     '"What good habit can you return to?",'),
    ('"מה יעזור לך להרגיש יותר מאורגן?"',
     '"What will help you feel more organized?"'),
    
    # Daily orientation questions - BALANCED
    ('"מה הכיוון שהכי מושך אותך היום?",',
     '"What direction appeals to you most today?",'),
    ('"באיזה תחום תרצה להתמקד היום?",',
     '"What area would you like to focus on today?",'),
    ('"מה יהפוך את היום הזה למשמעותי עבורך?"',
     '"What would make this day meaningful for you?"'),
    
    # Daily orientation questions - NEW_USER
    ('"מה הדבר הראשון שתעשה היום לטובת עצמך?",',
     '"What is the first thing you will do today for yourself?",'),
    ('"איך תרצה להתחיל את המסע שלך?",',
     '"How would you like to start your journey?",'),
    ('"מה יגרום לך להרגיש טוב היום?"',
     '"What will make you feel good today?"'),
    
    # Micro-suggestions - body/order
    ('"עשה פעולה פיזית קטנה שמסדרת משהו סביבך.",',
     '"Do a small physical action that organizes something around you.",'),
    ('"הזז את הגוף היום — אפילו הליכה קצרה.",',
     '"Move your body today — even a short walk.",'),
    ('"סדר פינה אחת בסביבה שלך.",',
     '"Tidy up one corner of your environment.",'),
    ('"עשה משהו מעשי שדחית."',
     '"Do something practical that you have been putting off."'),
    
    # Micro-suggestions - heart/contribution
    ('"שלח מילה טובה למישהו שלא ציפה לזה.",',
     '"Send a kind word to someone who does not expect it.",'),
    ('"הקשב למישהו היום — באמת הקשב.",',
     '"Listen to someone today — really listen.",'),
    ('"עשה משהו קטן עבור מישהו קרוב.",',
     '"Do something small for someone close to you.",'),
    ('"תן לעצמך רגע של חמלה היום."',
     '"Give yourself a moment of compassion today."'),
    
    # Micro-suggestions - head/exploration
    ('"מצא דבר אחד חדש שלא שמת לב אליו קודם.",',
     '"Find one new thing you had not noticed before.",'),
    ('"ארגן רעיון אחד שמסתובב לך בראש.",',
     '"Organize one idea that has been on your mind.",'),
    ('"למד משהו קטן שלא ידעת.",',
     '"Learn something small that you did not know.",'),
    ('"קבל החלטה אחת שדחית."',
     '"Make one decision you have been putting off."'),
    
    # Daily question completion
    ("'action_text': f\"השלמתי את השאלה היומית: {question.get('question_he', '')}\",",
     "'action_text': f\"Completed the daily question: {question.get('question', question.get('question_he', ''))}\","),
    
    # Direction impact message
    ('impact_message = f"הפעולה שלך חיזקה היום את שדה ה{direction_labels[suggested_direction]}"',
     'impact_message = f"Your action today strengthened the {direction_labels[suggested_direction]} field"'),
    
    # Invite reward message
    ('"message_he": f"הפעולה הראשונה שלך העניקה נקודת ערך ל{ANONYMOUS_ALIASES[inviter_alias_idx]}"',
     '"message": f"Your first action granted a value point to {ANONYMOUS_ALIASES[inviter_alias_idx]}"'),
    
    # Position insights
    ('insights=["אין מספיק נתונים. בצע פעולות כדי לראות את המיקום שלך."]',
     'insights=["Not enough data. Perform actions to see your position."]'),
    
    # Field position insights
    ('insights.append("אתה מיושר היטב עם השדה הקולקטיבי.")',
     'insights.append("You are well aligned with the collective field.")'),
    ('insights.append("המיקום שלך קרוב למרכז השדה הקולקטיבי.")',
     'insights.append("Your position is close to the center of the collective field.")'),
    ('insights.append("אתה רחוק ממרכז השדה הקולקטיבי.")',
     'insights.append("You are far from the center of the collective field.")'),
    ('insights.append("יש מרחק בין המיקום שלך לבין מרכז השדה הקולקטיבי.")',
     'insights.append("There is a distance between your position and the center of the collective field.")'),
    
    ('insights.append("נראה סחף לכיוון כאוס. מומלץ לשקול פעולת התאוששות או סדר.")',
     'insights.append("There appears to be drift toward chaos. Consider a Recovery or Order action.")'),
    ('insights.append("יש נטייה לבידוד. כדאי לשקול פעולת תרומה.")',
     'insights.append("There is a tendency toward isolation. Consider a Contribution action.")'),
    ('insights.append("אתה מתייצב לכיוון סדר.")',
     'insights.append("You are stabilizing toward Order.")'),
    ('insights.append("יש תנועה חיובית לכיוון תרומה.")',
     'insights.append("There is positive movement toward Contribution.")'),
    ('insights.append("אתה במצב התאוששות.")',
     'insights.append("You are in a Recovery state.")'),
    
    ('insights.append(f"המומנטום שלך חיובי לכיוון {direction_labels.get(momentum_direction, momentum_direction)}.")',
     'insights.append(f"Your momentum is positive toward {direction_labels.get(momentum_direction, momentum_direction)}.")'),
    ('insights.append("המומנטום מראה סחף מהאיזון.")',
     'insights.append("Momentum shows drift from balance.")'),
    
    # Pattern insights
    ('insight="אין מספיק נתונים לזיהוי דפוס. המשך לבצע פעולות."',
     'insight="Not enough data to identify a pattern. Keep performing actions."'),
    ('insight = "זוהה סחף לכיוון נזק. מומלץ לאזן עם התאוששות."',
     'insight = "Drift toward Harm detected. Balance with Recovery is recommended."'),
    ('insight = "זוהה סחף לכיוון הימנעות. מומלץ לאזן עם סדר."',
     'insight = "Drift toward Avoidance detected. Balance with Order is recommended."'),
    ('insight = "זוהה דפוס של בידוד (סדר ללא תרומה). מומלץ לפתוח לכיוון תרומה."',
     'insight = "Isolation pattern detected (Order without Contribution). Opening toward Contribution is recommended."'),
    ('insight = "נראה דפוס של התייצבות חיובית. המשך בכיוון זה."',
     'insight = "Positive stabilization pattern detected. Keep going in this direction."'),
    ('insight = "יש תנועה חיובית לכיוון תרומה."',
     'insight = "There is positive movement toward Contribution."'),
    ('insight = "הדפוס הנוכחי מאוזן יחסית."',
     'insight = "The current pattern is relatively balanced."'),
    
    # Weekly insight
    ('insight_he = "אין מספיק נתונים השבוע. התחל עם פעולה אחת."',
     'insight_he = "Not enough data this week. Start with one action."'),
    ('insight_he = "שבוע שקט. כדאי להוסיף עוד פעולות."',
     'insight_he = "A quiet week. Consider adding more actions."'),
    ('insight_he = "שבוע מאוזן! פעלת במגוון כיוונים."',
     'insight_he = "A balanced week! You acted in diverse directions."'),
    ('insight_he = f"השבוע התמקדת מאוד ב{label}. כדאי לשקול גיוון."',
     'insight_he = f"This week you were very focused on {label}. Consider diversifying."'),
    ('insight_he = f"השבוע עברת מהתאוששות לפעולה. כיוון מוביל: {label}."',
     'insight_he = f"This week you moved from recovery to action. Leading direction: {label}."'),
    ('insight_he = f"הכיוון המוביל שלך השבוע: {label}."',
     'insight_he = f"Your leading direction this week: {label}."'),
    
    # Orientation share
    ("orientation_label = direction_labels.get(orientation, 'איזון')",
     "orientation_label = direction_labels.get(orientation, 'Balance')"),
    ('message_he = f"היום אני באוריינטציית {orientation_label}"',
     'message_he = f"Today my orientation is {orientation_label}"'),
    
    # Headline
    ('headline_he = f"מדד ההתמצאות היום: {label} מובילה"',
     'headline_he = f"Orientation index today: {label} leads"'),
    ('headline_he += f" (אתמול: {yesterday_label})"',
     'headline_he += f" (yesterday: {yesterday_label})"'),
    ('headline_he = "מדד ההתמצאות היום: מאוזן"',
     'headline_he = "Orientation index today: Balanced"'),
    
    # Daily missions
    ("'mission_he': 'משימת היום: תרומה',",
     "'mission_he': 'Mission of the day: Contribution',"),
    ("'description_he': 'עשה פעולה קטנה שתעזור למישהו אחר היום'",
     "'description_he': 'Do a small action that will help someone else today'"),
    ("'mission_he': 'משימת היום: התאוששות',",
     "'mission_he': 'Mission of the day: Recovery',"),
    ("'description_he': 'קח רגע של מנוחה והטענה עצמית היום'",
     "'description_he': 'Take a moment of rest and self-recharging today'"),
    ("'mission_he': 'משימת היום: סדר',",
     "'mission_he': 'Mission of the day: Order',"),
    ("'description_he': 'ארגן דבר אחד קטן בסביבה שלך היום'",
     "'description_he': 'Organize one small thing in your environment today'"),
    ("'mission_he': 'משימת היום: חקירה',",
     "'mission_he': 'Mission of the day: Exploration',"),
    ("'description_he': 'נסה משהו חדש או למד דבר אחד חדש היום'",
     "'description_he': 'Try something new or learn one new thing today'"),
    
    # Time strings
    ('time_str = "עכשיו"', 'time_str = "now"'),
    ('time_str = f"{minutes}ד"', 'time_str = f"{minutes}m"'),
    ('time_str = f"{hours}ש"', 'time_str = f"{hours}h"'),
    
    # Invite limit
    ('return {"success": False, "message": "הגעת למגבלת קודי ההזמנה"}',
     'return {"success": False, "message": "You have reached the invite code limit"}'),
    
    # Weekly insight (direction_labels_he)
    ("'recovery': 'התאוששות', 'order': 'סדר',\n            'contribution': 'תרומה', 'exploration': 'חקירה'",
     "'recovery': 'Recovery', 'order': 'Order',\n            'contribution': 'Contribution', 'exploration': 'Exploration'"),
    ('insight_he = "אין מספיק נתונים השבוע. נסה לענות על השאלה היומית כל יום."',
     'insight_he = "Not enough data this week. Try answering the daily question every day."'),
    ('insight_he = f"השבוע הכיוון המוביל שלך היה {direction_labels_he.get(dominant, dominant)} ({distribution[dominant]}%). המשך לפעול בכיוון זה או נסה לאזן."',
     'insight_he = f"This week your leading direction was {direction_labels_he.get(dominant, dominant)} ({distribution[dominant]}%). Keep going in this direction or try to balance."'),
    ('insight_he = "השבוע הייתה לך פעילות מאוזנת בכל הכיוונים."',
     'insight_he = "This week you had balanced activity across all directions."'),
    
    # Greeting
    ("greeting = 'בוקר טוב'", "greeting = 'Good morning'"),
    ("greeting = 'צהריים טובים'", "greeting = 'Good afternoon'"),
    ("greeting = 'ערב טוב'", "greeting = 'Good evening'"),
    
    # Evening reflection
    ('reflection_he = "היום עוד לא ביצעת פעולות. מחר יום חדש."',
     'reflection_he = "You have not performed any actions today. Tomorrow is a new day."'),
    ('reflection_he = f"היום פעלת {today_total} פעמים, בעיקר בכיוון {dir_labels.get(chosen_direction, \'\')}. ההשפעה שלך על השדה: {impact_percent}%."',
     'reflection_he = f"Today you acted {today_total} times, mostly in the {dir_labels.get(chosen_direction, \'\')} direction. Your impact on the field: {impact_percent}%."'),
    
    # Base reflection
    ('base_reflection_he = f"בחרת לפעול מה{chosen_he}, והפעולות שלך היום תאמו את הבחירה."',
     'base_reflection_he = f"You chose to act from {chosen_he}, and your actions today aligned with that choice."'),
    ('base_reflection_he = f"בחרת לפעול מה{chosen_he}, אך רוב הפעולות היום נעו לכיוון ה{used_he}."',
     'base_reflection_he = f"You chose to act from {chosen_he}, but most of your actions today leaned toward {used_he}."'),
    
    # Base definitions
    ("'name_he': 'לב',", "'name_he': 'Heart',"),
    ("'description_he': 'מאיזה מרכז אתה פועל היום?',",
     "'description_he': 'Which center are you acting from today?',"),
    ("'allocations_he': ['קשרים ומערכות יחסים', 'אמפתיה והקשבה', 'תרומה ונתינה', 'תיקון רגשי'],",
     "'allocations_he': ['Relationships and connections', 'Empathy and listening', 'Contribution and giving', 'Emotional repair'],"),
    ("'name_he': 'ראש',", "'name_he': 'Head',"),
    ("'allocations_he': ['סדר ותכנון', 'למידה וחקירה', 'קבלת החלטות', 'חשיבה אסטרטגית'],",
     "'allocations_he': ['Order and planning', 'Learning and exploration', 'Decision making', 'Strategic thinking'],"),
    ("'name_he': 'גוף',", "'name_he': 'Body',"),
    ("'allocations_he': ['תנועה ובריאות', 'פעולה מעשית', 'משמעת ומחויבות', 'סדר פיזי'],",
     "'allocations_he': ['Movement and health', 'Practical action', 'Discipline and commitment', 'Physical order'],"),
    
    # Department labels
    ("DEPT_LABELS_HE = {'heart': 'לב', 'head': 'ראש', 'body': 'גוף'}",
     "DEPT_LABELS_HE = {'heart': 'Heart', 'head': 'Head', 'body': 'Body'}"),
    
    # Globe narrative
    ('"message_he": "הפעולה שלך נוספה לשדה האנושי"',
     '"message": "Your action has been added to the human field"'),
    
    # Globe trend
    ('trend = "עולה" if recent > older else ("יורד" if recent < older else "יציב")',
     'trend = "rising" if recent > older else ("falling" if recent < older else "stable")'),
    ('trend = "חדש" if recent > 0 else "שקט"',
     'trend = "new" if recent > 0 else "quiet"'),
    
    # Summary
    ('summary_he = "עוד לא ביצעת פעולות היום. התחל את היום עם השאלה היומית."',
     'summary_he = "You have not performed any actions today. Start the day with the daily question."'),
    ('summary_he = f"היום ביצעת {today_total} פעולות. הכיוון המוביל: {dir_labels.get(dominant_dir, \'\')}. הכוח הדומיננטי: {FORCE_LABELS_HE.get(dominant_force, \'\')}."',
     'summary_he = f"Today you performed {today_total} actions. Leading direction: {dir_labels.get(dominant_dir, \'\')}. Dominant force: {FORCE_LABELS_HE.get(dominant_force, \'\')}."'),
    
    # Identity
    ("identity = dir_labels.get(dominant_dir, 'חדש') + ' מוביל' if dominant_dir else 'משתמש חדש'",
     "identity = dir_labels.get(dominant_dir, 'New') + ' leader' if dominant_dir else 'New user'"),
    
    # Country names
    ('"BR": {"lat": -14.2, "lng": -51.9, "name": "ברזיל"}', '"BR": {"lat": -14.2, "lng": -51.9, "name": "Brazil"}'),
    ('"IN": {"lat": 20.6, "lng": 78.9, "name": "הודו"}', '"IN": {"lat": 20.6, "lng": 78.9, "name": "India"}'),
    ('"DE": {"lat": 51.2, "lng": 10.5, "name": "גרמניה"}', '"DE": {"lat": 51.2, "lng": 10.5, "name": "Germany"}'),
    ('"US": {"lat": 37.1, "lng": -95.7, "name": "ארה\\"ב"}', '"US": {"lat": 37.1, "lng": -95.7, "name": "USA"}'),
    ('"JP": {"lat": 36.2, "lng": 138.3, "name": "יפן"}', '"JP": {"lat": 36.2, "lng": 138.3, "name": "Japan"}'),
    ('"NG": {"lat": 9.1, "lng": 8.7, "name": "ניגריה"}', '"NG": {"lat": 9.1, "lng": 8.7, "name": "Nigeria"}'),
    ('"IL": {"lat": 31.0, "lng": 34.9, "name": "ישראל"}', '"IL": {"lat": 31.0, "lng": 34.9, "name": "Israel"}'),
    ('"FR": {"lat": 46.2, "lng": 2.2, "name": "צרפת"}', '"FR": {"lat": 46.2, "lng": 2.2, "name": "France"}'),
    ('"AU": {"lat": -25.3, "lng": 133.8, "name": "אוסטרליה"}', '"AU": {"lat": -25.3, "lng": 133.8, "name": "Australia"}'),
    ('"KR": {"lat": 35.9, "lng": 127.8, "name": "דרום קוריאה"}', '"KR": {"lat": 35.9, "lng": 127.8, "name": "South Korea"}'),
    ('"MX": {"lat": 23.6, "lng": -102.6, "name": "מקסיקו"}', '"MX": {"lat": 23.6, "lng": -102.6, "name": "Mexico"}'),
    ('"GB": {"lat": 55.4, "lng": -3.4, "name": "בריטניה"}', '"GB": {"lat": 55.4, "lng": -3.4, "name": "United Kingdom"}'),
    ('"CA": {"lat": 56.1, "lng": -106.3, "name": "קנדה"}', '"CA": {"lat": 56.1, "lng": -106.3, "name": "Canada"}'),
    ('"IT": {"lat": 41.9, "lng": 12.6, "name": "איטליה"}', '"IT": {"lat": 41.9, "lng": 12.6, "name": "Italy"}'),
    ('"ES": {"lat": 40.5, "lng": -3.7, "name": "ספרד"}', '"ES": {"lat": 40.5, "lng": -3.7, "name": "Spain"}'),
    ('"AR": {"lat": -38.4, "lng": -63.6, "name": "ארגנטינה"}', '"AR": {"lat": -38.4, "lng": -63.6, "name": "Argentina"}'),
    ('"TR": {"lat": 39.0, "lng": 35.2, "name": "טורקיה"}', '"TR": {"lat": 39.0, "lng": 35.2, "name": "Turkey"}'),
    ('"TH": {"lat": 15.9, "lng": 100.5, "name": "תאילנד"}', '"TH": {"lat": 15.9, "lng": 100.5, "name": "Thailand"}'),
    ('"PL": {"lat": 51.9, "lng": 19.1, "name": "פולין"}', '"PL": {"lat": 51.9, "lng": 19.1, "name": "Poland"}'),
    ('"NL": {"lat": 52.1, "lng": 5.3, "name": "הולנד"}', '"NL": {"lat": 52.1, "lng": 5.3, "name": "Netherlands"}'),
    
    # Globe direction labels
    ("GLOBE_DIR_LABELS = {'recovery': 'התאוששות', 'order': 'סדר', 'contribution': 'תרומה', 'exploration': 'חקירה'}",
     "GLOBE_DIR_LABELS = {'recovery': 'Recovery', 'order': 'Order', 'contribution': 'Contribution', 'exploration': 'Exploration'}"),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
    else:
        print(f"  WARNING: Not found in orientation.py: {old[:80]}...")

with open('/app/backend/routes/orientation.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("  Translated orientation.py")

print("\n=== Translation complete! ===")
