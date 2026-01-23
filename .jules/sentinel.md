## 2024-03-24 - [Leakage of Exception Details in Streamlit App]
**Vulnerability:** The application was catching exceptions and displaying `str(e)` directly to the user via `st.error`. This could leak sensitive internal information (paths, library versions, logic errors) to end-users.
**Learning:** In Streamlit apps, exception handling often defaults to displaying the error message for easier debugging during development. However, for production, this is a security risk.
**Prevention:** Always catch exceptions and display a generic message to the user ("An error occurred"), while logging the full traceback to the server console or a log file for developers to review.

## 2026-01-23 - [Path Traversal Risk in Internal Helper Functions]
**Vulnerability:** The `fix_image` function accepted a file path string and opened it without validation. While currently only called with trusted inputs, future code changes (e.g., exposing this parameter to user input) could lead to arbitrary file reads (Path Traversal).
**Learning:** Functions that handle file operations based on arguments should treat those arguments as untrusted, even if they are currently internal. "Defense in Depth" requires hardening these sinks against potential future misuse.
**Prevention:** Implement strict allowlists for file paths or validate that the input is a safe, expected file type/location before opening it. Refactor code to separate "processing from upload" vs "processing from path".
