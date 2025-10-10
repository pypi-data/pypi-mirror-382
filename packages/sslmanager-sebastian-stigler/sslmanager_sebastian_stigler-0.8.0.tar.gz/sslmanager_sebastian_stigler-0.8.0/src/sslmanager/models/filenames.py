from pathlib import Path

from pydantic import BaseModel, Field, computed_field


class Filenames(BaseModel):
    base_path:Path = Field(description="The base path for the files")
    file_prefix:str = Field(description="The file prefix")

    @computed_field
    @property
    def ssl_request_config_file(self) -> Path:
        return self.base_path / f"{self.file_prefix}-openssl.conf"

    @computed_field
    @property
    def ssl_request_file(self) -> Path:
        return self.base_path / f"{self.file_prefix}-certreq.pem"

    @computed_field
    @property
    def key_file(self)-> Path:
        return self.base_path / f"{self.file_prefix}-private-key.pem"

    @computed_field
    @property
    def key_pw_free_file(self)-> Path:
        return self.base_path / f"{self.file_prefix}-private-key-pw-free.pem"

    @computed_field
    @property
    def password_file(self)-> Path:
        return self.base_path / f"{self.file_prefix}-key-password.txt"

    @computed_field
    @property
    def cert_file(self)-> Path:
        return self.base_path / f"{self.file_prefix}-cert.pem"
    @computed_field
    @property
    def domain_list_csv_file(self)-> Path:
        return self.base_path / f"{self.file_prefix}-domains.csv"

    @classmethod
    def from_ssl_request_config_file(cls, ssl_request_config_file:Path):
        if not ssl_request_config_file.name.endswith("-openssl.conf"):
            raise AssertionError(f"The file  {ssl_request_config_file.name} is not a openssl.conf file.")
        base_path = ssl_request_config_file.parent
        file_prefix = ssl_request_config_file.name[:-13]
        return cls(base_path=base_path, file_prefix=file_prefix)