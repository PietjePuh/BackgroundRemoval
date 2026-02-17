import sys
from unittest.mock import MagicMock
import pytest
import os

def test_file_uploader_label_contains_constraint():
    """Test that the file uploader label contains explicit constraint information."""
    # Clean up sys.modules
    keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'streamlit' in k or 'PIL' in k or 'rembg' in k]
    for k in keys_to_remove:
        del sys.modules[k]

    # Mock streamlit
    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.sidebar.file_uploader.return_value = None
    mock_st.cache_data = lambda *args, **kwargs: lambda func: func
    mock_st.cache_resource = lambda *args, **kwargs: lambda func: func
    mock_st.session_state = {}

    sys.modules['streamlit'] = mock_st
    sys.modules['rembg'] = MagicMock()
    sys.modules['numpy'] = MagicMock()
    sys.modules['PIL'] = MagicMock()
    sys.modules['PIL.Image'] = MagicMock()

    # Import bg_remove
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
    import bg_remove

    # Check file_uploader call
    assert mock_st.sidebar.file_uploader.called
    args, kwargs = mock_st.sidebar.file_uploader.call_args
    label = args[0]

    # Assert label contains constraint info
    assert "(max 10MB)" in label, f"Label '{label}' does not contain '(max 10MB)'"
