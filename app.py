import io
import os
import zipfile

import streamlit as st
from PIL import Image
from rembg import remove

try:
    from supabase import create_client
except ImportError:
    create_client = None

st.set_page_config(
    page_title="ClearCut AI | Background Remover",
    page_icon="✨",
    layout="wide",
)

# Supabase is optional for local testing; image processing still works without it.
@st.cache_resource
def init_supabase():
    if create_client is None:
        return None
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None

supabase = init_supabase()

for key, default in {
    "is_logged_in": False,
    "user_email": "",
    "user_id": "",
    "account_credits": 0,
    "guest_trial_used": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [data-testid="stAppViewContainer"] {
  background-color: #1e293b; color: #f8fafc; font-family: Inter, sans-serif;
}
[data-testid="stSidebar"] { background-color: #0f172a; }
.block-container { max-width: 1100px; padding-top: 2rem; }
.hero {
  background: linear-gradient(135deg, #334155, #1e293b);
  border: 1px solid rgba(255,255,255,.1); border-radius: 20px;
  padding: 2.5rem 1.5rem; text-align: center; margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

def fetch_user_credits(user_id):
    if supabase is None or not user_id:
        return 0
    try:
        response = (supabase.table("user_profiles").select("credits")
                    .eq("id", user_id).maybe_single().execute())
        if response.data:
            return max(0, int(response.data.get("credits") or 0))
    except Exception as exc:
        st.warning(f"Could not load credits. Check the user_profiles table and permissions. Details: {exc}")
    return 0

with st.sidebar:
    st.markdown("## ⚙️ Workspace Account")
    if supabase is None:
        st.info("Supabase is not configured. Guest mode is enabled for testing.")
    elif not st.session_state.is_logged_in:
        login_tab, signup_tab = st.tabs(["Sign in", "Create account"])
        with login_tab:
            email = st.text_input("Email address", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Log in", use_container_width=True):
                try:
                    auth = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                    if auth.user:
                        st.session_state.is_logged_in = True
                        st.session_state.user_email = auth.user.email or email.strip()
                        st.session_state.user_id = auth.user.id
                        st.session_state.account_credits = fetch_user_credits(auth.user.id)
                        st.rerun()
                    st.error("Login failed. Check your credentials.")
                except Exception as exc:
                    st.error(f"Login failed: {exc}")
        with signup_tab:
            new_email = st.text_input("Email address", key="signup_email")
            new_password = st.text_input("Password (minimum 6 characters)", type="password", key="signup_password")
            if st.button("Create account", use_container_width=True):
                if len(new_password) < 6:
                    st.error("Password must contain at least 6 characters.")
                else:
                    try:
                        auth = supabase.auth.sign_up({"email": new_email.strip(), "password": new_password})
                        if auth.user:
                            st.success("Account created. Confirm your email if required, then sign in.")
                        else:
                            st.error("No user was returned. Check Supabase Auth settings.")
                    except Exception as exc:
                        st.error(f"Registration failed: {exc}")
    else:
        st.write(f"Signed in: **{st.session_state.user_email}**")
        st.metric("Available credits", st.session_state.account_credits)
        if st.button("Refresh credits", use_container_width=True):
            st.session_state.account_credits = fetch_user_credits(st.session_state.user_id)
            st.rerun()
        if st.button("Log out", use_container_width=True):
            for key, value in {
                "is_logged_in": False, "user_email": "", "user_id": "", "account_credits": 0
            }.items():
                st.session_state[key] = value
            st.rerun()

st.markdown("""
<div class="hero">
  <div>✨ CLEARCUT AI</div>
  <h1>Bulk Image Background Remover</h1>
  <p>Remove image backgrounds and download transparent PNGs in one ZIP file.</p>
</div>
""", unsafe_allow_html=True)

is_guest = supabase is None or not st.session_state.is_logged_in
if is_guest:
    if st.session_state.guest_trial_used:
        st.warning("Guest trial already used in this session. Configure Supabase and sign in to continue.")
    else:
        st.info("Guest mode: one image per session. Sign in with Supabase to process batches.")

files = st.file_uploader(
    "Upload images (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
)

if files:
    count = len(files)
    st.write(f"**{count} image(s) selected**")
    allowed = True
    if is_guest and st.session_state.guest_trial_used:
        allowed = False
        st.error("Guest allowance has already been used.")
    elif is_guest and count > 1:
        allowed = False
        st.error("Guest mode supports one image at a time. Sign in to process batches.")
    elif not is_guest and st.session_state.account_credits < count:
        allowed = False
        st.error(f"Insufficient credits: {count} needed, {st.session_state.account_credits} available.")

    if allowed and st.button("Remove backgrounds", type="primary", use_container_width=True):
        processed = []
        errors = []
        progress = st.progress(0, text="Starting background removal...")
        for index, uploaded in enumerate(files):
            try:
                input_bytes = uploaded.getvalue()
                with Image.open(io.BytesIO(input_bytes)) as img:
                    img.verify()
                output_bytes = remove(input_bytes)
                with Image.open(io.BytesIO(output_bytes)) as output_image:
                    output_image = output_image.convert("RGBA")
                    output = io.BytesIO()
                    output_image.save(output, format="PNG", optimize=True)
                base_name = os.path.splitext(os.path.basename(uploaded.name))[0]
                processed.append((f"{base_name}_no_bg.png", output.getvalue()))
            except Exception as exc:
                errors.append(f"{uploaded.name}: {exc}")
            progress.progress((index + 1) / count, text=f"Processed {index + 1} of {count}")

        if processed:
            archive_buffer = io.BytesIO()
            with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
                for filename, data in processed:
                    archive.writestr(filename, data)

            if is_guest:
                st.session_state.guest_trial_used = True
            else:
                # Only deduct for images that succeeded. For production payments, move credit
                # deduction to a server-side atomic database function to avoid race conditions.
                new_balance = st.session_state.account_credits - len(processed)
                try:
                    (supabase.table("user_profiles").update({"credits": new_balance})
                     .eq("id", st.session_state.user_id).execute())
                    st.session_state.account_credits = new_balance
                except Exception as exc:
                    st.error(f"Images are ready, but credits could not be updated. Contact the administrator before retrying. Details: {exc}")

            st.success(f"Successfully processed {len(processed)} image(s).")
            st.download_button(
                "Download transparent PNGs (ZIP)",
                data=archive_buffer.getvalue(),
                file_name="clearcut_processed_images.zip",
                mime="application/zip",
                use_container_width=True,
            )
        if errors:
            st.warning("Some files could not be processed:")
            for error in errors:
                st.write(f"- {error}")
        if not processed:
            st.error("No images were processed. Try a different image or check the app logs.")

st.caption("The first run can take longer while the AI background-removal model downloads.")
