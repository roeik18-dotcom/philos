# Supabase Setup Guide

## Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Sign up / Sign in
3. Click "New Project"
4. Fill in:
   - Name: `community-help` (or any name)
   - Database Password: (save this somewhere safe)
   - Region: Choose closest to your users
5. Wait ~2 minutes for project to be created

## Step 2: Create Database Table

1. In your Supabase project dashboard, click "SQL Editor" in the left sidebar
2. Click "New Query"
3. Copy the entire contents of `/app/supabase-setup.sql`
4. Paste into the SQL editor
5. Click "Run" or press Ctrl/Cmd + Enter
6. You should see "Success. No rows returned"

## Step 3: Get API Credentials

1. Click "Settings" (gear icon) in left sidebar
2. Click "API" under Project Settings
3. Copy two values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: Long string starting with `eyJhbG...`

## Step 4: Add Credentials to .env

1. Open `/app/frontend/.env`
2. Replace the placeholder values:

```bash
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3M...
```

3. Save the file

## Step 5: Restart Frontend

```bash
sudo supervisorctl restart frontend
```

Wait ~10 seconds, then test the app!

## Verify It's Working

1. Click "צריך עזרה?" and create a request
2. Go to Supabase dashboard → Table Editor → `requests`
3. You should see your request appear!
4. Click "הבקשות שלי" to see your requests
5. Have another device/browser accept the request
6. Refresh "הבקשות שלי" to see status update

## Troubleshooting

### "Missing Supabase credentials" error
- Check that `.env` has correct values
- Make sure no extra spaces around the `=` sign
- Restart frontend after changing .env

### Requests not showing
- Check browser console (F12) for errors
- Verify SQL setup ran successfully
- Check Row Level Security policies are created

### Status not updating
- Make sure you're using the same Supabase project
- Check browser console for API errors
- Try the "רענן" (refresh) button in My Requests page

## Security Notes (for v1)

- ✅ anon key is safe to expose (it's designed for frontend)
- ✅ Row Level Security (RLS) is enabled with open policies
- ⚠️  In v2, add user authentication and restrict policies
- ⚠️  Current setup allows anyone to read/write all requests

## Database Schema

The `requests` table has:
- `id`: UUID (auto-generated)
- `device_id`: Identifies which device created it
- `name`: Requester's first name
- `category`: body/emotion/mind  
- `description`: What help is needed
- `minutes`: Estimated duration
- `distance`: Optional distance
- `status`: waiting/accepted/in_progress/completed
- Timestamps: created_at, accepted_at, in_progress_at, completed_at
