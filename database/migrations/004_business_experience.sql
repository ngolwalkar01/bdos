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