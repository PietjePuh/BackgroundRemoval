import sys
from unittest.mock import MagicMock
import pytest
import os

def test_no_unsafe_allow_html():
    """
    Test that st.markdown is NOT called with unsafe_allow_html=True.
    This ensures we don't accidentally enable XSS risks.
    """
    # 1. Clean up sys.modules to ensure we load bg_remove with OUR mocks
    keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'PIL' in k or 'streamlit' in k or 'rembg' in k]
    for k in keys_to_remove:
        del sys.modules[k]

    # 2. Mock modules BEFORE importing bg_remove
    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.sidebar.file_uploader.return_value = None
    # Make cache_data a pass-through decorator
    mock_st.cache_data = lambda *args, **kwargs: lambda func: func

    sys.modules['streamlit'] = mock_st
    sys.modules['rembg'] = MagicMock()
    sys.modules['numpy'] = MagicMock()
    sys.modules['PIL'] = MagicMock()
    sys.modules['PIL.Image'] = MagicMock()

    # 3. Import the module
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
    import bg_remove

    # 4. Verify st.markdown calls
    # We expect st.markdown to be called.
    assert mock_st.markdown.called, "st.markdown should be called at least once"

    for call in mock_st.markdown.call_args_list:
        args, kwargs = call
        # Check kwargs
        if 'unsafe_allow_html' in kwargs:
            assert kwargs['unsafe_allow_html'] is False, f"Found unsafe_allow_html=True in st.markdown call: {args}"
