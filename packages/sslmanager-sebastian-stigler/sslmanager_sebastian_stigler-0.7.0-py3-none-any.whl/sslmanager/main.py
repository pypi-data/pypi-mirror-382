"""
The main class for dsproject
"""
import argparse
import logging
import sys

import coloredlogs
import shtab
from colorama import init

from . import __version__
from .plugin import PluginData

__author__ = 'Sebastian Stigler'
__copyright__ = 'Sebastian Stigler'
__license__ = 'mit'

_logger = logging.getLogger(__name__)


class SslManager:
    """SSL Manager """

    def __init__(self):
        init(autoreset=True)
        self.plugin_data = None
        self._parser = None
        self._plugins = {}

    def main(self, args):
        """Main method"""

        self.plugin_data = PluginData(
            self.create_parser()
        )
        self.register_plugins()
        self.plugin_data.args = self._parser.parse_args(args)
        self.setup_logging()
        self.run_subcommand()

    def create_parser(self):
        """Create the main parser object

        :return: ArgumentParser object
        """
        parser = argparse.ArgumentParser(
            prog='sslmanager',
            description=self.__class__.__doc__
        )
        shtab.add_argument_to(parser, ['-s', '--print-completion'])
        parser.add_argument(
            '--version',
            action='version',
            version='sslmanager {ver}'.format(ver=__version__))
        parser.add_argument(
            '-v',
            '--verbose',
            dest='loglevel',
            help=argparse.SUPPRESS,
            action='store_const',
            const=logging.INFO)
        parser.add_argument(
            '-vv',
            '--very-verbose',
            dest='loglevel',
            help=argparse.SUPPRESS,
            action='store_const',
            const=logging.DEBUG)
        parser.set_defaults(subcommand='')
        parser.set_defaults(func=parser.print_help)
        self._parser = parser
        return parser

    def setup_logging(self):
        """Setup basic logging"""
        log_format = '%(levelname)s: %(message)s'
        coloredlogs.install(
            fmt=log_format,
            datefmt='%Y-%m-%d %H:%M:%S',
            level=self.plugin_data.args.loglevel or logging.WARNING
        )

    def register_plugins(self):
        """Register all plugins"""
        import importlib.metadata
        entry_points = importlib.metadata.entry_points(group='sslmanager.plugin')
        for entry_point in sorted(entry_points, key=lambda k: k.name):
            plugin_factory = entry_point.load()
            plugin = plugin_factory()
            self._plugins[entry_point.name.split('_',1)[1]] = plugin
            plugin.register(self.plugin_data, entry_point.name.split('_',1)[1])

    def run_subcommand(self):
        """Run the subcommand of the chosen plugin

        :return:
        """

        self.plugin_data.args.func()


def run():
    """Entry point for console_scripts
    """
    dsproject = SslManager()
    dsproject.main(sys.argv[1:])


if __name__ == '__main__':
    run()
