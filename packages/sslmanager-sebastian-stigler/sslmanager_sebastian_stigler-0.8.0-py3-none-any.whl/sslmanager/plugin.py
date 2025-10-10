"""
The base class for a plugin (subcommand)
"""
import functools
import logging
from abc import ABC, abstractmethod

from .print_helper import State, print_status

__author__ = 'Sebastian Stigler'
__copyright__ = 'Sebastian Stigler'
__license__ = 'mit'

_logger = logging.getLogger(__name__)


class Plugin(ABC):
    """Plugin interface"""

    def __init__(self):
        super().__init__()
        self.data = None
        self.subcommand = None

    def register(self, data, subcommand):
        """Register the plugin with the dsproject tool

        The properties of the MainPluginInterface class will be set to local attributes.
        The subcommand parser will be registered with the main parser.

        :param data: shared data from the main object
        :param subcommand: Name of the subcommand
        :return:
        """
        self.data = data
        self.subcommand = subcommand
        self.subcommand_parser()

    @classmethod
    def factory(cls):
        """Plugin Factory

        :return: a instance of the plugin
        """
        return cls()

    @abstractmethod
    def subcommand_parser(self):
        """Argument parser for the plugin

        Adds a subcommand parser to the parent parser object
        :return: None
        """

    def create_subcommand_parser(self, help_text):
        """Helper to create a minimal subcommand parser

        This method should be used in the subcommand_parser method in
        the plugin class.

        :Example:

        In the subclass you implement the abstract method
        ``subcommand_parser`` like this::

            # ...
            def subcommand_parser(self):
                subcommand_parser = create_subcommand_parser(
                    'help text for the subcommand'
                )
            subcommand.add_argument(...)
            # ...

        :param help_text: Help text
        :return:
        """
        subcommand_parser = self.data.subparsers.add_parser(
            self.subcommand,
            help=help_text,
            description=self.__class__.__doc__.strip()
        )
        subcommand_parser.set_defaults(subcommand=self.subcommand)
        subcommand_parser.set_defaults(func=self.run)
        return subcommand_parser

    def print_status(self, text, state=State.NONE):
        """Print a formatted message

        :param text: Text
        :param state: State
        """
        print_status('cmd %s' % self.subcommand, text, state)

    @abstractmethod
    def run(self):
        """The main routine for the subcommand

        :return:
        """


class PluginData:
    """Interface in the main instance used by the plugins"""

    def __init__(self, parser):
        self._args = None
        self._subparsers = parser.add_subparsers(
            dest='subcommand',
            metavar='<subcommand>'
        )
        self._subparsers.required = True

    @property
    def args(self):
        """The parse command line arguments

        :raises LookupError: if called before it is set.
        :return: ArgumentParser object
        """
        if self._args is None:
            raise LookupError('args is not set yet')
        return self._args

    @args.setter
    def args(self, value):
        """Set the ArgumentParser object

        :param value: The ArgumentParser
        :raises: ValueError if it's called more than once
        """
        if self._args is not None:
            raise ValueError('You can\'t set args twice')
        self._args = value

    @property
    def subparsers(self):
        """return the subparser for the plugins"""
        return self._subparsers


class CommandFailed(Exception):
    """Custom Exception use in run method """


def raise_on_fail(func):
    """decorator to raise CommandFailed Error"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if not result:
            raise CommandFailed()
        return result

    return wrapper
