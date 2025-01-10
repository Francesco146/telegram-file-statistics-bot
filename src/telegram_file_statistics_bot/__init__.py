import gettext
import logging
import os

from dotenv import load_dotenv

load_dotenv(override=True, verbose=True)


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s "
        "(%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: bold_red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setFormatter(CustomFormatter())
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)

__all__ = ["database", "args", "handlers"]

match os.getenv("BOT_LANGUAGE"):
    case "it":
        it = gettext.translation("base", localedir="locales", languages=["it"])
        it.install()
        get_str = it.gettext
    case _:
        if os.getenv("BOT_LANGUAGE") != "en":
            logger.warning(
                "Unsupported language '%s', defaulting to English",
                os.getenv("BOT_LANGUAGE"),
            )
        get_str = gettext.gettext
