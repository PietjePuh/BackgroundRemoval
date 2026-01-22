## 2024-03-24 - [Leakage of Exception Details in Streamlit App]
**Vulnerability:** The application was catching exceptions and displaying `str(e)` directly to the user via `st.error`. This could leak sensitive internal information (paths, library versions, logic errors) to end-users.
**Learning:** In Streamlit apps, exception handling often defaults to displaying the error message for easier debugging during development. However, for production, this is a security risk.
**Prevention:** Always catch exceptions and display a generic message to the user ("An error occurred"), while logging the full traceback to the server console or a log file for developers to review.

## 2024-03-24 - [Unrestricted File Upload Limits in Streamlit]
**Vulnerability:** Default Streamlit configuration allows uploads up to 200MB, potentially enabling DoS attacks via resource exhaustion. Application-level checks only validate file size *after* the upload is complete and stored in memory.
**Learning:** Streamlit's default `server.maxUploadSize` is generous (200MB). Relying solely on Python-side checks (`if file.size > X`) is inefficient and risky for DoS protection.
**Prevention:** Enforce strict upload limits at the infrastructure level using `.streamlit/config.toml` (`server.maxUploadSize`) to reject large payloads before they consume application memory.
