create table if not exists public.candidate_research_profiles (
    candidate_id uuid primary key references public.discovery_candidates(id) on delete cascade,
    status text not null default 'pending' check (status in ('pending', 'running', 'completed', 'failed')),
    profile jsonb not null default '{}'::jsonb,
    evidence jsonb not null default '[]'::jsonb,
    error_message text,
    researched_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

drop trigger if exists candidate_research_profiles_set_updated_at on public.candidate_research_profiles;
create trigger candidate_research_profiles_set_updated_at
before update on public.candidate_research_profiles
for each row execute function public.set_updated_at();

alter table public.candidate_research_profiles enable row level security;
revoke all on table public.candidate_research_profiles from anon, authenticated;
grant all on table public.candidate_research_profiles to service_role;
