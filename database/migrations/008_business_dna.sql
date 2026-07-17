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
