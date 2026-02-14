## 2024-05-22 - Inline Constraints Reduce Cognitive Load
**Learning:** Users shouldn't have to search for file constraints (like size limits) in expandable sections or wait for an error message. Providing this info inline via tooltips prevents frustration and errors before they happen.
**Action:** Always check if file inputs have clear, accessible constraint information (size, type) visible or easily discoverable near the input itself.

## 2024-05-23 - Semantic Headings and Delightful Feedback
**Learning:** Using semantic elements like `st.subheader` instead of generic `st.write` significantly improves document structure for screen readers. Coupling this with `st.toast` for asynchronous success states provides necessary feedback that feels polished ("delightful") without cluttering the UI.
**Action:** Replace `st.write` with `st.header/subheader` for section titles and always include `st.toast` for successful completion of long-running tasks.

## 2025-05-24 - Action Proximity in Mobile Layouts
**Learning:** Placing primary actions (like 'Download') in a collapsible sidebar creates friction for mobile users who must toggle the menu to proceed. Co-locating the next logical action with the result (e.g., button below the image) creates a seamless flow.
**Action:** Move result-dependent actions out of sidebars and into the main content flow, directly adjacent to the content they act upon.

## 2025-05-25 - Default State Clarity
**Learning:** When an app pre-loads content (like a sample image), users can be confused if it's their data or a demo. Explicitly labeling sample content reduces confusion and guides the next action.
**Action:** Always label default/demo content with a caption or banner explaining it's a sample and how to replace it.

## 2026-02-13 - Dynamic Filenames Improve Workflow
**Learning:** Static download filenames (like 'fixed.png') force users to manually rename files, creating friction for batch processing. Preserving the original name context (e.g., 'photo_rmbg.png') feels more thoughtful and organized.
**Action:** Always derive download filenames from the input source to maintain context and improve file management.
