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