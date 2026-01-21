## 2024-05-22 - Inline Constraints Reduce Cognitive Load
**Learning:** Users shouldn't have to search for file constraints (like size limits) in expandable sections or wait for an error message. Providing this info inline via tooltips prevents frustration and errors before they happen.
**Action:** Always check if file inputs have clear, accessible constraint information (size, type) visible or easily discoverable near the input itself.

## 2025-05-23 - Ephemeral Feedback for Async Operations
**Learning:** For long-running operations (like AI processing), static progress bars can feel impersonal or leave users wondering "is it really done?". Adding a celebratory toast notification provides closure and a moment of delight.
**Action:** Use `st.toast` with an icon for successful completion of async tasks to signal "success" distinctly from "progress complete".
