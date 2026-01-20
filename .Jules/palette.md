## 2024-05-22 - Inline Constraints Reduce Cognitive Load
**Learning:** Users shouldn't have to search for file constraints (like size limits) in expandable sections or wait for an error message. Providing this info inline via tooltips prevents frustration and errors before they happen.
**Action:** Always check if file inputs have clear, accessible constraint information (size, type) visible or easily discoverable near the input itself.

## 2026-01-20 - Semantic Headers in Streamlit
**Learning:** Using `st.write` for headings degrades accessibility as it renders as plain text (paragraphs). `st.subheader` or `st.header` ensures proper HTML heading tags (`<h3>`, `<h2>`), allowing screen readers to navigate the page structure effectively.
**Action:** Replace stylistic text formatting in `st.write` with semantic `st.header`, `st.subheader`, or `st.caption` to improve document hierarchy and accessibility.
