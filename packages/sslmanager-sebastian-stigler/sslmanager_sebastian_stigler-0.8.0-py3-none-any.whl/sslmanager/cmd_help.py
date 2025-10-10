"""
Implements the help command

Inspired from https://medium.com/@george.shuklin/simple-implementation-of-help-command-a634711b70e
"""
import logging

from sslmanager.plugin import Plugin  # pylint: disable=import-error

__author__ = 'Sebastian Stigler'
__copyright__ = 'Sebastian Stigler'
__license__ = 'mit'

_logger = logging.getLogger(__name__)


class CmdHelp(Plugin):
    """ The help command displays the help for the subcommands. """

    def subcommand_parser(self):
        """Argument parser for the plugin

        Adds a subcommand parser to the parent parser object
        :return: None
        """
        help_parser = self.create_subcommand_parser(
            'display help for subcommands'
        )
        help_parser.add_argument(
            'name',
            nargs='?',
            help='Command to show help for',
            metavar='<subcommand>'
        )

    def run(self):
        """Print help for the subcommand or print available subcommands"""
        name = self.data.args.name
        if name:
            self.data.subparsers.choices[name].print_help()
        else:
            print("Use \'help <subcommand>\' to show help for given command\n")
            print('List of available commands:')
            for key in sorted(self.data.subparsers.choices.keys()):
                print(
                    '  {:<14s} - {:s}'.format(
                        key,
                        self.data.subparsers.choices[key].description
                    )
                )
