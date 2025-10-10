import argparse
import logging

from InquirerPy import prompt
from InquirerPy.base import Choice

from sslmanager.config import load_config, save_config
from sslmanager.helper import DEFAULT_STYLE
from sslmanager.models.config import Config, DomainConfig
from sslmanager.plugin import Plugin, CommandFailed, raise_on_fail
from sslmanager.print_helper import State

__author__ = 'Sebastian Stigler'
__copyright__ = 'Sebastian Stigler'
__license__ = 'mit'

_logger = logging.getLogger(__name__)


class CmdDelAlias(Plugin):
    """The del-alias command removes a server alias from the registered aliases."""

    def __init__(self):
        super().__init__()
        self.config: Config | None = None
        self.server_alias: DomainConfig | None = None

    def subcommand_parser(self):
        self.create_subcommand_parser(
            "delete a server alias from the config",
        )
        pass

    def run(self):
        self.config = load_config()

        try:
            self.choose_server_alias()
            self.remove_server_alias()
        except (CommandFailed, KeyboardInterrupt):
            self.print_status("Command failed! 👿☠️💣", State.FAIL)
        else:
            self.print_status(f"Command successfully removed the entry for {self.server_alias.server_alias}!. 🐍 🌟 ✨")

    @raise_on_fail
    def choose_server_alias(self):
        server_alias_choices = [Choice(value=e, name=e.server_alias) for e in self.config.domain_config]
        server_alias_choices.append(Choice(value=None, name="ABORT"))
        questions = [
            {
                "type": "list",
                "name": "server_alias",
                "message": "For which server alias is the certificate?",
                "choices": server_alias_choices,
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
        result = bool(answers["server_alias"])
        self.server_alias = answers["server_alias"]
        return result

    @raise_on_fail
    def remove_server_alias(self):
        name = self.server_alias.name
        base_path = self.server_alias.path.parent / "_REMOVED_ALIASES"
        base_path.joinpath(name)
        try:
            self.config.domain_config.remove(self.server_alias)
            base_path.parent.mkdir(parents=True, exist_ok=True)
            self.server_alias.path.rename(base_path)
            save_config(self.config)
        except Exception as e:
            _logger.exception(e)
            result = False
        else:
            result = True
        return result
