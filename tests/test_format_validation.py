import sys
import os
from unittest.mock import MagicMock

# Clean sys.modules of any previous bg_remove or streamlit or PIL
keys_to_remove = [k for k in sys.modules if 'bg_remove' in k or 'streamlit' in k or 'rembg' in k or 'PIL' in k]
for k in keys_to_remove:
    del sys.modules[k]

# Mock streamlit
mock_st = MagicMock()
mock_st.columns.return_value = [MagicMock(), MagicMock()]
mock_st.sidebar.file_uploader.return_value = None
mock_st.cache_data = lambda func: func
sys.modules['streamlit'] = mock_st

# Mock rembg
mock_rembg = MagicMock()
mock_rembg.remove = MagicMock(side_effect=lambda x: x) # Return input as output
sys.modules['rembg'] = mock_rembg

# Add current dir to path to find bg_remove
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bg_remove
from PIL import Image
from io import BytesIO
import pytest

def test_process_image_rejects_bmp():
    """Test that BMP images are rejected (returns None, None)."""
    # Create BMP
    img = Image.new('RGB', (100, 100), color=(255, 0, 0))
    buf = BytesIO()
    img.save(buf, format='BMP')
    bmp_bytes = buf.getvalue()

    image, fixed = bg_remove.process_image(bmp_bytes)

    # Expect rejection
    assert image is None
    assert fixed is None

def test_process_image_accepts_png():
    """Test that PNG images are accepted."""
    # Create PNG
    img = Image.new('RGB', (100, 100), color=(0, 0, 255))
    buf = BytesIO()
    img.save(buf, format='PNG')
    png_bytes = buf.getvalue()

    image, fixed = bg_remove.process_image(png_bytes)

    # Expect success
    assert image is not None
    assert fixed is not None
    assert image.format == 'PNG'

def test_process_image_accepts_jpeg():
    """Test that JPEG images are accepted."""
    # Create JPEG
    img = Image.new('RGB', (100, 100), color=(0, 255, 0))
    buf = BytesIO()
    img.save(buf, format='JPEG')
    jpeg_bytes = buf.getvalue()

    image, fixed = bg_remove.process_image(jpeg_bytes)

    # Expect success
    assert image is not None
    assert fixed is not None
    assert image.format == 'JPEG'
