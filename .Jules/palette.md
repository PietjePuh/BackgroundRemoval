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

## 2025-05-26 - Dynamic Filenames Reduce Friction
**Learning:** Users dislike renaming files after download. Automatically appending context (like `_rmbg`) to the original filename creates a seamless workflow and saves user effort.
**Action:** When offering file downloads, always attempt to derive a meaningful filename from the source input rather than using a static default.

## 2025-05-26 - Test Isolation in Streamlit Apps
**Learning:** Testing Streamlit apps that run on import is difficult when other tests mock `sys.modules`. Global state pollution causes cryptic failures in new tests.
**Action:** Use `importlib.reload()` or robust fixture-based module patching/restoration when testing Streamlit scripts to ensure a clean state for each test file.
