import logging
import subprocess
import sys
from itertools import filterfalse
from pathlib import Path

from InquirerPy import prompt
from colorama import Fore, Style

from sslmanager.config import load_config, load_ssl_request_config
from sslmanager.helper import (
    choose_server_alias_and_date,
    DEFAULT_STYLE,
    DomainNameValidator,
)
from sslmanager.models.config import Config, DomainConfig
from sslmanager.models.filenames import Filenames
from sslmanager.plugin import Plugin, CommandFailed, raise_on_fail

__author__ = "Sebastian Stigler"
__copyright__ = "Sebastian Stigler"
__license__ = "mit"

from sslmanager.print_helper import State

_logger = logging.getLogger(__name__)


class CmdUpload(Plugin):
    """The upload command copies the certificate and passwordless key to the server"""

    def __init__(self):
        super().__init__()
        self.config: Config | None = None
        self.common_name: str | None = None
        self.server_alias: DomainConfig | None = None
        self.date_path: Path | None = None
        self.datetime_prefix: str | None = None
        self.ssh_username: str | None = None
        self.server_name: str | None = None

    def subcommand_parser(self):
        """Argument parser for the plugin

        Adds a subcommand parser to the parent parser object
        :return: None
        """
        upload_parser = self.create_subcommand_parser(
            "upload certificate and passwordless key to the server",
        )

    def run(self):
        self.config = load_config()
        if self.config is None:
            self.print_status(
                Fore.RED
                + "sslmanager is not initialized!\n           Please run 'sslmanager init' first."
                + Style.RESET_ALL
            )
            sys.exit(1)
        try:
            self.choose_server_alias_and_date()
            self.choose_username_and_server()
            self.upload_certificate_and_key()
        except (CommandFailed, KeyboardInterrupt):
            self.print_status("Command failed! 👿☠️💣", State.FAIL)
        else:
            self.print_status(
                f"Command successfully upload certificate and passwordless key to {self.common_name}!. 🐍 🌟 ✨"
            )

    @raise_on_fail
    def choose_server_alias_and_date(self):
        answers = choose_server_alias_and_date(self.config.domain_config)

        self.server_alias = answers["server_alias"]
        self.date_path = answers["date_dir"]
        self.datetime_prefix = answers["datetime_prefix"]
        _logger.debug("answers = %s", answers)
        return all(x is not None for x in answers)

    @raise_on_fail
    def choose_username_and_server(self):
        ssl_request_config = load_ssl_request_config(self.server_alias.path)
        dns_names = sorted(
            set([ssl_request_config.common_name] + ssl_request_config.subject_alt_name)
        )
        completer = {key: None for key in dns_names}
        allowed_domains = sorted(
            set(
                [".".join(name.split(".")[-2:]) for name in dns_names]
                + (self.config.allowed_domains if self.config is not None else [])
            )
        )

        questions = [
            {
                "type": "input",
                "name": "ssh_username",
                "default": ssl_request_config.ssh_username,
                "message": "SSH username",
            },
            {
                "type": "input",
                "name": "server_name",
                "instruction": "Hit tab for suggestions.",
                "completer": completer,
                "message": "Server name",
                "filter": lambda result: str(result).strip(),
                "validate": DomainNameValidator(allowed_domains=allowed_domains),
            },
            {
                "type": "confirm",
                "name": "confirm",
                "message": lambda result: f"Is 👉  {result['ssh_username']}@{result['server_name']} 👈  correct?",
                "default": False,
            },
        ]
        answers = {"confirm": False}
        while not answers["confirm"]:
            answers = prompt(questions, style=DEFAULT_STYLE)
        del answers["confirm"]
        self.ssh_username = answers["ssh_username"]
        self.server_name = answers["server_name"]
        _logger.debug("answers = %s", answers)
        return all(x is not None for x in answers)

    @raise_on_fail
    def upload_certificate_and_key(self):
        fn = Filenames.from_ssl_request_config_file(
            self.date_path / self.datetime_prefix
        )
        if not fn.key_pw_free_file.is_file():
            _logger.debug(f"key file: {fn.key_pw_free_file}")
            self.print_status(
                Fore.RED
                + "Key file is missing. (Have you used the new-request command yet?)"
                + Style.RESET_ALL
            )
            return False
        if not fn.cert_file.is_file():
            _logger.debug(f"cert file: {fn.cert_file}")
            self.print_status(
                Fore.RED
                + "Certificate is missing. (Have you used the store-cert command yet?)"
                + Style.RESET_ALL
            )
            return False
        scp_cmd = [
            "/usr/bin/scp",
            str(fn.key_pw_free_file),
            str(fn.cert_file),
            f"{self.ssh_username}@{self.server_name}:~",
        ]
        try:
            subprocess.run(scp_cmd, check=True)
        except subprocess.CalledProcessError as e:
            _logger.exception(e)
            result = False
        else:
            result = True

        self.print_status(
            f"Certificate and key from {self.server_alias.server_alias} copied to {self.server_name}.",
            State.OK if result else State.FAIL,
        )
        return result
