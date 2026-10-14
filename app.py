import io
import os
import zipfile
import requests
import streamlit as st
from PIL import Image
from rembg import remove

try:
    from supabase import create_client
except ImportError:
    create_client = None

st.set_page_config(page_title="ClearCut AI — Pro Background Remover", page_icon="✦", layout="wide")

# Secrets are configured in Streamlit Cloud, never committed to Git.
@st.cache_resource
def get_supabase():
    if create_client is None:
        return None
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        return create_client(url, key) if url and key else None
    except Exception:
        return None

supabase = get_supabase()
PAYMENT_API_URL = st.secrets.get("PAYMENT_API_URL", os.getenv("PAYMENT_API_URL", "")).rstrip("/")

for key, default in {
    "logged_in": False, "email": "", "user_id": "", "access_token": "", "credits": 0, "plan": "Free",
    "guest_used": False, "last_payment_url": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
:root { color-scheme: dark; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #182b50 0%, #0b1020 45%, #080b14 100%); color: #eef2ff; font-family: Inter, sans-serif; }
[data-testid="stSidebar"] { background: #0c1222; border-right: 1px solid #263149; }
.block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 4rem; }
.hero { padding: 3rem 1.5rem; border: 1px solid #344568; border-radius: 28px; background: linear-gradient(130deg, rgba(36,63,112,.85), rgba(18,24,44,.95)); text-align: center; box-shadow: 0 24px 80px rgba(0,0,0,.22); }
.eyebrow { display:inline-block; border:1px solid #5776b8; color:#c6d8ff; background:#20365c; border-radius:99px; padding:6px 13px; font-size:12px; letter-spacing:.12em; font-weight:800; }
.hero h1 { font-size: clamp(2rem, 5vw, 3.6rem); letter-spacing:-.045em; line-height:1.1; color:#fff; margin:18px 0 12px; font-weight:900; }
.hero p { color:#bdc9e2; font-size:1.05rem; max-width:680px; margin:0 auto; }
.feature { background:#111a2c; border:1px solid #263550; padding:20px; border-radius:18px; min-height:125px; }
.feature h3 { color:#f3f6ff; font-size:1rem; margin:0 0 8px; }
.feature p { color:#9eacc7; font-size:.9rem; margin:0; }
.plan { background:linear-gradient(160deg,#141f34,#0e1525); border:1px solid #2a3a58; border-radius:22px; padding:24px; min-height:260px; }
.plan.pro { border-color:#779cff; box-shadow:0 0 0 1px #4268ba,0 18px 50px rgba(56,100,220,.12); }
.plan h3 { color:#f8faff; margin:10px 0; }
.plan .price { font-size:2.1rem; font-weight:900; color:white; letter-spacing:-.04em; }
.plan p, .muted { color:#9eacc7; }
.stButton>button, .stDownloadButton>button { border-radius:12px; min-height:44px; font-weight:700; }
hr { border-color:#27334b; }
</style>
""", unsafe_allow_html=True)

def load_profile(user_id):
    if supabase is None:
        return 0, "Free"
    try:
        result = supabase.table("user_profiles").select("credits, plan").eq("id", user_id).maybe_single().execute()
        if result.data:
            return max(0, int(result.data.get("credits") or 0)), result.data.get("plan") or "Free"
    except Exception:
        pass
    return 0, "Free"

def auth_box():
    with st.sidebar:
        st.markdown("## ✦ ClearCut AI")
        st.caption("Your creative production workspace")
        if supabase is None:
            st.warning("Account service is not configured. Set SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets.")
            return
        if not st.session_state.logged_in:
            sign_in, sign_up = st.tabs(["Sign in", "Create account"])
            with sign_in:
                email = st.text_input("Email", key="in_email")
                password = st.text_input("Password", type="password", key="in_password")
                if st.button("Sign in", use_container_width=True):
                    try:
                        user = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password}).user
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.email = user.email or email.strip()
                            st.session_state.user_id = user.id
                            st.session_state.access_token = supabase.auth.get_session().access_token if supabase.auth.get_session() else ""
                            st.session_state.credits, st.session_state.plan = load_profile(user.id)
                            st.rerun()
                    except Exception as exc:
                        st.error(f"Sign in failed: {exc}")
            with sign_up:
                email = st.text_input("Email", key="up_email")
                password = st.text_input("Password (6+ characters)", type="password", key="up_password")
                if st.button("Create account", use_container_width=True):
                    if len(password) < 6:
                        st.error("Use at least 6 characters.")
                    else:
                        try:
                            result = supabase.auth.sign_up({"email": email.strip(), "password": password})
                            if result.user:
                                st.success("Account created. Confirm your email if required, then sign in.")
                        except Exception as exc:
                            st.error(f"Sign-up failed: {exc}")
        else:
            st.write(f"**{st.session_state.email}**")
            st.metric("Plan", st.session_state.plan)
            st.metric("Credits", st.session_state.credits)
            if st.button("Refresh account", use_container_width=True):
                st.session_state.credits, st.session_state.plan = load_profile(st.session_state.user_id)
                st.rerun()
            if st.button("Sign out", use_container_width=True):
                for k, v in {"logged_in":False,"email":"","user_id":"","credits":0,"plan":"Free"}.items():
                    st.session_state[k] = v
                st.rerun()

auth_box()

st.markdown("""
<div class="hero">
  <span class="eyebrow">✦ AI IMAGE WORKFLOW</span>
  <h1>Make every image<br>ready for its next stage.</h1>
  <p>Remove backgrounds in seconds. Export clean transparent PNGs, process batches, and keep your workflow moving.</p>
</div>
""", unsafe_allow_html=True)

st.write("")
features = st.columns(3)
for col, title, desc in zip(features,
    ["✧ Clean cutouts", "▦ Batch workflow", "⇩ Ready to export"],
    ["AI-powered background removal with transparent edges.", "Process multiple images with a paid credit balance.", "Download individual PNGs together in one ZIP file."]):
    col.markdown(f'<div class="feature"><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)

st.write("")
st.markdown("## Choose your workspace")
st.caption("One-time credit packs. Prices below are starter defaults; update them before launch if needed.")
plans = [
    {"name":"Starter","price":99,"credits":25,"description":"For occasional product and social images","features":["25 image credits","Transparent PNG export","ZIP batch download"]},
    {"name":"Pro","price":299,"credits":100,"description":"For creators and small online stores","features":["100 image credits","Batch processing","Priority workspace access"]},
    {"name":"Studio","price":799,"credits":350,"description":"For frequent production work","features":["350 image credits","Large batch workflow","Best value per image"]},
]
cols = st.columns(3)
for col, plan in zip(cols, plans):
    is_pro = plan["name"] == "Pro"
    badge = "✦ MOST POPULAR" if is_pro else ("CREATOR PACK" if plan["name"] == "Starter" else "HIGH VOLUME")
    features_html = "".join(f"<li>{item}</li>" for item in plan["features"])
    col.markdown(
        f'<div class="plan {"pro" if is_pro else ""}><span class="eyebrow">{badge}</span>'
        f'<h3>{plan["name"]}</h3><div class="price">₹{plan["price"]}<span style="font-size:.9rem;color:#9eacc7;font-weight:500"> one-time</span></div>'
        f'<p>{plan["description"]}</p><hr><ul>{features_html}</ul><p><b>{plan["credits"]} image credits</b></p></div>',
        unsafe_allow_html=True)
    if col.button(f"Get {plan['name']}", key=f"buy_{plan['name']}", use_container_width=True, type="primary" if is_pro else "secondary"):
        if not st.session_state.logged_in:
            st.warning("Create an account or sign in first so credits can be added to the correct account.")
        elif not PAYMENT_API_URL:
            st.error("Payments are not configured yet. Deploy the payment API and set PAYMENT_API_URL in Streamlit Secrets.")
        else:
            try:
                response = requests.post(
                    f"{PAYMENT_API_URL}/create-payment-link",
                    json={"plan": plan["name"]},
                    headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                    timeout=25,
                )
                response.raise_for_status()
                st.session_state.last_payment_url = response.json()["payment_url"]
                st.link_button("Continue to secure Razorpay checkout", st.session_state.last_payment_url, use_container_width=True)
            except Exception as exc:
                st.error(f"Could not start checkout: {exc}")

if st.session_state.last_payment_url:
    st.info("After completing payment, allow the payment confirmation webhook a moment to update your credits, then use Refresh account.")

st.divider()
st.markdown("## Background removal workspace")
if not st.session_state.logged_in:
    st.info("Sign in to process images and associate credits with your account. Guest processing is disabled in this release to prevent trial abuse.")
else:
    uploads = st.file_uploader("Upload JPG or PNG images", type=["png","jpg","jpeg"], accept_multiple_files=True)
    if uploads:
        count = len(uploads)
        st.caption(f"{count} image(s) selected · {count} credit(s) required")
        if count > st.session_state.credits:
            st.error(f"Not enough credits. You have {st.session_state.credits}; this batch needs {count}.")
        elif st.button("Remove backgrounds", type="primary", use_container_width=True):
            # Credits are not charged here until a server-side atomic debit API is configured.
            # Do not enable paid usage until the debit endpoint is deployed.
            st.warning("Processing is temporarily gated until the server-side atomic credit debit endpoint is configured. This protects your paid credits from inconsistent balances.")
            # TODO: call atomic debit endpoint, then process images; refund credits on processing failure.

st.caption("ClearCut AI · Secure checkout powered by Razorpay · Never commit API secrets to the repository.")
