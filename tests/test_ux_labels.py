import sys
from unittest.mock import MagicMock
import os
import pytest

def test_file_uploader_label_contains_size_limit():
    """
    Verify that the file uploader label includes the size limit constraint.
    This ensures the UX improvement (inline constraint) is maintained.
    """
    # Clean up sys.modules to ensure we load bg_remove with OUR mocks
    keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'streamlit' in k or 'rembg' in k or 'PIL' in k]
    for k in keys_to_remove:
        del sys.modules[k]

    # Mock streamlit
    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.sidebar.file_uploader.return_value = None
    # Make cache_data a pass-through decorator (factory pattern)
    mock_st.cache_data = lambda *args, **kwargs: lambda func: func

    sys.modules['streamlit'] = mock_st
    sys.modules['rembg'] = MagicMock()
    sys.modules['numpy'] = MagicMock()

    # Mock PIL
    mock_image_module = MagicMock()
    # Mock DecompressionBombError as an Exception subclass
    class MockDecompressionBombError(Exception):
        pass
    mock_image_module.DecompressionBombError = MockDecompressionBombError

    sys.modules['PIL'] = MagicMock()
    sys.modules['PIL'].Image = mock_image_module
    sys.modules['PIL.Image'] = mock_image_module

    # Import the module
    # This will execute the top-level code, including st.sidebar.file_uploader
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
    import bg_remove

    # Check the call arguments of file_uploader
    # It is called in the module scope
    mock_st.sidebar.file_uploader.assert_called()

    # Get the arguments of the last call
    args, kwargs = mock_st.sidebar.file_uploader.call_args
    label = args[0]

    # Assertions
    assert "Upload an image" in label
    assert "(max 10MB)" in label, "Label should contain size limit constraint"
    assert label == "Upload an image (max 10MB)"
