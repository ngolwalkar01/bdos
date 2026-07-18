create extension if not exists pgcrypto;

create table if not exists public.users (
    id uuid primary key default gen_random_uuid(),
    oidc_subject text not null unique,
    email text,
    full_name text,
    picture_url text,
    onboarding_completed boolean not null default false,
    onboarding_step smallint not null default 0 check (onboarding_step between 0 and 7),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists users_set_updated_at on public.users;
create trigger users_set_updated_at
before update on public.users
for each row execute function public.set_updated_at();

alter table public.users enable row level security;
revoke all on table public.users from anon, authenticated;
grant all on table public.users to service_role;

create table if not exists public.user_profiles (
    user_id uuid primary key references public.users(id) on delete cascade,
    full_name text,
    professional_headline text,
    current_job_role text,
    years_experience smallint check (years_experience between 0 and 80),
    country text,
    preferred_timezone text,
    linkedin_url text,
    portfolio_url text,
    resume_path text,
    resume_filename text,
    resume_content_type text,
    resume_size_bytes bigint check (resume_size_bytes between 0 and 10485760),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

drop trigger if exists user_profiles_set_updated_at on public.user_profiles;
create trigger user_profiles_set_updated_at
before update on public.user_profiles
for each row execute function public.set_updated_at();

alter table public.user_profiles enable row level security;
revoke all on table public.user_profiles from anon, authenticated;
grant all on table public.user_profiles to service_role;

create table if not exists public.professional_experience (
    user_id uuid primary key references public.users(id) on delete cascade,
    primary_skills text[] not null default '{}',
    secondary_skills text[] not null default '{}',
    technologies text[] not null default '{}',
    frameworks text[] not null default '{}',
    platforms text[] not null default '{}',
    certifications text[] not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

drop trigger if exists professional_experience_set_updated_at on public.professional_experience;
create trigger professional_experience_set_updated_at
before update on public.professional_experience
for each row execute function public.set_updated_at();

alter table public.professional_experience enable row level security;
revoke all on table public.professional_experience from anon, authenticated;
grant all on table public.professional_experience to service_role;

create table if not exists public.business_experience (
    user_id uuid primary key references public.users(id) on delete cascade,
    industries text[] not null default '{}',
    business_problems text[] not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

drop trigger if exists business_experience_set_updated_at on public.business_experience;
create trigger business_experience_set_updated_at
before update on public.business_experience
for each row execute function public.set_updated_at();

alter table public.business_experience enable row level security;
revoke all on table public.business_experience from anon, authenticated;
grant all on table public.business_experience to service_role;

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

create table if not exists public.communication_styles (
    user_id uuid primary key references public.users(id) on delete cascade,
    tone text,
    writing_length text,
    communication_preferences text[] not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

drop trigger if exists communication_styles_set_updated_at on public.communication_styles;
create trigger communication_styles_set_updated_at
before update on public.communication_styles
for each row execute function public.set_updated_at();

alter table public.communication_styles enable row level security;
revoke all on table public.communication_styles from anon, authenticated;
grant all on table public.communication_styles to service_role;

create table if not exists public.business_dna_profiles (
 user_id uuid primary key references public.users(id) on delete cascade,
 profile jsonb not null default '{}'::jsonb,
 knowledge_documents jsonb not null default '{}'::jsonb,
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now()
);
drop trigger if exists business_dna_profiles_set_updated_at on public.business_dna_profiles;
create trigger business_dna_profiles_set_updated_at before update on public.business_dna_profiles
for each row execute function public.set_updated_at();
alter table public.business_dna_profiles enable row level security;
revoke all on table public.business_dna_profiles from anon, authenticated;
grant all on table public.business_dna_profiles to service_role;

create table if not exists public.discovery_strategies (
 id uuid primary key default gen_random_uuid(), user_id uuid not null references public.users(id) on delete cascade,
 version integer not null default 1, status text not null default 'draft' check (status in ('draft','active','archived')),
 strategy jsonb not null default '{}'::jsonb, prompt_version text, created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(), unique(user_id,version));
create table if not exists public.discovery_runs (
 id uuid primary key default gen_random_uuid(), user_id uuid not null references public.users(id) on delete cascade,
 strategy_id uuid references public.discovery_strategies(id) on delete set null,
 status text not null default 'pending' check (status in ('pending','running','completed','partial','failed')),
 sources text[] not null default '{}', discovered_count integer not null default 0, errors jsonb not null default '[]'::jsonb,
 started_at timestamptz, completed_at timestamptz, created_at timestamptz not null default now(), updated_at timestamptz not null default now());
create table if not exists public.opportunities (
 id uuid primary key default gen_random_uuid(), user_id uuid not null references public.users(id) on delete cascade,
 discovery_run_id uuid references public.discovery_runs(id) on delete set null, external_key text, title text not null,
 company_name text not null, source text not null, source_url text not null, opportunity_type text, country text, summary text,
 raw_data jsonb not null default '{}'::jsonb, status text not null default 'new' check (status in ('new','saved','ignored','qualified','rejected')),
 discovered_at timestamptz not null default now(), created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
 unique(user_id,source,source_url));
create table if not exists public.research_profiles (
 opportunity_id uuid primary key references public.opportunities(id) on delete cascade,
 status text not null default 'pending' check (status in ('pending','running','completed','partial','failed')),
 profile jsonb not null default '{}'::jsonb, evidence jsonb not null default '[]'::jsonb, researched_at timestamptz,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now());
create table if not exists public.qualifications (
 opportunity_id uuid primary key references public.opportunities(id) on delete cascade,
 verdict text not null check (verdict in ('qualified','rejected','needs_review')), dimensions jsonb not null default '{}'::jsonb,
 reasons jsonb not null default '[]'::jsonb, missing_data jsonb not null default '[]'::jsonb, engine_version text not null,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now());
create table if not exists public.opportunity_scores (
 opportunity_id uuid primary key references public.opportunities(id) on delete cascade,
 score smallint not null check (score between 0 and 100), confidence text not null check (confidence in ('low','medium','high')),
 breakdown jsonb not null default '{}'::jsonb, positive_signals jsonb not null default '[]'::jsonb,
 risk_signals jsonb not null default '[]'::jsonb, engine_version text not null,
 created_at timestamptz not null default now(), updated_at timestamptz not null default now());
create index if not exists discovery_strategies_user_status_idx on public.discovery_strategies(user_id,status);
create index if not exists discovery_runs_user_created_idx on public.discovery_runs(user_id,created_at desc);
create index if not exists opportunities_user_status_idx on public.opportunities(user_id,status);
create index if not exists opportunities_user_discovered_idx on public.opportunities(user_id,discovered_at desc);
do $$
declare table_name text;
begin
 foreach table_name in array array['discovery_strategies','discovery_runs','opportunities','research_profiles','qualifications','opportunity_scores']
 loop
  execute format('drop trigger if exists %I_set_updated_at on public.%I',table_name,table_name);
  execute format('create trigger %I_set_updated_at before update on public.%I for each row execute function public.set_updated_at()',table_name,table_name);
  execute format('alter table public.%I enable row level security',table_name);
  execute format('revoke all on table public.%I from anon, authenticated',table_name);
  execute format('grant all on table public.%I to service_role',table_name);
 end loop;
end $$;

create table if not exists public.discovery_candidates (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users(id) on delete cascade,
    discovery_run_id uuid references public.discovery_runs(id) on delete set null,
    source text not null,
    source_url text not null,
    title text,
    snippet text,
    raw_data jsonb not null default '{}'::jsonb,
    classification jsonb not null default '{}'::jsonb,
    status text not null default 'pending' check (status in ('pending', 'rejected', 'promoted')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, source, source_url)
);

create index if not exists discovery_candidates_user_status_idx
on public.discovery_candidates(user_id, status);

drop trigger if exists discovery_candidates_set_updated_at on public.discovery_candidates;
create trigger discovery_candidates_set_updated_at
before update on public.discovery_candidates
for each row execute function public.set_updated_at();

alter table public.discovery_candidates enable row level security;
revoke all on table public.discovery_candidates from anon, authenticated;
grant all on table public.discovery_candidates to service_role;

-- Preserve legacy raw web matches for audit, but remove them from the opportunity feed.
update public.opportunities
set status = 'rejected'
where source = 'Public Web' and status = 'new';
