import sys
from unittest.mock import MagicMock, patch
import os

# Clean up sys.modules to ensure we load bg_remove with OUR mocks
keys_to_remove = [
    k
    for k in sys.modules
    if "bg_remove" in k or "PIL" in k or "streamlit" in k or "rembg" in k
]
for k in keys_to_remove:
    del sys.modules[k]

# Mock modules BEFORE importing bg_remove
mock_st = MagicMock()
mock_st.columns.return_value = [MagicMock(), MagicMock()]
mock_st.sidebar.file_uploader.return_value = None
# Make cache_data a pass-through decorator (factory pattern)
mock_st.cache_data = lambda *args, **kwargs: lambda func: func

sys.modules["streamlit"] = mock_st
sys.modules["rembg"] = MagicMock()
sys.modules["numpy"] = MagicMock()

# Setup Image mock
mock_image_module = MagicMock()


class MockDecompressionBombError(Exception):
    pass


mock_image_module.DecompressionBombError = MockDecompressionBombError
# Assign values to filters to verify usage
mock_image_module.LANCZOS = 1
mock_image_module.BICUBIC = 2

# Crucial: Link PIL.Image in sys.modules AND on the PIL mock
sys.modules["PIL"] = MagicMock()
sys.modules["PIL"].Image = mock_image_module
sys.modules["PIL.Image"] = mock_image_module

# Import the module
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../"))
import bg_remove  # noqa: E402


def test_process_image_handles_decompression_bomb():
    """
    Test that process_image handles DecompressionBombError by showing a specific error.
    """
    # Mock Image.open to raise DecompressionBombError
    # We use side_effect with the INSTANCE of the exception
    exception_instance = bg_remove.Image.DecompressionBombError("Bomb!")

    with patch.object(bg_remove.Image, "open", side_effect=exception_instance):
        with patch.object(bg_remove.st, "error") as mock_error:
            image, fixed = bg_remove.process_image(b"fake_bytes")

            # Expect graceful failure
            assert image is None
            assert fixed is None

            # Expect specific error message (Target Behavior)
            mock_error.assert_called_with("Image is too large to process.")


def test_resize_image_uses_bicubic():
    """
    Test that resize_image uses BICUBIC filter.
    """
    # Create a mock image
    mock_img = MagicMock()
    mock_img.size = (5000, 5000)  # Large enough to trigger resize

    # We need to ensure resize returns something
    mock_img.resize.return_value = MagicMock()

    bg_remove.resize_image(mock_img, 2000)

    # Check that resize was called with BICUBIC
    # Note: verify the args. BICUBIC is 2 in our mock.
    # The call is image.resize((new_w, new_h), filter)
    args, kwargs = mock_img.resize.call_args

    # Debug print if assertions fail
    print(f"Resize called with args: {args}")

    assert args[1] == bg_remove.Image.BICUBIC
