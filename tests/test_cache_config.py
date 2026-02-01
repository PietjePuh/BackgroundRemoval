import sys
import os
import pytest
from unittest.mock import MagicMock

def test_cache_configuration():
    # Clean up sys.modules to ensure we load bg_remove with OUR mocks
    keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'streamlit' in k or 'PIL' in k or 'rembg' in k]
    for k in keys_to_remove:
        del sys.modules[k]

    # Mock streamlit BEFORE importing bg_remove
    mock_st = MagicMock()
    # Mock sub-components used in bg_remove
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.sidebar.file_uploader.return_value = None

    # Mock cache_data to inspect calls
    mock_st.cache_data = MagicMock()

    sys.modules['streamlit'] = mock_st

    # Mock PIL to support execution of fix_image during import
    mock_img_instance = MagicMock()
    mock_img_instance.format = "PNG"
    mock_img_instance.size = (100, 100)
    mock_img_instance.resize.return_value = mock_img_instance
    mock_img_instance.save = MagicMock()

    mock_PIL = MagicMock()
    mock_PIL.Image = MagicMock()
    mock_PIL.Image.open.return_value = mock_img_instance
    mock_PIL.Image.BICUBIC = 2
    mock_PIL.Image.DecompressionBombError = Exception

    sys.modules['PIL'] = mock_PIL

    # Mock rembg
    mock_rembg = MagicMock()
    mock_rembg.remove.return_value = mock_img_instance
    sys.modules['rembg'] = mock_rembg

    # Mock numpy
    sys.modules['numpy'] = MagicMock()

    # Import the module
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    import bg_remove

    # Check if cache_data was called with the expected arguments
    # We expect: st.cache_data(max_entries=10, ttl=3600)

    found = False
    for call in mock_st.cache_data.mock_calls:
        # call is (name, args, kwargs)
        _, args, kwargs = call
        if kwargs.get('max_entries') == 10 and kwargs.get('ttl') == 3600:
            found = True
            break

    if not found:
        print("\nCalls to st.cache_data:")
        for call in mock_st.cache_data.mock_calls:
            print(call)

    assert found, "st.cache_data was not called with max_entries=10 and ttl=3600"
