import sys
from unittest.mock import MagicMock
import os

def test_custom_bg_warning_and_label():
    """
    Test that the custom background uploader has the correct label and shows a warning when empty.
    """
    # 1. Clean up sys.modules
    keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'streamlit' in k or 'PIL' in k or 'rembg' in k]
    for k in keys_to_remove:
        del sys.modules[k]

    # 2. Mock modules
    mock_st = MagicMock()
    # Mock sidebar
    mock_st.sidebar = MagicMock()
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

    # 4. Call the function
    result = bg_remove.render_custom_background_uploader()

    # 5. Verify file_uploader label
    assert mock_st.sidebar.file_uploader.called
    args, kwargs = mock_st.sidebar.file_uploader.call_args
    label = args[0]
    assert "(PNG, JPG)" in label, f"Label '{label}' does not contain expected format info '(PNG, JPG)'"

    # 6. Verify info message is shown when upload is None
    assert mock_st.sidebar.info.called
    info_args = mock_st.sidebar.info.call_args[0][0]
    assert "Upload an image" in info_args
    assert result is None

def test_custom_bg_upload_success():
    """Test successful upload."""
    # 1. Clean up sys.modules
    keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'streamlit' in k]
    for k in keys_to_remove:
        del sys.modules[k]

    mock_st = MagicMock()
    mock_upload = MagicMock()
    mock_st.sidebar.file_uploader.return_value = mock_upload

    mock_st.cache_data = lambda *args, **kwargs: lambda func: func
    mock_st.cache_resource = lambda *args, **kwargs: lambda func: func
    mock_st.session_state = {}

    sys.modules['streamlit'] = mock_st
    sys.modules['rembg'] = MagicMock()
    sys.modules['numpy'] = MagicMock()

    mock_pil = MagicMock()
    mock_pil.Image.open.return_value = "opened_image"
    sys.modules['PIL'] = mock_pil
    sys.modules['PIL.Image'] = mock_pil.Image

    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
    import bg_remove

    result = bg_remove.render_custom_background_uploader()

    assert result == "opened_image"
    assert not mock_st.sidebar.info.called
