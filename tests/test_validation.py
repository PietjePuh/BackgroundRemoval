"""Tests for file upload validation logic."""

import pytest
from unittest.mock import MagicMock, patch


class TestValidateUploadedFile:
    """Tests for the validate_uploaded_file function."""

    def test_valid_file_within_size_limit(self, mock_env):
        bg_remove = mock_env["module"]

        upload = MagicMock()
        upload.size = 5 * 1024 * 1024  # 5MB
        upload.name = "photo.jpg"

        is_valid, error_msg = bg_remove.validate_uploaded_file(upload)

        assert is_valid is True
        assert error_msg is None

    def test_file_exactly_at_size_limit(self, mock_env):
        bg_remove = mock_env["module"]

        upload = MagicMock()
        upload.size = 10 * 1024 * 1024  # 10MB (exact limit)
        upload.name = "photo.jpg"

        is_valid, error_msg = bg_remove.validate_uploaded_file(upload)

        assert is_valid is True
        assert error_msg is None

    def test_file_exceeds_size_limit(self, mock_env):
        bg_remove = mock_env["module"]

        upload = MagicMock()
        upload.size = 15 * 1024 * 1024  # 15MB
        upload.name = "huge_photo.png"

        is_valid, error_msg = bg_remove.validate_uploaded_file(upload)

        assert is_valid is False
        assert "too large" in error_msg
        assert "huge_photo.png" in error_msg

    def test_tiny_file_is_valid(self, mock_env):
        bg_remove = mock_env["module"]

        upload = MagicMock()
        upload.size = 100  # 100 bytes
        upload.name = "tiny.png"

        is_valid, error_msg = bg_remove.validate_uploaded_file(upload)

        assert is_valid is True
        assert error_msg is None

    def test_file_one_byte_over_limit(self, mock_env):
        bg_remove = mock_env["module"]

        upload = MagicMock()
        upload.size = 10 * 1024 * 1024 + 1  # 10MB + 1 byte
        upload.name = "slightly_too_big.jpg"

        is_valid, error_msg = bg_remove.validate_uploaded_file(upload)

        assert is_valid is False
        assert "too large" in error_msg


class TestProcessImageFormatValidation:
    """Tests for format validation within process_image."""

    def test_accepts_png_format(self, mock_env):
        bg_remove = mock_env["module"]
        mock_image_module = mock_env["image_module"]

        mock_img = MagicMock()
        mock_img.format = "PNG"
        mock_img.size = (100, 100)
        mock_img.width = 100
        mock_img.height = 100
        mock_img.resize.return_value = mock_img

        with patch.object(mock_image_module, "open", return_value=mock_img):
            with patch("bg_remove.remove", return_value=MagicMock()):
                img, fixed = bg_remove.process_image(b"fake_bytes")
                assert img is not None
                assert fixed is not None

    def test_accepts_jpeg_format(self, mock_env):
        bg_remove = mock_env["module"]
        mock_image_module = mock_env["image_module"]

        mock_img = MagicMock()
        mock_img.format = "JPEG"
        mock_img.size = (100, 100)
        mock_img.width = 100
        mock_img.height = 100
        mock_img.resize.return_value = mock_img

        with patch.object(mock_image_module, "open", return_value=mock_img):
            with patch("bg_remove.remove", return_value=MagicMock()):
                img, fixed = bg_remove.process_image(b"fake_bytes")
                assert img is not None
                assert fixed is not None

    def test_rejects_gif_format(self, mock_env):
        bg_remove = mock_env["module"]
        mock_st = mock_env["st"]
        mock_image_module = mock_env["image_module"]

        mock_img = MagicMock()
        mock_img.format = "GIF"
        mock_img.size = (100, 100)
        mock_img.width = 100
        mock_img.height = 100

        with patch.object(mock_image_module, "open", return_value=mock_img):
            img, fixed = bg_remove.process_image(b"fake_bytes")
            assert img is None
            assert fixed is None
            mock_st.error.assert_called_with(
                "Unsupported image format. Please upload a PNG or JPEG image."
            )

    def test_rejects_bmp_format(self, mock_env):
        bg_remove = mock_env["module"]
        mock_image_module = mock_env["image_module"]

        mock_img = MagicMock()
        mock_img.format = "BMP"
        mock_img.size = (100, 100)
        mock_img.width = 100
        mock_img.height = 100

        with patch.object(mock_image_module, "open", return_value=mock_img):
            img, fixed = bg_remove.process_image(b"fake_bytes")
            assert img is None
            assert fixed is None

    def test_rejects_oversized_dimensions(self, mock_env):
        bg_remove = mock_env["module"]
        mock_st = mock_env["st"]
        mock_image_module = mock_env["image_module"]

        mock_img = MagicMock()
        mock_img.format = "PNG"
        mock_img.size = (7000, 7000)
        mock_img.width = 7000
        mock_img.height = 7000

        with patch.object(mock_image_module, "open", return_value=mock_img):
            img, fixed = bg_remove.process_image(b"fake_bytes")
            assert img is None
            assert fixed is None
            args, _ = mock_st.error.call_args
            assert "Image is too large in dimensions" in args[0]
