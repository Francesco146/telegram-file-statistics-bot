"""
Tests for the command line arguments parser.
"""

import sys
from argparse import Namespace

import pytest

from telegram_file_statistics_bot.args import parse_args

test_arguments = [
    (
        [],
        Namespace(token=None, database="file_statistics.db", debug=False, local=False),
    ),
    (
        ["--token", "12345"],
        Namespace(
            token="12345", database="file_statistics.db", debug=False, local=False
        ),
    ),
    (
        ["--database", "custom.db"],
        Namespace(token=None, database="custom.db", debug=False, local=False),
    ),
    (
        ["--debug"],
        Namespace(token=None, database="file_statistics.db", debug=True, local=False),
    ),
    (["--version"], None),
    (
        ["--local"],
        Namespace(token=None, database="file_statistics.db", debug=False, local=True),
    ),
    (
        ["--token", "12345", "--database", "custom.db", "--debug"],
        Namespace(token="12345", database="custom.db", debug=True, local=False),
    ),
]


@pytest.mark.parametrize("args, expected", test_arguments)
def test_parse_args(args, expected, monkeypatch):
    """
    Test parse_args with various argument combinations.
    """
    monkeypatch.setattr(sys, "argv", ["prog"] + args)

    # check if the program exits when --version is passed
    if "--version" in args:
        with pytest.raises(SystemExit):
            parse_args()
        return

    parsed_args = parse_args()
    assert parsed_args == expected
