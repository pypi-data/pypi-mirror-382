import logging
import secrets
import string
import subprocess
import sys
from datetime import datetime

from InquirerPy import prompt
from InquirerPy.base import Choice
from colorama import Style, Fore

from sslmanager.config import load_config, load_ssl_request_config
from sslmanager.models.config import Config, DomainConfig
from sslmanager.models.filenames import Filenames
from sslmanager.plugin import Plugin, CommandFailed, raise_on_fail
from sslmanager.print_helper import State
from sslmanager.helper import DEFAULT_STYLE

__author__ = 'Sebastian Stigler'
__copyright__ = 'Sebastian Stigler'
__license__ = 'mit'

_logger = logging.getLogger(__name__)


class CmdNewRequest(Plugin):
    """The new-request command creates a new ssl certificate request."""

    def __init__(self):
        super().__init__()
        self.domain_config_list: list[DomainConfig] = []
        self.config: Config | None = None
        now = datetime.now()
        self.date_path: str = now.strftime("%Y%m%d")
        self.datetime_prefix: str = now.strftime("%Y%m%d%H%M%S")

    def subcommand_parser(self):
        """Argument parser for the plugin

        Adds a subcommand parser to the parent parser object
        :return: None
        """
        new_request_parser = self.create_subcommand_parser(
            'create a new ssl certificate request',
        )

    def run(self):
        self.config = load_config()

        if self.config is None:
            self.print_status(
                Fore.RED + "sslmanager is not initialized!\n           Please run 'sslmanager init' first." + Style.RESET_ALL
            )
            sys.exit(1)

        try:
            self.choose_server_alias()
            self.batch_create_ssl_certificate_requests()
        except (CommandFailed, KeyboardInterrupt):
            self.print_status("Command failed! 👿☠️💣", State.FAIL)
        else:
            self.print_status(f"Command successfully created new ssl certificate requests!. 🐍 🌟 ✨")


    @raise_on_fail
    def choose_server_alias(self):
        server_alias_choices = [Choice(value=e, name=e.server_alias) for e in self.config.domain_config]
        questions = [
            {
                "type": "checkbox",
                "name": "server_alias_list",
                "message": "Which server alias do you want to use?",
                "instruction": "(You may choose more than one alias.)",
                "long_instruction": "📢  Mark the chosen server alias with the space bar.",
                "choices": server_alias_choices,
                "transformer": lambda res: "%s server alias selected" % len(res),
            },
        ]
        answers = prompt(questions, style=DEFAULT_STYLE)
        self.domain_config_list = answers["server_alias_list"]
        _logger.debug("server_alias_list: %s", self.domain_config_list)
        result = bool(self.domain_config_list)
        self.print_status("%s server alias selected" % len(self.domain_config_list), State.OK if result else State.FAIL)
        return result

    @raise_on_fail
    def batch_create_ssl_certificate_requests(self):
        res = [self.create_ssl_certificate_request(domain_config) for domain_config in self.domain_config_list]
        return any(res)

    def create_ssl_certificate_request(self, domain_config: DomainConfig):
        base_path = domain_config.path / self.date_path
        ssl_request_config = load_ssl_request_config(domain_config.path)

        file_prefix = f"{self.datetime_prefix}-{ssl_request_config.common_name.replace('.', '_')}"

        fn = Filenames(base_path=base_path, file_prefix=file_prefix)
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(12))

        request_cmd = [
            "/usr/bin/openssl",
            "req", "-batch", "-newkey", "rsa:2048", "-keyout", fn.key_file, "-passout", f"pass:{password}",
            "-out", fn.ssl_request_file, '-config', fn.ssl_request_config_file
        ]
        remove_password_cmd = [
            "/usr/bin/openssl",
            "rsa", "-in", fn.key_file, "-out", fn.key_pw_free_file, "-passin", f"pass:{password}"
        ]

        result = True
        try:
            base_path.mkdir(parents=True, exist_ok=True)
            fn.ssl_request_config_file.write_text(str(ssl_request_config))
            fn.domain_list_csv_file.write_text(ssl_request_config.domain_list_csv())
            fn.password_file.write_text(password)
            subprocess.run(request_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(remove_password_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            _logger.exception(e)
            result = False
        alias_date = f"{base_path.parent.name}/{base_path.name}"
        self.print_status(f"Creating ssl certificate request for {alias_date}.", State.OK if result else State.FAIL)
        print(f"{Fore.LIGHTCYAN_EX}\n{fn.ssl_request_file.read_text()}\n{Style.RESET_ALL}")
        return result
