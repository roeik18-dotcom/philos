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

## Key API Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/orientation/daily-question/{user_id}` | GET | Daily question + streak data |
| `/api/orientation/daily-answer/{user_id}` | POST | Submit answer + get impact |
| `/api/orientation/weekly-insight/{user_id}` | GET | 7-day aggregated insight |
| `/api/orientation/share/{user_id}` | GET | Share card data |
| `/api/orientation/index` | GET | Global orientation distribution |
| `/api/orientation/identity/{user_id}` | GET | User's orientation identity |
| `/api/orientation/decision-path/{user_id}` | GET | Action recommendation |
| `/api/collective/orientation_field` | GET | Collective field data |
| `/api/collective/field_history` | GET | Historical field data |

## Database Collections
- `philos_sessions` — User session data + history
- `philos_decisions` — Individual decisions
- `daily_questions` — Daily question records + answers
- `users` — User profiles + auth

## Backlog

### P1 — Upcoming
- Refactor `PhilosDashboard.js` into smaller tab-content components
- Fix unfinished SVG in `DecisionTreeSection.js`

### P2 — Future
- General UI polish and RTL improvements
- Persist impact message longer after answering
- Add animations to share card generation
