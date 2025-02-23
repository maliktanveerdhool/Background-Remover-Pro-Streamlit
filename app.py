import streamlit as st
from PIL import Image
import io
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# Attempt to import rembg
try:
    from rembg import remove, new_session
    rembg_available = True
except ImportError as e:
    st.error(f"Failed to import rembg: {str(e)}")
    rembg_available = False

# Create a session for rembg if available
session = new_session() if rembg_available else None

@st.cache_data
def remove_background(image_array, alpha_matting=False, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10):
    if not rembg_available:
        st.error("The rembg library is not available. Please check the installation and dependencies.")
        return image_array
    
    try:
        return remove(
            image_array,
            session=session,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=alpha_matting_background_threshold,
            alpha_matting_erode_size=alpha_matting_erode_size
        )
    except Exception as e:
        st.error(f"An error occurred while removing the background: {str(e)}")
        return image_array

def resize_image(image, max_size=1000):
    ratio = max_size / max(image.size)
    if ratio < 1:
        return image.resize((int(image.size[0] * ratio), int(image.size[1] * ratio)), Image.LANCZOS)
    return image

def main():
    st.set_page_config(page_title="Background Remover Pro", page_icon="🚀", layout="wide")
    
    st.title("🖼️ Background Remover Pro")
    st.write("Upload an image and remove its background with ease!")

    if not rembg_available:
        st.warning("The rembg library is not available. Background removal functionality is disabled.")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    col1, col2 = st.columns(2)

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image = resize_image(image)  # Resize large images
        col1.image(image, caption="Original Image", use_column_width=True)
        
        with st.expander("Advanced Options"):
            alpha_matting = st.checkbox("Enable Alpha Matting", value=False)
            if alpha_matting:
                alpha_matting_foreground_threshold = st.slider("Foreground Threshold", 0, 255, 240)
                alpha_matting_background_threshold = st.slider("Background Threshold", 0, 255, 10)
                alpha_matting_erode_size = st.slider("Erode Size", 0, 40, 10)
            else:
                alpha_matting_foreground_threshold = 240
                alpha_matting_background_threshold = 10
                alpha_matting_erode_size = 10

        if st.button("Remove Background", key="remove_bg"):
            if not rembg_available:
                st.error("Background removal is not available due to missing dependencies.")
            else:
                with st.spinner("Processing image..."):
                    try:
                        with ThreadPoolExecutor() as executor:
                            future = executor.submit(
                                remove_background,
                                np.array(image),
                                alpha_matting,
                                alpha_matting_foreground_threshold,
                                alpha_matting_background_threshold,
                                alpha_matting_erode_size
                            )
                            result = future.result()
                        result_image = Image.fromarray(result)
                        col2.image(result_image, caption="Background Removed", use_column_width=True)
                    
                        buf = io.BytesIO()
                        result_image.save(buf, format="PNG")
                        byte_im = buf.getvalue()
                        col2.download_button(
                            label="Download Result",
                            data=byte_im,
                            file_name="background_removed.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

    st.sidebar.title("About")
    st.sidebar.info(
        "This app uses the rembg library to quickly remove backgrounds from images. "
        "Upload an image, adjust the settings if needed, and click 'Remove Background' to see the result."
    )
    st.sidebar.title("Tips")
    st.sidebar.markdown(
        "- For faster processing, use images under 1000x1000 pixels.\n"
        "- Disable Alpha Matting for quicker results on simple images.\n"
        "- For complex images, enable Alpha Matting and adjust the sliders."
    )

if __name__ == "__main__":
    main()
