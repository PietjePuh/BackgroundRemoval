## 2024-03-24 - [Leakage of Exception Details in Streamlit App]
**Vulnerability:** The application was catching exceptions and displaying `str(e)` directly to the user via `st.error`. This could leak sensitive internal information (paths, library versions, logic errors) to end-users.
**Learning:** In Streamlit apps, exception handling often defaults to displaying the error message for easier debugging during development. However, for production, this is a security risk.
**Prevention:** Always catch exceptions and display a generic message to the user ("An error occurred"), while logging the full traceback to the server console or a log file for developers to review.

## 2025-02-12 - [Missing Server-Side Upload Enforcement]
**Vulnerability:** The application relied solely on Python-level checks for file size limits (`my_upload.size > MAX`), allowing large files to be uploaded and consume server resources before validation.
**Learning:** Application-level validation is insufficient for DoS protection against large payloads; the web server (Streamlit) must enforce limits before passing data to the application.
**Prevention:** Always configure `server.maxUploadSize` in `.streamlit/config.toml` to reject oversized payloads at the network/server layer.
