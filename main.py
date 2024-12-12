from dotenv import load_dotenv
from bot.args import parse_args
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers import handle_file, stats, reset, help_command
from bot.database import init_db, Database
from bot import logger
import logging

load_dotenv()


def main(token: str) -> None:
    """
    Main function to start the bot application.

    Args:
        token (str): The token for authenticating the bot with the Telegram API.

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
        logger.error("Token not provided. Exiting...")
        return

    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler(["start", "help"], help_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("reset", reset))

    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    args = parse_args()
    Database.db_path = args.database

    if args.debug:
        logger.setLevel(logging.DEBUG)

    init_db()
    main(args.token or os.getenv("TOKEN"))
