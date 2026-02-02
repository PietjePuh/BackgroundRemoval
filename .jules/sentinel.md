## 2024-03-24 - [Leakage of Exception Details in Streamlit App]
**Vulnerability:** The application was catching exceptions and displaying `str(e)` directly to the user via `st.error`. This could leak sensitive internal information (paths, library versions, logic errors) to end-users.
**Learning:** In Streamlit apps, exception handling often defaults to displaying the error message for easier debugging during development. However, for production, this is a security risk.
**Prevention:** Always catch exceptions and display a generic message to the user ("An error occurred"), while logging the full traceback to the server console or a log file for developers to review.

## 2026-01-26 - [Latent Path Traversal in Internal Helper Functions]
**Vulnerability:** The `fix_image` function accepted arbitrary file paths as strings without validation, relying solely on the caller to provide safe inputs.
**Learning:** Internal helper functions handling file I/O in Streamlit apps often get reused. Implicit trust in callers can lead to Path Traversal if the function is later exposed to user input.
**Prevention:** Enforce strict allowlists for file paths within the utility function itself, treating it as a security boundary.

## 2026-02-12 - [DoS Vulnerability via Image Resizing Algorithm]
**Vulnerability:** The application used `Image.LANCZOS` for resizing user-uploaded images. This filter is computationally expensive and scales poorly with image complexity, making it a vector for Denial of Service (DoS) attacks via CPU exhaustion.
**Learning:** High-quality image processing filters (like LANCZOS) often come with a significant performance cost that can be exploited in public-facing applications.
**Prevention:** Use `Image.BICUBIC` or `Image.BILINEAR` for resizing user content where strict fidelity is secondary to availability. Explicitly handle `Image.DecompressionBombError` to gracefully reject excessively large images.

## 2026-02-18 - [Unbounded Cache Growth via st.cache_data]
**Vulnerability:** The application used `@st.cache_data` without `max_entries` or `ttl`. This allows an attacker to exhaust server memory by uploading unique images, as each processed result is cached indefinitely.
**Learning:** Streamlit's caching defaults prioritize convenience over security. In production, unbounded caches are a Denial of Service (DoS) vector.
**Prevention:** Explicitly configure `max_entries` and `ttl` (Time To Live) on all Streamlit cache decorators to enforce resource boundaries.

## 2026-03-05 - [DoS via Large Image Dimensions]
**Vulnerability:** The application relied on `Image.DecompressionBombError` (default limit ~89MP) and file size limits (10MB) but allowed resizing of images with large dimensions (e.g. 100MP). Resizing extremely large images to the target size (2000px) using `Image.BICUBIC` consumes excessive CPU, leading to DoS.
**Learning:** File size limits are insufficient for DoS protection against compressed images (e.g., solid color PNGs). `Image.open` is lazy, allowing dimension checks before pixel loading.
**Prevention:** Implement an explicit check for maximum source dimensions (e.g., width/height > 6000) immediately after opening the image header and before any processing or resizing operations.
