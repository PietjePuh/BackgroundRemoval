import sys
from unittest.mock import MagicMock
import pytest


def test_jpeg_transparency_warning_shows():
    """Verify that a warning/info message is shown when JPEG output and Transparent background are selected."""

    # 1. Setup mocks
    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    # Configure selectbox (output_format) to return "JPEG"
    mock_st.sidebar.selectbox.return_value = "JPEG"

    # Configure radio (bg_mode) to return "transparent"
    mock_st.sidebar.radio.return_value = "transparent"

    # Configure file_uploader to return None (no file uploaded)
    mock_st.sidebar.file_uploader.return_value = None

    # Make cache decorators pass-through
    def mock_cache_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return lambda func: func

    mock_st.cache_data = mock_cache_decorator
    mock_st.cache_resource = mock_cache_decorator

    # Mock session state
    mock_st.session_state = {}

    # Mock other modules
    mock_pil = MagicMock()
    mock_image = MagicMock()
    mock_image.format = "PNG"
    mock_image.width = 100
    mock_image.height = 100
    mock_image.size = (100, 100)
    mock_pil.Image.open.return_value = mock_image

    mock_rembg_module = MagicMock()
    mock_rembg_module.remove.return_value = MagicMock()

    # Clean sys.modules
    keys_to_remove = [
        k
        for k in sys.modules
        if "bg_remove" in k or "PIL" in k or "streamlit" in k or "rembg" in k
    ]
    for k in keys_to_remove:
        del sys.modules[k]

    sys.modules["streamlit"] = mock_st
    sys.modules["rembg"] = mock_rembg_module
    sys.modules["numpy"] = MagicMock()
    sys.modules["PIL"] = mock_pil
    sys.modules["PIL.Image"] = mock_pil.Image
    sys.modules["PIL.ImageFilter"] = mock_pil.ImageFilter

    # 2. Import bg_remove to run the script
    try:
        import bg_remove  # noqa: F401
        pass
    except Exception as e:
        # Catch potential errors during import if script execution fails
        pytest.fail(f"Script execution failed: {e}")

    # 3. Verify the info message was shown
    # The expected warning message
    expected_msg = (
        "ℹ️ JPEG does not support transparency. Result will have a white background."
    )

    # Check if any call to sidebar.info matches
    calls = [args[0] for args, _ in mock_st.sidebar.info.call_args_list]
    assert expected_msg in calls, (
        f"Expected warning '{expected_msg}' not found in {calls}"
    )
