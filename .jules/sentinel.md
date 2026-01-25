## 2024-03-24 - [Leakage of Exception Details in Streamlit App]
**Vulnerability:** The application was catching exceptions and displaying `str(e)` directly to the user via `st.error`. This could leak sensitive internal information (paths, library versions, logic errors) to end-users.
**Learning:** In Streamlit apps, exception handling often defaults to displaying the error message for easier debugging during development. However, for production, this is a security risk.
**Prevention:** Always catch exceptions and display a generic message to the user ("An error occurred"), while logging the full traceback to the server console or a log file for developers to review.

## 2024-03-25 - [Path Traversal Risk in File Processing Utility]
**Vulnerability:** The `fix_image` function accepted arbitrary string file paths and opened them. While currently only called with hardcoded defaults, future refactoring or misuse could allow attackers to read sensitive files if user input flowed into this function.
**Learning:** Utility functions that handle file paths should be secure by default, not relying on the caller to provide safe inputs. This "Defense in Depth" approach prevents latent vulnerabilities from becoming exploitable later.
**Prevention:** Implement explicit whitelisting for allowed file paths or restrict file access to specific directories using strict validation or by designing APIs to accept file objects/streams instead of paths.
