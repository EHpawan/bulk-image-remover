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
begin
  if p_plan not in ('Starter', 'Pro', 'Studio')
     or p_credits not in (25, 100, 350)
     or p_amount_paise not in (9900, 29900, 79900) then
    raise exception 'Invalid plan payload';
  end if;

  insert into public.user_profiles (id, credits, plan)
  values (p_user_id, p_credits, p_plan)
  on conflict (id) do update
    set credits = coalesce(public.user_profiles.credits, 0) + excluded.credits,
        plan = excluded.plan;

  insert into public.razorpay_fulfilled_payments
    (payment_link_id, user_id, plan, credits_added, amount_paise)
  values (p_payment_link_id, p_user_id, p_plan, p_credits, p_amount_paise)
  on conflict (payment_link_id) do nothing;

  -- If already fulfilled, roll back the accidental second credit increment.
  if not found then
    update public.user_profiles
      set credits = greatest(0, coalesce(credits, 0) - p_credits)
      where id = p_user_id;
    return jsonb_build_object('duplicate', true);
  end if;
  return jsonb_build_object('duplicate', false, 'credits_added', p_credits);
end;
$$;

revoke all on function public.fulfill_razorpay_payment(text, uuid, text, integer, integer) from public, anon, authenticated;
grant execute on function public.fulfill_razorpay_payment(text, uuid, text, integer, integer) to service_role;
