"""
This module initializes the telegram file statistics bot.
It sets up environment variables and configures logging.
"""

import gettext
import logging
import os

from dotenv import load_dotenv

load_dotenv(override=True, verbose=True)


class CustomFormatter(logging.Formatter):
    """Custom log formatter for the bot.

    Args:
        logging (logging.Formatter): The logging formatter class.

    Returns:
        logging.Formatter: A custom log formatter for the bot.
    """

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + log_format + reset,
        logging.INFO: grey + log_format + reset,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: bold_red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

    def __str__(self):
        return f"<CustomFormatter log_format='{self.log_format}'>"

    def __repr__(self):
        return f"CustomFormatter(log_format={self.log_format!r})"


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)

match os.getenv("BOT_LANGUAGE"):
    case "it":
        it = gettext.translation("base", localedir="locales", languages=["it"])
        it.install()
        get_str = it.gettext
        nget_str = it.ngettext
    case _:
        if os.getenv("BOT_LANGUAGE") != "en":
            logger.warning(
                "Unsupported language '%s', defaulting to English",
                os.getenv("BOT_LANGUAGE"),
            )
        get_str = gettext.gettext
        nget_str = gettext.ngettext
