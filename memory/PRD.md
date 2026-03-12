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
1. **Dashboard Refactor** — Extracted 6 tab components from PhilosDashboard.js: `HomeTab.js`, `FeedTab.js`, `CommunityTab.js`, `InsightsTab.js`, `TheoryTab.js`, `HistoryTab.js` in `/app/frontend/src/pages/tabs/`.
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

### Phase 13 — Polish & Field Pulse (completed 2026-03-11)
1. **Field Pulse Ripple** — Globe shows expanding ring animations at user point locations using `ringsData` prop. `SendToGlobeButton` dispatches `globe-field-pulse` CustomEvent; `FieldGlobeSection` listens and adds temporary 3s ring. User points from API also show persistent rings.
2. **Impact Message Persistence** — Extended showSuccess timeout from 4s to 8s; SendToGlobe confirmation from 4s to 6s.
3. **RTL Polish** — Added `text-align: right` to `.philos-section`, RTL-aware button and flex alignment rules, direction consistency.
4. **Share Card Animations** — Smooth modal entrance (scale+fade via `cardSlideIn`), exit animation on close/backdrop click, `Loader2` spinner during image generation.

### Phase 14 — Field Heartbeat (completed 2026-03-11)
1. **Ambient Globe Pulse** — CSS-only `fieldHeartbeat` animation: inset box-shadow glow behind globe. Duration scales from 6s (idle) to 2s (200+ actions). Color derived from today's dominant field direction. Zero JS overhead.

### Phase 15 — Product Structure Rebuild (completed 2026-03-11)
Reorganized the entire Home experience into 6 clear narrative layers:
1. **Entry Layer** (`EntryLayer.js`) — "Why am I here?" Dark manifesto block explaining Philos in emotional Hebrew.
2. **Personal Orientation** (`DailyOpeningSection`) — "Where am I now?" Compass, dominant force, suggested direction.
3. **Opposition Layer** (`OppositionLayer.js`) — "Between which poles?" 4 visual tension bars: סדר↔כאוס, התאוששות↔דלדול, תרומה↔נסיגה, חקירה↔קיבעון.
4. **Action Layer** (`DailyOrientationQuestion`) — "What do I do now?" Daily question with theory context.
5. **Field Layer** (`FieldImpactLayer.js`) — "How does my action affect the world?" Dark block showing today's field stats and action→field connection.
6. **Closing Layer** (`ClosingLayer.js`) — "What changed today?" Narrative reflection, direction moved, field effect bars, tomorrow hint.

Community features (mission, feed, streaks, invites) moved to collapsible secondary section below the 6 layers.

### Phase 16 — Orientation Feed + Value Engine + Subscription (completed 2026-03-11)
1. **"For You" Feed** — Personalized feed tab (`FeedTab`) with 5 card types: action (user alias/country/direction/impact), question, reflection, leader, mission. API: `GET /api/orientation/feed/for-you/{user_id}`.
2. **Value Engine** — Scoring system: internal value (recovery+order), external value (contribution+exploration), collective value (globe points+invites+streaks). API: `GET /api/orientation/value-profile/{user_id}`.
3. **Value Niches** — 6 niches: Builder of Order, Explorer, Contributor, Regenerator, Social Connector, Deep Thinker. Auto-assigned by action patterns. API: `GET /api/orientation/niches`.
4. **Gamified Progression** — 10 levels, 10 badges (first_action, streaks, all_directions, niche_found), milestones. All returned in value-profile endpoint.
5. **Subscription Foundation** — 3 plans: Free ($0), Plus ($9.99), Collective ($24.99) with Stripe integration. APIs: plans, status, checkout, checkout-status, webhook. Components: `SubscriptionSection`.
6. **Value Economy** — Symbolic value points (internal/external/collective) separated from monetary subscription. Leader status at total_value >= 100.

| New Endpoint | Method | Purpose |
|---|---|---|
| `/api/orientation/feed/for-you/{user_id}` | GET | Personalized feed cards |
| `/api/orientation/value-profile/{user_id}` | GET | Full value profile + progression |
| `/api/orientation/niches` | GET | All 6 value niches |
| `/api/orientation/subscription/plans` | GET | Available subscription plans |
| `/api/orientation/subscription/status/{user_id}` | GET | User's current plan |
| `/api/orientation/subscription/checkout` | POST | Create Stripe checkout session |
| `/api/orientation/subscription/checkout-status/{session_id}` | GET | Check payment status |
| `/api/webhook/stripe` | POST | Stripe webhook handler |

New DB Collections: `user_globe_points`, `payment_transactions`, `subscriptions`

### Phase 17 — Social Field Expansion Frontend Integration (completed 2026-03-12)
All backend endpoints for this phase were completed in Phase 16. This phase wired up the 6 new frontend components:
1. **Global Field Dashboard** (`GlobalFieldDashboard.js`) — Dark hero card at top of Home tab showing dominant direction, total actions today, active regions, direction distribution bars, and top regions. API: `GET /api/orientation/field-dashboard`.
2. **Personal Compass AI** (`CompassAISection.js`) — Placed after narrative layers on Home tab. Shows dominant/weak direction, balance score bar, and suggested action in Hebrew. API: `GET /api/orientation/compass-ai/{user_id}`.
3. **Community Tab** — New "קהילה" tab replacing the old "מערכת" (System) tab. Contains 3 sections:
   - **Mission Engine** (`MissionsSection.js`) — Global missions with direction tags, progress bars, participant counts, and Join buttons. API: `GET/POST /api/orientation/missions`.
   - **Circles System** (`CirclesSection.js`) — 6 value-based communities in 2-column grid. Join buttons update member counts. API: `GET/POST /api/orientation/value-circles`.
   - **Value Leaders** (`LeadersSection.js`) — Top 7 global leaders ranked by impact score with alias, country, niche. API: `GET /api/orientation/leaders`.
4. **Tab Restructure** — 6 tabs in order: Home (בית), Feed (פיד), Community (קהילה), Insights (תובנות), Theory (תיאוריה), History (היסטוריה). System tab removed from navigation.
5. **Feed Algorithm** — Already upgraded in Phase 16 backend. `FeedCard.js` handles 5 card types: action, question, reflection, leader, mission.

| New Endpoint | Method | Purpose |
|---|---|---|
| `/api/orientation/field-dashboard` | GET | Global field state: dominant direction, actions, regions |
| `/api/orientation/missions` | GET | List all field missions |
| `/api/orientation/missions/join` | POST | Join a mission |
| `/api/orientation/value-circles` | GET | List all value circles |
| `/api/orientation/value-circles/join` | POST | Join a circle |
| `/api/orientation/leaders` | GET | Global leaderboard |
| `/api/orientation/compass-ai/{user_id}` | GET | Personal compass analysis |

New DB Collections: `missions`, `circles`

### Phase 18 — Circle Detail View (completed 2026-03-12)
1. **Circle Detail Page** — Clicking any circle card in Community tab opens a detail view with header (name, direction tag, description, member count), Join/Leave toggle, and 3 inner tabs.
2. **Circle Feed** — Inner feed tab showing 8 recent member actions with alias, action text, direction, and impact score.
3. **Circle Leaderboard** — Top 5 ranked members by impact with alias, country, actions count.
4. **Circle Missions** — Direction-specific missions tied to the circle with progress bars and target counts.
5. **Join/Leave Toggle** — Members can join or leave circles. Button state reflects current membership via `is_member` field.
6. **Back Navigation** — "חזרה למעגלים" button returns to the circles list within the Community tab.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/orientation/value-circles/{circle_id}?user_id=` | GET | Circle detail: info, is_member, feed, leaderboard, missions |
| `/api/orientation/value-circles/leave` | POST | Leave a circle |

### Phase 19 — Real-User Testing Preparation (completed 2026-03-12)
1. **Admin Analytics Page** (`/admin`) — Hidden page showing KPIs (Total Users, Total Actions, DAU Today, Actions/User), D1/D7 retention rates, 7-day DAU bar chart, and user feedback list.
2. **Floating Feedback Button** — Appears on all 6 tabs (bottom-left). Opens modal with type selector (confusion/improvement/bug), text input, and submit. Stores to MongoDB via `POST /api/feedback`.
3. **Onboarding Flow** — 3-step flow for new users: (1) Welcome + explain Philos, (2) Choose first direction from 4 options, (3) Send first point to globe. Dispatches `globe-field-pulse` event on completion. Uses localStorage `philos_onboarding_complete` to show only once.
4. **Globe Restoration** — `FieldGlobeSection` added back to HomeTab (above fold) after it was lost in the SystemTab→CommunityTab transition.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/admin/analytics` | GET | DAU, actions/user, D1/D7 retention, totals |
| `/api/admin/feedback` | GET | List all user feedback (latest 100) |
| `/api/feedback` | POST | Submit user feedback (text, type, page) |
| `/api/onboarding/first-action` | POST | Record first direction + add globe point |

New DB Collection: `feedback`

### Phase 20 — Human Action Record / Public Profile (completed 2026-03-12)
1. **Public Profile Page** (`/profile/{user_id}`) — Publicly accessible, shareable URL. Document-style layout with Hebrew RTL.
2. **Identity Header** — Alias, country, member since date, dominant direction badge, niche badge.
3. **Opposition Axes** — 3 visual sliders: Chaos↔Order, Ego↔Collective, Exploration↔Stability. Computed from direction ratios.
4. **Value Growth** — Impact score, level, circle memberships, level progress bar, niche progress bar, streak, badges count.
5. **Direction Distribution** — Stacked color bar showing contribution/recovery/order/exploration breakdown.
6. **Chronological Action Record** — Expandable list of actions. Each action shows date, direction, action text, impact score. On expand: 4-layer multidimensional meaning (personal/social/value/system) using rule-based interpretation.
7. **Profile Links** — Added to feed action cards (avatar + alias), feed leader cards, community leaderboard entries, circle detail leaders.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/profile/{user_id}/record` | GET | Full human action record for any user |

Rule-based meaning engine: `ACTION_MEANINGS` dict maps each direction to 4 Hebrew interpretation layers (personal, social, value, system).

### Phase 21 — Share Human Action Record (completed 2026-03-12)
1. **Share Button** — Added to profile page top bar. Opens a modal with a dark, elegant share card.
2. **Share Card Design** — Dark (#1a1a2e) themed card with: alias + avatar, country, direction badge, impact/level/actions stats, 3 opposition axis sliders, highlighted recent action (if any), date, and "Philos Orientation" branding. Documentary, symbolic, not flashy.
3. **Download Image** — Generates PNG via `html-to-image` (toPng, pixelRatio 2) and triggers browser download.
4. **Copy Link** — Copies shareable profile URL to clipboard with visual confirmation.
5. **No Social API** — Manual sharing only for now.

### Phase 22 — Addictive Autonomous Engagement Loop (completed 2026-03-12)
Strengthened 6 existing loops without adding new pages/tabs:
1. **Daily Opening Hook** — EntryLayer rewritten as dynamic personal hook. Fetches live field-dashboard + compass-ai data. Shows: today's world direction, user's dominant force, recommended action, CTA "התחל פעולה" that smooth-scrolls to daily question.
2. **Fast Action Loop** — QuickDecisionButton rewritten as 3-tap FAB: tap → pick direction (4 buttons) → instant reward. Uses `/api/onboarding/first-action`, dispatches globe pulse.
3. **Immediate Reward** — DailyOrientationQuestion enhanced: animated "+impact" score, streak indicator, niche progress bar with "עוד X" remaining, link to Human Action Record.
4. **Identity Growth** — After each action: niche progress nudge, next milestone indicator, profile link ("צפה ברשומה שלך").
5. **Curiosity Loop** — ClosingLayer enhanced: tension narrative (opposing direction rising), return hook ("השדה ממשיך להשתנות"), emotional cliffhanger per direction.
6. **Living Field Presence** — Globe ambient pulses every 8-12s, auto-refresh every 45s. GlobalFieldDashboard auto-refreshes every 30s with animated counter and "חי" (live) indicator.

Backend fix: streak calculation added to `POST /api/orientation/daily-answer/{user_id}`. Now returns `impact_score`, `streak`, `niche_info`, `identity_link`.

### Phase 23 — Orientation Map Layer (completed 2026-03-12)
1. **Persistent Orientation Diagram** — Compact compass visible on ALL 6 tabs, showing the 6-stage loop: מציאות (Reality) → אדם (Human) → ניגוד (Opposition) → בחירה (Choice) → פעולה (Action) → שדה (Field). Active stage has larger pulsing node, past stages show indigo dots, future stages gray.
2. **Stage Animation** — Stages transition via `orientation-stage` CustomEvent dispatched by:
   - EntryLayer: `reality` → `human` (on field data + compass data load)
   - OppositionLayer: `opposition` (on compass data load)
   - DailyOrientationQuestion: `choice` (question loaded) → `action` (answer submitted)
   - SendToGlobeButton + QuickDecisionButton: `field` (globe point sent)
   - Auto-advance: reality → human after 2 seconds
3. **Strengthened Opposition Layer** — Now fetches user's real opposition axes from `/api/profile/{userId}/record` and displays 3 mini axis bars (סדר↔כאוס, קולקטיב↔אגו, יציבות↔חקירה) in a dark card showing the user's personal position between forces.

## Backlog

### P0 — Next Focus
- Real-user testing and retention measurement

### P1 — Technical Debt
- Refactor `server.py` into modular routes/models/services
- Optimize feed endpoint (cache mission query)

### P2 — Future
- Additional UI polish and micro-interactions
- Private/group circles feature
- Expanded profile page
- Circle detail view (feed + leaderboard per circle)
