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
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

# Import the module
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
import bg_remove  # noqa: E402

def test_process_image_rejects_large_dimensions():
    """Test that process_image rejects images that exceed the max source dimension."""
    mock_img = MagicMock()
    mock_img.format = "PNG"
    # Dimensions larger than the planned 6000 limit
    mock_img.size = (7000, 7000)
    mock_img.width = 7000
    mock_img.height = 7000

    with patch.object(bg_remove.Image, "open", return_value=mock_img):
        with patch.object(bg_remove.st, "error") as mock_error:
            # Call process_image
            img, fixed = bg_remove.process_image(b"fake_bytes")

            # Assertions
            # 1. Should return None, None
            assert img is None
            assert fixed is None

            # 2. Should show a specific error message
            # The exact message depends on implementation, but checking substring or call
            # We planned to check: "Image is too large in dimensions"
            args, _ = mock_error.call_args
            assert "Image is too large in dimensions" in args[0]
