"""
Styles for InquirerPy
"""
__author__ = "Sebastian Stigler"
__copyright__ = "Sebastian Stigler"
__license__ = "mit"

import re
import sys
from pathlib import Path
from typing import Any

from InquirerPy import prompt
from InquirerPy.base import Choice
from prompt_toolkit.validation import Validator, ValidationError

from sslmanager.models.config import Config, DomainConfig
from sslmanager.models.openssl_config import CommonOpensslRequestConfig
from sslmanager.types.domain_name import DomainName

DEFAULT_STYLE = {
    "separator": "#66cc66 bold",
    "footer": "#ACACAC",
    "questionmark": "#2196f3 bold",
    "selected": "#cc5454",
    "pointer": "#FF9D00 bold",
    "instruction": "#0e8b14 bold",
    "long_instruction": "#0ca612 bold",
    "answer": "#FF9D00 bold",
    "question": "bold",
    "input": "#FF9D00 ",
}


def collect_common_ssl_request(csrc: CommonOpensslRequestConfig):
    questions = [
        {
            "type": "input",
            "name": name,
            "message": field_info.description + ':',
            "default": getattr(csrc, name)
        }
        for name, field_info in CommonOpensslRequestConfig.model_fields.items()
    ]
    questions.append({"type": "confirm",
                      "name": "confirm",
                      "message": "Are these entries correct?",
                      "default": False, })

    answers = {"confirm": False}
    while not answers["confirm"]:
        answers = prompt(questions, style=DEFAULT_STYLE)
    del answers["confirm"]

    csrc.update(**answers)
    return csrc


class DomainNameValidator(Validator):
    def __init__(self, is_list: bool = False, *, allowed_domains: list[DomainName] | None = None):
        super().__init__()
        self.is_list = is_list
        self.allowed_domains = allowed_domains
        self.pattern = r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"

    def validate(self, document):
        """validation

         :param document: text document
         :raises ValidationError: if the input is invalid
         :return:
         """
        if self.is_list:
            entries = [domain.strip() for domain in document.text.split('\n') if domain.strip()]
            for i, entry in enumerate(entries):
                self.check_domain_name_pattern(entry, document.text.find(entry))
        else:
            self.check_domain_name_pattern(document.text.strip(), len(document.text))

    def check_domain_name_pattern(self, entry:str, cursor_position:int):
        if not re.match(self.pattern, entry):
            raise ValidationError(message=f"Invalid domain name {entry}", cursor_position=cursor_position)
        if self.allowed_domains:
            if not any(entry.endswith(domain) for domain in self.allowed_domains):
                raise ValidationError(message=f"Domain name {entry} is not of an allowed domain {self.allowed_domains}", cursor_position=cursor_position)


class ServerAliasValidator(Validator):

    def __init__(self, config: Config, force:bool = False):
        super().__init__()
        self.config = config
        self.force = force

    def validate(self, document):
        """validation

        :param document: text document
        :raises ValidationError: if the input is invalid
        :return:
        """
        server_alias = document.text.strip()
        storage_path = self.config.base_path.expanduser() / server_alias
        if not server_alias:
            raise ValidationError(message="Server alias is required.")
        if self.config.get_domain_config(server_alias) is not None and not self.force:
            raise ValidationError(message="Server alias already exists.")
        if storage_path.exists() and not self.force:
            raise ValidationError(message="Server alias (path) already exists.")


def get_date_paths(path: Path):
    """get dated directories within a server_alias"""
    dirs = sorted(
        {
            (x, x.name)
            for x in path.iterdir()
            if x.is_dir() and re.match(pattern=r"20\d\d\d\d\d\d", string=x.name)
        }, key=lambda c: c[1], reverse=True
    )
    return [Choice(value=d[0], name=d[1]) for d in dirs]


def get_datetime_prefix(path: Path):
    """get datetime prefixes within a date directory of a server_alias"""
    prefixes = sorted(
        {
            (x.name, "{h}:{m}:{s}".format(h=x.name[8:10], m=x.name[10:12], s=x.name[12:14]))
            for x in path.iterdir()
            if x.is_file and re.match(pattern=r"20\d{12}", string=x.name[:14]) and x.name.endswith('-openssl.conf')
        }, key=lambda c: c[1], reverse=True
    )
    return [Choice(value=p[0], name=p[1]) for p in prefixes]


def choose_server_alias_and_date(domain_config:list[DomainConfig]) -> dict[str, Any]:
        server_alias_choices = [Choice(value=e, name=e.server_alias) for e in domain_config]
        questions = [
            {
                "type": "list",
                "name": "server_alias",
                "message": "For which server alias is the certificate?",
                "choices": server_alias_choices,
                "validate": lambda ans: len(get_date_paths(ans.path)) > 0,
                "invalid_message": "No certificate request available for this server alias",
            },
            {
                "type": "list",
                "name": "date_dir",
                "message": "When was the request created (date)?",
                "choices": lambda ans: get_date_paths(ans['server_alias'].path)
            },
            {
                "type": "list",
                "name": "datetime_prefix",
                "message": "At what time was the request created?",
                "choices": lambda ans: get_datetime_prefix(ans['date_dir'])
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
        return answers
