"""
Test cases for the module `telegram_file_statistics_bot.__init__`.
"""

import logging

import pytest

from telegram_file_statistics_bot import CustomFormatter


@pytest.fixture(scope="module", name="test_formatter")
def custom_formatter():
    """Initializes a CustomFormatter instance for testing.

    Returns:
        CustomFormatter: A CustomFormatter instance for testing
    """
    return CustomFormatter()


def test_format_debug(test_formatter: CustomFormatter):
    """Tests the formatting of a debug log message.

    Args:
        - test_formatter (CustomFormatter): The test CustomFormatter instance.
    """
    record = logging.LogRecord(
        name="test",
        level=logging.DEBUG,
        pathname=__file__,
        lineno=10,
        msg="Debug message",
        args=(),
        exc_info=None
    )
    formatted_message = test_formatter.format(record)
    assert "\x1b[38;20m" in formatted_message
    assert "Debug message" in formatted_message


def test_format_info(test_formatter: CustomFormatter):
    """Tests the formatting of a info log message.

    Args:
        - test_formatter (CustomFormatter): The test CustomFormatter instance.
    """
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=20,
        msg="Info message",
        args=(),
        exc_info=None
    )
    formatted_message = test_formatter.format(record)
    assert "\x1b[38;20m" in formatted_message
    assert "Info message" in formatted_message


def test_format_warning(test_formatter: CustomFormatter):
    """Tests the formatting of a warning log message.

    Args:
        - test_formatter (CustomFormatter): The test CustomFormatter instance.
    """
    record = logging.LogRecord(
        name="test",
        level=logging.WARNING,
        pathname=__file__,

        lineno=30,
        msg="Warning message",
        args=(),
        exc_info=None
    )
    formatted_message = test_formatter.format(record)
    assert "\x1b[33;20m" in formatted_message
    assert "Warning message" in formatted_message


def test_format_error(test_formatter: CustomFormatter):
    """Tests the formatting of a error log message.

    Args:
        - test_formatter (CustomFormatter): The test CustomFormatter instance.
    """
    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname=__file__,
        lineno=40,
        msg="Error message",
        args=(),
        exc_info=None
    )
    formatted_message = test_formatter.format(record)
    assert "\x1b[31;1m" in formatted_message
    assert "Error message" in formatted_message


def test_format_critical(test_formatter: CustomFormatter):
    """Tests the formatting of a critical log message.

    Args:
        - test_formatter (CustomFormatter): The test CustomFormatter instance.
    """
    record = logging.LogRecord(
        name="test",
        level=logging.CRITICAL,
        pathname=__file__,
        lineno=50,
        msg="Critical message",
        args=(),
        exc_info=None
    )
    formatted_message = test_formatter.format(record)
    assert "\x1b[31;1m" in formatted_message
    assert "Critical message" in formatted_message
