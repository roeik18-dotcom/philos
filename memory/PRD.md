# Philos Orientation - PRD

## Original Problem Statement
Build "Philos Orientation" — a sophisticated single-page decision engine and dashboard for real-time decision analysis and mental navigation. Hebrew (RTL) UI.

## Core Loop
**Base → Choice → Action → Field → Reflection**

## Architecture
- Frontend: React + Tailwind + Shadcn/UI | Backend: FastAPI + MongoDB | Auth: JWT

## Completed Features

### Phases 1–23 (prior sessions)
Core dashboard, engagement, community, missions, UI polish, referral, validation, demo agents, theory, stabilization, globe, pulse, heartbeat, product rebuild, feed + value + subscription, social, circles, testing prep, profiles, share, engagement loop, orientation map.

### Phase 24 — Clarity & Meaning (2026-03-12)
Symbolic narrative, opposition tension mirror, globe readability, performance.

### Phase 25 — Daily Base Allocation (2026-03-12)
Base selection (לב/ראש/גוף), gating logic, department tracking.

### Phase 26 — Base Loop Deepening (2026-03-12)
Base-influenced questions, base reflection sentence.

### Phase 27 — Invite Code System (2026-03-12)
5 codes per user (PH-XXXX), optional on registration, influence chain tracking.

### Phase 28 — Invite Reward System (2026-03-12)
1. **First Action Credit** — When invitee completes first daily action → inviter gets 1 value credit
   - Triggers on `daily_questions.answered == True` count <= 1
   - Double-credit prevention via `invite_rewards` collection check
   - NOT on signup — only on first action
2. **Notification** — Invitee sees "הפעולה הראשונה שלך העניקה נקודת ערך ל{alias}" in DailyOrientationQuestion impact area
3. **Active Invitee Tracking** — `invite-stats` returns per-invitee active status (based on daily_questions answered count)
4. **Profile Stats** — InviteSection shows 4 metrics: joined, active, credits, remaining. ProfilePage InfluenceChain shows active_invitees count and invite_credits.

## Key API Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| `/api/auth/register` | POST | Register with optional invite_code |
| `/api/orientation/invite-stats/{user_id}` | GET | Codes + credits + active invitees |
| `/api/orientation/daily-answer/{user_id}` | POST | Action + invite reward trigger |
| `/api/orientation/daily-base/{user_id}` | GET/POST | Base selection |
| `/api/orientation/daily-question/{user_id}` | GET | Base-influenced question |
| `/api/orientation/day-summary/{user_id}` | GET | Summary + dept + reflection |
| `/api/orientation/field-dashboard` | GET | Field narrative |
| `/api/profile/{user_id}/record` | GET | Profile + influence chain + credits |

## DB Collections
users, invites, invite_rewards, daily_bases, daily_questions, philos_decisions, philos_sessions, demo_events, demo_agents, user_globe_points, daily_missions, missions, circles, feedback, subscriptions, payment_transactions

## Backlog
### P0
- AI Interpretation layer (deferred)
- Real-user observation
### P1
- Refactor server.py into modules
### P2
- Department weekly insights
- Time-of-day narratives
- Private/group circles
