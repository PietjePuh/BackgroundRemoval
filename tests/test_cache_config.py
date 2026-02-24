import sys
import os
import pytest
from unittest.mock import MagicMock


def test_cache_configuration():
    # Clean up sys.modules to ensure we load bg_remove with OUR mocks
    keys_to_remove = [
        k
        for k in sys.modules
        if "bg_remove" in k or "streamlit" in k or "PIL" in k or "rembg" in k
    ]
    for k in keys_to_remove:
        del sys.modules[k]

    # Mock streamlit BEFORE importing bg_remove
    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.sidebar.file_uploader.return_value = None

    # Mock cache_data to inspect calls
    mock_st.cache_data = MagicMock()
    # Ensure it returns a callable so it can act as a decorator
    mock_st.cache_data.return_value = lambda func: func

    sys.modules["streamlit"] = mock_st

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

    sys.modules["PIL"] = mock_PIL

    # Mock rembg
    mock_rembg = MagicMock()
    mock_rembg.remove.return_value = mock_img_instance
    sys.modules["rembg"] = mock_rembg

    # Mock numpy
    sys.modules["numpy"] = MagicMock()

    # Import the module
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    import bg_remove  # noqa: F401

    # Verify that ALL calls to st.cache_data have limits.
    # We expect 2 calls (process_image and convert_image).

    assert len(mock_st.cache_data.mock_calls) >= 2, (
        "Expected at least 2 cached functions"
    )

    for call in mock_st.cache_data.mock_calls:
        name, args, kwargs = call

        # Check for unbounded usage: @st.cache_data (without args) results in the function being passed as the first arg.
        if args and (callable(args[0]) or hasattr(args[0], "__name__")):
            pytest.fail(
                f"Unbounded cache usage detected! @st.cache_data used without arguments on {args[0]}"
            )

        # Check that limits are present in kwargs
        if not args:
            if "max_entries" not in kwargs:
                pytest.fail(f"Missing max_entries in cache config: {kwargs}")
            if "ttl" not in kwargs:
                pytest.fail(f"Missing ttl in cache config: {kwargs}")

            # Specifically check the values match our policy
            assert kwargs["max_entries"] == 10
            assert kwargs["ttl"] == 3600
