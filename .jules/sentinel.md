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

## 2026-01-31 - [Strict Image Format Validation]
**Vulnerability:** The application relied on `st.file_uploader` extensions for format validation, allowing potentially malicious files with renamed extensions (e.g., BMP renamed to PNG) to be processed by PIL.
**Learning:** `st.file_uploader` only validates the file extension on the client side (and simple server check). Libraries like PIL determine format by parsing the file header (magic bytes), which should be explicitly validated against an allowlist.
**Prevention:** Immediately after opening an image with `Image.open()`, check `image.format` against a strict allowlist (e.g., `["JPEG", "PNG"]`) before further processing.
