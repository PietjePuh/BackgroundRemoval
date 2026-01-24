## 2024-03-24 - [Leakage of Exception Details in Streamlit App]
**Vulnerability:** The application was catching exceptions and displaying `str(e)` directly to the user via `st.error`. This could leak sensitive internal information (paths, library versions, logic errors) to end-users.
**Learning:** In Streamlit apps, exception handling often defaults to displaying the error message for easier debugging during development. However, for production, this is a security risk.
**Prevention:** Always catch exceptions and display a generic message to the user ("An error occurred"), while logging the full traceback to the server console or a log file for developers to review.

## 2026-01-24 - [Path Traversal Prevention in File Processors]
**Vulnerability:** The `fix_image` function accepted a string path argument which it opened directly. While current usage was safe, future changes could allow arbitrary file reading if user input were passed to this function.
**Learning:** Functions designed to process files should accept file objects/bytes whenever possible. If they must accept paths, strict allowlisting of allowed paths is required to prevent Path Traversal.
**Prevention:** Use an explicit allowlist (e.g., `DEFAULT_IMAGES`) for file paths. Validate that the input path is in this allowlist before opening the file.
