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
from .database import Database, init_db
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
        token (str): The token for authenticating the bot with the Telegram API.
        local (bool): A flag indicating whether the bot should run with a telegram api bot local server.

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
        application.read_timeout(1000)  # high value for large files in local mode

    application = application.build()
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(
        MessageHandler(
            filters.Document.ALL,
            lambda update, context: handle_file(update, context, local),
        )
    )
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("reset", reset))

    application.add_handler(CallbackQueryHandler(callback_query_handler))

    logger.info(get_str("Bot is starting..."))
    try:
        application.run_polling()
    except Exception as e:
        if local:
            logger.error(get_str("Make sure the local server is running."))
        logger.error(e)


def main() -> None:
    """
    Entry point for the bot when called from a script or CLI.
    """
    args = parse_args()
    Database.db_path = args.database

    if args.debug:
        logger.setLevel(logging.DEBUG)

    init_db()
    logger.debug(get_str("Current configuration:"))
    for arg in vars(args):
        if arg not in ["token"]:
            logger.debug(f"  * {arg}: {getattr(args, arg)}")

    run_bot(args.token or os.getenv("TOKEN"), args.local)


if __name__ == "__main__":
    main()
