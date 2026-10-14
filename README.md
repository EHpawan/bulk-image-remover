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
