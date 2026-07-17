create table if not exists public.communication_styles (
    user_id uuid primary key references public.users(id) on delete cascade,
    tone text,
    writing_length text,
    communication_preferences text[] not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

drop trigger if exists communication_styles_set_updated_at on public.communication_styles;
create trigger communication_styles_set_updated_at
before update on public.communication_styles
for each row execute function public.set_updated_at();

alter table public.communication_styles enable row level security;
revoke all on table public.communication_styles from anon, authenticated;
grant all on table public.communication_styles to service_role;
