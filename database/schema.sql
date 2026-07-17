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