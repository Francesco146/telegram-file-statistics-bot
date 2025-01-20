"""
This module contains tests for the helper module.
"""

from unittest.mock import MagicMock

import pytest
from telegram import Update

from telegram_file_statistics_bot.helper import get_send_function


def test_get_send_function_message():
    """Tests get_send_function with a message update."""
    update = MagicMock(spec=Update)
    update.message = MagicMock()
    update.callback_query = None

    send_function = get_send_function(update)
    assert send_function == update.message.reply_text


def test_get_send_function_callback_query():
    """Tests get_send_function with a callback query update."""
    update = MagicMock(spec=Update)
    update.message = None
    update.callback_query = MagicMock()

    send_function = get_send_function(update)
    assert send_function == update.callback_query.edit_message_text


def test_get_send_function_no_message_or_callback_query():
    """Tests get_send_function with no message or callback query."""
    update = MagicMock(spec=Update)
    update.message = None
    update.callback_query = None

    with pytest.raises(ValueError):
        get_send_function(update)
