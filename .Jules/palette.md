## 2024-05-22 - Inline Constraints Reduce Cognitive Load
**Learning:** Users shouldn't have to search for file constraints (like size limits) in expandable sections or wait for an error message. Providing this info inline via tooltips prevents frustration and errors before they happen.
**Action:** Always check if file inputs have clear, accessible constraint information (size, type) visible or easily discoverable near the input itself.

## 2024-05-23 - Async Feedback Delight
**Learning:** For asynchronous operations (like image processing), a subtle toast notification upon completion adds a layer of delight and reassurance that isn't conveyed by a stopped progress bar alone.
**Action:** Use `st.toast` with an appropriate icon (e.g., 🎉) for successful completion of heavy background tasks.
