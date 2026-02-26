import sys
from unittest.mock import MagicMock

def test_jpeg_transparent_warning_shows():
    """Verify that a warning/info message is shown when JPEG format and Transparent background are selected."""

    # 1. Setup mocks
    mock_st = MagicMock()
    # Ensure columns returns iterables to avoid iteration errors
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    # Configure output_format to "JPEG" (first call to selectbox in sidebar)
    mock_st.sidebar.selectbox.return_value = "JPEG"

    # Configure bg_mode to "transparent" (radio button)
    mock_st.sidebar.radio.return_value = "transparent"

    # Mock file_uploader to return None (no file uploaded yet)
    mock_st.sidebar.file_uploader.return_value = None

    # Make cache decorators pass-through
    def mock_cache_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return lambda func: func

    mock_st.cache_data = mock_cache_decorator
    mock_st.cache_resource = mock_cache_decorator

    # Mock other modules
    mock_pil = MagicMock()
    mock_st.image = MagicMock()

    # Clean sys.modules
    keys_to_remove = [k for k in sys.modules if "bg_remove" in k or "PIL" in k or "streamlit" in k or "rembg" in k]
    for k in keys_to_remove:
        del sys.modules[k]

    sys.modules["streamlit"] = mock_st
    sys.modules["rembg"] = MagicMock()
    sys.modules["numpy"] = MagicMock()
    sys.modules["PIL"] = mock_pil
    sys.modules["PIL.Image"] = mock_pil.Image
    sys.modules["PIL.ImageFilter"] = mock_pil.ImageFilter

    # 2. Import bg_remove to run the script
    import bg_remove  # noqa: F401

    # 3. Verify the info message was shown
    # Note: Using assert_any_call because there might be other calls
    mock_st.sidebar.info.assert_any_call("ℹ️ JPEG does not support transparency. Result will have a white background.")
