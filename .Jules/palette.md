## 2024-05-22 - Inline Constraints Reduce Cognitive Load
**Learning:** Users shouldn't have to search for file constraints (like size limits) in expandable sections or wait for an error message. Providing this info inline via tooltips prevents frustration and errors before they happen.
**Action:** Always check if file inputs have clear, accessible constraint information (size, type) visible or easily discoverable near the input itself.

## 2026-01-25 - Ephemeral Success Feedback
**Learning:** For long-running asynchronous operations (like image processing), users need positive confirmation that the task is finished, especially if they've looked away. A toast notification provides this "delight" without requiring a modal dismissal.
**Action:** Use `st.toast` with a celebratory icon for successful completion of heavy background tasks.
