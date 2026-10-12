import streamlit as st
from rembg import remove
from PIL import Image
import io
import zipfile

# 1. SEARCH OPTIMIZED PAGE CONFIGURATION (SEO)
st.set_page_config(
    page_title="Bulk Background Remover - Free Online AI Image Eraser",
    page_icon="✂️",
    layout="centered",
    menu_items={
        'Get Help': 'https://github.com',
        'Report a bug': 'https://github.com/issues',
        'About': "# Bulk Background Remover\nAn open-source AI tool to erase image backdrops in batches completely free. Built for high-speed e-commerce product image preparation."
    }
)

st.title("✂️ Free Bulk Background Remover")
st.write("Clean backgrounds instantly. Free up to 3 images per batch!")

# 2. Monetization Configuration
FREE_LIMIT = 3
STRIPE_PAYMENT_URL = "https://stripe.com"

# 3. User Upload Deck
uploaded_files = st.file_uploader(
    "Upload JPG or PNG files for background removal:", 
    type=["png", "jpg", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    num_files = len(uploaded_files)
    
    if num_files > FREE_LIMIT:
        st.error(f"⚠️ Batch size limit exceeded! You uploaded {num_files} images. The free limit is {FREE_LIMIT}.")
        st.info("🎯 Need to process large commercial inventories or catalogs all at once?")
        
        st.markdown(
            f'<a href="{STRIPE_PAYMENT_URL}" target="_blank">'
            '<button style="background-color:#FF4B4B; color:white; border:none; '
            'padding:14px 28px; font-size:18px; font-weight:bold; border-radius:8px; cursor:pointer; width:100%;">'
            '🚀 Unlock Unlimited Bulk Processing ($9.99)</button></a>',
            unsafe_allow_html=True
        )
    else:
        st.info(f"Processing {num_files} image(s)...")
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            progress_bar = st.progress(0)
            
            for i, file in enumerate(uploaded_files):
                input_image_bytes = file.read()
                output_image_bytes = remove(input_image_bytes)
                
                # Dynamic string isolation for clean filenames
                file_name_clean = file.name.rsplit('.', 1)[0]
                clean_name = f"no_bg_{file_name_clean}.png"
                
                zip_file.writestr(clean_name, output_image_bytes)
                progress_bar.progress((i + 1) / num_files)
                
        st.success("🎉 Batch execution complete!")
        st.download_button(
            label="📥 Download Background Removed Images (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="bg_removed_batch.zip",
            mime="application/zip"
        )
