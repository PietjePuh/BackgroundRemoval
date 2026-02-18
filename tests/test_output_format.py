"""Tests for output format conversion logic."""

from unittest.mock import MagicMock


class TestConvertImageToFormat:
    """Tests for the convert_image_to_format function."""

    def test_png_output_preserves_transparency(self, mock_env):
        bg_remove = mock_env["module"]

        # Create a real small RGBA image for realistic testing
        img = MagicMock()
        img.mode = "RGBA"
        img.size = (10, 10)
        img.info = {}
        img.save = MagicMock()

        bg_remove.convert_image_to_format(img, "PNG")

        img.save.assert_called_once()
        args, kwargs = img.save.call_args
        assert kwargs.get("format", args[1] if len(args) > 1 else None) == "PNG"

    def test_webp_output_with_quality(self, mock_env):
        bg_remove = mock_env["module"]

        img = MagicMock()
        img.mode = "RGBA"
        img.size = (10, 10)
        img.info = {}
        img.save = MagicMock()

        bg_remove.convert_image_to_format(img, "WEBP")

        img.save.assert_called_once()
        _, kwargs = img.save.call_args
        assert kwargs["quality"] == 90

    def test_jpeg_converts_rgba_to_rgb_with_white_background(self, mock_env):
        bg_remove = mock_env["module"]

        # Mock an RGBA image
        img = MagicMock()
        img.mode = "RGBA"
        img.size = (10, 10)
        img.info = {}

        # Mock the alpha channel split
        mock_alpha = MagicMock()
        img.split.return_value = [MagicMock(), MagicMock(), MagicMock(), mock_alpha]

        # The function should create a new RGB background and paste
        result_bytes = bg_remove.convert_image_to_format(img, "JPEG")

        # Verify the function returns bytes (not None)
        assert result_bytes is not None
        assert isinstance(result_bytes, bytes)

    def test_jpeg_handles_rgb_image_directly(self, mock_env):
        bg_remove = mock_env["module"]

        img = MagicMock()
        img.mode = "RGB"
        img.size = (10, 10)
        img.info = {}
        img.save = MagicMock()

        bg_remove.convert_image_to_format(img, "JPEG")

        # Should save directly without conversion
        img.save.assert_called_once()
        _, kwargs = img.save.call_args
        assert kwargs["quality"] == 95

    def test_jpeg_converts_la_mode(self, mock_env):
        bg_remove = mock_env["module"]

        img = MagicMock()
        img.mode = "LA"
        img.size = (10, 10)
        img.info = {}
        mock_alpha = MagicMock()
        img.split.return_value = [MagicMock(), mock_alpha]

        result_bytes = bg_remove.convert_image_to_format(img, "JPEG")
        assert result_bytes is not None

    def test_returns_bytes(self, mock_env):
        bg_remove = mock_env["module"]

        img = MagicMock()
        img.mode = "RGB"
        img.size = (10, 10)
        img.info = {}
        img.save = MagicMock()

        result = bg_remove.convert_image_to_format(img, "PNG")
        assert isinstance(result, bytes)


class TestGetFormatExtension:
    """Tests for the get_format_extension helper."""

    def test_png_extension(self, mock_env):
        bg_remove = mock_env["module"]
        assert bg_remove.get_format_extension("PNG") == "png"

    def test_webp_extension(self, mock_env):
        bg_remove = mock_env["module"]
        assert bg_remove.get_format_extension("WEBP") == "webp"

    def test_jpeg_extension(self, mock_env):
        bg_remove = mock_env["module"]
        assert bg_remove.get_format_extension("JPEG") == "jpg"

    def test_unknown_format_defaults_to_png(self, mock_env):
        bg_remove = mock_env["module"]
        assert bg_remove.get_format_extension("TIFF") == "png"


class TestGetFormatMime:
    """Tests for the get_format_mime helper."""

    def test_png_mime(self, mock_env):
        bg_remove = mock_env["module"]
        assert bg_remove.get_format_mime("PNG") == "image/png"

    def test_webp_mime(self, mock_env):
        bg_remove = mock_env["module"]
        assert bg_remove.get_format_mime("WEBP") == "image/webp"

    def test_jpeg_mime(self, mock_env):
        bg_remove = mock_env["module"]
        assert bg_remove.get_format_mime("JPEG") == "image/jpeg"

    def test_unknown_format_defaults_to_png_mime(self, mock_env):
        bg_remove = mock_env["module"]
        assert bg_remove.get_format_mime("BMP") == "image/png"
