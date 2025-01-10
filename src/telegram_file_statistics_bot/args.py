import argparse

from . import get_str


def parse_args() -> argparse.Namespace:
    """
    Parses command-line arguments for the Telegram Bot for File Statistics.

    Returns:
        argparse.Namespace: A namespace object containing the parsed arguments.

    Arguments:
        -t, --token (str): Bot token (or set TOKEN environment variable).
        -db, --database (str): Path to the SQLite database file (default: "file_statistics.db").
        -d, --debug: Enable debug mode for logging.
    """
    parser = argparse.ArgumentParser(
        description=get_str("Telegram Bot for File Statistics"),
        prog="telegram-file-statistics-bot",
        epilog=get_str("Made with ❤️ by @Francesco146"),
    )
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        help=get_str("Bot token (or set TOKEN environment variable)"),
        default=None,
    )
    parser.add_argument(
        "-db",
        "--database",
        type=str,
        help=get_str("Path to the SQLite database file"),
        default="file_statistics.db",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help=get_str("Enable debug mode for logging"),
        default=False,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="telegram-file-statistics-bot v1.1.0",
        help=get_str("Show the version of the program"),
    )
    parser.add_argument(
        "-l",
        "--local",
        action="store_true",
        help=get_str("Run the bot in a telegram api bot local server"),
        default=False,
    )

    return parser.parse_args()
