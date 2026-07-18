create table if not exists public.candidate_qualifications (
    candidate_id uuid primary key references public.discovery_candidates(id) on delete cascade,
    verdict text not null check (verdict in ('qualified', 'rejected', 'needs_review')),
    score smallint not null check (score between 0 and 100),
    dimensions jsonb not null default '{}'::jsonb,
    reasons jsonb not null default '[]'::jsonb,
    risks jsonb not null default '[]'::jsonb,
    missing_data jsonb not null default '[]'::jsonb,
    opportunity jsonb not null default '{}'::jsonb,
    engine_version text not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

drop trigger if exists candidate_qualifications_set_updated_at on public.candidate_qualifications;
create trigger candidate_qualifications_set_updated_at
before update on public.candidate_qualifications
for each row execute function public.set_updated_at();

alter table public.candidate_qualifications enable row level security;
revoke all on table public.candidate_qualifications from anon, authenticated;
grant all on table public.candidate_qualifications to service_role;
