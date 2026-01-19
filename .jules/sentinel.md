# Sentinel's Journal

## 2026-01-19 - Information Leakage in Streamlit Error Messages

**Vulnerability:** The application was catching exceptions and displaying `str(e)` directly to users via `st.error()`. This can expose internal paths, stack traces, or library-specific details that should not be visible to end-users.

**Learning:** Streamlit apps often default to "helpful" error messages for developers, but this practice persists into production. Specifically, `rembg` or `PIL` errors might contain system paths (e.g., model download locations like `~/.u2net`) or dependency versions.

**Prevention:** Always catch specific exceptions where possible, but for catch-all blocks (`except Exception`), log the full details to stderr/stdout (for admin visibility) and display a generic, sanitized message to the UI user.
