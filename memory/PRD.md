# Philos Orientation - Product Requirements Document

## Original Problem Statement
Create a mindfulness/decision-making app that evolved into the **Philos Orientation** system - a comprehensive mental navigation and decision engine with visual dashboard.

## Current State (December 2025)

### What's Implemented ✅

#### Core Decision Engine
- Action evaluation with value tagging
- Decision computation (Allowed/Blocked)
- Balance Score calculation: `100 - (|chaos_order| + |ego_collective|)`
- Trajectory tracking and projection
- Smart fallbacks based on gap_type

#### Dashboard UI (`/app/frontend/src/pages/PhilosDashboard.js`)
- **Header**: Title, tagline, session counter, Reset Session button
- **State Sliders**: Gap type, Physical Capacity, Chaos/Order, Ego/Collective
- **Emotional State**: Calm/Stressed/Confused buttons that adjust chaos_order
- **Micro Actions**: Quick energy recovery buttons (+10 energy)
- **Quick Actions**: Pre-defined action buttons
- **Action Evaluation**: Text input + Evaluate Decision button
- **Decision Display**: Status, projection values, Value Tag badge
- **Decision Explanation**: Reasoning for the decision
- **Suggested Actions**: Vector suggestion when outside optimal zone
- **Orientation Status Panel**: Order, Collective, Energy, Balance Score
- **Suggested Stabilizing Actions**: Appears when balance < 30
- **Recover Energy**: Buttons that increase physical_capacity
- **Daily Loop**: Visual workflow guide
- **Decision Map**: 2D visualization with animated dot, trajectory path, suggestion arrow
- **Decision History**: Last 20 decisions with time, action, status
- **Session Summary**: Actions count, Balance Score, Trajectory, Energy status
- **Personal Map**: Direction indicators, Top Values, Decision Timeline, Value Graph, Your Pattern
- **Orientation Field**: Order Drift, Collective Drift, Harm Pressure, Recovery Stability
- **Collective Value Map**: Value distribution circles, Collective Pattern summary
- **Share Card**: Modal with downloadable PNG card
- **Export Session**: Download JSON data

#### Value Tag System
- **contribution**: help, support, friend, give, assist, share, care
- **recovery**: walk, breathe, stretch, water, rest, sleep, pause
- **harm**: angry, attack, insult, shout, hurt, revenge, fight
- **order**: organize, clean, plan, focus, work, structure, sort
- **avoidance**: ignore, avoid, delay, scroll, escape, postpone

#### Data Persistence
- localStorage saving/loading
- Session state preservation across page reloads
- Reset Session functionality with confirmation

#### Visualizations
- Decision Map with animated dot movement
- Trajectory path connecting previous decisions
- Suggestion vector arrow toward optimal zone
- Optimal zone glow when balanced
- Value Graph with clustered nodes by value_tag
- Mini timeline bars for decision history
- Clustered circles for value distribution

### Technical Stack
- **Frontend**: React 18, Tailwind CSS
- **Visualization**: SVG-based graphics
- **Persistence**: localStorage
- **Export**: html-to-image for PNG, JSON download

### Architecture
```
/app/frontend/src/
├── pages/
│   └── PhilosDashboard.js  # Main app (~1500 lines)
├── components/
│   └── philos/
│       └── DecisionMap.js  # 2D map visualization
└── App.js
```

## Key Metrics

### Balance Score
- Formula: `100 - (|chaos_order| + |ego_collective|)`
- Green (≥70): Balanced
- Yellow (40-69): Unstable
- Red (<40): Conflict

### Orientation Field Metrics
- **Order Drift**: (order + recovery) - (harm + avoidance)
- **Collective Drift**: contribution - harm
- **Harm Pressure**: harm / total decisions
- **Recovery Stability**: recovery / total decisions

### Optimal Zone
- Order: 20-60
- Collective: 10-50

## Completed Features (This Session)

1. ✅ Fixed blank page bug
2. ✅ Simplified Action Evaluation flow
3. ✅ Added Decision Explanation
4. ✅ Added Decision History (20 items)
5. ✅ Added Trajectory Map with animated dots
6. ✅ Added Vector Suggestion Engine
7. ✅ Added Vector Arrow on Decision Map
8. ✅ Added Orientation Status Panel
9. ✅ Added Reset Session button
10. ✅ Added Quick Demo Actions
11. ✅ Added Emotional State buttons
12. ✅ Added Micro Actions for energy recovery
13. ✅ Added Balance Score with color coding
14. ✅ Added Suggested Stabilizing Actions
15. ✅ Added Recover Energy section
16. ✅ Added Daily Loop visualization
17. ✅ Updated header with tagline
18. ✅ Added Session Summary
19. ✅ Added Export Session (JSON)
20. ✅ Added Share Card with PNG download
21. ✅ Added Personal Map with Value Graph
22. ✅ Added Collective Value Map
23. ✅ Added Orientation Field metrics
24. ✅ Improved value_tag detection
25. ✅ Added session persistence (localStorage)

## Backlog / Future Tasks

### P1 - High Priority
- [ ] User authentication
- [ ] Cloud sync for session data
- [ ] Multi-device support

### P2 - Medium Priority
- [ ] Social features (share with community)
- [ ] Global value map across users
- [ ] Historical trend analysis
- [ ] Weekly/monthly reports

### P3 - Low Priority
- [ ] Mobile app (React Native)
- [ ] Notifications/reminders
- [ ] Integration with calendar
- [ ] AI-powered suggestions

## Preview URL
https://orientation-map-1.preview.emergentagent.com
