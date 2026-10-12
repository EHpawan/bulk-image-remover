import streamlit as st
from rembg import remove
from PIL import Image
import io
import zipfile

# 1. Page Configuration
st.set_page_config(page_title="Pro Bulk Background Remover", layout="centered")
st.title("✂️ Pro Bulk Background Remover")
st.write("Clean backgrounds instantly. Free up to 3 images!")

# 2. Add Monetization Tier Threshold
FREE_LIMIT = 3
# Paste your real Stripe Payment link inside the quotes below
STRIPE_PAYMENT_URL = "https://stripe.com"

# 3. File Uploader Layout
uploaded_files = st.file_uploader(
    "Choose JPG or PNG images", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

# 4. Processing Logic Gate
if uploaded_files:
    num_files = len(uploaded_files)
    
    # PAYWALL GATE CHECK
    if num_files > FREE_LIMIT:
        st.error(f"⚠️ You uploaded {num_files} images. The free tier is limited to {FREE_LIMIT} images per batch.")
        st.info("💡 Need to process large commercial batches for e-commerce or design?")
        
        # Large eye-catching payment button
        st.markdown(
            f'<a href="{STRIPE_PAYMENT_URL}" target="_blank">'
            '<button style="background-color:#FF4B4B; color:white; border:none; '
            'padding:12px 24px; font-size:18px; border-radius:8px; cursor:pointer; width:100%;">'
            '🚀 Unlock Unlimited Bulk Processing ($9.99/mo)</button></a>',
            unsafe_allow_html=True
        )
    else:
        # EXECUTE PROCESSING FOR FREE TIER VALID USERS
        st.info(f"Processing {num_files} image(s)...")
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            progress_bar = st.progress(0)
            
            for i, file in enumerate(uploaded_files):
                input_image_bytes = file.read()
                output_image_bytes = remove(input_image_bytes)
                
                # Keep file names clean
                file_root = file.name.rsplit('.', 1)[0]
                clean_name = f"no_bg_{file_root}.png"
                
                zip_file.writestr(clean_name, output_image_bytes)
                progress_bar.progress((i + 1) / num_files)
                
        st.success("🎉 Batch processed successfully!")
        st.download_button(
            label="📥 Download Free Images (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="free_bg_removed.zip",
            mime="application/zip"
        )
