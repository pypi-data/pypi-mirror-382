"""
Help subcommand processor
"""

import os
from argparse import Namespace
from pathlib import Path


class HelpCommand:                      # pylint: disable=too-few-public-methods
    """
    Subprocessor for the 'help' command
    """

    _SUB_COMMAND = "help"


    def __init__(self, help_doc: Path):
        self._help_doc = help_doc


    def add_subparser(self, subparsers) -> None:
        """
        Create and add a subparser for opening module help
        """

        subparser = subparsers.add_parser(self._SUB_COMMAND,
                                          help="Open the module's help file")

        subparser.set_defaults(func=self._open_help,
                               help=[self._SUB_COMMAND, '--help'])


    def _open_help(self, args: Namespace) -> None:  # pylint: disable=unused-argument
        """
        Subparser command

        Open the help document for the module
        """

        os.startfile(self._help_doc)
