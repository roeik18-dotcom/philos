# Philos Orientation - Product Requirements Document
## Mental Navigation System

**Last Updated:** December 2025  
**Status:** Stable MVP Complete  
**Preview URL:** https://decision-engine-47.preview.emergentagent.com

---

## Original Problem Statement

Build a complex, client-side decision engine and dashboard called "Philos Orientation." The application serves as a sophisticated single-page tool for real-time decision analysis and mental navigation.

### Core Requirements (All Completed ✅)
- Interactive decision map to visualize decision states
- Suggestion engine for optimal actions
- Decision history and trajectory tracking
- Personal, Collective, and Global value maps
- Session persistence (localStorage + cloud backend)
- Session Library to browse, load, and delete past sessions
- Value Constellation Map visualization
- Session Comparison Engine
- Weekly Cognitive Report
- Decision Path Engine with path suggestions
- User Authentication for cross-device sync

### User Language & UI
- **User Communication:** English
- **UI Language:** Hebrew (עִבְרִית)
- **Layout:** Right-to-Left (RTL)

---

## Implemented Features

### Phase 1: Core Engine ✅
- [x] Event Zero state (physical_capacity, chaos_order, ego_collective, gap_type)
- [x] Action evaluation with decision outcomes
- [x] Value tagging system (contribution, recovery, order, harm, avoidance)
- [x] Balance score calculation
- [x] Suggested vector toward optimal zone

### Phase 2: Decision Path Engine ✅
- [x] 3 suggested action paths generation
- [x] Deterministic algorithm with value preferences
- [x] Predicted metrics display
- [x] Best path highlighting ("מומלץ")
- [x] Risky path marking ("מסוכן")

### Phase 3: Path Learning Layer ✅
- [x] Path selection tracking
- [x] Predicted vs actual comparison
- [x] Match quality assessment
- [x] Hebrew insights generation

### Phase 4: Adaptive Path Engine ✅
- [x] Learning history storage
- [x] Adaptive scoring rules
- [x] Score boosts and penalties
- [x] Decision Path Engine integration

### Phase 5: Persistent Memory Layer ✅
- [x] MongoDB cloud storage
- [x] LocalStorage fallback
- [x] Anonymous user_id support
- [x] API endpoints for all data types

### Phase 6: User Authentication ✅
- [x] Email/password registration
- [x] JWT token authentication
- [x] Password hashing (bcrypt)
- [x] Anonymous data migration
- [x] Hebrew RTL auth screen

### Phase 7: Multi-Device Continuity ✅
- [x] Full data hydration on login
- [x] Cross-device sync
- [x] "מסונכרן בין מכשירים" status
- [x] Logout state preservation

### Phase 8: Collective Layer ✅
- [x] Cross-user aggregated analytics
- [x] Value distribution visualization
- [x] Dominant value/direction indicators
- [x] Hebrew insights

### Phase 9: Collective Trends ✅
- [x] Time-based trends (14-day history)
- [x] SVG sparkline visualizations
- [x] Period comparison (7 days vs 7 days)
- [x] Change indicators
- [x] Hebrew trend insights

### Phase 10: Global Field Visualization ✅
- [x] SVG-based living value system map
- [x] Chaos/Order and Ego/Collective axes
- [x] Harm pressure and recovery zones
- [x] Animated direction indicator (pulsing dot)
- [x] Field state assessment (healthy/tense/organized/balanced)
- [x] Hebrew insights based on collective data
- [x] Real-time data from /api/collective/layer

### Phase 11: Data Generation Layer ✅
- [x] Multiple decisions per session (50 max)
- [x] Auto-save every decision to MongoDB
- [x] Decision frequency tracking
- [x] Floating Quick Decision button with templates
- [x] Decision Chains with parent_decision_id
- [x] Decision History Section
- [x] Decision Tree Visualization
- [x] Chain Insights Section
- [x] Weekly Behavioral Report
- [x] Monthly Progress Report
- [x] Quarterly Review Section
- [x] Daily Decision Prompt (rotating questions)

---

## Architecture Summary

```
Frontend:  React 18 + Tailwind CSS + Shadcn/UI
Backend:   FastAPI + Motor (async MongoDB)
Database:  MongoDB
Auth:      JWT + bcrypt
State:     Custom Hook (usePhilosState)
```

### Key Files
- `usePhilosState.js` - Central state management (~830 lines)
- `PhilosDashboard.js` - Main dashboard (~270 lines)
- `cloudSync.js` - Cloud sync service (~400 lines)
- `server.py` - FastAPI backend (~1650 lines)
- `sections/` - 20 UI components (including GlobalFieldSection)

---

## Future Backlog (P2)

1. **Password Reset** - Forgot password functionality
2. **Email Verification** - Verify email on registration
3. **Export/Import** - Session data portability
4. **Advanced Analytics** - Enhanced dashboard views
5. **PWA Support** - Mobile-optimized experience

---

## Changelog

### March 8, 2026
- ✅ Implemented Decision Path Engine
- ✅ Implemented Path Learning Layer
- ✅ Implemented Adaptive Path Engine
- ✅ Implemented Persistent Memory Layer
- ✅ Implemented User Authentication
- ✅ Refactored state management to usePhilosState hook
- ✅ Implemented Multi-Device Continuity
- ✅ Implemented Collective Layer Phase 1
- ✅ Implemented Collective Layer Phase 2 (Trends)
- ✅ Implemented Global Field Visualization
- ✅ Implemented Data Generation Layer (auto-save, frequency tracking, quick input)
- ✅ Created PROJECT_SNAPSHOT.md

---

**Product State:** STABLE MVP - All core features complete
