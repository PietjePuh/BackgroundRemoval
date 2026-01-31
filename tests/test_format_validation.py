import sys
from unittest.mock import MagicMock, patch
import pytest
import io
import importlib
from PIL import Image

@pytest.fixture
def bg_remove_module():
    """
    Fixture to mock streamlit and other dependencies, then import bg_remove.
    Uses patch.dict to avoid polluting global sys.modules.
    """
    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.sidebar.file_uploader.return_value = None
    mock_st.cache_data = lambda func: func

    mock_rembg = MagicMock()
    mock_numpy = MagicMock()

    # We patch sys.modules. We preserve existing modules (like PIL) but override the ones we mock.
    modules_to_patch = {
        'streamlit': mock_st,
        'rembg': mock_rembg,
        'numpy': mock_numpy,
    }

    # We need to make sure bg_remove is re-imported within this patch context
    # so it picks up the mocked 'streamlit'.
    # If it was already in sys.modules, we should remove it from the *dict* we are about to apply?
    # No, patch.dict applies changes.

    # We must remove 'bg_remove' from the REAL sys.modules before patching,
    # OR force a reload inside the patch.
    # But if we remove it from real sys.modules, we might affect other tests?
    # Ideally, we restore it. patch.dict does restore.

    # Strategy:
    # 1. Start patch.dict
    # 2. If bg_remove is in sys.modules, reload it. If not, import it.
    #    (Reloading works if the dependencies in sys.modules are the mocks)

    with patch.dict(sys.modules, modules_to_patch):
        if 'bg_remove' in sys.modules:
            # We must reload it to pick up the new mocked streamlit
            import bg_remove
            importlib.reload(bg_remove)
        else:
            import bg_remove

        yield bg_remove

def test_process_image_rejects_bmp(bg_remove_module):
    """
    Test that process_image rejects BMP format.
    """
    # Create a BMP image in memory
    img = Image.new('RGB', (100, 100), color='red')
    buf = io.BytesIO()
    img.save(buf, format='BMP')
    bmp_bytes = buf.getvalue()

    # Access the mocked streamlit from the module
    mock_st = bg_remove_module.st

    with patch.object(bg_remove_module, "remove", return_value=Image.new('RGBA', (100, 100))):
        with patch.object(mock_st, "error") as mock_error:
            image, fixed = bg_remove_module.process_image(bmp_bytes)

            assert image is None
            assert fixed is None

            # Check for error message
            args, _ = mock_error.call_args
            assert "Unsupported image format" in args[0]

def test_process_image_accepts_png(bg_remove_module):
    """
    Test that process_image accepts PNG format.
    """
    img = Image.new('RGB', (100, 100), color='blue')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    png_bytes = buf.getvalue()

    with patch.object(bg_remove_module, "remove", return_value=Image.new('RGBA', (100, 100))):
        image, fixed = bg_remove_module.process_image(png_bytes)
        assert image is not None
        assert fixed is not None
