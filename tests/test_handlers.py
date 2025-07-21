"""
This module contains tests for the handlers module.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Document, Update
from telegram.ext import ContextTypes

from telegram_file_statistics_bot.handlers import handle_file


@pytest.fixture(name="test_mock_update")
def mock_update():
    """Creates a mock update object."""
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(id=12345)
    update.message = MagicMock()
    update.message.document = MagicMock(spec=Document)
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture(name="test_mock_context")
def mock_context():
    """Creates a mock context object."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot.get_file = AsyncMock()
    return context


@pytest.fixture(name="test_mock_database")
def mock_database():
    """Creates a mock database object."""
    with patch("telegram_file_statistics_bot.handlers.Database") as mock:
        yield mock


@pytest.fixture(name="test_mock_logger")
def mock_logger():
    """Creates a mock logger object."""
    with patch("telegram_file_statistics_bot.handlers.logger") as mock:
        yield mock


@pytest.fixture(name="test_mock_handle_archive")
def mock_handle_archive():
    """Creates a mock handle_archive function."""
    with patch(
        "telegram_file_statistics_bot.handlers.handle_archive", new_callable=AsyncMock
    ) as mock:
        yield mock


@pytest.fixture(name="test_mock_is_archive")
def mock_is_archive():
    """Creates a mock is_archive function."""
    with patch("telegram_file_statistics_bot.handlers.is_archive") as mock:
        yield mock


@pytest.fixture(name="test_mock_get_str")
def mock_get_str():
    """Creates a mock get_str function."""
    with patch("telegram_file_statistics_bot.handlers.get_str") as mock:
        yield mock


@pytest.mark.asyncio
async def test_handle_file_no_effective_user(test_mock_update, test_mock_context):
    """Tests handle_file with no effective user."""
    test_mock_update.effective_user = None
    await handle_file(test_mock_update, test_mock_context, local_mode=False)
    test_mock_update.message.reply_text.assert_not_called()


@pytest.mark.asyncio
async def test_handle_file_no_message(test_mock_update, test_mock_context):
    """Tests handle_file with no message."""
    test_mock_update.message = None
    await handle_file(test_mock_update, test_mock_context, local_mode=False)
    test_mock_context.bot.is_archive.assert_not_called()


@pytest.mark.asyncio
async def test_handle_file_no_document(test_mock_update, test_mock_context):
    """Tests handle_file with no document."""
    test_mock_update.message.document = None
    await handle_file(test_mock_update, test_mock_context, local_mode=False)
    test_mock_update.message.reply_text.assert_not_called()


@pytest.mark.asyncio
async def test_handle_file_no_file_name_or_size(
    test_mock_update, test_mock_context, test_mock_get_str
):
    """Tests handle_file with no file name or size."""
    test_mock_update.message.document.file_name = None
    test_mock_update.message.document.file_size = None
    test_mock_get_str.return_value = "File name or size not found."

    test_mock_context.bot.is_archive.assert_not_called()


@pytest.mark.asyncio
async def test_handle_file_archive_non_local_mode(
    test_mock_update, test_mock_context, test_mock_is_archive, test_mock_get_str
):
    """Tests handle_file with an archive in non-local mode."""
    test_mock_is_archive.return_value = True
    test_mock_get_str.return_value = "Archives are not supported in non-local mode."
    await handle_file(test_mock_update, test_mock_context, local_mode=False)
    test_mock_update.message.reply_text.assert_called_with(
        "Archives are not supported in non-local mode."
    )


@pytest.mark.asyncio
async def test_handle_file_non_archive(
    test_mock_update,
    test_mock_context,
    test_mock_is_archive,
    test_mock_database,
    test_mock_get_str,
):
    """Tests handle_file with a non-archive file."""
    test_mock_is_archive.return_value = False
    test_mock_get_str.side_effect = ["Processing file", "File received"]
    test_mock_update.message.document.file_name = "test.txt"
    test_mock_update.message.document.file_size = 1024
    await handle_file(test_mock_update, test_mock_context, local_mode=False)
    test_mock_database().get_user_data.assert_called_once_with(
        test_mock_update.effective_user.id
    )
    test_mock_database().update_user_data.assert_called_once()


@pytest.mark.asyncio
async def test_handle_file_error(
    test_mock_update, test_mock_context, test_mock_get_str
):
    """Tests handle_file with an error."""
    test_mock_update.message.document.file_name = None
    test_mock_update.message.document.file_size = None
    test_mock_get_str.return_value = "Error handling file."
    await handle_file(test_mock_update, test_mock_context, local_mode=False)
    test_mock_context.bot.is_archive.assert_not_called()
