create table if not exists public.user_profiles (
    user_id uuid primary key references public.users(id) on delete cascade,
    full_name text,
    professional_headline text,
    current_role text,
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