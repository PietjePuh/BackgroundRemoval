"""Tests for batch processing and ZIP archive creation."""

import zipfile
from io import BytesIO
from unittest.mock import MagicMock, patch


class TestCreateZipArchive:
    """Tests for the create_zip_archive function."""

    def test_creates_valid_zip_with_single_file(self, mock_env):
        bg_remove = mock_env["module"]

        images_data = [("test.png", b"fake_image_data")]
        result = bg_remove.create_zip_archive(images_data)

        assert isinstance(result, bytes)
        assert len(result) > 0

        # Verify it is a valid ZIP
        zf = zipfile.ZipFile(BytesIO(result))
        assert zf.namelist() == ["test.png"]
        assert zf.read("test.png") == b"fake_image_data"

    def test_creates_valid_zip_with_multiple_files(self, mock_env):
        bg_remove = mock_env["module"]

        images_data = [
            ("image1.png", b"data1"),
            ("image2.webp", b"data2"),
            ("image3.jpg", b"data3"),
        ]
        result = bg_remove.create_zip_archive(images_data)

        zf = zipfile.ZipFile(BytesIO(result))
        assert len(zf.namelist()) == 3
        assert zf.read("image1.png") == b"data1"
        assert zf.read("image2.webp") == b"data2"
        assert zf.read("image3.jpg") == b"data3"

    def test_creates_empty_zip_for_empty_list(self, mock_env):
        bg_remove = mock_env["module"]

        result = bg_remove.create_zip_archive([])

        zf = zipfile.ZipFile(BytesIO(result))
        assert zf.namelist() == []

    def test_zip_uses_deflate_compression(self, mock_env):
        bg_remove = mock_env["module"]

        images_data = [("test.png", b"x" * 1000)]
        result = bg_remove.create_zip_archive(images_data)

        zf = zipfile.ZipFile(BytesIO(result))
        info = zf.getinfo("test.png")
        assert info.compress_type == zipfile.ZIP_DEFLATED


class TestBatchSizeLimit:
    """Tests for batch processing limits."""

    def test_max_batch_size_constant_exists(self, mock_env):
        bg_remove = mock_env["module"]
        assert hasattr(bg_remove, "MAX_BATCH_SIZE")
        assert bg_remove.MAX_BATCH_SIZE == 10

    def test_output_formats_constant(self, mock_env):
        bg_remove = mock_env["module"]
        assert hasattr(bg_remove, "OUTPUT_FORMATS")
        assert "PNG" in bg_remove.OUTPUT_FORMATS
        assert "WEBP" in bg_remove.OUTPUT_FORMATS
        assert "JPEG" in bg_remove.OUTPUT_FORMATS


class TestFixImageBatch:
    """Tests for fix_image when used in batch context."""

    def test_fix_image_returns_tuple_on_success(self, mock_env):
        bg_remove = mock_env["module"]

        mock_upload = MagicMock()
        mock_upload.name = "test.jpg"
        mock_upload.getvalue.return_value = b"fake_bytes"

        mock_original = MagicMock()
        mock_fixed = MagicMock()
        mock_fixed.mode = "RGBA"

        with patch.object(bg_remove, "process_image", return_value=(mock_original, mock_fixed)):
            with patch.object(bg_remove, "apply_background_replacement", return_value=mock_fixed):
                with patch.object(bg_remove, "convert_image_to_format", return_value=b"output_bytes"):
                    result = bg_remove.fix_image(mock_upload, output_format="PNG")

                    assert result is not None
                    assert len(result) == 4
                    image, processed, filename, result_bytes = result
                    assert image is mock_original
                    assert filename == "test_rmbg.png"
                    assert result_bytes == b"output_bytes"

    def test_fix_image_returns_none_on_failure(self, mock_env):
        bg_remove = mock_env["module"]

        mock_upload = MagicMock()
        mock_upload.name = "test.jpg"
        mock_upload.getvalue.return_value = b"fake_bytes"

        with patch.object(bg_remove, "process_image", return_value=(None, None)):
            result = bg_remove.fix_image(mock_upload)
            assert result is None

    def test_fix_image_generates_correct_webp_filename(self, mock_env):
        bg_remove = mock_env["module"]

        mock_upload = MagicMock()
        mock_upload.name = "vacation_photo.png"
        mock_upload.getvalue.return_value = b"fake_bytes"

        mock_original = MagicMock()
        mock_fixed = MagicMock()
        mock_fixed.mode = "RGBA"

        with patch.object(bg_remove, "process_image", return_value=(mock_original, mock_fixed)):
            with patch.object(bg_remove, "apply_background_replacement", return_value=mock_fixed):
                with patch.object(bg_remove, "convert_image_to_format", return_value=b"output"):
                    result = bg_remove.fix_image(mock_upload, output_format="WEBP")

                    assert result is not None
                    _, _, filename, _ = result
                    assert filename == "vacation_photo_rmbg.webp"

    def test_fix_image_generates_correct_jpeg_filename(self, mock_env):
        bg_remove = mock_env["module"]

        mock_upload = MagicMock()
        mock_upload.name = "portrait.jpeg"
        mock_upload.getvalue.return_value = b"fake_bytes"

        mock_original = MagicMock()
        mock_fixed = MagicMock()
        mock_fixed.mode = "RGBA"

        with patch.object(bg_remove, "process_image", return_value=(mock_original, mock_fixed)):
            with patch.object(bg_remove, "apply_background_replacement", return_value=mock_fixed):
                with patch.object(bg_remove, "convert_image_to_format", return_value=b"output"):
                    result = bg_remove.fix_image(mock_upload, output_format="JPEG")

                    assert result is not None
                    _, _, filename, _ = result
                    assert filename == "portrait_rmbg.jpg"

    def test_fix_image_blocks_disallowed_path(self, mock_env):
        bg_remove = mock_env["module"]
        mock_st = mock_env["st"]

        result = bg_remove.fix_image("/etc/passwd")

        assert result is None
        mock_st.error.assert_called_with("Invalid image path.")

    def test_fix_image_allows_default_image_path(self, mock_env):
        bg_remove = mock_env["module"]

        mock_original = MagicMock()
        mock_fixed = MagicMock()
        mock_fixed.mode = "RGBA"

        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", new_callable=MagicMock) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = (
                    b"fake_bytes"
                )
                with patch.object(
                    bg_remove,
                    "process_image",
                    return_value=(mock_original, mock_fixed),
                ):
                    with patch.object(
                        bg_remove,
                        "apply_background_replacement",
                        return_value=mock_fixed,
                    ):
                        with patch.object(
                            bg_remove,
                            "convert_image_to_format",
                            return_value=b"output",
                        ):
                            result = bg_remove.fix_image("./zebra.jpg")

                            assert result is not None
                            mock_open.assert_called_with("./zebra.jpg", "rb")
