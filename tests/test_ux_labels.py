import sys
from unittest.mock import MagicMock
import os

def test_file_uploader_label_contains_constraint():
    """
    Test that the file uploader label explicitly includes the size constraint.
    This is a UX requirement to reduce cognitive load.
    """
    # 1. Clean up sys.modules to ensure we load bg_remove with OUR mocks
    keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'PIL' in k or 'streamlit' in k or 'rembg' in k]
    for k in keys_to_remove:
        del sys.modules[k]

    # 2. Mock modules BEFORE importing bg_remove
    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.sidebar.file_uploader.return_value = None
    # Mock caches
    mock_st.cache_data = lambda *args, **kwargs: lambda func: func
    mock_st.cache_resource = lambda *args, **kwargs: lambda func: func
    mock_st.session_state = {}

    sys.modules['streamlit'] = mock_st
    sys.modules['rembg'] = MagicMock()
    sys.modules['numpy'] = MagicMock()
    sys.modules['PIL'] = MagicMock()
    sys.modules['PIL.Image'] = MagicMock()

    # 3. Import the module
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
    import bg_remove  # noqa: F401

    # 4. Verify file_uploader label
    assert mock_st.sidebar.file_uploader.called
    args, kwargs = mock_st.sidebar.file_uploader.call_args
    label = args[0]

    assert "max 10MB" in label, f"File uploader label '{label}' should contain '(max 10MB)' constraint"
