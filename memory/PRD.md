# Philos Orientation - Product Requirements Document

## Original Problem Statement
Build a comprehensive "Value + Risk + Trust" system for the "Philos Orientation" application. The project has evolved through implementation of the V+R+T engine, full Hebrew-to-English translation, and now an investor-facing visual platform landing page.

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + Pydantic + MongoDB
- **AI**: Claude Sonnet 4.5 via `emergentintegrations`
- **Visualization**: react-globe.gl, three.js, CSS animations
- **Payments**: Stripe
- **Scheduling**: APScheduler

## Routing
- `/` — Platform landing page (investor-facing, primary entry)
- `/trust-test` — Public trust test flow
- `/dashboard` — Authenticated user dashboard
- `/admin` — Admin panel
- `/profile/{id}` — User profile
- `/invite/{code}` — Invite page

## What's Been Implemented

### Core System (Complete)
- Full V+R+T reputation engine
- User auth, orientation map, daily questions
- Decision path, identity, collective field
- Social features, globe, invite system

### Full English Translation (Complete)
- All frontend and backend translated from Hebrew to English
- LTR layout, English fonts

### Platform Landing Page (Complete - March 2026)
- Dark futuristic design with animated nodes
- 13-node system chain: Cosmos → Space → Matter → Energy → Motion → Life → Human → Forces → Conflict → Orientation → Decision → Action → Impact
- Globe-style layered visualization (Cosmos/Life/Human rings)
- Flow diagrams: Directional Forces, Fundamental Contradictions, Orientation Engine
- Investor sections: Problem → Model → System Engine → Application → Vision
- CTA buttons linking to /trust-test
- Scroll-reveal animations via IntersectionObserver
- Files: PlatformLandingPage.js, platform.css

### SEO & Indexing (Complete - March 2026)
- sitemap.xml for all public pages (/, /trust-test)
- robots.txt allowing all crawlers
- Google Analytics GA4 (G-5MNK51HSQ1) active
- Google Search Console verification tag active
- Updated meta title, description, keywords
- Open Graph tags (og:title, og:description, og:type, og:url, og:site_name, og:locale)
- Twitter Card meta tags
- Canonical URL tag
- Files: sitemap.xml, robots.txt, index.html

### Product MVP (Complete - March 2026)
- 5 pages built under `/app` routes with shared layout and navigation
- `/app/feed` — Action Feed with category filters, action cards (title, description, category, location, contributor, community, timestamp)
- `/app/post` — Post Action form (auth required) with Title, Description, Category, Community, Location + geolocation detect
- `/app/map` — Impact Map using Leaflet + dark CartoCDN tiles, colored markers by category, popups with action details
- `/app/profile` — User profile with avatar, stats (Actions, Impact Score, Verified), contribution categories, communities
- `/app/dashboard` — Daily dashboard with summary stats, network activity, suggested actions
- Auth gating: Post/Profile/Dashboard require sign-in
- Full E2E flow verified: Post → Feed → Map
- Mobile responsive with bottom tab bar
- OG image (1200x630) for social sharing added
- Files: ProductApp.js, ActionFeed.js, PostAction.js, ImpactMap.js, ProductProfile.js, DailyDashboard.js, app.css

### Reactions & Trust Score System (Complete - March 2026)
- 3 reaction types on every action card: Support (+1), Useful (+2), Verified (+5)
- Toggle on/off with optimistic UI updates
- Trust Score per action (displayed as badge when > 0)
- Aggregate Trust Score per user in profile
- Feed endpoint supports viewer_id for user_reacted flags
- Profile shows 4 stats: Trust Score, Actions, Impact Score, Verified
- Files modified: ActionFeed.js, ProductProfile.js, app.css, actions.py

### Share Action Feature (Complete - March 2026)
- Share button on every feed card opens modal with preview (user, title, community, trust score)
- 4 share options: Copy Link, WhatsApp, LinkedIn, Twitter/X
- Shareable action page at /app/action/{id} with full preview card
- Backend GET /api/actions/{action_id} endpoint for single action lookup
- Files: ActionFeed.js (ShareModal), ActionSharePage.js, app.css, actions.py

### Dynamic OG Tags (Complete - March 2026)
- Backend-rendered HTML at /api/share/action/{id} with dynamic OG + Twitter meta tags
- Server-side OG image generation (1200x630) with Pillow: avatar, title, community, trust score, Philos branding
- Social share URLs updated to use /api/share/action/{id} for WhatsApp/LinkedIn/Twitter
- Meta refresh redirect to SPA for real users
- Files: og_share.py

### Opportunity System (Complete - March 2026)
- 8 seeded opportunities (jobs, grants, collaborations, support) with trust score requirements
- /app/opportunities page with type filters and Eligible/Locked status
- Progress bar shows unlock count
- Opportunities preview in user profile (top 3)
- Files: opportunities.py, OpportunitiesPage.js, ProductProfile.js

### Community Funds (Complete - March 2026)
- 5 seeded communities with fund data (raised, distributed, balance)
- /app/community-funds leaderboard with expandable transaction history
- Summary stats: total raised, distributed, balance
- Files: community.py, CommunityFundsPage.js

### Leaderboard (Complete - March 2026)
- /app/leaderboard with users ranked by trust score (MongoDB aggregation)
- Top 3 podium display
- Per-user stats: trust score, total actions, categories
- Files: leaderboard.py, LeaderboardPage.js

### Weekly Impact Report (Complete - March 2026)
- /app/report (auth required) with weekly summary
- Stats: week actions, trust earned, total trust, rank, categories, communities
- Network-wide stats: active users, total actions, trust generated
- All-time summary with rank
- Files: leaderboard.py, WeeklyReportPage.js

## Prioritized Backlog
### P2: Expand Trust-Aware AI
### P2: Define and Map Risk Signals
### P3: ProfilePage Refactoring
### P3: Legacy Hebrew DB Data Migration

## Test Credentials
- Email: `newuser@test.com` | Password: `password123`
