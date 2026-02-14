import streamlit as st
from rembg import remove, new_session
from PIL import Image
import numpy as np
from io import BytesIO
import os
import traceback
import time

st.set_page_config(layout="wide", page_title="Image Background Remover", page_icon="✂️")

st.title("Remove background from your image")
st.write(
    "Try uploading an image to watch the background magically removed. Full quality images can be downloaded below the result."
)
st.markdown(
    "This code is open source and available [here](https://github.com/PietjePuh/BackgroundRemoval) on GitHub. Special thanks to the [rembg library](https://github.com/danielgatis/rembg).",
    unsafe_allow_html=True,
)
st.sidebar.header("Upload Image")

# Increased file size limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Maximum allowed source dimensions to prevent DoS via resizing
MAX_SOURCE_DIMENSION = 6000

# Max dimensions for processing
MAX_IMAGE_SIZE = 2000  # pixels

# Allowed default images
DEFAULT_IMAGES = ["./zebra.jpg", "./wallaby.png"]


def check_rate_limit():
    """Rate limiting to prevent DoS via repeated processing"""
    if "request_times" not in st.session_state:
        st.session_state["request_times"] = []

    now = time.time()
    # Clean up old requests (1 minute window)
    st.session_state["request_times"] = [
        t for t in st.session_state["request_times"] if now - t < 60
    ]

    if len(st.session_state["request_times"]) >= 5:  # Limit: 5 per minute
        return False

    st.session_state["request_times"].append(now)
    return True


# Download the fixed image
@st.cache_data
def convert_image(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im


# Resize image while maintaining aspect ratio
def resize_image(image, max_size):
    width, height = image.size
    if width <= max_size and height <= max_size:
        return image

    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))

    return image.resize((new_width, new_height), Image.BICUBIC)


@st.cache_resource
def get_session():
    return new_session("u2net")


@st.cache_data(max_entries=10, ttl=3600)
def process_image(image_bytes):
    """Process image with caching to avoid redundant processing"""
    try:
        image = Image.open(BytesIO(image_bytes))

        # Security: Enforce strict format validation
        # PIL detects the format based on the file header, not extension
        if image.format not in ["JPEG", "PNG"]:
            print(
                f"Security Warning: Unsupported image format detected: {image.format}"
            )
            st.error("Unsupported image format. Please upload a PNG or JPEG image.")
            return None, None

        # Security: Check dimensions to prevent DoS via resizing
        if image.width > MAX_SOURCE_DIMENSION or image.height > MAX_SOURCE_DIMENSION:
            print(f"Security Warning: Image dimensions too large: {image.size}")
            st.error(
                f"Image is too large in dimensions. Max allowed: {MAX_SOURCE_DIMENSION}x{MAX_SOURCE_DIMENSION}"
            )
            return None, None

        # Resize large images to prevent memory issues
        resized = resize_image(image, MAX_IMAGE_SIZE)
        # Process the image
        session = get_session()
        fixed = remove(resized, session=session)
        return image, fixed
    except Image.DecompressionBombError as e:
        print(f"Decompression Bomb Error: {e}")  # Log for security audit
        st.error("Image is too large to process.")
        return None, None
    except Exception as e:
        print(f"Error processing image: {str(e)}")  # Log for debugging
        st.error("An error occurred while processing the image. Please try again.")
        return None, None


def get_download_filename(filename):
    """Generates a filename for the processed image."""
    base, _ = os.path.splitext(os.path.basename(filename))
    return f"{base}_rmbg.png"


def fix_image(upload):
    try:
        start_time = time.time()
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()

        status_text.text("Loading image...")
        progress_bar.progress(10)

        # Read image bytes
        if isinstance(upload, str):
            # Default image path
            if upload not in DEFAULT_IMAGES:
                st.error("Invalid image path.")
                print(
                    f"Security Warning: Attempted access to disallowed file: {upload}"
                )
                return

            if not os.path.exists(upload):
                st.error(f"Default image not found at path: {upload}")
                return
            with open(upload, "rb") as f:
                image_bytes = f.read()
            original_filename = upload
        else:
            # Uploaded file
            image_bytes = upload.getvalue()
            original_filename = upload.name

        status_text.text("Processing image...")
        progress_bar.progress(30)

        # Process image (using cache if available)
        image, fixed = process_image(image_bytes)
        if image is None or fixed is None:
            return

        progress_bar.progress(80)
        status_text.text("Displaying results...")

        # Display images
        col1.subheader("Original Image :camera:")
        col1.image(image, use_container_width=True)

        col2.subheader("Background Removed :sparkles:")
        col2.image(fixed, use_container_width=True)

        if isinstance(upload, str):
            col2.caption(
                "💡 This is a sample result. Upload your own image in the sidebar!"
            )

        # Prepare download button
        col2.markdown("\n")
        col2.download_button(
            "📥 Download transparent image",
            convert_image(fixed),
            get_download_filename(original_filename),
            "image/png",
            help="Download the processed image with transparent background",
            use_container_width=True,
            type="primary",
            key="download_fixed",
        )

        progress_bar.progress(100)
        processing_time = time.time() - start_time
        status_text.text(f"Completed in {processing_time:.2f} seconds")
        st.toast("Image processed successfully! 🎉", icon="🎉")

    except Exception as e:
        st.error("An error occurred. Please try again.")
        st.sidebar.error("Failed to process image")
        # Log the full error for debugging
        print(f"Error in fix_image: {traceback.format_exc()}")


# UI Layout
col1, col2 = st.columns(2)
my_upload = st.sidebar.file_uploader(
    "Upload an image",
    type=["png", "jpg", "jpeg"],
    help="Supported formats: PNG, JPG, JPEG. Maximum supported size: 10MB",
)

# Information about limitations
with st.sidebar.expander("ℹ️ Image Guidelines"):
    st.write("""
    - Maximum file size: 10MB
    - Large images will be automatically resized
    - Supported formats: PNG, JPG, JPEG
    - Processing time depends on image size
    """)

# Process the image
if my_upload is not None:
    if my_upload.size > MAX_FILE_SIZE:
        st.error(
            f"The uploaded file is too large. Please upload an image smaller than {MAX_FILE_SIZE/1024/1024:.1f}MB."
        )
    else:
        # Check rate limit for new uploads
        file_id = f"{my_upload.name}-{my_upload.size}"
        if (
            "last_upload_id" not in st.session_state
            or st.session_state["last_upload_id"] != file_id
        ):
            if not check_rate_limit():
                st.error(
                    "Rate limit exceeded. Please wait a minute before processing another image."
                )
                st.stop()
            st.session_state["last_upload_id"] = file_id

        fix_image(upload=my_upload)
else:
    # Try default images in order of preference
    for img_path in DEFAULT_IMAGES:
        if os.path.exists(img_path):
            fix_image(img_path)
            break
    else:
        st.info("Please upload an image to get started!")
