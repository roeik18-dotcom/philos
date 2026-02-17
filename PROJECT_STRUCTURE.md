# Community Help Platform - Project Structure

## 📁 Project Overview

Hebrew RTL community help platform with Supabase backend, status tracking, and trust metrics.

## 🗂️ Directory Structure

```
/app/
├── frontend/                      # React frontend application
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── ui/              # Shadcn UI components
│   │   │   ├── BottomNav.js     # 4-item navigation (בית, הבקשות שלי, היסטוריה, פרופיל)
│   │   │   ├── CategoryCard.js  # גוף/רגש/מחשבה selection cards
│   │   │   ├── RequestCard.js   # Request display with Accept button
│   │   │   ├── Timer.js         # Circular countdown timer
│   │   │   ├── DailySummary.js  # Daily stats (עזרתי/התחלתי/לא עזרתי)
│   │   │   └── CreateRequestModal.js  # "צריך עזרה?" form modal
│   │   │
│   │   ├── pages/               # Main application pages
│   │   │   ├── HomePage.js      # Category selection + request flow
│   │   │   ├── MyRequestsPage.js  # User's created requests with status
│   │   │   ├── HistoryPage.js   # Past help activities with repeat badges
│   │   │   └── ProfilePage.js   # Stats + trust metrics
│   │   │
│   │   ├── lib/
│   │   │   ├── supabase.js      # Supabase client + API functions
│   │   │   └── utils.js         # Utility functions
│   │   │
│   │   ├── data/
│   │   │   ├── requests.js      # Preset community requests (fallback)
│   │   │   └── tasks.js         # Legacy task library
│   │   │
│   │   ├── hooks/
│   │   │   ├── useLocalStorage.js  # Persistent storage hook
│   │   │   └── use-toast.js     # Toast notifications
│   │   │
│   │   ├── App.js               # Main app component
│   │   ├── index.js             # React entry point
│   │   ├── App.css              # Component styles
│   │   └── index.css            # Global styles + Hebrew fonts (Rubik, Heebo)
│   │
│   ├── public/
│   │   ├── index.html
│   │   └── demo-trust-data.html  # Test data for trust metrics
│   │
│   ├── package.json             # Dependencies (@supabase/supabase-js, etc.)
│   ├── tailwind.config.js       # Custom colors (sage, clay, dusty blue)
│   ├── postcss.config.js
│   └── .env.example             # Environment template
│
├── backend/
│   ├── server.py                # FastAPI server (minimal, for future use)
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Backend environment template
│
├── supabase-setup.sql           # Complete DB schema + RLS policies
├── SUPABASE_SETUP.md            # Step-by-step setup guide
├── SUPABASE_IMPLEMENTATION.md   # Technical documentation
└── README.md                    # Project overview

```

## 🎨 Design System

### Colors
- **Background**: #F9F7F2 (Warm Alabaster)
- **Foreground**: #4A4238 (Deep Mocha)
- **Body Category**: #A7C4BC (Sage Green)
- **Emotion Category**: #D4A5A5 (Clay Rose)
- **Mind Category**: #A0C1D1 (Dusty Blue)

### Typography
- **Headings/Buttons**: Rubik (Hebrew support)
- **Body Text**: Heebo
- **Direction**: RTL (right-to-left)

### Key Components
- Minimal & calm aesthetic
- Soft neutral colors
- Rounded corners (1.5rem)
- Glass-morphism effects
- Mobile-first responsive

## 🗄️ Database Schema

### Table: `requests`
```sql
id              uuid PRIMARY KEY
created_at      timestamptz
device_id       text (identifies creator)
name            text (first name)
category        'body' | 'emotion' | 'mind'
description     text (help needed)
minutes         int (1-120)
distance        text (optional)
status          'waiting' | 'accepted' | 'in_progress' | 'completed'
accepted_at     timestamptz
in_progress_at  timestamptz
completed_at    timestamptz
```

### Indexes
- `requests_status_idx` on status
- `requests_device_idx` on device_id
- `requests_created_idx` on created_at DESC

## 🔄 Request Lifecycle

```
waiting → accepted → in_progress → completed
   ↓          ↓           ↓            ↓
ממתינה    התקבלה      בדרך        הושלמה
```

### State Guards
- **Accept**: Only if status='waiting' (prevents double-accept)
- **Start**: Only if status='accepted' (prevents invalid start)
- **Finish**: Only if status='in_progress' (ensures proper flow)

## 🔑 Key Features

### v1 (Current)
- ✅ Community request creation (no auth)
- ✅ Device-based identification (UUID in localStorage)
- ✅ FIFO queue (oldest request shown first)
- ✅ Real-time status updates (10s polling)
- ✅ Trust metrics (repeat request tracking)
- ✅ Hebrew RTL UI
- ✅ Status transition guards
- ✅ Duplicate prevention

### Navigation Pages
1. **בית (Home)**: Category selection → Request → Timer → Summary
2. **הבקשות שלי (My Requests)**: Track your created requests
3. **היסטוריה (History)**: Past help activities with repeat badges
4. **פרופיל (Profile)**: Stats + trust metrics

## 🛠️ Setup Instructions

1. **Install Dependencies**
   ```bash
   cd /app/frontend && yarn install
   cd /app/backend && pip install -r requirements.txt
   ```

2. **Configure Supabase**
   - Create project at supabase.com
   - Run `/app/supabase-setup.sql` in SQL Editor
   - Copy URL + anon key to `/app/frontend/.env`

3. **Environment Variables**
   ```bash
   cp frontend/.env.example frontend/.env
   cp backend/.env.example backend/.env
   # Edit .env files with your values
   ```

4. **Start Services**
   ```bash
   sudo supervisorctl restart frontend
   sudo supervisorctl restart backend
   ```

## 📦 Dependencies

### Frontend
- React 18
- @supabase/supabase-js
- Tailwind CSS
- Shadcn UI components
- lucide-react (icons)
- date-fns (date handling)

### Backend
- FastAPI
- uvicorn
- python-dotenv
- pymongo (if using MongoDB for stats)

## 🔐 Security (v1)

- ✅ Row Level Security (RLS) enabled
- ✅ Public policies (pilot version)
- ⚠️ No user authentication yet
- ⚠️ Device ID only (not secure for production)

### Future (v2)
- Add user authentication
- Restrict RLS policies
- Real-time subscriptions (no polling)
- Push notifications

## 🧪 Testing

See `SUPABASE_IMPLEMENTATION.md` for detailed testing flows.

## 📝 Notes

- Hebrew UI throughout
- Mobile-first design
- Local storage for device ID
- Supabase for shared requests
- Auto-refresh every 10 seconds
- State machine enforced at DB level
