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
