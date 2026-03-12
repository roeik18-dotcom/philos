# Philos Orientation - PRD

## Original Problem Statement
Build "Philos Orientation" — a sophisticated single-page decision engine and dashboard for real-time decision analysis and mental navigation. The UI is in **Hebrew (RTL)**.

## Core Architecture
- **Frontend:** React (CRA) with Tailwind CSS, Shadcn/UI, Lucide icons
- **Backend:** FastAPI + MongoDB
- **Auth:** JWT-based custom auth + anonymous user flow
- **Language:** Hebrew RTL

## Completed Features

### Phases 1–23 (completed prior sessions)
Core dashboard, engagement features, community layer, field missions, UI polish, referral leaderboard, product validation, demo agents, core theory integration, stabilization, globe interaction, field pulse, field heartbeat, product structure rebuild, orientation feed + value engine + subscription, social field expansion, circle detail view, real-user testing prep, human action record, share profile, engagement loop, orientation map layer.

### Phase 24 — Clarity & Meaning Refinement (completed 2026-03-12)
1. **World State Language** — Backend `_generate_field_narrative()` generates symbolic Hebrew sentences (no numbers). `GlobalFieldDashboard`, `FieldGlobeSection`, `EntryLayer` all display narrative.
2. **Opposition Engine Expansion** — 3 tension arcs (סדר↔כאוס, קולקטיב↔אגו, יציבות↔חקירה) with glowing position dots and interpretive Hebrew lines.
3. **Globe Readability** — Simplified header, dominant direction highlighted, fewer/calmer pulses.
4. **Performance** — Reduced intervals, limited ring accumulation, memoized computations.

### Phase 25 — Daily Base Allocation (completed 2026-03-12)
1. **Daily Base Selection** — User chooses one center each morning: לב (Heart), ראש (Head), or גוף (Body). Dark card UI with icons, selection glow, and potential allocations display. Saves to `daily_bases` collection.
   - Heart allocations: קשרים ומערכות יחסים, אמפתיה והקשבה, תרומה ונתינה, תיקון רגשי
   - Head allocations: סדר ותכנון, למידה וחקירה, קבלת החלטות, חשיבה אסטרטגית
   - Body allocations: תנועה ובריאות, פעולה מעשית, משמעת ומחויבות, סדר פיזי
2. **Gating Logic** — Daily question is blocked until base is selected. Gate message: "בחר בסיס יומי כדי להמשיך לפעולה".
3. **Compact Confirmed View** — After selection, shows "המרכז שלך היום" with base name + allocation tags.
4. **Enhanced End-of-Day Summary** — ClosingLayer now includes:
   - Chosen daily base with color indicator
   - Energy allocation bars (Heart/Head/Body distribution %)
   - Most active department, preferred department (historical), neglected department
5. **Direction → Department Mapping** — contribution→heart, recovery→body, order→head, exploration→head

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/orientation/daily-base/{user_id}` | GET | Today's base status + 3 definitions + dept history |
| `/api/orientation/daily-base/{user_id}` | POST | Set today's base (heart/head/body) |
| `/api/orientation/day-summary/{user_id}` | GET | Enhanced with dept_allocation, most_used/neglected/preferred dept |

New DB Collection: `daily_bases`

## Key API Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/orientation/field-dashboard` | GET | Field state + `field_narrative_he` |
| `/api/orientation/daily-base/{user_id}` | GET/POST | Daily base selection |
| `/api/orientation/day-summary/{user_id}` | GET | Day summary + dept analysis |
| `/api/orientation/globe-activity` | GET | Globe points data |
| `/api/profile/{user_id}/record` | GET | Profile + opposition_axes |
| `/api/orientation/daily-question/{user_id}` | GET | Daily question |
| `/api/orientation/daily-answer/{user_id}` | POST | Submit answer |
| `/api/admin/analytics` | GET | Admin dashboard |

## Database Collections
- `users`, `philos_decisions`, `demo_events`, `demo_agents`, `user_globe_points`
- `daily_questions`, `daily_missions`, `missions`, `circles`, `daily_bases`
- `invites`, `feedback`, `subscriptions`, `payment_transactions`

## Backlog

### P0 — Next Focus
- AI Interpretation layer (user requested, deferred to after base allocation)
- Continue real-user observation

### P1 — Technical Debt
- Refactor `server.py` into modular routes/models/services

### P2 — Future
- Base-aware daily question generation (questions influenced by chosen base)
- Department-specific insights in weekly reports
- Additional narrative templates based on time-of-day
- Private/group circles
