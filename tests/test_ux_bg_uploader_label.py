import sys
from unittest.mock import MagicMock
import os


def test_bg_uploader_label_has_constraint():
    """
    Test that the custom background image file uploader explicitly includes the size constraint.
    UX Goal: Inline constraints reduce cognitive load.
    """
    # 1. Clean up sys.modules
    keys_to_remove = [
        k
        for k in sys.modules
        if "bg_remove" in k or "streamlit" in k or "PIL" in k or "rembg" in k
    ]
    for k in keys_to_remove:
        del sys.modules[k]

    # 2. Mock modules
    mock_st = MagicMock()
    mock_st.columns.return_value = [MagicMock(), MagicMock()]
    mock_st.sidebar.file_uploader.return_value = None

    # We need to test the background uploader, so we must mock the radio button
    # to return 'custom_image' so that the code path is executed.
    mock_st.sidebar.radio.return_value = "custom_image"

    # Mock caches
    mock_st.cache_data = lambda *args, **kwargs: lambda func: func
    mock_st.cache_resource = lambda *args, **kwargs: lambda func: func
    # Mock session state
    mock_st.session_state = {}

    sys.modules["streamlit"] = mock_st
    sys.modules["rembg"] = MagicMock()
    sys.modules["numpy"] = MagicMock()
    sys.modules["PIL"] = MagicMock()
    sys.modules["PIL.Image"] = MagicMock()

    # 3. Import the module
    sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../"))
    import bg_remove  # noqa: F401

    # 4. Verify file_uploader calls
    assert mock_st.sidebar.file_uploader.called

    # Find the call for the background uploader
    bg_uploader_call = None
    for call in mock_st.sidebar.file_uploader.call_args_list:
        args, kwargs = call
        if kwargs.get("key") == "bg_image_uploader":
            bg_uploader_call = call
            break

    assert bg_uploader_call is not None, "Background uploader was not called"

    args, kwargs = bg_uploader_call
    label = args[0]

    # Assert label contains "(max 10MB)" constraint
    assert "(max 10MB)" in label, (
        f"Label '{label}' does not contain size constraint '(max 10MB)'"
    )

    # Assert help text is present
    assert "help" in kwargs, "Help text is missing from the background uploader"
    help_text = kwargs["help"]
    assert "Maximum: 10MB" in help_text, (
        f"Help text '{help_text}' does not contain 'Maximum: 10MB'"
    )
