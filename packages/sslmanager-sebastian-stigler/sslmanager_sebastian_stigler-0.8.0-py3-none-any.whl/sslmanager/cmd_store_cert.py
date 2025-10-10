import logging
import sys
from argparse import ArgumentTypeError
from pathlib import Path

from colorama import Fore, Style

from sslmanager.config import load_config
from sslmanager.helper import choose_server_alias_and_date
from sslmanager.models.config import DomainConfig, Config
from sslmanager.models.filenames import Filenames
from sslmanager.plugin import Plugin, CommandFailed, raise_on_fail
from sslmanager.print_helper import State

__author__ = 'Sebastian Stigler'
__copyright__ = 'Sebastian Stigler'
__license__ = 'mit'

_logger = logging.getLogger(__name__)


def path_exist_type(value: str) -> Path:
    result = Path(value)
    if not result.is_file():
        ArgumentTypeError(f'"{value}" is not a file.')
    return result


class CmdStoreCert(Plugin):
    """The store-cert command stores the issued certificate in"""

    def __init__(self):
        super().__init__()
        self.config: Config | None = None
        self.server_alias: DomainConfig | None = None
        self.date_path: Path | None = None
        self.datetime_prefix: str | None = None

    def subcommand_parser(self):
        """Argument parser for the plugin

        Adds a subcommand parser to the parent parser object
        :return: None
        """
        store_cert_parser = self.create_subcommand_parser(
            'store cert with the corresponding request / key'
        )
        store_cert_parser.add_argument(
            'certificate',
            type=path_exist_type,
            help="path to the ssl certificate file"
        )

    def run(self):
        self.config = load_config()
        if self.config is None:
            self.print_status(
                Fore.RED + "sslmanager is not initialized!\n           Please run 'sslmanager init' first." + Style.RESET_ALL
            )
            sys.exit(1)

        try:
            self.choose_server_alias_and_date()
            self.store_issued_cert()
        except (CommandFailed, KeyboardInterrupt):
            self.print_status("Command failed! 👿☠️💣", State.FAIL)
        else:
            self.print_status(f"Command successfully moved certificate to {self.server_alias.server_alias}!. 🐍 🌟 ✨")

    @raise_on_fail
    def choose_server_alias_and_date(self):
        answers = choose_server_alias_and_date(self.config.domain_config)

        self.server_alias = answers["server_alias"]
        self.date_path = answers["date_dir"]
        self.datetime_prefix = answers["datetime_prefix"]
        _logger.debug("answers = %s", answers)
        return all(x is not None for x in answers)

    @raise_on_fail
    def store_issued_cert(self):
        fn = Filenames.from_ssl_request_config_file(self.date_path / self.datetime_prefix)
        try:
            self.data.args.certificate.rename(fn.cert_file)
        except FileExistsError as err:
            _logger.exception(err)
            result = False
        else:
            result = fn.cert_file.is_file()

        self.print_status(f"Store issued certificate as <base_path>/{'/'.join(fn.cert_file.parts[-3:])}",
                          State.OK if result else State.FAIL)
        return result


