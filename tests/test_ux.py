import sys
from unittest.mock import MagicMock, patch
import pytest
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

# Import the module which runs the script
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
import bg_remove

def test_file_uploader_has_inline_constraint():
    """Test that the file uploader label includes the size constraint (max 10MB)."""
    # Check the call arguments of st.sidebar.file_uploader
    # The first argument is the label
    call_args = mock_st.sidebar.file_uploader.call_args
    assert call_args is not None, "st.sidebar.file_uploader was not called"

    label = call_args[0][0]
    assert "(max 10MB)" in label, f"Label '{label}' does not contain inline constraint '(max 10MB)'"
