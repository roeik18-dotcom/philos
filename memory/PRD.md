# Philos Orientation - PRD

## Original Problem Statement
Build "Philos Orientation" — a sophisticated single-page decision engine and dashboard for real-time decision analysis and mental navigation. Hebrew (RTL) UI.

## Core Loop
**Base → Choice → Action → Field → Reflection**

## Architecture
- Frontend: React + Tailwind + Shadcn/UI | Backend: FastAPI + MongoDB | Auth: JWT

## Completed Features

### Phases 1–26 (prior)
Core dashboard, engagement, community, missions, UI polish, referral, validation, demo agents, theory, stabilization, globe, pulse, heartbeat, product rebuild, feed + value + subscription, social, circles, testing prep, profiles, share, engagement loop, orientation map, clarity & meaning, daily base allocation, base loop deepening.

### Phase 27 — Invite Code System (2026-03-12)
5 codes per user (PH-XXXX), optional on registration, influence chain tracking.

### Phase 28 — Invite Reward System (2026-03-12)
First action credit, notification, active invitee tracking, profile stats.

### Phase 29 — Human Action Record Redesign (2026-03-12)
Complete profile page redesign as a documentary "Human Action Record":

1. **Dark Theme** — Full dark background (#0a0a12), documentary feel, not social-media-like
2. **Hero Section** — Direction-colored initial, alias, location, member date, identity markers (direction + niche badges), "invited by" lineage
3. **Prominent Share** — "שתף רשומה" and "העתק קישור" buttons directly in hero, not hidden in top bar
4. **Stats Strip** — 4 clean metrics: Impact score, Total actions, Streak (ימים), Field Contribution %
5. **Field Contribution** — New backend field: `field_contribution.field_percentage` = user's actions as % of total field actions
6. **Direction Distribution** — Thin color bar with dominant direction highlighted, others dimmed
7. **Opposition Axes** — 3 tension arcs with glowing position dots matching HomeTab mirror style
8. **Influence Chain** — Full section: invited_by alias, invitees with count, active invitees, value credits
9. **Action Record** — Dark card design, expandable meanings (personal, social, value, system)
10. **Upgraded Share Card** — Includes stats strip (impact/actions/streak/field%), opposition axes, influence data (invitees/active/credits), Philos branding, profile URL

## Key API Endpoints
| Endpoint | Method | Returns |
|---|---|---|
| `/api/profile/{user_id}/record` | GET | identity, action_record, opposition_axes, value_growth, direction_distribution, **field_contribution**, influence_chain |
| `/api/orientation/invite-stats/{user_id}` | GET | codes, credits, active_invitees |
| `/api/orientation/daily-answer/{user_id}` | POST | action + invite reward trigger |
| `/api/orientation/daily-base/{user_id}` | GET/POST | base selection |
| `/api/orientation/daily-question/{user_id}` | GET | base-influenced question |
| `/api/orientation/day-summary/{user_id}` | GET | summary + dept + reflection |
| `/api/orientation/field-dashboard` | GET | field narrative |

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
