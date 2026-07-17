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