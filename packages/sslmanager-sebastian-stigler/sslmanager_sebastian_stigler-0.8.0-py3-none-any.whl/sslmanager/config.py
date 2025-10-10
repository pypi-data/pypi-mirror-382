import logging
import os
from pathlib import Path
from typing import Type

from pydantic import BaseModel
from pydantic_core import ValidationError

from sslmanager.models.config import Config
from sslmanager.models.openssl_config import CommonOpensslRequestConfig, OpensslRequestConfig

_logger = logging.getLogger(__name__)

BASE_PATH: Path = Path(os.environ.get("SSLMANAGER_BASE_PATH", '~/.config/sslmanager')).expanduser()
CONFIG_PATH: Path = BASE_PATH / 'config.json'
COMMON_SSL_REQUEST_PATH: Path = BASE_PATH / 'common_ssl_request.json'
SSL_REQUEST_CONFIG_FILE: str = "ssl_request_config.json"


def _load(cls: Type[BaseModel] | Type[OpensslRequestConfig], path: Path) -> BaseModel | OpensslRequestConfig | None:
    try:
        with open(path, 'r') as f:
            content = f.read()
        return cls.model_validate_json(content)
    except (FileNotFoundError, ValidationError) as err:
        _logger.debug(err)
        return None


def _save(model: BaseModel, path: Path) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    with open(path, 'w') as f:
        f.write(model.model_dump_json(indent=2))


def load_config(path: Path = CONFIG_PATH) -> Config | None:
    return _load(Config, path)


def save_config(obj: Config, path: Path = CONFIG_PATH) -> None:
    _save(obj, path)


def load_common_ssl_request(path: Path = COMMON_SSL_REQUEST_PATH) -> CommonOpensslRequestConfig | None:
    return _load(CommonOpensslRequestConfig, path)


def save_common_ssl_request(obj: CommonOpensslRequestConfig,
                            path: Path = COMMON_SSL_REQUEST_PATH) -> None:
    _save(obj, path)


def load_ssl_request_config(server_alias_path: Path) -> OpensslRequestConfig:
    return _load(OpensslRequestConfig, server_alias_path / SSL_REQUEST_CONFIG_FILE)


def save_ssl_request_config(obj: OpensslRequestConfig, path: Path) -> None:
    _save(obj, path / SSL_REQUEST_CONFIG_FILE)
