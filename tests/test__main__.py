"""
This module contains the tests for the __main__ module.
"""

from unittest.mock import MagicMock, patch

import pytest

from telegram_file_statistics_bot.__main__ import run_bot


@pytest.fixture(scope="module", name="test_mock_application_builder")
def mock_application_builder():
    """Initializes a mocked ApplicationBuilder for testing.

    Yields:
        MagicMock: A mocked ApplicationBuilder for testing.
    """
    with patch(
        "telegram_file_statistics_bot.__main__.ApplicationBuilder"
    ) as mock:
        yield mock


@pytest.fixture(scope="module", name="test_mock_logger")
def mock_logger():
    """Initializes a mocked logger for testing.

    Yields:
        MagicMock: A mocked logger for testing.
    """
    with patch("telegram_file_statistics_bot.__main__.logger") as mock:
        yield mock


def test_run_bot_no_token(test_mock_logger):
    """Tests the run_bot function without a token.

    Args:
        test_mock_logger (MagicMock): The mocked logger.
    """
    run_bot("", False)
    test_mock_logger.error.assert_called_with("Token not provided. Exiting...")


def test_run_bot_with_token(test_mock_application_builder):
    """Tests the run_bot function with a token.

    Args:
        test_mock_application_builder (MagicMock):
        The mocked ApplicationBuilder
    """
    mock_app = MagicMock()
    token_ptr = test_mock_application_builder.return_value.token
    local_mode_ptr = token_ptr.return_value.local_mode

    local_mode_ptr.return_value.build.return_value = mock_app

    run_bot("test_token", False)

    token_ptr.assert_called_with(
        "test_token")
    mock_app.add_handler.assert_called()
    mock_app.run_polling.assert_called()


def test_run_bot_local_mode(test_mock_application_builder):
    """Tests the run_bot function with local mode enabled.

    Args:
        test_mock_application_builder (MagicMock):
        The mocked ApplicationBuilder
    """
    mock_app = MagicMock()
    test_mock_application_builder.return_value = MagicMock(
        token=MagicMock(return_value=MagicMock(
            local_mode=MagicMock(return_value=MagicMock(
                base_url=MagicMock(),
                base_file_url=MagicMock(),
                read_timeout=MagicMock(),
                build=MagicMock(return_value=mock_app),
            ))
        ))
    )

    run_bot("test_token", True)

    token_ptr = test_mock_application_builder.return_value.token
    local_mode_ptr = token_ptr.return_value.local_mode

    token_ptr.assert_called_with("test_token")

    local_mode_ptr.assert_called_with(True)
    local_mode_ptr.return_value.base_url.assert_called_with(
        "http://0.0.0.0:8081/bot"
    )
    local_mode_ptr.return_value.base_file_url.assert_called_with(
        "http://0.0.0.0:8081/file/bot"
    )
    local_mode_ptr.return_value.read_timeout.assert_called_with(1000)

    mock_app.add_handler.assert_called()
    mock_app.run_polling.assert_called()


def test_run_bot_exception_handling(
    test_mock_application_builder, test_mock_logger
):
    """Tests the exception handling of the run_bot function.

    Args:
        - test_mock_application_builder (MagicMock):
        The mocked ApplicationBuilder.
        - test_mock_logger (MagicMock): The mocked logger.
    """
    mock_app = MagicMock()

    token_ptr = test_mock_application_builder.return_value.token
    local_mode_ptr = token_ptr.return_value.local_mode

    local_mode_ptr.return_value.build.return_value = mock_app

    mock_app.run_polling.side_effect = ConnectionError("Connection error")

    run_bot("test_token", True)

    test_mock_logger.info.assert_any_call("Bot is starting...")
    test_mock_logger.error.assert_any_call(
        "Make sure the local server is running."
    )
