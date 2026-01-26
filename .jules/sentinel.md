## 2024-03-24 - [Leakage of Exception Details in Streamlit App]
**Vulnerability:** The application was catching exceptions and displaying `str(e)` directly to the user via `st.error`. This could leak sensitive internal information (paths, library versions, logic errors) to end-users.
**Learning:** In Streamlit apps, exception handling often defaults to displaying the error message for easier debugging during development. However, for production, this is a security risk.
**Prevention:** Always catch exceptions and display a generic message to the user ("An error occurred"), while logging the full traceback to the server console or a log file for developers to review.

## 2026-01-26 - [Latent Path Traversal in Internal Helper Functions]
**Vulnerability:** The `fix_image` function accepted arbitrary file paths as strings without validation, relying solely on the caller to provide safe inputs.
**Learning:** Internal helper functions handling file I/O in Streamlit apps often get reused. Implicit trust in callers can lead to Path Traversal if the function is later exposed to user input.
**Prevention:** Enforce strict allowlists for file paths within the utility function itself, treating it as a security boundary.
