create table if not exists public.decision_maker_preferences (
    user_id uuid primary key references public.users(id) on delete cascade,
    decision_maker_roles text[] not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

drop trigger if exists decision_maker_preferences_set_updated_at on public.decision_maker_preferences;
create trigger decision_maker_preferences_set_updated_at
before update on public.decision_maker_preferences
for each row execute function public.set_updated_at();

alter table public.decision_maker_preferences enable row level security;
revoke all on table public.decision_maker_preferences from anon, authenticated;
grant all on table public.decision_maker_preferences to service_role;
