import streamlit as st
from rembg import remove, new_session
from PIL import Image, ImageFilter
from io import BytesIO
import os
import traceback
import time
import zipfile

st.set_page_config(layout="wide", page_title="Image Background Remover", page_icon="✂️")

st.title("Remove background from your image")
st.write(
    "Try uploading an image to watch the background magically removed. Full quality images can be downloaded below the result."
)
st.markdown(
    "This code is open source and available [here](https://github.com/PietjePuh/BackgroundRemoval) on GitHub. Special thanks to the [rembg library](https://github.com/danielgatis/rembg)."
)

# --- Sidebar Configuration ---
st.sidebar.header("Upload & Settings")

# Increased file size limit
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Maximum allowed source dimensions to prevent DoS via resizing
MAX_SOURCE_DIMENSION = 6000

# Max dimensions for processing
MAX_IMAGE_SIZE = 2000  # pixels

# Allowed default images
DEFAULT_IMAGES = ["./zebra.jpg", "./wallaby.png"]

# Supported output formats
OUTPUT_FORMATS = ["PNG", "WEBP", "JPEG"]

# Maximum images allowed in batch processing
MAX_BATCH_SIZE = 10


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


def validate_uploaded_file(upload):
    """Validate an uploaded file for size and format.

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if upload.size > MAX_FILE_SIZE:
        return (
            False,
            f"File '{upload.name}' is too large ({upload.size / 1024 / 1024:.1f}MB). Maximum: {MAX_FILE_SIZE / 1024 / 1024:.1f}MB.",
        )
    return True, None


def convert_image_to_format(img, output_format="PNG"):
    """Convert a PIL image to the specified format and return bytes.

    Args:
        img: PIL Image object
        output_format: One of 'PNG', 'WEBP', 'JPEG'

    Returns:
        bytes: The image encoded in the specified format
    """
    buf = BytesIO()
    save_kwargs = {}

    if output_format == "JPEG":
        # JPEG does not support transparency; composite onto white background
        if img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in img.info
        ):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")
        save_kwargs["quality"] = 95
    elif output_format == "WEBP":
        save_kwargs["quality"] = 90
        save_kwargs["lossless"] = False

    img.save(buf, format=output_format, **save_kwargs)
    return buf.getvalue()


# Download the fixed image (legacy wrapper for backward compatibility)
@st.cache_data(max_entries=10, ttl=3600)
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


def format_file_size(size_in_bytes):
    """Format a file size in bytes to a human-readable string."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"


def apply_background_replacement(
    fixed_img,
    bg_mode,
    bg_color=None,
    bg_blur_radius=15,
    bg_custom_image=None,
    original_img=None,
):
    """Apply background replacement to a processed (transparent) image.

    Args:
        fixed_img: PIL Image with transparent background (RGBA)
        bg_mode: One of 'transparent', 'solid_color', 'blur', 'custom_image'
        bg_color: Hex color string for solid_color mode
        bg_blur_radius: Blur radius for blur mode
        bg_custom_image: PIL Image for custom_image mode
        original_img: Original PIL Image for blur mode

    Returns:
        PIL Image with the replacement background applied
    """
    if bg_mode == "transparent":
        return fixed_img

    # Ensure the fixed image is RGBA
    if fixed_img.mode != "RGBA":
        fixed_img = fixed_img.convert("RGBA")

    target_size = fixed_img.size

    if bg_mode == "solid_color" and bg_color is not None:
        # Parse hex color
        hex_color = bg_color.lstrip("#")
        r, g, b = (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )
        background = Image.new("RGBA", target_size, (r, g, b, 255))
        background.paste(fixed_img, (0, 0), fixed_img)
        return background

    if bg_mode == "blur" and original_img is not None:
        blurred = original_img.copy()
        blurred = blurred.resize(target_size, Image.BICUBIC)
        blurred = blurred.filter(ImageFilter.GaussianBlur(radius=bg_blur_radius))
        if blurred.mode != "RGBA":
            blurred = blurred.convert("RGBA")
        blurred.paste(fixed_img, (0, 0), fixed_img)
        return blurred

    if bg_mode == "custom_image" and bg_custom_image is not None:
        custom_bg = bg_custom_image.copy()
        custom_bg = custom_bg.resize(target_size, Image.BICUBIC)
        if custom_bg.mode != "RGBA":
            custom_bg = custom_bg.convert("RGBA")
        custom_bg.paste(fixed_img, (0, 0), fixed_img)
        return custom_bg

    # Fallback: return as-is
    return fixed_img


def create_zip_archive(images_data):
    """Create a ZIP archive from a list of (filename, bytes) tuples.

    Args:
        images_data: List of (filename, image_bytes) tuples

    Returns:
        bytes: ZIP archive content
    """
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, img_bytes in images_data:
            zf.writestr(filename, img_bytes)
    return zip_buffer.getvalue()


def get_format_extension(output_format):
    """Get the file extension for a given output format."""
    extensions = {"PNG": "png", "WEBP": "webp", "JPEG": "jpg"}
    return extensions.get(output_format, "png")


def get_format_mime(output_format):
    """Get the MIME type for a given output format."""
    mimes = {"PNG": "image/png", "WEBP": "image/webp", "JPEG": "image/jpeg"}
    return mimes.get(output_format, "image/png")


def fix_image(
    upload,
    output_format="PNG",
    bg_mode="transparent",
    bg_color=None,
    bg_blur_radius=15,
    bg_custom_image=None,
):
    """Process a single image: remove background, apply replacement, display results.

    Args:
        upload: File upload object or string path to default image
        output_format: Output format (PNG, WEBP, JPEG)
        bg_mode: Background mode (transparent, solid_color, blur, custom_image)
        bg_color: Hex color for solid_color mode
        bg_blur_radius: Blur radius for blur mode
        bg_custom_image: PIL Image for custom background

    Returns:
        tuple: (original_image, result_image, output_filename, result_bytes) or None on failure
    """
    try:
        # Read image bytes
        if isinstance(upload, str):
            # Default image path
            if upload not in DEFAULT_IMAGES:
                st.error("Invalid image path.")
                print(
                    f"Security Warning: Attempted access to disallowed file: {upload}"
                )
                return None

            if not os.path.exists(upload):
                st.error(f"Default image not found at path: {upload}")
                return None
            with open(upload, "rb") as f:
                image_bytes = f.read()
            original_filename = os.path.basename(upload)
        else:
            # Uploaded file
            image_bytes = upload.getvalue()
            original_filename = upload.name

        # Process image (using cache if available)
        image, fixed = process_image(image_bytes)
        if image is None or fixed is None:
            return None

        # Apply background replacement
        result = apply_background_replacement(
            fixed_img=fixed,
            bg_mode=bg_mode,
            bg_color=bg_color,
            bg_blur_radius=bg_blur_radius,
            bg_custom_image=bg_custom_image,
            original_img=image,
        )

        # Generate output filename
        ext = get_format_extension(output_format)
        filename_base = os.path.splitext(original_filename)[0]
        output_filename = f"{filename_base}_rmbg.{ext}"

        # Convert to output format
        result_bytes = convert_image_to_format(result, output_format)

        return image, result, output_filename, result_bytes

    except Exception:
        st.error("An error occurred. Please try again.")
        print(f"Error in fix_image: {traceback.format_exc()}")
        return None


def display_single_result(
    image,
    result,
    output_filename,
    result_bytes,
    output_format,
    is_default=False,
    key_suffix="",
):
    """Display the before/after comparison and download button for a single image."""
    col1, col2 = st.columns(2)

    col1.subheader("Original Image :camera:")
    col1.image(image, use_container_width=True)

    col2.subheader("Background Removed :sparkles:")
    col2.image(result, use_container_width=True)

    if is_default:
        col2.caption("This is a sample result. Upload your own image in the sidebar!")

    col2.markdown("\n")
    size_str = format_file_size(len(result_bytes))
    resolution_str = f"{result.width}x{result.height}"
    col2.download_button(
        f"Download {output_format} image ({size_str})",
        result_bytes,
        output_filename,
        get_format_mime(output_format),
        help=f"Download {output_filename}\nSize: {size_str}\nResolution: {resolution_str}",
        use_container_width=True,
        type="primary",
        key=f"download_{key_suffix}",
    )


def display_batch_results(results, output_format):
    """Display results for batch processing in a grid layout.

    Args:
        results: List of (original_image, result_image, output_filename, result_bytes) tuples
        output_format: The output format used
    """
    if not results:
        return

    st.subheader(f"Processed {len(results)} image(s)")

    # Display results in a grid (2 columns: original | result per image)
    for idx, (image, result, output_filename, result_bytes) in enumerate(results):
        with st.expander(f"Image {idx + 1}: {output_filename}", expanded=(idx < 3)):
            col1, col2 = st.columns(2)

            col1.subheader("Original :camera:")
            col1.image(image, use_container_width=True)

            col2.subheader("Result :sparkles:")
            col2.image(result, use_container_width=True)
            size_str = format_file_size(len(result_bytes))
            col2.download_button(
                f"Download {output_filename} ({size_str})",
                result_bytes,
                output_filename,
                get_format_mime(output_format),
                use_container_width=True,
                key=f"download_batch_{idx}",
            )

    # Download All as ZIP
    st.markdown("---")
    zip_data = [(filename, img_bytes) for _, _, filename, img_bytes in results]
    zip_bytes = create_zip_archive(zip_data)
    zip_size_str = format_file_size(len(zip_bytes))
    st.download_button(
        f"Download All as ZIP ({zip_size_str})",
        zip_bytes,
        "background_removed_images.zip",
        "application/zip",
        help=f"Download {len(results)} images as a ZIP archive\nTotal size: {zip_size_str}",
        use_container_width=True,
        type="primary",
        key="download_all_zip",
    )


# --- Sidebar Controls ---

# Output format selection
output_format = st.sidebar.selectbox(
    "Output format",
    OUTPUT_FORMATS,
    index=0,
    help="Choose output format. JPEG will use a white background since it does not support transparency.",
)

# Background replacement options
st.sidebar.markdown("---")
st.sidebar.subheader("Background Replacement")
bg_mode = st.sidebar.radio(
    "Background mode",
    ["transparent", "solid_color", "blur", "custom_image"],
    format_func=lambda x: {
        "transparent": "Transparent",
        "solid_color": "Solid Color",
        "blur": "Blurred Original",
        "custom_image": "Custom Image",
    }[x],
    help="Choose what to replace the background with",
)

if output_format == "JPEG" and bg_mode == "transparent":
    st.sidebar.info(
        "ℹ️ JPEG does not support transparency. Result will have a white background."
    )

bg_color = None
bg_blur_radius = 15
bg_custom_image = None

if bg_mode == "solid_color":
    bg_color = st.sidebar.color_picker("Background color", "#FFFFFF")
elif bg_mode == "blur":
    bg_blur_radius = st.sidebar.slider(
        "Blur radius", 5, 50, 15, help="Higher values create a more blurred background"
    )
elif bg_mode == "custom_image":
    bg_upload = st.sidebar.file_uploader(
        "Upload background image",
        type=["png", "jpg", "jpeg"],
        key="bg_image_uploader",
    )
    if bg_upload is not None:
        bg_custom_image = Image.open(bg_upload)
    else:
        st.sidebar.info("👆 Upload an image to use as background")

# File uploader (batch mode)
st.sidebar.markdown("---")
my_uploads = st.sidebar.file_uploader(
    "Upload image(s) (max 10MB each)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    help=f"Supported formats: PNG, JPG, JPEG. Maximum: {MAX_FILE_SIZE // (1024 * 1024)}MB per file. Up to {MAX_BATCH_SIZE} images.",
)

# Information about limitations
with st.sidebar.expander("Image Guidelines"):
    st.write("""
    - Maximum file size: 10MB per image
    - Up to 10 images at once (batch mode)
    - Large images will be automatically resized
    - Supported formats: PNG, JPG, JPEG
    - Output formats: PNG, WEBP, JPEG
    - Processing time depends on image size
    """)

# --- Main Processing ---
if my_uploads:
    # Enforce batch size limit
    if len(my_uploads) > MAX_BATCH_SIZE:
        st.error(f"Too many files. Maximum {MAX_BATCH_SIZE} images allowed at once.")
        st.stop()

    # Validate all files first
    valid_uploads = []
    for upload in my_uploads:
        is_valid, error_msg = validate_uploaded_file(upload)
        if not is_valid:
            st.error(error_msg)
        else:
            valid_uploads.append(upload)

    if not valid_uploads:
        st.error("No valid files to process.")
        st.stop()

    # Check rate limit
    if not check_rate_limit():
        st.error(
            "Rate limit exceeded. Please wait a minute before processing another image."
        )
        st.stop()

    # Single image mode: display with full comparison view
    if len(valid_uploads) == 1:
        upload = valid_uploads[0]
        start_time = time.time()
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()

        status_text.text("Loading image...")
        progress_bar.progress(10)

        status_text.text("Processing image...")
        progress_bar.progress(30)

        result = fix_image(
            upload,
            output_format=output_format,
            bg_mode=bg_mode,
            bg_color=bg_color,
            bg_blur_radius=bg_blur_radius,
            bg_custom_image=bg_custom_image,
        )

        if result is not None:
            image, processed, output_filename, result_bytes = result
            progress_bar.progress(80)
            status_text.text("Displaying results...")

            display_single_result(
                image,
                processed,
                output_filename,
                result_bytes,
                output_format,
                is_default=False,
                key_suffix="single",
            )

            progress_bar.progress(100)
            processing_time = time.time() - start_time
            status_text.text(f"Completed in {processing_time:.2f} seconds")
            st.toast("Image processed successfully!", icon="✅")

    # Batch mode: process all and show grid
    else:
        start_time = time.time()
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()

        results = []
        for idx, upload in enumerate(valid_uploads):
            progress_pct = int(10 + (80 * idx / len(valid_uploads)))
            progress_bar.progress(progress_pct)
            status_text.text(f"Processing image {idx + 1} of {len(valid_uploads)}...")

            result = fix_image(
                upload,
                output_format=output_format,
                bg_mode=bg_mode,
                bg_color=bg_color,
                bg_blur_radius=bg_blur_radius,
                bg_custom_image=bg_custom_image,
            )
            if result is not None:
                results.append(result)

        progress_bar.progress(90)
        status_text.text("Preparing results...")

        display_batch_results(results, output_format)

        progress_bar.progress(100)
        processing_time = time.time() - start_time
        status_text.text(
            f"Completed {len(results)} images in {processing_time:.2f} seconds"
        )
        st.toast(
            f"Batch processing complete! {len(results)} images processed.", icon="✅"
        )

else:
    # No uploads: show default image
    for img_path in DEFAULT_IMAGES:
        if os.path.exists(img_path):
            result = fix_image(
                img_path,
                output_format=output_format,
                bg_mode=bg_mode,
                bg_color=bg_color,
                bg_blur_radius=bg_blur_radius,
                bg_custom_image=bg_custom_image,
            )
            if result is not None:
                image, processed, output_filename, result_bytes = result
                display_single_result(
                    image,
                    processed,
                    output_filename,
                    result_bytes,
                    output_format,
                    is_default=True,
                    key_suffix="default",
                )
            break
    else:
        st.info("Please upload an image to get started!")
