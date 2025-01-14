"""
This module serves as the entry point for the telegram file statistics bot.
It initializes and runs the bot application.
"""

import logging
import os

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from . import get_str, logger
from .args import parse_args
from .database import Database
from .handlers import (
    callback_query_handler,
    handle_file,
    help_command,
    reset,
    start_command,
    stats,
)


def run_bot(token: str, local: bool) -> None:
    """
    Main function to start the bot application.

    Args:
        - token (str): The token for authenticating the bot with the
        Telegram API.
        - local (bool): A flag indicating whether the bot should run with
        a telegram api bot local server.

    Returns:
        None

    The function performs the following steps:
    1. Checks if the token is provided. If not, logs an error and exits.
    2. Builds the bot application using the provided token.
    3. Adds command handlers for "start" and "help" commands.
    4. Adds a message handler for handling all document messages.
    5. Adds command handlers for "stats" and "reset" commands.
    6. Logs that the bot is starting and runs the bot in polling mode.
    """
    if not token:
        logger.error(get_str("Token not provided. Exiting..."))
        return

    application = ApplicationBuilder().token(token).local_mode(local)

    if local:
        application.base_url("http://0.0.0.0:8081/bot")
        application.base_file_url("http://0.0.0.0:8081/file/bot")
        # high value for large files in local mode
        application.read_timeout(1000)

    application = application.build()

    application.add_handler(
        CommandHandler(
            "help", lambda update, _: help_command(update)
        )
    )
    application.add_handler(
        CommandHandler(
            "start", lambda update, _: start_command(update)
        )
    )
    application.add_handler(
        MessageHandler(
            filters.Document.ALL,
            lambda update, context: handle_file(update, context, local),
        )
    )
    application.add_handler(
        CommandHandler(
            "stats",
            lambda update, _: stats(update)
        )
    )
    application.add_handler(
        CommandHandler(
            "reset",
            lambda update, _: reset(update)
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            lambda update, _: callback_query_handler(update)
        )
    )

    logger.info(get_str("Bot is starting..."))
    try:
        application.run_polling()
    except (ConnectionError, TimeoutError) as error:
        if local:
            logger.error(get_str("Make sure the local server is running."))
        logger.error(error)


def main() -> None:
    """
    Entry point for the bot when called from a script or CLI.
    """
    args = parse_args()

    sqlite_db = Database(args.database)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    sqlite_db.init_db()

    logger.debug(get_str("Current configuration:"))
    logger.debug("  * language: %s", os.getenv('BOT_LANGUAGE', 'en'))
    for arg in vars(args):
        if arg not in ["token"]:
            logger.debug("  * %s: %s", arg, getattr(args, arg))

    run_bot(args.token or os.getenv("TELEGRAM_TOKEN", ""), args.local)


if __name__ == "__main__":
    main()
