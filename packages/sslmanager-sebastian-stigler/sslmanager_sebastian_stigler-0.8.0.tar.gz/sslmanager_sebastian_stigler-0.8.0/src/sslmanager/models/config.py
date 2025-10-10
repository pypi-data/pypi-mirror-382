import re
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_core import PydanticCustomError

from sslmanager.types.domain_name import DomainName


class DomainConfig(BaseModel):
    server_alias: str = Field(description="The alias of the server.")
    path: Path = Field(
        description="The path (relative to the basePath) of the directory to store the the certificates.")

    def __len__(self) -> int:
        return len(self.server_alias)


class Config(BaseModel):
    base_path: Path = Field(description="The base path for all ssl certificate directories.")
    allowed_domains: list[DomainName] = Field(default_factory=list, description="The list of allowed domains.")
    domain_config: list[DomainConfig] = Field(default_factory=list,
                                              description="The list of domain-specific configuration objects.")
    model_config = ConfigDict(validate_assignment=True)

    def get_domain_config(self, server_alias) -> Path | None:
        res = [entry for entry in self.domain_config if entry.server_alias == server_alias]
        if len(res) == 0:
            return None
        return res[0].path

    def add_domain_config(self, server_alias, path: Path) -> bool:
        if self.get_domain_config(server_alias) is not None:
            return False
        domain_config = self.domain_config.copy()
        domain_config.append(DomainConfig(server_alias=server_alias, path=path))
        self.domain_config = sorted(domain_config, key=lambda x: x.server_alias)
        return True

    def add_allowed_domain(self, domain: DomainName| list[DomainName]) -> bool:
        allowed_domains = self.allowed_domains.copy()
        if isinstance(domain, list):
            return any([self.add_allowed_domain(d) for d in domain])
        if domain in self.allowed_domains:
            return False
        allowed_domains.append(domain)
        self.allowed_domains = allowed_domains
        return True

    @field_validator('allowed_domains', mode='before')
    @classmethod
    def validate_allowed_domains(cls, v: list[DomainName]) -> list[DomainName]:
        v = [x.strip() for x in v]
        for i, domain in enumerate(v):
            if re.match(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$",
                        domain) is None:
                raise PydanticCustomError(
                    'base_domain_error',
                    "allowed_domains[{idx}] '{current_domain}' is not from a valid domain",
                    {'idx': i, 'current_domain': domain}
                )
        return v
