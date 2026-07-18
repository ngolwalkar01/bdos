-- Results created before Business DNA semantic qualification are retained for audit
-- but are no longer eligible for the user-facing opportunity feed.
update public.opportunities
set status = 'rejected'
where status = 'new';
