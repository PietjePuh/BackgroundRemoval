import sys
from unittest.mock import MagicMock
import pytest

def test_custom_bg_warning_shows_when_no_image_uploaded():
    """Verify that a warning/info message is shown when custom background mode is selected but no image is uploaded."""

    # Store original modules to restore later
    original_modules = sys.modules.copy()

    try:
        # 1. Setup mocks
        mock_st = MagicMock()
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        # Configure cache decorators to be pass-through
        def mock_cache_decorator(*args, **kwargs):
            # Handle both @st.cache_data and @st.cache_data(...)
            if len(args) == 1 and callable(args[0]):
                return args[0]
            return lambda func: func

        mock_st.cache_data = mock_cache_decorator
        mock_st.cache_resource = mock_cache_decorator
        mock_st.session_state = {}

        # Configure the radio button to return "custom_image"
        mock_st.sidebar.radio.return_value = "custom_image"

        # Configure file_uploader to return None (no file uploaded)
        mock_st.sidebar.file_uploader.return_value = None

        # Mock other modules to prevent ImportErrors
        mock_pil = MagicMock()
        # Ensure Image.open returns a valid mock with format
        mock_image = MagicMock()
        mock_image.format = "PNG"
        mock_image.width = 100
        mock_image.height = 100
        mock_image.size = (100, 100)
        mock_pil.Image.open.return_value = mock_image

        mock_pil.Image.new.return_value = MagicMock()
        mock_pil.Image.BICUBIC = 3
        mock_pil.Image.LANCZOS = 1

        # Subclass Exception for DecompressionBombError
        class MockDecompressionBombError(Exception):
            pass
        mock_pil.Image.DecompressionBombError = MockDecompressionBombError

        mock_pil.ImageFilter = MagicMock()

        # Clean sys.modules to ensure fresh import
        # Remove modules related to what we are mocking
        keys_to_remove = [k for k in sys.modules if "bg_remove" in k or "PIL" in k or "streamlit" in k or "rembg" in k]
        for k in keys_to_remove:
            del sys.modules[k]

        sys.modules["streamlit"] = mock_st
        sys.modules["rembg"] = MagicMock()
        # Mock rembg.remove to return an image
        sys.modules["rembg"].remove.return_value = MagicMock()

        sys.modules["numpy"] = MagicMock()
        sys.modules["PIL"] = mock_pil
        sys.modules["PIL.Image"] = mock_pil.Image
        sys.modules["PIL.ImageFilter"] = mock_pil.ImageFilter

        # 2. Import bg_remove to run the script
        import bg_remove

        # 3. Verify the info message was shown
        # We expect st.sidebar.info to be called with a specific message
        mock_st.sidebar.info.assert_called_with("👆 Upload an image to use as background")

    finally:
        # Restore original modules
        # This is a crude way to restore, but effectively undoes our pollution
        # First, remove everything currently in sys.modules
        sys.modules.clear()
        # Then update with original
        sys.modules.update(original_modules)
