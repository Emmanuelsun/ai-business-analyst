create table public.reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  title text not null,
  created_at timestamptz not null default now(),
  html text not null
);

alter table public.reports enable row level security;

create policy "Users can read their own reports"
  on public.reports for select
  to authenticated
  using ( (select auth.uid()) = user_id );

create policy "Users can add their own reports"
  on public.reports for insert
  to authenticated
  with check ( (select auth.uid()) = user_id );

create policy "Users can delete their own reports"
  on public.reports for delete
  to authenticated
  using ( (select auth.uid()) = user_id );