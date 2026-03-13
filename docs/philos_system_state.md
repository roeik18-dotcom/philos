# Philos Orientation - Complete Project State
**Session Date:** March 10, 2026
**Status:** Ready for continuation

---

## 🚀 QUICK START FOR NEXT SESSION

```bash
# Preview URL
https://trust-ledger-11.preview.emergentagent.com

# Resume file
/app/frontend/src/components/philos/sections/DailyOrientationQuestion.js

# Current task
Add streak badge + impact message to Daily Question component
```

---

## ✅ COMPLETED FEATURES (8 total)

1. **Orientation Compass** - Visual map with user position vs collective center
2. **Identity Layer** - 9 identity types (recovery_dominant, avoidance_loop, etc.)
3. **Daily Orientation Question** - Identity-based questions with completion tracking
4. **Orientation Snapshots** - Daily identity snapshots saved to DB
5. **Field Today Distribution** - 24h collective distribution (4 bars)
6. **Decision Path Engine** - Concrete action recommendations
7. **Historical Momentum** - 4-week sparkline with trend detection
8. **User Comparison** - Percentile rankings vs collective

---

## 🔄 IN PROGRESS

### Task 1: Orientation Streak (P0)
- **Backend:** ✅ DONE - Returns `streak` and `longest_streak`
- **Frontend:** 🔄 STARTED - Added `impactMessage` state
- **TODO:** Add streak badge: `🔥 7 ימים רצופים`

### Task 2: Personal Impact (P0)
- **Backend:** ✅ DONE - Returns `impact_message` after answer
- **Frontend:** TODO - Display: "הפעולה שלך חיזקה היום את שדה התרומה"

---

## 📋 PENDING TASKS

| Task | Priority | Backend | Frontend |
|------|----------|---------|----------|
| Weekly Insight Card | P1 | ✅ | TODO |
| Orientation Share Card | P1 | ✅ | TODO |
| Orientation Index Page | P2 | ✅ | TODO |

---

## 🔌 API ENDPOINTS

### Orientation Core
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/orientation/field` | GET | Collective field + momentum |
| `/api/orientation/field-today` | GET | 24h distribution |
| `/api/orientation/history` | GET | 4-week snapshots |
| `/api/orientation/identity/{user_id}` | GET | User identity |
| `/api/orientation/compare/{user_id}` | GET | Percentile ranking |

### Daily System
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/orientation/daily-question/{user_id}` | GET | Question + streak |
| `/api/orientation/daily-answer/{user_id}` | POST | Answer + impact |

### Ready for Frontend
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/orientation/weekly-insight/{user_id}` | GET | 7-day insight |
| `/api/orientation/share/{user_id}` | GET | Share card data |
| `/api/orientation/index` | GET | Public index |
| `/api/decision-path/{user_id}` | GET | Action recommendation |

---

## 🗄️ DATABASE SCHEMA

### philos_sessions
```javascript
{
  user_id: String,
  history: [{ id, action_text, value_tag, timestamp, chaos_order, ego_collective }],
  global_stats: { recovery, order, contribution, exploration, harm, avoidance },
  last_synced: String
}
```

### daily_questions
```javascript
{
  user_id: String,
  date: String,           // YYYY-MM-DD
  question_id: String,
  question_he: String,
  suggested_direction: String,
  answered: Boolean,
  answered_at: String
}
```

### orientation_snapshots
```javascript
{
  user_id: String,
  date: String,
  identity_type: String,
  dominant_direction: String,
  direction_counts: Object,
  avoidance_ratio: Number,
  momentum: String
}
```

---

## 📁 KEY FILES

```
/app/
├── backend/
│   └── server.py                          # All API endpoints
├── frontend/src/
│   ├── pages/
│   │   └── PhilosDashboard.js             # Main dashboard
│   ├── components/philos/sections/
│   │   ├── DailyOrientationQuestion.js    # 🔄 CURRENT EDIT
│   │   ├── OrientationIdentitySection.js
│   │   ├── OrientationFieldToday.js
│   │   ├── DecisionPathSection.js
│   │   ├── OrientationCompassSection.js
│   │   └── index.js
│   └── services/
│       └── recommendationService.js
└── docs/
    └── philos_system_state.md             # THIS FILE
```

---

## 🎨 UI CONSTANTS

```javascript
// Direction Colors
const directionColors = {
  recovery: '#3b82f6',     // Blue
  order: '#6366f1',        // Indigo
  contribution: '#22c55e', // Green
  exploration: '#f59e0b'   // Amber
};

// Hebrew Labels
const directionLabels = {
  recovery: 'התאוששות',
  order: 'סדר',
  contribution: 'תרומה',
  exploration: 'חקירה'
};
```

---

## 📐 DASHBOARD LAYOUT

```
Home Tab:
├── DailyOrientationQuestion    ← Add streak here
├── MonthlyOrientationSection
├── WeeklyOrientationSummary
├── HomeNavigationSection
├── OrientationCompassSection
├── OrientationIdentitySection
├── OrientationFieldToday
└── DecisionPathSection
```

---

## 🔧 IMPLEMENTATION GUIDE

### To complete Streak display:
```jsx
// In DailyOrientationQuestion.js, after line 143 (header section):
{questionData.streak > 0 && (
  <div className="flex items-center gap-1 text-orange-500 text-sm">
    <span>🔥</span>
    <span className="font-medium">{questionData.streak} ימים רצופים</span>
  </div>
)}
```

### To complete Impact message:
```jsx
// Store impact from API response:
const result = await response.json();
if (result.impact_message) {
  setImpactMessage(result.impact_message);
}

// Display after success:
{impactMessage && (
  <p className="text-sm text-green-600 mt-2">{impactMessage}</p>
)}
```

---

## ✨ THEORY MODEL

**Four Directions:** Recovery, Order, Contribution, Exploration

**Balancing Paths:**
- harm → recovery
- avoidance → order
- isolation → contribution
- rigidity → exploration

---

**END OF STATE FILE - Ready for next session**
