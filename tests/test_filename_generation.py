import sys
import os
from unittest.mock import MagicMock

# Clean up sys.modules
keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'PIL' in k or 'streamlit' in k or 'rembg' in k]
for k in keys_to_remove:
    del sys.modules[k]

# Mock modules
mock_st = MagicMock()
mock_st.columns.return_value = [MagicMock(), MagicMock()]
mock_st.sidebar.file_uploader.return_value = None
mock_st.cache_data = lambda *args, **kwargs: lambda func: func
mock_st.cache_resource = lambda *args, **kwargs: lambda func: func

sys.modules['streamlit'] = mock_st
sys.modules['rembg'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

import bg_remove

def test_get_download_filename_simple():
    assert bg_remove.get_download_filename("image.jpg") == "image_rmbg.png"

def test_get_download_filename_path():
    assert bg_remove.get_download_filename("/path/to/image.jpg") == "image_rmbg.png"

def test_get_download_filename_no_extension():
    assert bg_remove.get_download_filename("image") == "image_rmbg.png"

def test_get_download_filename_png():
    assert bg_remove.get_download_filename("image.png") == "image_rmbg.png"
