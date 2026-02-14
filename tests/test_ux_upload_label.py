import sys
import os
import pytest
from unittest.mock import MagicMock

def test_upload_label_has_constraints():
    # Clean up sys.modules to ensure we load bg_remove with OUR mocks
    keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'streamlit' in k or 'PIL' in k or 'rembg' in k]
    for k in keys_to_remove:
        del sys.modules[k]

    # Mock streamlit BEFORE importing bg_remove
    mock_st = MagicMock()
    # Mock sub-components used in bg_remove
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.sidebar.file_uploader.return_value = None

    # Mock cache_data to prevent errors
    mock_st.cache_data = lambda *args, **kwargs: lambda func: func

    # Mock session state
    mock_st.session_state = {}

    sys.modules['streamlit'] = mock_st

    # Mock PIL
    mock_PIL = MagicMock()
    mock_PIL.Image = MagicMock()
    mock_PIL.Image.BICUBIC = 2
    mock_PIL.Image.DecompressionBombError = Exception
    sys.modules['PIL'] = mock_PIL

    # Mock rembg
    sys.modules['rembg'] = MagicMock()

    # Mock numpy
    sys.modules['numpy'] = MagicMock()

    # Import the module
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import bg_remove

    # Check if file_uploader was called with the expected label

    calls = mock_st.sidebar.file_uploader.call_args_list
    assert len(calls) > 0, "st.sidebar.file_uploader was not called"

    args, kwargs = calls[0]
    label = args[0]

    assert "(max 10MB)" in label, f"Label '{label}' does not contain size constraint '(max 10MB)'"
