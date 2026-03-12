# Philos Orientation - PRD

## Original Problem Statement
Build "Philos Orientation" — a sophisticated single-page decision engine and dashboard for real-time decision analysis and mental navigation. The UI is in **Hebrew (RTL)**.

## Core Architecture
- **Frontend:** React (CRA) with Tailwind CSS, Shadcn/UI, Lucide icons
- **Backend:** FastAPI + MongoDB
- **Auth:** JWT-based custom auth + anonymous user flow
- **Language:** Hebrew RTL

## Core Loop
**Base → Choice → Action → Field → Reflection**

## Completed Features

### Phases 1–23 (completed prior sessions)
Core dashboard, engagement features, community layer, field missions, UI polish, referral leaderboard, product validation, demo agents, core theory integration, stabilization, globe interaction, field pulse, field heartbeat, product structure rebuild, orientation feed + value engine + subscription, social field expansion, circle detail view, real-user testing prep, human action record, share profile, engagement loop, orientation map layer.

### Phase 24 — Clarity & Meaning Refinement (completed 2026-03-12)
1. **World State Language** — `_generate_field_narrative()` generates symbolic Hebrew sentences (no numbers)
2. **Opposition Engine** — 3 tension arcs with glowing position dots and interpretive lines
3. **Globe Readability** — Simplified header, dominant direction highlighted, fewer pulses
4. **Performance** — Reduced intervals, limited ring accumulation

### Phase 25 — Daily Base Allocation (completed 2026-03-12)
1. **Base Selection** — לב (Heart), ראש (Head), גוף (Body) with dark card UI, allocations display
2. **Gating Logic** — Daily question blocked until base is selected
3. **Department Tracking** — Direction→Department mapping, energy allocation bars in end-of-day
4. **Enhanced Summary** — Most active, preferred, neglected departments

### Phase 26 — Base Loop Deepening (completed 2026-03-12)
1. **Base → Daily Question** — Chosen base influences the daily question:
   - גוף → physical/practical: "עשה פעולה פיזית קטנה שמסדרת משהו סביבך", "סדר פינה אחת בסביבה שלך"
   - לב → relational/emotional: "שלח מילה טובה למישהו שלא ציפה לזה", "הקשב למישהו היום — באמת הקשב"
   - ראש → thinking/exploring: "מצא דבר אחד חדש שלא שמת לב אליו קודם", "קבל החלטה אחת שדחית"
   - Questions are one-sentence, simple, actionable — no theory
2. **Base Reflection** — End-of-day `base_reflection_he` observational sentence:
   - Alignment: "בחרת לפעול מהלב, והפעולות שלך היום תאמו את הבחירה."
   - Misalignment: "בחרת לפעול מהלב, אך רוב הפעולות היום נעו לכיוון הראש."
   - Mirror, not teacher — observational, short

## Key API Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/orientation/field-dashboard` | GET | Field state + `field_narrative_he` |
| `/api/orientation/daily-base/{user_id}` | GET/POST | Daily base selection |
| `/api/orientation/daily-question/{user_id}` | GET | Base-influenced daily question |
| `/api/orientation/daily-answer/{user_id}` | POST | Submit answer |
| `/api/orientation/day-summary/{user_id}` | GET | Day summary + dept analysis + base_reflection_he |
| `/api/orientation/globe-activity` | GET | Globe points data |
| `/api/profile/{user_id}/record` | GET | Profile + opposition_axes |
| `/api/admin/analytics` | GET | Admin dashboard |

## Database Collections
- `users`, `philos_decisions`, `demo_events`, `demo_agents`, `user_globe_points`
- `daily_questions`, `daily_missions`, `missions`, `circles`, `daily_bases`
- `invites`, `feedback`, `subscriptions`, `payment_transactions`

## Backlog

### P0 — Next Focus
- AI Interpretation layer (deferred — interprets through Philos framework)
- Real-user observation and retention analysis

### P1 — Technical Debt
- Refactor `server.py` into modular routes/models/services

### P2 — Future
- Department-specific weekly insights
- Time-of-day narrative variations
- Private/group circles
