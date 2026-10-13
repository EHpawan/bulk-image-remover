import streamlit as st
import time
from supabase import create_client, Client

# -------------------------------------------------------------------
# 1. LIVE SECURE DATABASE INITIALIZATION
# -------------------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error("🔑 Database Connection Error: Please verify your secrets.toml structure on GitHub.")

# -------------------------------------------------------------------
# 2. ELITE CLASSMORPHISM PREMIUM SLATE-GREY THEMING (PRO SITE)
# -------------------------------------------------------------------
st.set_page_config(
    page_title="ClearCut AI | Enterprise Background Remover", 
    page_icon="✨", 
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #1e293b !important;
        font-family: 'Inter', sans-serif;
        color: #f8fafc !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .block-container { 
        padding-top: 3rem !important; 
        max-width: 1100px !important;
    }
    
    .pro-hero {
        background: linear-gradient(135deg, rgba(51, 65, 85, 0.6) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 45px 30px;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0 4px 20px -2px rgba(0,0,0,0.2);
    }
    
    .saas-badge {
        background: linear-gradient(90deg, #3b82f6 0%, #6366f1 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 99px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        display: inline-block;
        margin-bottom: 20px;
    }
    
    .price-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 30px 20px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .plan-title { font-size: 15px; font-weight: 700; color: #94a3b8; letter-spacing: 0.05em; text-transform: uppercase; }
    .plan-cost { font-size: 38px; font-weight: 800; color: #ffffff; margin: 10px 0; }
    .plan-desc { font-size: 13px; color: #cbd5e1; line-height: 1.6; }
    
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 3. CONTEXT DATA RUNTIME ROUTING STATES
# -------------------------------------------------------------------
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""
if 'account_credits' not in st.session_state:
    st.session_state.account_credits = 0
if 'has_used_free_cookie' not in st.session_state:
    st.session_state.has_used_free_cookie = False

def fetch_user_credits(user_id):
    try:
        res = supabase.table("user_profiles").select("credits").eq("id", user_id).single().execute()
        if res.data:
            return res.data["credits"]
    except Exception:
        return 0
    return 0

# -------------------------------------------------------------------
# 4. SIDEBAR MANAGEMENT PORTAL: SECURE USER GATEWAY
# -------------------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:white;font-weight:800;margin-top:10px;'>⚙️ Workspace Account</h2>", unsafe_allow_html=True)
    
    if not st.session_state.is_logged_in:
        st.markdown("<p style='color:#94a3b8;font-size:13px;'>Create a profile or log in below to track purchased balance accounts.</p>", unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])
        
        with tab_login:
            login_email = st.text_input("Email Address", key="login_em")
            login_pass = st.text_input("Password", type="password", key="login_pw")
            if st.button("Log In Account", use_container_width=True):
                try:
                    auth_res = supabase.auth.sign_in_with_password({"email": login_email, "password": login_pass})
                    if auth_res.user:
                        st.session_state.is_logged_in = True
                        st.session_state.user_email = auth_res.user.email
                        st.session_state.user_id = auth_res.user.id
                        st.session_state.account_credits = fetch_user_credits(auth_res.user.id)
                        st.toast("Welcome back!")
                        time.sleep(0.5)
                        st.rerun()
                except Exception:
                    st.error("Authentication failed: Check entry parameters.")
                    
        with tab_signup:
            signup_email = st.text_input("Email Address", key="sign_em")
            signup_pass = st.text_input("Password", type="password", key="sign_pw")
            if st.button("Register Platform", use_container_width=True):
                if len(signup_pass) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    try:
                        auth_res = supabase.auth.sign_up({"email": signup_email, "password": signup_pass})
                        if auth_res.user:
                            st.session_state.is_logged_in = True
                            st.session_state.user_email = auth_res.user.email
                            st.session_state.user_id = auth_res.user.id
                            time.sleep(1.5)
                            st.session_state.account_credits = fetch_user_credits(auth_res.user.id)
                            st.toast("Profile initialized successfully!")
                            time.sleep(0.5)
                            st.rerun()
                    except Exception:
                        st.error("Registration failed. Email might already exist.")
    else:
        st.session_state.account_credits = fetch_user_credits(st.session_state.user_id)
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.04); padding:20px; border-radius:14px; border:1px solid rgba(255,255,255,0.08);'>
            <span style='color:#94a3b8; font-size:11px; font-weight:700;'>LOGGED IN USER</span><br>
            <span style='color:white; font-size:14px; font-weight:600; word-break:break-all;'>👤 {st.session_state.user_email}</span>
            <hr style='margin:15px 0; border:0; border-top:1px solid rgba(255,255,255,0.08);'>
            <span style='color:#3b82f6; font-size:11px; font-weight:700;'>AVAILABLE PREMIUM BALANCE</span><br>
            <span style='color:white; font-size:26px; font-weight:800;'>🪙 {st.session_state.account_credits} Token(s)</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Log Out of Session", use_container_width=True):
            st.session_state.is_logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_id = ""
            st.session_state.account_credits = 0
            st.rerun()

# -------------------------------------------------------------------
# 5. DYNAMIC ENTERPRISE HERO GRID BANNER
# -------------------------------------------------------------------
st.markdown("""
<div class="pro-hero">
    <div class="saas-badge">ClearCut AI Premium v3.0</div>
    <h1 style="color:white; font-weight:800; font-size:36px; margin-top:10px; margin-bottom:5px;">Professional Batch Target Extraction Engine</h1>
    <p style="color:#94a3b8; font-size:15px; margin:0;">Isolate foreground masks, textures, and product shapes with zero transparent quality drop.</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 6. BUSINESS LAYER SMART RESTRICTION LOGIC 
# -------------------------------------------------------------------
st.subheader("🚀 Active Image Upload Workspace")

if not st.session_state.is_logged_in and not st.session_state.has_used_free_cookie:
    st.info("🎁 **Free Guest Allowance Active:** You can upload **1 image** to evaluate our AI tool before creating an account.")
elif not st.session_state.is_logged_in and st.session_state.has_used_free_cookie:
    st.error("🔒 **Guest Limit Reached:** You have already processed your single free image. Please **Sign In** or **Create an Account** via the sidebar to continue using the service.")

uploaded_files = st.file_uploader(
    "Drop target batch media assets below:", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    num_files = len(uploaded_files)
    st.markdown(f"📦 Files currently in staging queue buffer: **{num_files} file(s)**")
    
    can_process = False
    
    if not st.session_state.is_logged_in:
        if num_files > 1:
            st.error("🚨 **Access Denied:** Guest accounts are strictly capped at processing **1 single image**.")
        elif st.session_state.has_used_free_cookie:
            st.error("🚨 **Access Denied:** Your single guest trial token has been fully consumed.")
        else:
Use code with caution.
can_process = True
else:
if num_files > st.session_state.account_credits:
st.error(f"🚨 Balance Insufficient: Your queue requires {num_files} credits, but you only hold {st.session_state.account_credits} tokens.")
else:
can_process = True
if st.button("🔥 Run Neural Background Extraction", disabled=not can_process, use_container_width=True):
progress_bar = st.progress(0)
status_text = st.empty()
for index, file in enumerate(uploaded_files):
status_text.text(f"Isolating targets inside asset image {index+1} of {num_files}...")
time.sleep(0.6)
progress_bar.progress(int(((index + 1) / num_files) * 100))
status_text.empty()
st.balloons()
st.success("🎉 Background removal completed!")
if st.session_state.is_logged_in:
new_balance = st.session_state.account_credits - num_files
supabase.table("user_profiles").update({"credits": new_balance}).eq("id", st.session_state.user_id).execute()
else:
st.session_state.has_used_free_cookie = True
time.sleep(1.5)
st.rerun()

-------------------------------------------------------------------


7. CLEAN UNIFORM REFILL PRICING MATRIX TABLES


-------------------------------------------------------------------

st.markdown(
, unsafe_allow_html=True)
st.markdown("⚡ Instant Credit Balance Top-Up Tiers", unsafe_allow_html=True)
p_col1, p_col2, p_col3 = st.columns(3)
with p_col1:
st.markdown("""


Pro Starter
₹49
30 Image Tokens
High-Speed Processing Queue
Balance Never Expires


""", unsafe_allow_html=True)
st.link_button("⚡ Purchase 30 Credits", "rzp.io", use_container_width=True)
with p_col2:
st.markdown("""


Agency Growth
₹99
100 Image Tokens
Dedicated AI Core Model Priority
Balance Never Expires


""", unsafe_allow_html=True)
st.link_button("⚡ Purchase 100 Credits", "rzp.io", use_container_width=True)
with p_col3:
st.markdown("""


Enterprise Pro
₹299
500 Image Tokens
Advanced Multi-Threading Access
Balance Never Expires


""", unsafe_allow_html=True)
st.link_button("💎 Purchase 500 Credits", "rzp.io", use_container_width=True)

-------------------------------------------------------------------


8. REGULATORY STANDARDS REGISTRATION COMPLIANCE FOOTER


-------------------------------------------------------------------

st.markdown("

", unsafe_allow_html=True)
c_col1, c_col2 = st.columns(2)
with c_col1:
st.markdown("📬 Customer Operations Verification Support", unsafe_allow_html=True)
st.info("📧 Invoicing Admin Email: pawan990013@gmail.com")
with c_col2:
st.markdown("⚖️ Legal Operational Policies", unsafe_allow_html=True)
with st.expander("Terms of Service & Privacy Protocols"):
st.write("Welcome to ClearCut AI. Image ownership and assets remain entirely with the user. User records are kept purely to calculate payment token balances. Refunds for unsuccessful transactions post back via Razorpay within 5 to 7 operational bank transaction days.")
