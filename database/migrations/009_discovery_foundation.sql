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
