import logging
import sys

from InquirerPy import prompt
from colorama import Style, Fore

from sslmanager.config import load_config, load_common_ssl_request, save_ssl_request_config, save_config
from sslmanager.models.openssl_config import OpensslRequestConfig, CommonOpensslRequestConfig
from sslmanager.plugin import Plugin, CommandFailed, raise_on_fail

__author__ = 'Sebastian Stigler'
__copyright__ = 'Sebastian Stigler'
__license__ = 'mit'

from sslmanager.print_helper import State
from sslmanager.helper import DEFAULT_STYLE, collect_common_ssl_request, DomainNameValidator, \
    ServerAliasValidator

_logger = logging.getLogger(__name__)


class CmdAddAlias(Plugin):
    """The add-alias command sets up a new server."""

    def __init__(self):
        super().__init__()
        self.config = None
        self.server_alias: str | None = None
        self._common_ssl_request_config: CommonOpensslRequestConfig | None = None
        self.common: CommonOpensslRequestConfig | None = None  # New copy
        self.open_ssl_request_config: OpensslRequestConfig | None = None

    def subcommand_parser(self):
        """Argument parser for the plugin

        Adds a subcommand parser to the parent parser object
        :return: None
        """
        add_alias_parser = self.create_subcommand_parser(
            'add a new server alias to the config'
        )
        add_alias_parser.add_argument(
            '-f',
            '--force',
            action='store_true',
            help='replace existing config',
        )
        add_alias_parser.add_argument(
            '-I',
            '--ignore-allowed-domains',
            action='store_true',
            help='ignore restrictions to allowed domains',
        )

    def run(self):
        self.config = load_config()
        self._common_ssl_request_config = load_common_ssl_request()
        if self.config is None or self._common_ssl_request_config is None:
            self.print_status(
                Fore.RED + "sslmanager is not initialized!\n           Please run 'sslmanager init' first." + Style.RESET_ALL
            )
            sys.exit(1)
        print("Answer the following questions:")
        try:
            self.collect_server_alias()
            self.collect_common_ssl_request_config()
            self.collect_ssl_request_config()
            self.create_server_alias_path_and_store_configs()
        except (CommandFailed, KeyboardInterrupt):
            self.print_status("Command failed! 👿☠️💣", State.FAIL)
        else:
            self.print_status(f"Command successfully created an entry for {self.server_alias}!. 🐍 🌟 ✨")

    @raise_on_fail
    def collect_server_alias(self):
        force = self.data.args.force
        answers = {"confirm": False, "server_alias": ""}
        questions = [
            {
                "type": "input",
                "name": "server_alias",
                "message": "Server Alias",
                "default": lambda _: answers["server_alias"],
                "filter": lambda val: val.strip(),
                "validate": ServerAliasValidator(self.config, force=force),
            },
            {
                "type": "confirm",
                "name": "confirm",
                "message": "Is this server alias correct?",
                "default": False,
            }]
        while not answers["confirm"]:
            answers = prompt(questions, style=DEFAULT_STYLE)
        del answers["confirm"]

        server_alias = answers["server_alias"]
        server_alias_path = self.config.base_path.expanduser() / server_alias
        result = self.config.add_domain_config(server_alias, server_alias_path)
        self.server_alias = server_alias
        if not result:
            self.print_status("Set the server_alias to " + server_alias, State.FAIL)
        return result

    @raise_on_fail
    def collect_common_ssl_request_config(self):
        common = collect_common_ssl_request(self._common_ssl_request_config)
        self.common = common

        _logger.debug('self.common = %r', self.common)
        result = bool(self.common)
        if not result:
            self.print_status("Set the common entries of the ssl certificate request.", State.FAIL)
        return result

    @raise_on_fail
    def collect_ssl_request_config(self):
        allowed_domains = self.config.allowed_domains if self.config is not None and not self.data.args.ignore_allowed_domains else []

        questions = [
            {
                "type": "input",
                "name": "common_name",
                "message": OpensslRequestConfig.model_fields['common_name'].description,
                "validate": DomainNameValidator(allowed_domains=allowed_domains),
            },
            {
                "type": "confirm",
                "name": "subject_alt_name_choice",
                "message": "Do you want to use alternative names, too?",
                "default": False,
            },
            {
                "type": "input",
                "name": "subject_alt_name",
                "multiline": True,
                "default": lambda result: result['common_name'],
                "instruction": "Always add the common name, too",
                "message": OpensslRequestConfig.model_fields['subject_alt_name'].description,
                "filter": lambda domains: [domain.strip() for domain in domains.split("\n") if domain.strip()],
                "transformer": lambda domains: ", ".join([domain.strip() for domain in domains.split("\n") if domain.strip()]),
                "validate": DomainNameValidator(True, allowed_domains=allowed_domains),
                "when": lambda res: res["subject_alt_name_choice"],
            },
            {
                "type": "input",
                "name": "ssh_username",
                "message": OpensslRequestConfig.model_fields['ssh_username'].description,
            },
            {
                "type": "confirm",
                "name": "confirm",
                "message": "Is this correct?",
                "default": False,
            }
        ]
        answers = {"confirm": False}
        while not answers["confirm"]:
            answers = prompt(questions, style=DEFAULT_STYLE)
        del answers["confirm"]
        del answers["subject_alt_name_choice"]
        if answers["subject_alt_name"] is None:
            answers["subject_alt_name"] = [ answers["common_name"] ]
        self.open_ssl_request_config = OpensslRequestConfig.from_common(self.common, **answers)
        _logger.debug('self.open_ssl_request_config = %r', self.open_ssl_request_config)

        result = bool(self.open_ssl_request_config)
        if not result:
            self.print_status("Set specific entries of the ssl certificate request.", State.FAIL)
        return result

    @raise_on_fail
    def create_server_alias_path_and_store_configs(self):
        server_alias_path = self.config.get_domain_config(self.server_alias)
        result = server_alias_path is not None
        if not server_alias_path.exists() or self.data.args.force:
            try:
                server_alias_path.mkdir(exist_ok=True)
                save_ssl_request_config(self.open_ssl_request_config, server_alias_path)
                save_config(self.config)
            except Exception as e:
                _logger.exception(e)
                result = False
        if not result:
            self.print_status("New server alias created and stored.", State.FAIL)
        return result
