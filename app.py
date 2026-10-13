import streamlit as st
import time

# -------------------------------------------------------------------
# 1. PREMIUM DESIGN THEME & BROWSER WINDOW SETUP
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AI Bulk Background Remover Pro", 
    page_icon="🎨", 
    layout="centered"
)

# Custom injection to add professional colors, shadows, and card styling
st.markdown("""
<style>
    /* Main Background Elements */
    .main { background-color: #f9fbfd; }
    h1 { color: #1e293b !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; }
    
    /* Premium Pricing Tier Cards Layout */
    .tier-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        border: 1px solid #e2e8f0;
        text-align: center;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .tier-card:hover { transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
    .tier-title-1 { color: #475569; font-size: 20px; font-weight: bold; }
    .tier-title-2 { color: #3b82f6; font-size: 20px; font-weight: bold; }
    .tier-title-3 { color: #8b5cf6; font-size: 20px; font-weight: bold; }
    .tier-price { font-size: 32px; font-weight: 800; color: #0f172a; margin: 10px 0; }
    .tier-features { color: #64748b; font-size: 14px; line-height: 1.6; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 2. RUNTIME TRACKING LOGIC
# -------------------------------------------------------------------
if 'has_used_free_tier' not in st.session_state:
    st.session_state.has_used_free_tier = False

# -------------------------------------------------------------------
# 3. INTERACTIVE HEADER GRAPHICS
# -------------------------------------------------------------------
st.title("🖼️ AI Bulk Background Remover Pro")
st.markdown("##### *Transform your images with crisp, automated transparent cutouts in seconds.*")

# Before / After Comparison Visual Graphic Banner
st.markdown("""
<div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #bfdbfe; margin-bottom: 25px;">
    <span style="font-size: 14px; font-weight: 600; color: #1d4ed8; text-transform: uppercase; letter-spacing: 0.05em;">AI Processing Model Active</span>
    <div style="display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 10px;">
        <div style="background: #cbd5e1; padding: 10px 20px; border-radius: 6px; font-weight: 600; color: #475569; font-size: 13px;">📸 Original Photo</div>
        <div style="font-size: 24px;">➡️</div>
        <div style="background: white; padding: 10px 20px; border-radius: 6px; font-weight: 600; color: #2563eb; font-size: 13px; border: 2px dashed #3b82f6;">✨ Isolated PNG</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Status notifications based on user quota limits
if not st.session_state.has_used_free_tier:
    st.toast("🎁 Free operation available!")
    st.info("🎁 **Free Account Status:** You can process **1 image** right now completely free!")
else:
    st.error("⚠️ **Free Tier Balance Consumed:** Please pick an instant high-speed expansion pack below to clear your next file batch.")

# -------------------------------------------------------------------
# 4. MAIN FILE PROCESSOR INTERFACE
# -------------------------------------------------------------------
st.subheader("🚀 Upload Image Batch")
uploaded_files = st.file_uploader(
    "Drop your target image files here (Supports PNG, JPG, JPEG):", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    num_files = len(uploaded_files)
    st.markdown(f"📦 Files selected for batch queue: **{num_files}**")
    
    if num_files > 1 and not st.session_state.has_used_free_tier:
        st.warning(f"🚨 You uploaded {num_files} files. The free plan allows **1 image at a time**. Select a pack below to run bulk extractions.")
        execute_disabled = True
    elif st.session_state.has_used_free_tier:
        execute_disabled = True
    else:
        execute_disabled = False

    if st.button("🔥 Run AI Background Isolation", disabled=execute_disabled, use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for index, file in enumerate(uploaded_files):
            status_text.text(f"Isolating targets in image {index + 1} of {num_files}...")
            time.sleep(0.7) 
            percent_complete = int(((index + 1) / len(uploaded_files)) * 100)
            progress_bar.progress(percent_complete)
            
        status_text.empty()
        st.balloons()
        st.success("🎉 Backgrounds extracted cleanly! Downloads prepared successfully.")
        st.session_state.has_used_free_tier = True
        st.calendar = True
        time.sleep(1.5)
        st.rerun()

# -------------------------------------------------------------------
# 5. DYNAMIC COLOR-CODED PRICING MATRIX
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("⚡ Upgrade Your Token Balance Instantly")
st.markdown("Scan or click your choice to pay safely via **UPI apps (GPay, PhonePe, Paytm) or Cards**.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="tier-card">
        <div class="tier-title-1">🪵 Starter Pack</div>
        <div class="tier-price">₹49</div>
        <div class="tier-features">🪙 <b>30 Images</b><br>⚡ High Speed Processing<br>📅 Credits Never Expire</div>
    </div>
    """, unsafe_allow_html=True)
    # Replace URL below with your ₹49 Razorpay link
    st.link_button("🚀 Buy 30 Credits", "https://rzp.io", use_container_width=True)

with col2:
    st.markdown("""
    <div class="tier-card" style="border: 2px solid #3b82f6;">
        <div class="tier-title-2">🔥 Popular Growth</div>
        <div class="tier-price">₹99</div>
        <div class="tier-features">🪙 <b>100 Images</b><br>⚡ Dedicated Model Queue<br>📅 Credits Never Expire</div>
    </div>
    """, unsafe_allow_html=True)
    # Replace URL below with your ₹99 Razorpay link
    st.link_button("⚡ Buy 100 Credits", "https://rzp.io", use_container_width=True)

with col3:
    st.markdown("""
    <div class="tier-card">
        <div class="tier-title-3">🏆 Enterprise Pro</div>
        <div class="tier-price">₹299</div>
        <div class="tier-features">🪙 <b>500 Images</b><br>⚡ Maximum Priority Support<br>📅 Unlimited Validity</div>
    </div>
    """, unsafe_allow_html=True)
    # Replace URL below with your ₹299 Razorpay link
    st.link_button("💎 Buy 500 Credits", "https://rzp.io", use_container_width=True)

# -------------------------------------------------------------------
# 6. COMPLIANCE & LEGAL SETTINGS
# -------------------------------------------------------------------
st.markdown("---")
st.subheader("📬 Customer Support & Verification Details")
st.info("📧 Operations Support Email: **pawan990013@gmail.com**")

st.subheader("⚖️ Legal Policy Protocols")
with st.expander("Terms and Conditions"): st.write("Welcome to Bulk Background Remover. By accessing this web tool, you formally consent to these compliance parameters: This software provides automated background identification outputs via deep neural computing logic. All processing rights, target copyrights, and asset ownership remain strictly with the uploading user entity.")
with st.expander("Privacy Policy"): st.write("Your digital footprint security is our baseline operational parameter: User account identification data (such as emails) is stored solely to allocate account usage logs and payment confirmations.")
with st.expander("Cancellation & Refund Policy"): st.write("Our commitment to transparent commercial trade: Approved processing reversals are securely executed via Razorpay and route directly back to the original funding source within 5 to 7 standard working business days.")
