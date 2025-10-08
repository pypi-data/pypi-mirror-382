import logging
import os.path
import sys

from InquirerPy import prompt
from InquirerPy.validator import PathValidator
from colorama import Style, Fore

from sslmanager.config import load_config, save_common_ssl_request, save_config
from sslmanager.models.config import Config
from sslmanager.models.openssl_config import CommonOpensslRequestConfig
from sslmanager.plugin import Plugin, CommandFailed, raise_on_fail
from sslmanager.print_helper import State
from sslmanager.helper import collect_common_ssl_request, DEFAULT_STYLE, DomainNameValidator

__author__ = 'Sebastian Stigler'
__copyright__ = 'Sebastian Stigler'
__license__ = 'mit'

_logger = logging.getLogger(__name__)


class CmdInit(Plugin):
    """The init command sets up the sslmanager for the first time.

    It sets the common entries for the ssl request and
    where the settings for the domains will be stored.
    """

    def __init__(self):
        super().__init__()
        self.common = None
        self.config = None

    def subcommand_parser(self):
        """Argument parser for the plugin

        Adds a subcommand parser to the parent parser object
        :return: None
        """
        init_parser = self.create_subcommand_parser(
            'setup common ssl request entries and base path for the data',
        )
        init_parser.add_argument(
            '-f',
            '--force',
            action='store_true',
            help='replace existing config',
        )

    def run(self):
        force = self.data.args.force
        if load_config() is not None and not force:
            self.print_status(
                Fore.RED + "sslmanager is already initialized.\n           Use '-f|--force' to overwrite it anyway." + Style.RESET_ALL)
            sys.exit(1)
        print("Answer the following questions:")
        try:
            self.collect_base_config()
            self.collect_common_ssl_request_config()
            self.confirm_saving()
            self.save_base_config()
            self.save_common_ssl_request_config()
        except (CommandFailed, KeyboardInterrupt):
            self.print_status("Init command failed!", State.FAIL)
        else:
            self.print_status("Init command completed successfully. 🐍 🌟 ✨")

    @raise_on_fail
    def collect_common_ssl_request_config(self):

        common = collect_common_ssl_request(CommonOpensslRequestConfig())
        self.common = common
        _logger.debug('self.common = %r', self.common)
        result = bool(self.common)
        if not result:
            self.print_status("Set the common entries of the ssl certificate request.", State.FAIL)
        return result

    @raise_on_fail
    def collect_base_config(self):

        questions = [
            {
                "type": "filepath",
                "name": "base_path",
                "default": "~/",
                "message": "The base path for the ssl certificates:",
                "filter": lambda x: os.path.expanduser(x),
                "only_directories": True,
                "validate": PathValidator(is_dir=True, message="Input is not a directory"),
            },
            {
                "type": "input",
                "name": "allowed_domains",
                "multiline": True,
                "message": "The allowed domains (each in a new line):",
                "filter": lambda domains: [domain.strip() for domain in domains.split("\n") if domain.strip()],
                "validate": DomainNameValidator(True),
            },
            {
                "type": "confirm",
                "name": "confirm",
                "message": "Is this correct?",
                "default": False,
            }]
        answers = {"confirm": False}
        while not answers["confirm"]:
            answers = prompt(questions, style=DEFAULT_STYLE)
        del answers["confirm"]

        self.config = Config(**answers)
        _logger.debug('self.config = %r', self.config)

        result = bool(self.config)
        if not result:
             self.print_status("Set the base path of the ssl certificate requests.", State.FAIL)
        return result

    @raise_on_fail
    def confirm_saving(self):
        if not self.data.args.force:
            return True
        questions = [{
            "type": "confirm",
            "name": "confirm",
            "message": "Do you want to save this new settings and overwrite the old ones?",
            "default": False,
        }]
        answers = prompt(questions, style=DEFAULT_STYLE)
        if not answers["confirm"]:
            self.print_status(Fore.RED + "The new settings will not be saved." + Style.RESET_ALL)
        return answers["confirm"]

    @raise_on_fail
    def save_common_ssl_request_config(self):
        result = True
        try:
            save_common_ssl_request(self.common)
        except Exception as e:
            _logger.exception(e)
            result = False
        self.print_status("Save the common ssl request config.", State.OK if result else State.FAIL)
        return result

    @raise_on_fail
    def save_base_config(self):
        result = True
        try:
            save_config(self.config)
        except Exception as e:
            _logger.exception(e)
            result = False
        self.print_status("Save the base config.", State.OK if result else State.FAIL)
        return result
