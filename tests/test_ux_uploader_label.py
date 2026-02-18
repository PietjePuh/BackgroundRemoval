import sys
from unittest.mock import MagicMock
import os

def test_uploader_label_has_constraint():
    """
    Test that the file uploader label includes the size constraint.
    UX Goal: Inline constraints reduce cognitive load.
    """
    # 1. Clean up sys.modules
    keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'streamlit' in k or 'PIL' in k or 'rembg' in k]
    for k in keys_to_remove:
        del sys.modules[k]

    # 2. Mock modules
    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.sidebar.file_uploader.return_value = None
    # Mock caches
    mock_st.cache_data = lambda *args, **kwargs: lambda func: func
    mock_st.cache_resource = lambda *args, **kwargs: lambda func: func
    # Mock session state
    mock_st.session_state = {}

    sys.modules['streamlit'] = mock_st
    sys.modules['rembg'] = MagicMock()
    sys.modules['numpy'] = MagicMock()
    sys.modules['PIL'] = MagicMock()
    sys.modules['PIL.Image'] = MagicMock()

    # 3. Import the module
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
    import bg_remove  # noqa: F401

    # 4. Verify file_uploader call
    assert mock_st.sidebar.file_uploader.called
    args, kwargs = mock_st.sidebar.file_uploader.call_args
    label = args[0]

    # Assert label contains "(max 10MB)"
    assert "(max 10MB)" in label, f"Label '{label}' does not contain size constraint '(max 10MB)'"
