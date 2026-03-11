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
1. **Entrance animations** — Staggered fadeInUp for all sections (animate-section-1 through 8)
2. **Animated progress bars** — Mission, percentile, weekly, and index bars animate from 0% on load
3. **Completion animations** — completionPulse on daily question, glowIn on numbers/streak badges
4. **RTL layout cleanup** — Fixed text-left → text-right in WeeklyInsight, consistent dir="rtl"
5. **Consistent spacing** — Standardized all tabs to space-y-5
6. **Tab nav polish** — rounded-2xl, backdrop-blur, hover states
7. **Hover effects** — philos-section base class with shadow-md hover, active:scale on buttons

### Phase 7 — Referral Leaderboard (completed 2026-03-11)
1. **Referral Leaderboard** — Top 10 inviters with anonymous aliases, invite counts, streaks, ranked medals for top 3

### Phase 8 — Product Validation (completed 2026-03-11)
1. **Onboarding** — 3-screen flow: compass meaning, daily question purpose, field effect. Progress dots, skip/next navigation, localStorage persistence
2. **Admin Retention Review** — Enhanced metrics dashboard with 6 KPIs: active users, question completion rate, D2 retention, mission participation, avg streak, invite conversions
3. **Invite Tracking Report** — Funnel visualization (sent→opened→accepted) with conversion rates. Invite open tracking via GET /invite/{code}

### Phase 10 — Core Theory Integration (completed 2026-03-11)
1. **Daily Opening Section** — Compass state visualization with 4-direction percentages, Hebrew greeting (time-based), dominant force, suggested direction with theory explanation. Endpoint: `GET /api/orientation/daily-opening/{user_id}`. Component: `DailyOpeningSection.js` on Home tab.
2. **End of Day Summary** — Reflection text, streak counter, field impact percentage, today's action count, direction breakdown pills, global field effect bars. Endpoint: `GET /api/orientation/day-summary/{user_id}`. Component: `DaySummarySection.js` on Home tab.
3. **Global Field Globe** — 3D globe visualization using `react-globe.gl` showing demo agent + user activity points across 20 countries, color-coded by direction, with direction legend. Lazy-loaded for performance. Endpoint: `GET /api/orientation/globe-activity`. Component: `FieldGlobeSection.js` on System tab.
4. **Direction Explanations** — 4 expandable direction cards (Contribution, Recovery, Order, Exploration) each showing symbolic meaning, human behavior example, and collective field effect in Hebrew. Endpoint: `GET /api/orientation/directions`. Component: `DirectionExplanationsSection.js` on Theory tab.

## Key API Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/orientation/daily-opening/{user_id}` | GET | Daily opening: compass state, dominant force, suggested direction |
| `/api/orientation/day-summary/{user_id}` | GET | End of day: chosen direction, impact, streak, global field effect |
| `/api/orientation/globe-activity` | GET | Globe data: points with lat/lng/direction/color from demo agents |
| `/api/orientation/directions` | GET | 4 directions with symbolic meaning, behavior examples, field effects |
| `/api/orientation/daily-question/{user_id}` | GET | Daily question + streak data |
| `/api/orientation/daily-answer/{user_id}` | POST | Submit answer + get impact |
| `/api/orientation/weekly-insight/{user_id}` | GET | 7-day aggregated insight |
| `/api/orientation/share/{user_id}` | GET | Share card data |
| `/api/orientation/index` | GET | Global orientation distribution |
| `/api/orientation/identity/{user_id}` | GET | User's orientation identity |
| `/api/orientation/decision-path/{user_id}` | GET | Action recommendation |
| `/api/orientation/mission-today` | GET | Today's community challenge |
| `/api/orientation/active-users` | GET | Active users today + streak users |
| `/api/orientation/relative-score/{user_id}` | GET | User's percentile among all users |
| `/api/orientation/circles` | GET | User counts per direction |
| `/api/orientation/streaks` | GET | Community streak stats |
| `/api/collective/orientation_field` | GET | Collective field data |
| `/api/collective/field_history` | GET | Historical field data |

### Phase 9 — Demo Agents (completed 2026-03-11)
1. **50 Demo Agents** — Seeded with aliases (Atlas, Nova, Sage...), 20 countries, 4 orientation directions
2. **Auto-generation** — Background task generates 8-15 events every 5 minutes, auto-cleans events older than 3 hours
3. **Feed integration** — Demo events appear in Orientation Feed with country flags, marked as demo=true
4. **Metrics isolation** — Demo agents excluded from all KPI metrics (active_users_today, etc.)

## Database Collections
- `demo_agents` — 50 simulated agents (agent_id, alias, country, country_code, orientation_direction)
- `demo_events` — Auto-generated activity events (direction, timestamp, demo=true, country_code)
- `philos_sessions` — User session data + history
- `philos_decisions` — Individual decisions
- `daily_questions` — Daily question records + answers
- `daily_missions` — Daily community challenge (date, direction, participants, target)
- `invites` — Invite codes (code, inviter_id, used_by, use_count)
- `users` — User profiles + auth

### Phase 11 — Stabilization (completed 2026-03-11)
1. **Dashboard Refactor** — Extracted 5 tab components from PhilosDashboard.js (640→267 lines): `HomeTab.js`, `InsightsTab.js`, `SystemTab.js`, `TheoryTab.js`, `HistoryTab.js` in `/app/frontend/src/pages/tabs/`.
2. **DecisionTreeSection SVG Fix** — Replaced fragile div-based tree connectors with proper SVG `<path>` elements using cubic bezier curves. Added layout engine for node positioning.

### Phase 12 — Globe Interaction Layer (completed 2026-03-11)
1. **Send Point to Globe** — `SendToGlobeButton` component appears after daily action completion. Calls `POST /api/orientation/globe-point`, shows launch animation + confirmation "הפעולה שלך נוספה לשדה האנושי".
2. **Mission Glow** — Globe atmosphere color dynamically matches current daily mission direction (green/blue/indigo/orange).
3. **Live Globe Header** — Shows today's total action count + dominant direction in Hebrew above globe.
4. **Region Interaction** — Click points on globe to view region popup: country name, dominant direction, action count, direction bars, trend label.
5. **New DB collection** — `user_globe_points` stores user-submitted globe points (lat, lng, direction, country_code, timestamp).

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/orientation/globe-point` | POST | Add user action point to globe |
| `/api/orientation/globe-activity` | GET | Globe data + today_stats + mission_glow |
| `/api/orientation/globe-region/{country_code}` | GET | Region details: dominant dir, count, trend |

## Backlog

### P1 — Upcoming
- Refactor `server.py` into modular routes/models/services

### P2 — Future
- General UI polish and RTL improvements
- Persist impact message longer after answering
- Add animations to share card generation
