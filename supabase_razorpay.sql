-- Run in Supabase SQL Editor before enabling payments.
-- This function makes webhook fulfillment idempotent: each Razorpay payment link can credit an account only once.
create table if not exists public.razorpay_fulfilled_payments (
  payment_link_id text primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  plan text not null,
  credits_added integer not null check (credits_added > 0),
  amount_paise integer not null check (amount_paise > 0),
  fulfilled_at timestamptz not null default now()
);

alter table public.razorpay_fulfilled_payments enable row level security;
revoke all on public.razorpay_fulfilled_payments from anon, authenticated;

create or replace function public.fulfill_razorpay_payment(
  p_payment_link_id text,
  p_user_id uuid,
  p_plan text,
  p_credits integer,
  p_amount_paise integer
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  inserted_count integer;
begin
  if p_plan not in ('Starter', 'Pro', 'Studio')
     or (p_plan = 'Starter' and (p_credits <> 25 or p_amount_paise <> 9900))
     or (p_plan = 'Pro' and (p_credits <> 100 or p_amount_paise <> 29900))
     or (p_plan = 'Studio' and (p_credits <> 350 or p_amount_paise <> 79900)) then
    raise exception 'Invalid plan payload';
  end if;

  insert into public.razorpay_fulfilled_payments
    (payment_link_id, user_id, plan, credits_added, amount_paise)
  values (p_payment_link_id, p_user_id, p_plan, p_credits, p_amount_paise)
  on conflict (payment_link_id) do nothing;

  get diagnostics inserted_count = row_count;
  if inserted_count = 0 then
    return jsonb_build_object('duplicate', true);
  end if;

  update public.user_profiles
    set credits = coalesce(credits, 0) + p_credits,
        plan = p_plan
    where id = p_user_id;

  if not found then
    raise exception 'User profile not found; transaction rolled back';
  end if;

  return jsonb_build_object('duplicate', false, 'credits_added', p_credits);
end;
$$;

revoke all on function public.fulfill_razorpay_payment(text, uuid, text, integer, integer) from public, anon, authenticated;
grant execute on function public.fulfill_razorpay_payment(text, uuid, text, integer, integer) to service_role;
