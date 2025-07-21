"""
This module contains tests for the archive_utils module.
"""

import asyncio
import os
import tempfile
import zipfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_file_statistics_bot.archive_utils import (
    extract_archive,
    get_archive_absolute_path,
    is_archive,
    process_extracted_files,
    update_user_statistics,
)


@pytest.fixture(scope="function", name="test_mock_user_stats")
def mock_user_stats():
    """Initializes a mock user statistics dictionary for testing."""
    return {
        "total_size": 0,
        "file_count": 0,
        "streamable": 0,
        "extension_categories": {},
    }


def test_get_archive_absolute_path():
    """Tests the conversion of a URL file path to an absolute path."""
    relative_path = (
        "http://0.0.0.0:8081/file/bot<token>//var/lib/telegram-bot-api/"
        "<token>/documents/file.zip"
    )
    expected_absolute_path = "api/telegram-bot-api-data/<token>/documents/file.zip"
    assert get_archive_absolute_path(relative_path) == expected_absolute_path


def test_extract_archive():
    """
    Tests the extraction of a zip archive by creating
    a zip file with a test file and extracting it.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path = os.path.join(temp_dir, "test.zip")
        extracted_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extracted_dir, exist_ok=True)

        # Create a zip file for testing
        with zipfile.ZipFile(archive_path, "w") as archive:
            test_file_path = os.path.join(extracted_dir, "test.txt")
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write("Test content")
            archive.write(test_file_path, arcname="test.txt")

        with tempfile.TemporaryDirectory() as output_dir:
            extract_archive(archive_path, output_dir)
            assert os.path.exists(os.path.join(output_dir, "test.txt"))


def test_update_user_statistics(test_mock_user_stats):
    """Tests the update of user statistics with a test file.

    Args:
        test_mock_user_stats (dict): A mock user statistics dictionary.
    """
    file_name = "video.mp4"
    file_size = 1024
    update_user_statistics(test_mock_user_stats, file_name, file_size)

    assert test_mock_user_stats["total_size"] == file_size
    assert test_mock_user_stats["file_count"] == 1
    assert test_mock_user_stats["streamable"] == 1
    assert test_mock_user_stats["extension_categories"] == {".mp4": 1}


def test_is_archive():
    """Tests the detection of archive files."""
    assert is_archive("archive.zip") is True
    assert is_archive("document.txt") is False


def test_process_extracted_files_detailed_sizes(tmp_path):
    # Create a fake extracted file
    test_file = tmp_path / "file1.txt"
    test_file.write_bytes(b"a" * 1234)

    # Mock update and user_stats
    mock_update = MagicMock()
    mock_update.message = MagicMock()
    mock_update.message.reply_text = AsyncMock()
    user_stats = {
        "ignored_extensions": [],
        "extension_categories": {},
        "detailed_sizes": True,
        "total_size": 0,
        "file_count": 0,
        "streamable": 0,
    }
    user_id = 42

    # Patch Database to avoid real DB writes
    with patch("telegram_file_statistics_bot.archive_utils.Database") as mock_db:
        mock_db().__getitem__.return_value = user_stats
        mock_db().__setitem__ = MagicMock()
        # Run with detailed_sizes True
        asyncio.run(
            process_extracted_files(str(tmp_path), user_id, user_stats, mock_update)
        )
        # Check for raw bytes in reply
        assert any(
            "1234 bytes" in str(call.args)
            for call in mock_update.message.reply_text.call_args_list
        )
        mock_update.message.reply_text.reset_mock()
        # Now test with detailed_sizes False
        user_stats["detailed_sizes"] = False
        asyncio.run(
            process_extracted_files(str(tmp_path), user_id, user_stats, mock_update)
        )
        assert any(
            "1.2 kB" in str(call.args) or "1.2 KB" in str(call.args)
            for call in mock_update.message.reply_text.call_args_list
        )
