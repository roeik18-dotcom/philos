# Philos Orientation – Project State (Advanced MVP)

**Last Updated:** March 10, 2026  
**Project Phase:** Advanced MVP Complete – Ready for Real User Testing

---

## 1. Project Name and Goal

**Project:** Philos Orientation  
**Tagline:** Mental Navigation System  
**Language:** Hebrew (עברית) with RTL layout  

**Primary Goal:**  
A sophisticated single-page decision engine and dashboard for real-time decision analysis and mental navigation. The system helps users identify behavioral patterns, receive directional recommendations, and learn from outcomes over time.

**Core Philosophy:**  
Turn reflection into actionable navigation – helping users make better decisions through pattern recognition, recommendation engines, and behavioral feedback loops.

---

## 2. Implemented Core Engines

### Decision Evaluation Engine
- **Action Input:** Users enter actions/decisions in Hebrew
- **NLP Classification:** Backend classifies actions into 5 value tags:
  - תרומה (contribution) - positive
  - התאוששות (recovery) - positive  
  - סדר (order) - positive
  - נזק (harm) - negative
  - הימנעות (avoidance) - negative
- **Metrics:** chaos_order, ego_collective, balance_score

### Decision Chain System
- Parent-child decision relationships
- Decision trees visualization
- Chain insights analysis
- Follow-up action tracking

### Decision Replay System
- Counterfactual exploration ("what if I chose differently?")
- Alternative path predictions
- Replay metadata storage
- Replay insights aggregation

### Collective Layer
- Cross-user anonymized analytics
- Collective value distribution
- User vs. collective comparison
- Collective trajectory tracking

---

## 3. Implemented Recommendation System

### Next Best Direction Engine
**File:** `NextBestDirectionSection.js`

**6-Priority Recommendation Algorithm:**
1. **Negative Drift** (harm/avoidance >40%) → recommends recovery or order
2. **Collective Gap** (user below collective >15%) → recommends gap direction
3. **Replay Blind Spots** → recommends unexplored direction
4. **Positive Momentum** → reinforces contribution
5. **Replay Preferences** → recommends frequently replayed direction
6. **Balance Deficit** → recommends lowest positive score direction

**Features:**
- SVG compass indicator with direction arrow and strength arc
- Hebrew insight texts with reason footer
- "פעל לפי ההמלצה" (Follow Recommendation) button
- Action suggestions: "כיוון מומלץ להיום: לסיים משימה פתוחה אחת"

### Follow Recommendation Flow
1. User clicks "פעל לפי ההמלצה"
2. Action input prefilled with recommendation
3. Page scrolls to input and focuses
4. Indicator shows "הפעולה הזו נובעת מהכיוון המומלץ"
5. Metadata saved with decision when evaluated

### Recommendation Follow-Through Analytics
**File:** `RecommendationFollowThroughSection.js`

- Follow rate (שיעור מעקב)
- Alignment rate (התאמת תוצאות)
- Most/least followed directions
- Pattern analysis (strongest/weakest)
- Hebrew insights

---

## 4. Behavioral Loops (Daily, Weekly, Monthly)

### Daily Orientation Loop
**File:** `DailyOrientationLoopSection.js`  
**Color:** Amber gradient  
**Storage:** `localStorage.philos_daily_orientation`

**Shows on new day:**
- "התמצאות יומית" header
- "היום מתחיל מחזור חדש של החלטות."
- Yesterday's pattern analysis
- Today's recommended direction
- "התחל את היום" button

**Metadata saved:**
- day_started
- orientation_direction
- orientation_pattern_reference
- yesterday_count

### Weekly Orientation Summary
**File:** `WeeklyOrientationSummarySection.js`  
**Color:** Purple gradient  
**Storage:** `localStorage.philos_weekly_orientation`

**Shows on new week:**
- "סיכום שבועי" header
- Last week's dominant pattern
- Strongest positive (↑) and negative (↓) movements
- This week's recommended direction
- "התחל את השבוע" button

**Metadata saved:**
- weekId (year-week format: 2026-W11)
- week_started
- weekly_orientation_direction
- weekly_pattern_reference
- last_week_decisions

### Monthly Orientation
**File:** `MonthlyOrientationSection.js`  
**Color:** Teal/Cyan gradient  
**Storage:** `localStorage.philos_monthly_orientation`

**Shows on new month:**
- "התמצאות חודשית" header
- Hebrew month name (e.g., פברואר)
- Last month's dominant pattern
- Strongest positive/negative movements
- This month's recommended direction
- "התחל את החודש" button

**Metadata saved:**
- monthId (year-month format: 2026-M03)
- month_started
- monthly_orientation_direction
- monthly_pattern_reference
- last_month_decisions

**Visual Hierarchy:** Monthly (teal) → Weekly (purple) → Daily (amber) → Home

---

## 5. Dashboard Structure

### Tab Navigation
**4 Tabs:** בית | תובנות | מערכת | היסטוריה

### Home Tab (בית)
Clean entry screen readable in under 5 seconds:
- Monthly/Weekly/Daily Orientation (when applicable)
- **מצב היום** (Current State): Pattern analysis
- **כיוון מומלץ** (Recommended Direction): Direction badge + action suggestion
- Action input with "פעל לפי ההמלצה" button
- Decision result display
- Recent history (3 items) with "הצג הכל" link

### Insights Tab (תובנות)
Analytics and reports:
- Chain Insights
- Recommendation Follow-Through Analytics
- Weekly Behavioral Report
- Monthly Progress Report
- Quarterly Review
- Replay Insights Summary
- Decision Path Engine
- Path Learning
- Adaptive Learning

### System Tab (מערכת)
Advanced system features:
- Recommendation Calibration
- Replay Adaptive Effect
- Collective Mirror
- Collective Trajectory
- Collective Layer
- Collective Trends
- Global Field
- Value Constellation
- Personal Map
- Collective Value Map

### History Tab (היסטוריה)
Historical data and sessions:
- Decision History with Chains
- Decision Replay
- Decision Tree Visualization
- Decision Map
- Orientation Status
- Session Library
- Session Comparison
- Weekly Cognitive Report
- Global Value Field
- Global Trend
- Session Summary
- Reset Session

---

## 6. Calibration Logic

### Recommendation Calibration
**File:** `RecommendationCalibrationSection.js`

**Purpose:** Self-correcting recommendation weights based on actual outcomes

**Calibration Formula:**
- Weights bounded between -5 and +5
- High alignment (>60%) → boost weight (+1 to +5)
- Low alignment (<30%) → reduce weight (-1 to -5)
- Follow rate amplifies/dampens adjustments

**Integration:**
- `calculateCalibrationWeights` exported and used in `NextBestDirectionSection.js`
- Applied as adjustment layer to base recommendation algorithm
- New reason: "calibration_boost" with "מבוסס על כיול אוטומטי מתוצאות בפועל"
- "משקל מכויל" indicator when calibration affects recommendation

**Display:**
- SVG visualization of calibrated weights
- Strongest (הכי מחוזק) and weakest (מופחת) directions
- Hebrew insights

---

## 7. Data Storage and Metadata

### Backend (MongoDB)
**Collections:**
- `decisions` - User decisions with value tags and metrics
- `replays` - Replay session metadata
- `philos_user_stats` - Aggregated user statistics
- `users` - Authenticated user accounts

**Decision Schema:**
```json
{
  "user_id": "string",
  "decision_id": "string",
  "parent_decision_id": "string | null",
  "action": "string",
  "decision": "string",
  "value_tag": "contribution|recovery|order|harm|avoidance",
  "chaos_order": "number",
  "ego_collective": "number",
  "balance_score": "number",
  "followed_recommendation": "boolean",
  "recommendation_direction": "string",
  "recommendation_reason": "string",
  "recommendation_strength": "number",
  "timestamp": "datetime"
}
```

### Frontend (localStorage)
**Keys:**
- `philos_user_id` - Persistent anonymous user ID
- `philos_daily_orientation` - Daily orientation state
- `philos_weekly_orientation` - Weekly orientation state
- `philos_monthly_orientation` - Monthly orientation state
- `philos_history` - Local decision history cache

### Cloud Sync
- `cloudSync.js` - Central sync service
- `dataService.js` - Cached API calls (30s TTL for collective, 60s for trends)
- `getUserId()` - Persistent anonymous user identification

---

## 8. Current Project Phase

### Phase: Advanced MVP Complete

**Status:** Ready for Real User Testing

**Completed Features:**
- ✅ Core decision evaluation engine
- ✅ Decision chain system with trees
- ✅ Decision replay system
- ✅ 6-priority recommendation algorithm
- ✅ Follow recommendation flow with metadata
- ✅ Recommendation follow-through analytics
- ✅ Self-correcting calibration system
- ✅ Daily orientation loop
- ✅ Weekly orientation summary
- ✅ Monthly orientation
- ✅ Tabbed dashboard (Home/Insights/System/History)
- ✅ Simplified Home Mode
- ✅ Collective layer with user comparison
- ✅ System stabilization (API caching, loading states, error handling)
- ✅ JWT authentication
- ✅ Persistent anonymous user ID
- ✅ Multi-device sync for authenticated users

**Technical Stack:**
- Frontend: React with Tailwind CSS, Shadcn/UI components
- Backend: FastAPI with MongoDB
- Sync: localStorage + Cloud backend
- Auth: JWT-based with passlib/python-jose

**Key Files:**
- `usePhilosState.js` - Central state management (~1180 lines)
- `PhilosDashboard.js` - Main dashboard with tabs (~500 lines)
- `cloudSync.js` - Cloud sync service (~440 lines)
- `server.py` - FastAPI backend (~2000 lines)
- `sections/` - 33 UI components

**Next Priority Tasks:**
1. Real User Readiness Pass (onboarding hints, empty states, helper text)
2. Refactor `usePhilosState.js` into smaller domain-specific hooks
3. Add quarterly orientation for annual planning

**Future/Backlog:**
- Password Reset / Email Verification
- Export/Import session data
- PWA Support
- LLM-enhanced path generation

---

## Test Credentials

**Registered User:**
- Email: `newuser@test.com`
- Password: `password123`

**Anonymous User:**
- Automatic via persistent `philos_user_id` in localStorage

---

## Preview URL

https://decision-engine-lab.preview.emergentagent.com

---

*Document generated: March 10, 2026*
