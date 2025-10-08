from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator, Any

from pydantic import BaseModel, Field, EmailStr, ValidationInfo, field_validator, ValidationError, \
    ConfigDict
from pydantic_core import PydanticCustomError

from sslmanager.types.domain_name import DomainName

_init_context_var = ContextVar('_init_context_var', default=None)


@contextmanager
def init_context(*value: DomainName) -> Iterator[None]:
    token = _init_context_var.set({'domain_names': value})
    try:
        yield
    finally:
        _init_context_var.reset(token)


class CommonOpensslRequestConfig(BaseModel):
    country_name: str = Field(default='DE', description="Country Name (2 letter code)")
    state_or_province_name: str = Field(default='Baden-Wuerttemberg', description="State or Province Name (full name)")
    locality_name: str = Field(default='Aalen', description="Your City")
    organization_name: str = Field(default='Hochschule Aalen - Technik und Wirtschaft',
                                   description="Organization Name (eg. company)")
    email_address: EmailStr = Field(default='sebastian.stigler@hs-aalen.de', description="Email Address")

    model_config = ConfigDict(validate_assignment=True)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)


class OpensslRequestConfig(CommonOpensslRequestConfig):
    common_name: DomainName = Field(examples=["in-stigler.htw-aalen.de"], description="Common name of the server")
    subject_alt_name: list[DomainName] = Field(default_factory=list, description="Subject Alternative Names")
    ssh_username: str = Field(examples=["stigler"], description="SSH username")

    @property
    def string_subject_alt_name(self) -> str:
        return ", ".join(f"DNS:{entry}" for entry in self.subject_alt_name)

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self.__pydantic_validator__.validate_python(
            data,
            self_instance=self,
            context=_init_context_var.get(),
        )

    @classmethod
    def from_common(cls, common_config: CommonOpensslRequestConfig, common_name: str,
                    subject_alt_name: list[DomainName], ssh_username: str) -> 'OpensslRequestConfig':
        return cls(common_name=common_name, subject_alt_name=subject_alt_name, ssh_username=ssh_username,
                   **common_config.model_dump())

    def __str__(self):
        return template.format(cfg=self)

    def domain_list_csv(self):
        """create a csv file with domain names"""
        domain_names = set([self.common_name] + self.subject_alt_name)
        return "\r\n".join(["DNS Name"] + list(sorted(domain_names)))


    @field_validator('common_name')
    @classmethod
    def validate_common_name(cls, v: DomainName, info: ValidationInfo) -> DomainName:
        context = info.context
        if context:
            domain_names = context.get('domain_names', [])
            if not any(v.endswith(domain_name) for domain_name in domain_names):
                raise PydanticCustomError(
                    'base_domain_error',
                    "common_name '{common_name}' is not from an allowed domain {allowed_domain_names}",
                    {'common_name': v, 'allowed_domain_names': domain_names}
                )
        return v

    @field_validator('subject_alt_name')
    @classmethod
    def validate_subject_alt_name(cls, v: list[DomainName], info: ValidationInfo) -> list[DomainName]:
        context = info.context
        if context:
            domain_names = context.get('domain_names', [])
            for i, alt_name in enumerate(v):
                if not any(alt_name.endswith(domain_name) for domain_name in domain_names):
                    raise PydanticCustomError(
                        'base_domain_error',
                        "subject_alt_name[{idx}] '{current_alt_name}' is not from an allowed domain {allowed_domain_names}",
                        {'idx': i, 'current_alt_name': alt_name, 'allowed_domain_names': domain_names}
                    )
        return v


template = """
####################################################################
[ req ]
distinguished_name    = req_distinguished_name

string_mask = nombstr

# The extensions to add to a certificate request
req_extensions = v3_req

# GWDG default options for certificate request
[ req_distinguished_name ]
countryName                 = Country Name (2 letter code)
countryName_default         = {cfg.country_name}
countryName_min             = 2
countryName_max             = 2

stateOrProvinceName         = State or Province Name (full name)
stateOrProvinceName_default = {cfg.state_or_province_name}

localityName                = Your City
localityName_default        = {cfg.locality_name}

0.organizationName          = Organization Name (eg, company)
0.organizationName_default  = {cfg.organization_name}

commonName                  = YOUR NAME
commonName_max              = 64
commonName_default          = {cfg.common_name}
 
emailAddress                = E-MAIL
emailAddress_max            = 64
emailAddress_default        = {cfg.email_address}
 
[ v3_req ]
subjectAltName              = {cfg.string_subject_alt_name}
 
####################################################################
""".lstrip()

if __name__ == '__main__':
    with init_context('hs-aalen.de', 'htw-aalen.de'):
        print(
            OpensslRequestConfig(common_name="bantel.htw-aalen.de", subject_alt_name=['bantel.informatik.hs-aalen.de']))

    print('-' * 10, '\n')

    try:
        with init_context('htw-aalen.de'):
            print(
                OpensslRequestConfig(common_name="bantel.htw-aalen.de",
                                     subject_alt_name=['bantel.informatik.hs-aalen.de']))
    except ValidationError as e:
        print(e)

    print('-' * 10, '\n')
    print(
        OpensslRequestConfig(common_name="bantel.htw-aalen.de", subject_alt_name=['bantel.informatik.hs-aalen.de']))
