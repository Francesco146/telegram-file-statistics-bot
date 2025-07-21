from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Update
from telegram.ext import ContextTypes

from telegram_file_statistics_bot.handlers import ignore_extensions_command


@pytest.mark.asyncio
async def test_ignore_extensions_add_and_list():
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(id=12345)
    update.message = MagicMock()
    send_mock = AsyncMock()
    with patch(
        "telegram_file_statistics_bot.handlers.get_send_function",
        return_value=send_mock,
    ):
        with patch("telegram_file_statistics_bot.handlers.Database") as MockDB:
            db_instance = MockDB.return_value
            db_instance.get_user_data.return_value = {"ignored_extensions": []}
            context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
            context.args = [".exe", ".mp3"]
            await ignore_extensions_command(update, context)
            db_instance.update_user_data.assert_called_once()
            send_mock.assert_called_with("Added to ignore list: .exe, .mp3")
            # Now test listing
            db_instance.get_user_data.return_value = {
                "ignored_extensions": [".exe", ".mp3"]
            }
            context.args = []
            await ignore_extensions_command(update, context)
            send_mock.assert_called_with("Ignored extensions: .exe, .mp3")


@pytest.mark.asyncio
async def test_ignore_extensions_remove():
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(id=12345)
    update.message = MagicMock()
    send_mock = AsyncMock()
    with patch(
        "telegram_file_statistics_bot.handlers.get_send_function",
        return_value=send_mock,
    ):
        with patch("telegram_file_statistics_bot.handlers.Database") as MockDB:
            db_instance = MockDB.return_value
            db_instance.get_user_data.return_value = {
                "ignored_extensions": [".exe", ".mp3"]
            }
            context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
            context.args = ["-rm", ".exe"]
            await ignore_extensions_command(update, context)
            db_instance.update_user_data.assert_called_once()
            send_mock.assert_called_with("Removed from ignore list: .exe")
            # Remove non-existent
            context.args = ["-rm", ".zip"]
            await ignore_extensions_command(update, context)
            send_mock.assert_called_with("No matching extensions found in ignore list.")
