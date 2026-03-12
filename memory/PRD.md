# Philos Orientation - PRD

## Original Problem Statement
Build "Philos Orientation" — a sophisticated single-page decision engine and dashboard for real-time decision analysis and mental navigation. The UI is in **Hebrew (RTL)**.

## Core Architecture
- **Frontend:** React (CRA) with Tailwind CSS, Shadcn/UI, Lucide icons
- **Backend:** FastAPI + MongoDB
- **Auth:** JWT-based custom auth + anonymous user flow
- **Language:** Hebrew RTL

## Completed Features

### Phase 1 — Core Dashboard (completed prior sessions)
- Orientation Compass (user vs collective)
- Orientation Identity classification
- Daily Orientation Question
- Orientation Field Today (24h distribution)
- Decision Path (actionable recommendation)
- Historical Momentum Sparkline (4-week trend)
- Collective Mirror, Trajectory, Layer, Trends
- Session management, Replay, Decision History
- Weekly/Monthly/Quarterly reports
- Theory section
- Onboarding flow

### Phase 2 — Engagement Features (completed 2026-03-10)
1. **Orientation Streak** — Flame icon + count in DailyOrientationQuestion, longest streak tracking
2. **Personal Impact on Field** — After answering daily question, shows impact message + percent
3. **Orientation Share Card** — Modal with downloadable/shareable card showing orientation, streak, compass position
4. **Weekly Orientation Insight** — Distribution bars + Hebrew insight text on Insights tab
5. **Orientation Index Page** — Global distribution chart with active users/actions on System tab

### Phase 3 — Community Layer (completed 2026-03-10)
1. **Active Users Indicator** — Header shows active users today + users on streak
2. **Relative Orientation Score** — User's percentile compared to all users today
3. **Orientation Circles** — 2x2 grid showing user counts per direction
4. **Community Streak Overview** — Users on streak + longest streak today

### Phase 4 — Field Mission System (completed 2026-03-10)
1. **Daily Community Challenge** — Auto-rotating mission per day (contribution/recovery/order/exploration)
2. **Mission Progress** — Real-time participant count + progress bar toward target (5000)
3. **Mission Contribution** — Daily answer auto-increments mission when direction matches
4. **Contribution Feedback** — "הפעולה שלך תרמה למשימת היום" shown after matching action

### Phase 5 — UI Polish (completed 2026-03-11)
1. **Entrance animations** — Staggered fadeInUp for all sections
2. **Animated progress bars** — Mission, percentile, weekly, and index bars animate from 0%
3. **Completion animations** — completionPulse on daily question, glowIn on numbers
4. **RTL layout cleanup** — Consistent dir="rtl"
5. **Consistent spacing** — Standardized all tabs to space-y-5
6. **Tab nav polish** — rounded-2xl, backdrop-blur, hover states
7. **Hover effects** — philos-section base class with shadow-md hover

### Phase 7 — Referral Leaderboard (completed 2026-03-11)
### Phase 8 — Product Validation (completed 2026-03-11)
### Phase 9 — Demo Agents (completed 2026-03-11)
### Phase 10 — Core Theory Integration (completed 2026-03-11)
### Phase 11 — Stabilization (completed 2026-03-11)
### Phase 12 — Globe Interaction Layer (completed 2026-03-11)
### Phase 13 — Polish & Field Pulse (completed 2026-03-11)
### Phase 14 — Field Heartbeat (completed 2026-03-11)
### Phase 15 — Product Structure Rebuild (completed 2026-03-11)
### Phase 16 — Orientation Feed + Value Engine + Subscription (completed 2026-03-11)
### Phase 17 — Social Field Expansion (completed 2026-03-12)
### Phase 18 — Circle Detail View (completed 2026-03-12)
### Phase 19 — Real-User Testing Preparation (completed 2026-03-12)
### Phase 20 — Human Action Record / Public Profile (completed 2026-03-12)
### Phase 21 — Share Human Action Record (completed 2026-03-12)
### Phase 22 — Addictive Autonomous Engagement Loop (completed 2026-03-12)
### Phase 23 — Orientation Map Layer (completed 2026-03-12)

### Phase 24 — Clarity & Meaning Refinement (completed 2026-03-12)
Focus: Making the existing system clearer, calmer, and more meaningful. No new pages/tabs.

1. **World State Language** — Backend generates `field_narrative_he`: a single symbolic Hebrew sentence describing the human field state (e.g. "השדה נוטה לחקירה היום", "פעילות תרומה עולה", "סדר מתייצב במספר אזורים"). No numbers in the sentence. Narrative varies by: dominant direction strength, momentum, secondary tensions, regional spread.
   - `_generate_field_narrative()` function in backend
   - `GlobalFieldDashboard.js` rewritten to show only narrative + living pulse dot
   - `EntryLayer.js` uses narrative instead of stat badges
   - `FieldGlobeSection.js` header shows narrative as primary text

2. **Opposition Engine Expansion** — `OppositionLayer.js` completely redesigned as a personal tension mirror:
   - 3 tension arcs: סדר↔כאוס, קולקטיב↔אגו, יציבות↔חקירה
   - Glowing position dot on each arc showing user's personal position
   - Short interpretive Hebrew line below each arc (e.g. "אתה נוטה לסדר, אבל הכאוס מושך")
   - Dark card aesthetic — feels like a mirror, not a chart
   - Data from `/api/profile/{user_id}/record` opposition_axes

3. **Globe Readability (3-second rule)** — `FieldGlobeSection.js` rewritten for clarity:
   - Simplified header: "מצב השדה" + narrative + dominant direction dot + thin bar
   - Direction legend highlights dominant direction, dims others
   - Fewer simultaneous ring pulses (max 2-3 vs previous 5+)
   - Slower, calmer ambient pulses (8-12s vs 6-9s)
   - Larger spike pulses for dominant direction
   - Reduced heartbeat glow intensity

4. **Performance & Stability** — Optimized all globe-related code:
   - Reduced overlapping intervals (globe: 45s, field: 30s)
   - Limited ringsData array to prevent accumulation (max 2-3 active)
   - Memoized colorMap computation
   - Cleaner timer cleanup in useEffect hooks
   - Softer heartbeat glow (reduced shadow intensity)

## Key API Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/orientation/field-dashboard` | GET | Field state + `field_narrative_he` symbolic sentence |
| `/api/orientation/globe-activity` | GET | Globe points data |
| `/api/orientation/globe-region/{cc}` | GET | Region details |
| `/api/profile/{user_id}/record` | GET | Profile + opposition_axes for tension mirror |
| `/api/orientation/daily-opening/{user_id}` | GET | Compass state, dominant force |
| `/api/orientation/compass-ai/{user_id}` | GET | Personal compass analysis |
| `/api/orientation/daily-answer/{user_id}` | POST | Submit answer + rewards |
| `/api/admin/analytics` | GET | Admin dashboard data |

## Database Collections
- `users`, `philos_decisions`, `demo_events`, `demo_agents`, `user_globe_points`
- `daily_questions`, `daily_missions`, `missions`, `circles`
- `invites`, `feedback`, `subscriptions`, `payment_transactions`

## Backlog

### P0 — Next Focus
- Continue observation phase with real users
- Analyze collected behavioral data

### P1 — Technical Debt
- Refactor `server.py` into modular routes/models/services
- Optimize feed endpoint (cache mission query)

### P2 — Future
- Private/group circles feature
- Expanded profile page interactions
- Additional narrative templates based on time-of-day
