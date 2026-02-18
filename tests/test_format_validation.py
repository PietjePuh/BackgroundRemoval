import sys
from unittest.mock import MagicMock, patch
import os

# Clean up sys.modules to ensure we load bg_remove with OUR mocks
keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'PIL' in k or 'streamlit' in k or 'rembg' in k]
for k in keys_to_remove:
    del sys.modules[k]

# Mock modules BEFORE importing bg_remove
mock_st = MagicMock()
mock_st.columns.return_value = [MagicMock(), MagicMock()]
mock_st.sidebar.file_uploader.return_value = None
# Make cache_data a pass-through decorator (factory pattern)
mock_st.cache_data = lambda *args, **kwargs: lambda func: func

sys.modules['streamlit'] = mock_st
sys.modules['rembg'] = MagicMock()
sys.modules['numpy'] = MagicMock()

mock_image_module = MagicMock()
# Fix for catching DecompressionBombError which must be an Exception subclass
class MockDecompressionBombError(Exception):
    pass
mock_image_module.DecompressionBombError = MockDecompressionBombError

sys.modules['PIL'] = MagicMock()
sys.modules['PIL'].Image = mock_image_module
sys.modules['PIL.Image'] = mock_image_module

# Import the module
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
import bg_remove  # noqa: E402

def test_process_image_validates_format_success():
    """Test that process_image accepts valid formats (PNG, JPEG)."""
    mock_img = MagicMock()
    mock_img.format = "PNG"
    mock_img.size = (100, 100)
    mock_img.width = 100
    mock_img.height = 100
    # Mock resize to return the image itself (or another mock)
    mock_img.resize.return_value = mock_img

    with patch.object(bg_remove.Image, "open", return_value=mock_img):
        # We also need to mock remove to return something
        with patch("bg_remove.remove", return_value=MagicMock()):
             img, fixed = bg_remove.process_image(b"fake_bytes")
             assert img is not None
             assert fixed is not None

def test_process_image_rejects_invalid_format():
    """Test that process_image rejects invalid formats (e.g. GIF)."""
    mock_img = MagicMock()
    mock_img.format = "GIF"
    mock_img.size = (100, 100)
    mock_img.width = 100
    mock_img.height = 100

    with patch.object(bg_remove.Image, "open", return_value=mock_img):
        with patch.object(bg_remove.st, "error") as mock_error:
            img, fixed = bg_remove.process_image(b"fake_bytes")

            assert img is None
            assert fixed is None
            mock_error.assert_called_with("Unsupported image format. Please upload a PNG or JPEG image.")
