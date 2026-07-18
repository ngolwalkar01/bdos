create table if not exists public.opportunity_feedback (
    id uuid primary key default gen_random_uuid(),
    opportunity_id uuid not null references public.opportunities(id) on delete cascade,
    user_id uuid not null references public.users(id) on delete cascade,
    action text not null check (action in ('saved', 'not_relevant', 'restored')),
    reason text check (reason is null or reason in (
        'wrong_skill', 'wrong_industry', 'wrong_opportunity_type', 'location_mismatch',
        'budget_mismatch', 'weak_evidence', 'not_an_opportunity', 'already_closed', 'other'
    )),
    details text,
    created_at timestamptz not null default now()
);

create index if not exists opportunity_feedback_user_created_idx
on public.opportunity_feedback(user_id, created_at desc);

create index if not exists opportunity_feedback_opportunity_idx
on public.opportunity_feedback(opportunity_id);

alter table public.opportunity_feedback enable row level security;
revoke all on table public.opportunity_feedback from anon, authenticated;
grant all on table public.opportunity_feedback to service_role;
