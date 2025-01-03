from dotenv import load_dotenv
from bot.args import parse_args
import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from bot.handlers import (
    handle_file,
    stats,
    reset,
    help_command,
    start_command,
    callback_query_handler,
)
from bot.database import init_db, Database
from bot import logger, _
import logging

load_dotenv()


def main(token: str, local: bool) -> None:
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
        logger.error(_("Token not provided. Exiting..."))
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

    logger.info(_("Bot is starting..."))
    application.run_polling()


if __name__ == "__main__":
    args = parse_args()
    Database.db_path = args.database

    if args.debug:
        logger.setLevel(logging.DEBUG)

    init_db()
    logger.debug(_("Current configuration:"))
    for arg in vars(args):
        if arg not in ["token"]:
            logger.debug(f"  * {arg}: {getattr(args, arg)}")

    main(args.token or os.getenv("TOKEN"), args.local)
