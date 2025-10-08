import argparse
import sys

from colorama import Fore, Style

from sslmanager.config import load_config
from sslmanager.plugin import Plugin


class CmdListAlias(Plugin):
    """The list-alias command list all registered server aliases."""

    def subcommand_parser(self):
        list_alias_parser = self.create_subcommand_parser(
            "list all registered server aliases"
        )

    def run(self):
        config = load_config()

        if config is None:
            self.print_status(
                Fore.RED + "sslmanager is not initialized!\n           Please run 'sslmanager init' first." + Style.RESET_ALL
            )
            sys.exit(1)

        self.print_status("The registered server aliases are listed below:")
        for alias in config.domain_config:
            print(4 * " ", "🔸", alias.server_alias)
