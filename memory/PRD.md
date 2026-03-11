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
| `/api/orientation/mission-today` | GET | Today's community challenge |
| `/api/orientation/active-users` | GET | Active users today + streak users |
| `/api/orientation/relative-score/{user_id}` | GET | User's percentile among all users |
| `/api/orientation/circles` | GET | User counts per direction |
| `/api/orientation/streaks` | GET | Community streak stats |
| `/api/collective/orientation_field` | GET | Collective field data |
| `/api/collective/field_history` | GET | Historical field data |

## Database Collections
- `philos_sessions` — User session data + history
- `philos_decisions` — Individual decisions
- `daily_questions` — Daily question records + answers
- `daily_missions` — Daily community challenge (date, direction, participants, target)
- `invites` — Invite codes (code, inviter_id, used_by, use_count)
- `users` — User profiles + auth

## Backlog

### P1 — Upcoming
- Refactor `PhilosDashboard.js` into smaller tab-content components
- Fix unfinished SVG in `DecisionTreeSection.js`

### P2 — Future
- General UI polish and RTL improvements
- Persist impact message longer after answering
- Add animations to share card generation
