-- Supabase table setup for community help requests
-- Run this in Supabase SQL Editor

create table if not exists public.requests (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),

  device_id text not null,           -- מי יצר (ללא לוגין)
  name text not null,                -- שם פרטי מבקש
  category text not null check (category in ('body','emotion','mind')),
  description text not null,
  minutes int not null check (minutes between 1 and 120),
  distance text,

  status text not null default 'waiting'
    check (status in ('waiting','accepted','in_progress','completed')),

  accepted_at timestamptz,
  in_progress_at timestamptz,
  completed_at timestamptz
);

create index if not exists requests_status_idx on public.requests(status);
create index if not exists requests_device_idx on public.requests(device_id);
create index if not exists requests_created_idx on public.requests(created_at desc);

-- Enable Row Level Security
alter table public.requests enable row level security;

-- כולם יכולים לקרוא בקשות (כדי לראות "ממתינה")
create policy "public read requests"
on public.requests
for select
to anon
using (true);

-- כולם יכולים ליצור בקשה
create policy "public insert requests"
on public.requests
for insert
to anon
with check (true);

-- כולם יכולים לעדכן סטטוס (v1 פיילוט). נשדרג אחר כך.
create policy "public update requests"
on public.requests
for update
to anon
using (true)
with check (true);
