import sys
from unittest.mock import MagicMock


def test_custom_bg_warning_shows_when_no_image_uploaded():
    """Verify that a warning/info message is shown when custom background mode is selected but no image is uploaded."""

    # 1. Setup mocks
    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    # Configure the radio button to return "custom_image"
    mock_st.sidebar.radio.return_value = "custom_image"

    # Configure file_uploader to return None (no file uploaded)
    mock_st.sidebar.file_uploader.return_value = None

    # Make cache decorators pass-through to avoid MagicMock unpacking issues
    def mock_cache_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return lambda func: func

    mock_st.cache_data = mock_cache_decorator
    mock_st.cache_resource = mock_cache_decorator

    # Mock other modules
    mock_pil = MagicMock()
    # Ensure Image.open returns a mock that has proper attributes if needed
    mock_image = MagicMock()
    mock_image.format = "PNG"
    mock_image.width = 100
    mock_image.height = 100
    mock_image.size = (100, 100)
    mock_pil.Image.open.return_value = mock_image

    # Mock rembg remove to return a mock image
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

    # 3. Verify the info message was shown
    mock_st.sidebar.info.assert_called_with("👆 Upload an image to use as background")
