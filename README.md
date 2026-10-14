# ClearCut AI — Bulk Image Background Remover

A Streamlit application that removes image backgrounds using `rembg` and exports transparent PNGs in a ZIP archive.

## Features
- Single-image and batch processing
- Transparent PNG output
- ZIP download for processed images
- Optional Supabase email/password authentication and credit balances
- Guest mode for testing without Supabase

## Run locally

Use Python 3.11 (see `runtime.txt`). In a terminal, from the repository folder:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

The first background-removal run downloads/initializes the model and may take longer. Keep sufficient RAM and disk space available.

## Optional Supabase setup

Without Supabase secrets, the app runs in guest/testing mode. To enable accounts, add these secrets to `.streamlit/secrets.toml` locally or to the Streamlit Community Cloud app's Secrets settings:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_KEY = "YOUR-SUPABASE-ANON-KEY"
```

Use the Supabase **publishable/anon key**, never a service-role key in a client-facing app. Keep secrets out of GitHub. Configure Supabase Auth email settings as needed.

The account code expects a `public.user_profiles` table with:
- `id` UUID primary key matching `auth.users.id`
- `credits` integer, not null, default 0

Before accepting payments or selling credits, implement server-side row-level security and an atomic server-side credit deduction (for example, a Postgres function/RPC). The current client-side balance update is a prototype and is not safe as a paid-credit ledger. Add a signup trigger or server-side workflow to create profile rows.

## Publish on Streamlit Community Cloud

1. Push/merge the code to your GitHub default branch.
2. Sign in at https://share.streamlit.io/ and choose **Create app**.
3. Select repository `EHpawan/bulk-image-remover`, the branch you deployed, and `app.py` as the main file.
4. Deploy. Add the Supabase secrets in the app's **Settings → Secrets** if using account features.
5. Test with a small JPG and PNG, confirm the output has transparency, and test the ZIP download.
6. Review app logs for dependency/model errors before sharing the public URL.

## Known production considerations
- Model inference consumes memory and CPU; batch size and image size should be limited on small hosting instances.
- Guest usage is tracked in Streamlit session state and is not abuse-proof.
- Do not enable paid credits until the balance deduction and authorization rules are enforced server-side.
- Add file-size limits, rate limits, privacy/retention messaging, and error monitoring before broad public launch.


## Pro plans and Razorpay (deployment is required)

The UI contains Starter, Pro, and Studio one-time credit packs. The checkout UI is only enabled when a separately hosted payment API is configured. Do not advertise payments as live until you finish the steps below and test them with Razorpay test mode.

### Deploy the payment API

The repository contains `payment_api.py`, a FastAPI backend. Deploy it as a separate Python web service (for example on Render) with the repository root as the source, build command `pip install -r payment-requirements.txt`, and start command:

```bash
uvicorn payment_api:app --host 0.0.0.0 --port $PORT
```

Set these environment variables in the backend host's secret settings:
- `RAZORPAY_KEY_ID` — Razorpay test key while testing, live key only after account approval
- `RAZORPAY_KEY_SECRET` — keep private on the backend only
- `RAZORPAY_WEBHOOK_SECRET` — secret configured for the webhook endpoint
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY` — used to validate the logged-in user's access token
- `SUPABASE_SERVICE_ROLE_KEY` — backend only; never place this in Streamlit secrets or GitHub

In Streamlit Community Cloud, set `PAYMENT_API_URL` to the HTTPS URL of the deployed backend. Keep the existing Supabase URL and publishable/anon key in Streamlit Secrets.

### Configure the webhook

In the Razorpay dashboard, create a webhook pointing to `https://YOUR-PAYMENT-API/razorpay-webhook`, subscribe to `payment_link.paid`, and set the webhook secret to the exact value in `RAZORPAY_WEBHOOK_SECRET`.

### Prepare Supabase

Review and run `supabase_razorpay.sql` in Supabase SQL Editor. Ensure `user_profiles` has a `plan` text column, `credits` integer column, and a profile row for every registered user. Check the function/table permissions and schema before production.

### Important release gate

- First test using Razorpay test keys and test payments; verify webhook delivery and credit balance changes.
- The image-processing action is deliberately gated in this prototype until a server-side atomic credit-debit/refund endpoint is implemented and tested. Do not sell credits or tell users that processing credits are ready yet.
- The current UI prices are starter examples (₹99 / ₹299 / ₹799); confirm pricing, taxes, refund policy, support contact, and terms before launch.
- Never put Razorpay key secrets or Supabase service-role keys in Streamlit Secrets, browser code, or GitHub.
