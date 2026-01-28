## 2024-05-22 - Inline Constraints Reduce Cognitive Load
**Learning:** Users shouldn't have to search for file constraints (like size limits) in expandable sections or wait for an error message. Providing this info inline via tooltips prevents frustration and errors before they happen.
**Action:** Always check if file inputs have clear, accessible constraint information (size, type) visible or easily discoverable near the input itself.

## 2024-05-23 - Semantic Headings and Delightful Feedback
**Learning:** Using semantic elements like `st.subheader` instead of generic `st.write` significantly improves document structure for screen readers. Coupling this with `st.toast` for asynchronous success states provides necessary feedback that feels polished ("delightful") without cluttering the UI.
**Action:** Replace `st.write` with `st.header/subheader` for section titles and always include `st.toast` for successful completion of long-running tasks.

## 2024-05-24 - Action Clarity with Tooltips and Icons
**Learning:** Generic button labels like "Download" can be ambiguous. Adding an icon (📥) provides visual scanning speed, and a tooltip clarifies the specific outcome (e.g., "Save to computer"), reducing hesitation for users.
**Action:** Enhance primary action buttons with relevant icons and descriptive tooltips, especially for file operations.
