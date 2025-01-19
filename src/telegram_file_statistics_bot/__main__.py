"""
This module serves as the entry point for the telegram file statistics bot.
It initializes and runs the bot application.
"""

import logging
import os

from telegram.error import NetworkError
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
        if os.getenv("AM_I_IN_A_DOCKER_CONTAINER", "False").lower() == "true":
            base_url = "http://telegram-bot-api:8081/bot"
            base_file_url = "http://telegram-bot-api:8081/file/bot"
        else:
            base_url = "http://0.0.0.0:8081/bot"
            base_file_url = "http://0.0.0.0:8081/file/bot"

        application.base_url(base_url)
        application.base_file_url(base_file_url)
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
    except (ConnectionError, TimeoutError, NetworkError) as error:
        logger.error(error)
        if local:
            logger.error(get_str("Make sure the local server is running."))


def main() -> None:
    """
    Entry point for the bot when called from a script or CLI.
    """
    args = parse_args()

    database_via_env = os.getenv("DATABASE_FILE", args.database)

    database_file_path = args.database or database_via_env

    if args.database and args.database != database_via_env:
        logger.warning(
            get_str(
                "Environment variable DATABASE_FILE is overridden by the command-line argument."  # pylint: disable=line-too-long # noqa: E501
            )
        )

    sqlite_db = Database(database_file_path)

    debug_via_env = os.getenv("DEBUG_MODE", str(args.debug)).lower() == "true"

    should_debug = args.debug or debug_via_env

    if args.debug and args.debug != debug_via_env:
        logger.warning(
            get_str(
                "Environment variable DEBUG_MODE is overridden by the command-line argument."  # pylint: disable=line-too-long # noqa: E501
            )
        )

    if should_debug:
        logger.setLevel(logging.DEBUG)

    sqlite_db.init_db()

    token_via_env = os.getenv("TELEGRAM_TOKEN", args.token)
    token = args.token or token_via_env

    if args.token and args.token != token_via_env:
        logger.warning(
            get_str(
                "Environment variable TELEGRAM_TOKEN is overridden by the command-line argument."  # pylint: disable=line-too-long # noqa: E501
            )
        )

    local_via_env = os.getenv(
        "LOCAL_SERVER_MODE", str(args.local)).lower() == "true"
    local = args.local or local_via_env

    if args.local and args.local != local_via_env:
        logger.warning(
            get_str(
                "Environment variable LOCAL_SERVER_MODE is overridden by the command-line argument."  # pylint: disable=line-too-long # noqa: E501
            )
        )

    logger.debug(get_str("Current configuration:"))
    logger.debug(get_str("  * language: %s"), os.getenv('BOT_LANGUAGE', 'en'))
    logger.debug(get_str("  * database: %s"), database_file_path)
    logger.debug(get_str("  * debug: %s"), should_debug)
    logger.debug(get_str("  * local: %s"), local)

    run_bot(token, local)


if __name__ == "__main__":
    main()
