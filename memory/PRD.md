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
Core dashboard, engagement features, community layer, field missions, UI polish, referral leaderboard, product validation, demo agents, core theory, stabilization, globe interaction, field pulse, heartbeat, product rebuild, orientation feed + value engine + subscription, social expansion, circle detail, real-user testing prep, human action record, share profile, engagement loop, orientation map.

### Phase 24 — Clarity & Meaning Refinement (completed 2026-03-12)
1. **World State Language** — Symbolic Hebrew narrative sentences, no numbers
2. **Opposition Engine** — 3 tension arcs with glowing position dots
3. **Globe Readability** — Simplified header, fewer/calmer pulses
4. **Performance** — Reduced intervals, limited ring accumulation

### Phase 25 — Daily Base Allocation (completed 2026-03-12)
1. **Base Selection** — לב (Heart), ראש (Head), גוף (Body) with dark card UI
2. **Gating Logic** — Daily question blocked until base is selected
3. **Department Tracking** — Direction→Department mapping, energy allocation bars
4. **Enhanced Summary** — Most active, preferred, neglected departments

### Phase 26 — Base Loop Deepening (completed 2026-03-12)
1. **Base → Daily Question** — Chosen base influences question content (body→physical, heart→relational, head→thinking)
2. **Base Reflection** — End-of-day observational sentence comparing intention vs action

### Phase 27 — Invite Code System (completed 2026-03-12)
1. **Invite Code Generation** — Each user gets 5 codes in `PH-XXXX` format (e.g. PH-A3K9)
   - Auto-generated on registration and first login for existing users
   - `MAX_INVITE_CODES = 5` per user
2. **Registration with Invite Code** — Optional `invite_code` field on registration
   - Validates code exists, links inviter→invitee relationship
   - Invalid codes rejected with Hebrew error message
   - `invited_by` field stored on user document
3. **Invite Stats** — `/api/orientation/invite-stats/{user_id}` returns:
   - All codes with used/unused status
   - Remaining code count
   - Total successful invites
   - Who invited this user (alias)
   - List of invitees (aliases)
4. **Influence Chain on Profile** — `/api/profile/{user_id}/record` returns `influence_chain`
   - ProfilePage shows "הוזמן על ידי [alias]" in identity header
   - InfluenceChain section shows inviter and invitees
5. **InviteSection Rewrite** — Shows:
   - Stats (used/remaining counts)
   - First unused code with copy button
   - Expandable all-codes list
   - "Invited by" badge if user was invited
   - Invitees list showing who they brought

## Key API Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/auth/register` | POST | Register with optional invite_code |
| `/api/auth/login` | POST | Login + auto-generate codes for existing users |
| `/api/orientation/invite-stats/{user_id}` | GET | Full invite stats + influence chain |
| `/api/orientation/create-invite/{user_id}` | POST | Create new code (respects limit) |
| `/api/orientation/invite/{code}` | GET | Validate code + get inviter alias |
| `/api/orientation/daily-base/{user_id}` | GET/POST | Daily base selection |
| `/api/orientation/daily-question/{user_id}` | GET | Base-influenced daily question |
| `/api/orientation/day-summary/{user_id}` | GET | Summary + dept + base_reflection_he |
| `/api/orientation/field-dashboard` | GET | Field state + narrative |
| `/api/profile/{user_id}/record` | GET | Profile + influence_chain |
| `/api/admin/analytics` | GET | Admin dashboard |

## Database Collections
- `users` (id, email, password_hash, invited_by, created_at)
- `invites` (code, inviter_id, used_by[], use_count, opened_count)
- `daily_bases`, `daily_questions`, `philos_decisions`
- `demo_events`, `demo_agents`, `user_globe_points`
- `daily_missions`, `missions`, `circles`
- `feedback`, `subscriptions`, `payment_transactions`

## Backlog

### P0 — Next Focus
- AI Interpretation layer (deferred — interprets through Philos framework)
- Real-user observation and retention analysis

### P1 — Technical Debt
- Refactor `server.py` into modular routes/models/services

### P2 — Future
- Value credit rewards when invitee completes first action
- Department-specific weekly insights
- Time-of-day narrative variations
- Private/group circles
