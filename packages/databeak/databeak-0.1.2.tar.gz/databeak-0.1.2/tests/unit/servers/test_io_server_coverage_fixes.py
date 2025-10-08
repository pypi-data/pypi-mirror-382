"""Tests to address specific coverage gaps and reach 80%+ coverage."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import pandas as pd
import pytest
from fastmcp.exceptions import ToolError

from databeak.servers.io_server import (
    MAX_URL_SIZE_MB,
    detect_file_encoding,
    export_csv,
    get_encoding_fallbacks,
    get_session_info,
    load_csv,
    load_csv_from_content,
    load_csv_from_url,
)
from tests.test_mock_context import create_mock_context


class TestEncodingDetectionFallbacks:
    """Test encoding detection and fallback edge cases."""

    def test_detect_file_encoding_chardet_none_detection(self) -> None:
        """Test when chardet returns None for encoding."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            f.write(b"test,data\n1,2")
            temp_path = f.name

        try:
            with patch("chardet.detect") as mock_detect:
                mock_detect.return_value = {"encoding": None, "confidence": 0.8}

                encoding = detect_file_encoding(temp_path)
                assert encoding == "utf-8"  # Should fallback to utf-8

        finally:
            Path(temp_path).unlink()

    def test_detect_file_encoding_low_confidence(self) -> None:
        """Test when chardet has low confidence."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            f.write(b"test,data\n1,2")
            temp_path = f.name

        try:
            with patch("chardet.detect") as mock_detect:
                mock_detect.return_value = {"encoding": "ISO-8859-1", "confidence": 0.3}

                encoding = detect_file_encoding(temp_path)
                assert encoding == "utf-8"  # Should fallback to utf-8 due to low confidence

        finally:
            Path(temp_path).unlink()

    def test_detect_file_encoding_import_error(self) -> None:
        """Test when chardet import fails."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            f.write(b"test,data\n1,2")
            temp_path = f.name

        try:
            with patch("chardet.detect", side_effect=ImportError("chardet not available")):
                encoding = detect_file_encoding(temp_path)
                assert encoding == "utf-8"  # Should fallback to utf-8

        finally:
            Path(temp_path).unlink()

    def test_detect_file_encoding_unicode_error(self) -> None:
        """Test when chardet raises UnicodeError."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            f.write(b"\xff\xfe\x00\x00")  # Invalid UTF sequence
            temp_path = f.name

        try:
            with patch("chardet.detect", side_effect=UnicodeError("Invalid sequence")):
                encoding = detect_file_encoding(temp_path)
                assert encoding == "utf-8"  # Should fallback to utf-8

        finally:
            Path(temp_path).unlink()

    def test_detect_file_encoding_os_error(self) -> None:
        """Test when file reading fails."""
        with patch("builtins.open", side_effect=OSError("File not accessible")):
            encoding = detect_file_encoding("/nonexistent/path")
            assert encoding == "utf-8"  # Should fallback to utf-8

    def test_get_encoding_fallbacks_utf_variants(self) -> None:
        """Test fallbacks for UTF-16 encoding."""
        fallbacks = get_encoding_fallbacks("utf-16")

        # Should include UTF variants but not the primary encoding
        assert "utf-16" in fallbacks
        assert "utf-8" in fallbacks
        assert "utf-32" in fallbacks
        assert "cp1252" in fallbacks

    def test_get_encoding_fallbacks_windows_encoding(self) -> None:
        """Test fallbacks for Windows-1251 encoding."""
        fallbacks = get_encoding_fallbacks("windows-1251")

        # Should prioritize Windows encodings
        assert "windows-1251" in fallbacks
        assert "cp1251" in fallbacks
        assert "latin1" in fallbacks
        assert "utf-8" in fallbacks

    def test_get_encoding_fallbacks_deduplication(self) -> None:
        """Test that duplicates are removed from fallback list."""
        fallbacks = get_encoding_fallbacks("utf-8")

        # Should not have duplicates
        assert len(fallbacks) == len(set(fallbacks))


@pytest.mark.asyncio
class TestLoadCsvEncodingFallbackPaths:
    """Test specific encoding fallback paths in load_csv."""

    async def test_load_csv_auto_detection_failure_with_fallback(self) -> None:
        """Test when auto-detection fails but fallback succeeds."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as f:
            # Write content with special characters
            f.write("name,city\nJosé,São Paulo".encode("latin1"))
            temp_path = f.name

        try:
            with patch("databeak.servers.io_server.detect_file_encoding") as mock_detect:
                # Mock detection to raise an error
                mock_detect.side_effect = Exception("Detection failed")

                # This should trigger the fallback encoding path
                result = await load_csv(
                    create_mock_context(),
                    file_path=temp_path,
                    encoding="utf-8",  # Will fail, trigger fallbacks
                )

                assert result.success
                assert result.rows_affected == 1

        finally:
            Path(temp_path).unlink()

    async def test_load_csv_memory_check_in_fallback_encoding(self) -> None:
        """Test memory limit check during encoding fallback."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            encoding="latin1",
        ) as f:
            f.write("col1,col2\n1,2")
            temp_path = f.name

        try:
            # Mock pandas.read_csv to succeed with fallback but return large df
            large_df = pd.DataFrame({"col1": ["data"] * 1000, "col2": ["data"] * 1000})

            with (
                patch("pandas.read_csv") as mock_read_csv,
                patch(
                    "databeak.servers.io_server.MAX_MEMORY_USAGE_MB",
                    0.001,
                ),  # Very low limit
            ):
                # First call fails with encoding error, second returns large df
                mock_read_csv.side_effect = [
                    UnicodeDecodeError("utf-8", b"", 0, 1, "encoding error"),
                    large_df,
                ]

                with pytest.raises(ToolError):
                    await load_csv(create_mock_context(), file_path=temp_path, encoding="utf-8")

        finally:
            Path(temp_path).unlink()

    async def test_load_csv_row_limit_in_fallback_encoding(self) -> None:
        """Test row limit check during encoding fallback."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            encoding="latin1",
        ) as f:
            f.write("col1,col2\n1,2")
            temp_path = f.name

        try:
            # Mock pandas.read_csv to succeed with fallback but return large df
            large_df = pd.DataFrame({"col1": range(10000), "col2": range(10000)})

            with (
                patch("pandas.read_csv") as mock_read_csv,
                patch("databeak.servers.io_server.MAX_ROWS", 5),  # Very low limit
            ):
                # First call fails with encoding error, second returns large df
                mock_read_csv.side_effect = [
                    UnicodeDecodeError("utf-8", b"", 0, 1, "encoding error"),
                    large_df,
                ]

                with pytest.raises(ToolError):
                    await load_csv(create_mock_context(), file_path=temp_path, encoding="utf-8")

        finally:
            Path(temp_path).unlink()


@pytest.mark.asyncio
class TestLoadCsvErrorPaths:
    """Test error handling paths in load_csv."""

    async def test_load_csv_os_error(self) -> None:
        """Test OSError handling in load_csv."""
        with (
            patch("pathlib.Path.stat", side_effect=OSError("File access denied")),
            pytest.raises(ToolError),
        ):
            await load_csv(create_mock_context(), file_path="/some/file.csv")

    async def test_load_csv_pandas_empty_data_error(self) -> None:
        """Test pandas EmptyDataError handling."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("")  # Empty file
            temp_path = f.name

        try:
            with (
                patch("pandas.read_csv", side_effect=pd.errors.EmptyDataError("No data")),
                pytest.raises(pd.errors.EmptyDataError, match="No data"),
            ):
                await load_csv(create_mock_context(), file_path=temp_path)
        finally:
            Path(temp_path).unlink()

    async def test_load_csv_pandas_parser_error(self) -> None:
        """Test pandas ParserError handling."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("invalid,csv\ndata")
            temp_path = f.name

        try:
            with (
                patch("pandas.read_csv", side_effect=pd.errors.ParserError("Parse failed")),
                pytest.raises(pd.errors.ParserError, match="Parse failed"),
            ):
                await load_csv(create_mock_context(), file_path=temp_path)
        finally:
            Path(temp_path).unlink()

    async def test_load_csv_memory_error(self) -> None:
        """Test MemoryError handling."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("col1,col2\n1,2")
            temp_path = f.name

        try:
            with (
                patch("pandas.read_csv", side_effect=MemoryError("Out of memory")),
                pytest.raises(MemoryError),
            ):
                await load_csv(create_mock_context(), file_path=temp_path)
        finally:
            Path(temp_path).unlink()


@pytest.mark.asyncio
class TestLoadCsvFromUrlEncodingFallbacks:
    """Test URL loading encoding fallback paths."""

    @patch("databeak.servers.io_server.urlopen")
    @patch("pandas.read_csv")
    async def test_load_url_memory_check_in_fallback(
        self, mock_read_csv: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """Test memory check during URL encoding fallback."""
        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "text/csv", "Content-Length": "100"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Large DataFrame for memory limit test
        large_df = pd.DataFrame({"col1": ["x"] * 10000, "col2": ["y"] * 10000})

        # First encoding fails, second succeeds but exceeds memory
        mock_read_csv.side_effect = [
            UnicodeDecodeError("utf-8", b"", 0, 1, "encoding error"),
            large_df,
        ]

        with (
            patch("databeak.servers.io_server.MAX_MEMORY_USAGE_MB", 0.001),
            pytest.raises(ToolError),
        ):
            await load_csv_from_url(
                create_mock_context(),
                url="http://example.com/data.csv",
                encoding="utf-8",
            )

    @patch("databeak.servers.io_server.urlopen")
    @patch("pandas.read_csv")
    async def test_load_url_row_check_in_fallback(
        self, mock_read_csv: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """Test row limit check during URL encoding fallback."""
        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "text/csv", "Content-Length": "100"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Large DataFrame for row limit test
        large_df = pd.DataFrame({"col1": range(10000), "col2": range(10000)})

        # First encoding fails, second succeeds but exceeds row limit
        mock_read_csv.side_effect = [
            UnicodeDecodeError("utf-8", b"", 0, 1, "encoding error"),
            large_df,
        ]

        with patch("databeak.servers.io_server.MAX_ROWS", 5), pytest.raises(ToolError):
            await load_csv_from_url(
                create_mock_context(),
                url="http://example.com/data.csv",
                encoding="utf-8",
            )


@pytest.mark.asyncio
class TestLoadCsvFromUrlErrorPaths:
    """Test error handling paths in load_csv_from_url."""

    async def test_load_url_timeout_error(self) -> None:
        """Test timeout error handling."""
        with (
            patch(
                "databeak.servers.io_server.urlopen",
                side_effect=TimeoutError("Request timeout"),
            ),
            pytest.raises(ToolError),
        ):
            await load_csv_from_url(create_mock_context(), url="http://example.com/data.csv")

    async def test_load_url_url_error(self) -> None:
        """Test URLError handling."""
        with (
            patch(
                "databeak.servers.io_server.urlopen",
                side_effect=URLError("Connection failed"),
            ),
            pytest.raises(ToolError),
        ):
            await load_csv_from_url(create_mock_context(), url="http://example.com/data.csv")

    @patch("databeak.servers.io_server.urlopen")
    async def test_load_url_content_size_exceeded(self, mock_urlopen: MagicMock) -> None:
        """Test content size limit exceeded."""
        mock_response = MagicMock()
        mock_response.headers = {
            "Content-Type": "text/csv",
            "Content-Length": str((MAX_URL_SIZE_MB + 10) * 1024 * 1024),  # Exceed limit
        }
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with pytest.raises(ToolError):
            await load_csv_from_url(create_mock_context(), url="http://example.com/large_file.csv")

    @patch("databeak.servers.io_server.urlopen")
    async def test_load_url_content_type_warning(self, mock_urlopen: MagicMock) -> None:
        """Test content type warning path."""
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "text/html", "Content-Length": "100"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Mock pandas to succeed
        with patch("pandas.read_csv", return_value=pd.DataFrame({"col": [1, 2]})):
            result = await load_csv_from_url(
                create_mock_context(),
                url="http://example.com/data.csv",
            )
            assert result.success

    async def test_load_url_pandas_empty_data_error(self) -> None:
        """Test pandas EmptyDataError in URL loading."""
        with patch("databeak.servers.io_server.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.headers = {"Content-Type": "text/csv"}
            mock_urlopen.return_value.__enter__.return_value = mock_response

            with (
                patch("pandas.read_csv", side_effect=pd.errors.EmptyDataError("No data")),
                pytest.raises(pd.errors.EmptyDataError, match="No data"),
            ):
                await load_csv_from_url(create_mock_context(), url="http://example.com/empty.csv")

    async def test_load_url_pandas_parser_error(self) -> None:
        """Test pandas ParserError in URL loading."""
        with patch("databeak.servers.io_server.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.headers = {"Content-Type": "text/csv"}
            mock_urlopen.return_value.__enter__.return_value = mock_response

            with (
                patch("pandas.read_csv", side_effect=pd.errors.ParserError("Parse error")),
                pytest.raises(pd.errors.ParserError, match="Parse error"),
            ):
                await load_csv_from_url(create_mock_context(), url="http://example.com/bad.csv")

    async def test_load_url_memory_error(self) -> None:
        """Test MemoryError in URL loading."""
        with patch("databeak.servers.io_server.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.headers = {"Content-Type": "text/csv"}
            mock_urlopen.return_value.__enter__.return_value = mock_response

            with (
                patch("pandas.read_csv", side_effect=MemoryError("Out of memory")),
                pytest.raises(MemoryError),
            ):
                await load_csv_from_url(create_mock_context(), url="http://example.com/large.csv")

    async def test_load_url_os_error(self) -> None:
        """Test OSError in URL loading."""
        with patch("databeak.servers.io_server.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.headers = {"Content-Type": "text/csv"}
            mock_urlopen.return_value.__enter__.return_value = mock_response

            with (
                patch("pandas.read_csv", side_effect=OSError("Network error")),
                pytest.raises(OSError),
            ):
                await load_csv_from_url(create_mock_context(), url="http://example.com/file.csv")


@pytest.mark.asyncio
class TestLoadCsvFromContentErrorPaths:
    """Test error handling paths in load_csv_from_content."""

    async def test_load_content_empty_dataframe(self) -> None:
        """Test when parsed CSV results in empty DataFrame."""
        # Mock pandas to return empty DataFrame
        with (
            patch("pandas.read_csv", return_value=pd.DataFrame()),
            pytest.raises(ToolError),
        ):
            await load_csv_from_content(create_mock_context(), content="header\n")


@pytest.mark.asyncio
class TestExportCsvErrorPaths:
    """Test error handling paths in export_csv."""

    async def test_export_csv_excel_dependency_error(self) -> None:
        """Test Excel export with missing openpyxl dependency."""
        # Create session with data
        csv_content = "name,value\ntest,123"
        ctx = create_mock_context()
        await load_csv_from_content(ctx, csv_content)
        session_id = ctx.session_id

        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            temp_path = tmp.name

        try:
            with (
                patch("pandas.ExcelWriter", side_effect=ImportError("No module named 'openpyxl'")),
                pytest.raises(ToolError),
            ):
                await export_csv(create_mock_context(session_id), file_path=temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def test_export_csv_parquet_dependency_error(self) -> None:
        """Test Parquet export with missing pyarrow dependency."""
        # Create session with data
        csv_content = "name,value\ntest,123"
        ctx = create_mock_context()
        await load_csv_from_content(ctx, csv_content)
        session_id = ctx.session_id

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as tmp:
            temp_path = tmp.name

        try:
            with (
                patch(
                    "pandas.DataFrame.to_parquet",
                    side_effect=ImportError("No module named 'pyarrow'"),
                ),
                pytest.raises(ToolError),
            ):
                await export_csv(create_mock_context(session_id), file_path=temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def test_export_csv_invalid_path_error(self) -> None:
        """Test export with invalid file path."""
        # Create session with data
        csv_content = "name,value\ntest,123"
        ctx = create_mock_context()
        await load_csv_from_content(ctx, csv_content)
        session_id = ctx.session_id

        with pytest.raises(ToolError):
            await export_csv(create_mock_context(session_id), file_path="\x00invalid\x00path")

    # Note: temp file cleanup test removed since export_csv no longer uses temp files


@pytest.mark.asyncio
class TestSessionManagementErrorPaths:
    """Test error handling in session management functions."""

    async def test_get_session_info_exception_handling(self) -> None:
        """Test exception handling in get_session_info."""
        with patch("databeak.servers.io_server.get_session_only") as mock_get_session_only:
            mock_get_session_only.side_effect = Exception("Session manager error")
            with pytest.raises(Exception, match="Session manager error"):
                await get_session_info(create_mock_context())


@pytest.mark.asyncio
class TestSpecificCoveragePaths:
    """Target specific uncovered lines to reach 80% coverage."""

    async def test_load_csv_other_exception_in_fallback(self) -> None:
        """Test non-UnicodeDecodeError exception during encoding fallback."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            encoding="latin1",
        ) as f:
            f.write("col1,col2\n1,2")
            temp_path = f.name

        try:
            with patch("pandas.read_csv") as mock_read_csv:
                # First call: UnicodeDecodeError, Second call: different error, Third: success
                mock_read_csv.side_effect = [
                    UnicodeDecodeError("utf-8", b"", 0, 1, "encoding error"),
                    ValueError("Different error type"),
                    pd.DataFrame({"col1": [1], "col2": [2]}),
                ]

                result = await load_csv(
                    create_mock_context(),
                    file_path=temp_path,
                    encoding="utf-8",
                )
                assert result.success
                assert mock_read_csv.call_count == 3

        finally:
            Path(temp_path).unlink()

    @patch("databeak.servers.io_server.urlopen")
    @patch("pandas.read_csv")
    async def test_load_url_other_exception_in_fallback(
        self, mock_read_csv: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """Test non-UnicodeDecodeError exception during URL encoding fallback."""
        # Mock response
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "text/csv", "Content-Length": "100"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Encoding error, then different error, then success
        mock_read_csv.side_effect = [
            UnicodeDecodeError("utf-8", b"", 0, 1, "encoding error"),
            ValueError("Different error"),
            pd.DataFrame({"col": [1, 2]}),
        ]

        result = await load_csv_from_url(
            create_mock_context(),
            url="http://example.com/data.csv",
            encoding="utf-8",
        )

        assert result.success
        assert mock_read_csv.call_count == 3

    async def test_load_csv_df_none_after_fallback_attempt(self) -> None:
        """Test when df remains None after encoding fallback."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("col1,col2\n1,2")
            temp_path = f.name

        try:
            with (
                patch(
                    "pandas.read_csv",
                    side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "always fails"),
                ),
                pytest.raises(ToolError),
            ):
                await load_csv(create_mock_context(), file_path=temp_path, encoding="utf-8")
        finally:
            Path(temp_path).unlink()

    @patch("databeak.servers.io_server.urlopen")
    async def test_load_url_df_none_after_fallback(self, mock_urlopen: MagicMock) -> None:
        """Test when df remains None after URL encoding fallback."""
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "text/csv"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with (
            patch(
                "pandas.read_csv",
                side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "always fails"),
            ),
            pytest.raises(ToolError),
        ):
            await load_csv_from_url(create_mock_context(), url="http://example.com/data.csv")

    @patch("databeak.servers.io_server.urlopen")
    async def test_load_url_df_none_check(self, mock_urlopen: MagicMock) -> None:
        """Test URL loading df None check after successful response."""
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "text/csv"}
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with patch("pandas.read_csv", return_value=None), pytest.raises(TypeError):
            await load_csv_from_url(create_mock_context(), url="http://example.com/data.csv")
