import hashlib
import hmac
import json
import os
from typing import Literal

import requests
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, EmailStr

app = FastAPI(title="ClearCut AI Payments API", version="1.0.0")

RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")

PLANS = {
    "Starter": {"amount": 9900, "credits": 25, "label": "ClearCut Starter - 25 credits"},
    "Pro": {"amount": 29900, "credits": 100, "label": "ClearCut Pro - 100 credits"},
    "Studio": {"amount": 79900, "credits": 350, "label": "ClearCut Studio - 350 credits"},
}

class CheckoutRequest(BaseModel):
    plan: Literal["Starter", "Pro", "Studio"]

def authenticated_user(authorization: str):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Sign in required")
    token = authorization.removeprefix("Bearer ").strip()
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(503, "Supabase authentication is not configured")
    response = requests.get(f"{SUPABASE_URL}/auth/v1/user", headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {token}"}, timeout=15)
    if response.status_code != 200:
        raise HTTPException(401, "Invalid or expired session")
    return response.json()

def require_config():
    if not all([RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY]):
        raise HTTPException(503, "Payment service is not fully configured")

def supabase_request(path: str, method: str = "GET", payload=None, params=None):
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.request(method, f"{SUPABASE_URL}/rest/v1/{path}", headers=headers, json=payload, params=params, timeout=20)
    if response.status_code >= 400:
        raise HTTPException(502, f"Database operation failed ({response.status_code})")
    return response

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/create-payment-link")
def create_payment_link(body: CheckoutRequest, authorization: str = Header(default="")):
    require_config()
    user = authenticated_user(authorization)
    plan = PLANS[body.plan]
    payload = {
        "amount": plan["amount"],
        "currency": "INR",
        "accept_partial": False,
        "description": plan["label"],
        "customer": {"email": str(user.get("email", ""))},
        "notify": {"email": True, "sms": False},
        "reminder_enable": False,
        "notes": {
            "user_id": user["id"],
            "plan": body.plan,
            "credits": str(plan["credits"]),
        },
    }
    try:
        response = requests.post(
            "https://api.razorpay.com/v1/payment_links",
            auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET),
            json=payload,
            timeout=25,
        )
        if response.status_code >= 400:
            raise HTTPException(502, f"Razorpay could not create checkout ({response.status_code})")
        data = response.json()
        return {"payment_url": data["short_url"], "payment_link_id": data["id"]}
    except requests.RequestException:
        raise HTTPException(502, "Could not reach Razorpay. Please retry.")

@app.post("/razorpay-webhook")
async def razorpay_webhook(request: Request, x_razorpay_signature: str = Header(default="")):
    require_config()
    if not RAZORPAY_WEBHOOK_SECRET:
        raise HTTPException(503, "Webhook secret is not configured")
    raw = await request.body()
    expected = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode(), raw, hashlib.sha256).hexdigest()
    if not x_razorpay_signature or not hmac.compare_digest(expected, x_razorpay_signature):
        raise HTTPException(400, "Invalid webhook signature")
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid JSON")
    if event.get("event") != "payment_link.paid":
        return {"received": True, "ignored": True}

    entity = event.get("payload", {}).get("payment_link", {}).get("entity", {})
    link_id = entity.get("id")
    notes = entity.get("notes") or {}
    user_id = notes.get("user_id")
    plan_name = notes.get("plan")
    plan = PLANS.get(plan_name)
    if not link_id or not user_id or not plan:
        raise HTTPException(400, "Payment link metadata is incomplete")
    if int(entity.get("amount_paid") or 0) < plan["amount"] or entity.get("currency") != "INR":
        raise HTTPException(400, "Paid amount or currency does not match the selected plan")

    # Idempotency: record each payment-link ID in a dedicated table with a unique constraint
    # and apply credit increments in a single database transaction/RPC. Never increment directly
    # in a webhook handler without this protection.
    rpc_payload = {"p_payment_link_id": link_id, "p_user_id": user_id, "p_plan": plan_name,
                   "p_credits": plan["credits"], "p_amount_paise": plan["amount"]}
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/fulfill_razorpay_payment",
        headers={"apikey": SUPABASE_SERVICE_ROLE_KEY,
                 "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                 "Content-Type": "application/json"},
        json=rpc_payload, timeout=20,
    )
    if response.status_code >= 400:
        raise HTTPException(502, "Could not safely apply payment credits; webhook can be retried")
    return {"received": True, "fulfilled": True}
