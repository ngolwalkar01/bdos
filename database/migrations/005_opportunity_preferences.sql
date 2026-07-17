create table if not exists public.opportunity_preferences (
    user_id uuid primary key references public.users(id) on delete cascade,
    opportunity_types text[] not null default '{}',
    company_sizes text[] not null default '{}',
    preferred_industries text[] not null default '{}',
    preferred_countries text[] not null default '{}',
    budget_type text,
    budget_currency text,
    budget_min numeric(14, 2),
    budget_max numeric(14, 2),
    remote_preferences text[] not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint opportunity_budget_range check (
        budget_min is null or budget_max is null or budget_max >= budget_min
    )
);

drop trigger if exists opportunity_preferences_set_updated_at on public.opportunity_preferences;
create trigger opportunity_preferences_set_updated_at
before update on public.opportunity_preferences
for each row execute function public.set_updated_at();

alter table public.opportunity_preferences enable row level security;
revoke all on table public.opportunity_preferences from anon, authenticated;
grant all on table public.opportunity_preferences to service_role;