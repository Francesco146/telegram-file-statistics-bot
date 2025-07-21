import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram_file_statistics_bot.archive_utils import process_extracted_files


@pytest.mark.asyncio
async def test_process_extracted_files_ignores_extensions():
    # Setup temp dir and files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create files with different extensions
        file_paths = [
            os.path.join(temp_dir, "file1.txt"),
            os.path.join(temp_dir, "file2.exe"),
            os.path.join(temp_dir, "file3.mp3"),
        ]
        for path in file_paths:
            with open(path, "w", encoding="utf-8") as f:
                f.write("test")

        # Mock update and user_stats
        update = MagicMock()
        update.message = MagicMock()
        update.message.reply_text = AsyncMock()
        user_id = 123
        user_stats = {
            "total_size": 0,
            "file_count": 0,
            "streamable": 0,
            "extension_categories": {},
            "ignored_extensions": [".exe", ".mp3"],
        }
        with patch("telegram_file_statistics_bot.archive_utils.Database") as mock_db:
            mock_db.return_value.update_user_data = MagicMock()
            await process_extracted_files(temp_dir, user_id, user_stats, update)

        # Only .txt file should be processed
        calls = [call[0][0] for call in update.message.reply_text.call_args_list]
        assert any("file1.txt" in c for c in calls)
        assert not any("file2.exe" in c for c in calls)
        assert not any("file3.mp3" in c for c in calls)
        assert not any("file2.exe" in c for c in calls)
        assert not any("file3.mp3" in c for c in calls)
