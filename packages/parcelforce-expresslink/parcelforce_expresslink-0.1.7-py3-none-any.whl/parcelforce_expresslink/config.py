import functools
import os
from importlib.resources import files
from pathlib import Path
from typing import cast, Self

from loguru import logger
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env(env_name: str = 'PARCELFORCE_ENV') -> Path:
    env = os.getenv(env_name)
    if not env:
        raise ValueError(f'{env_name} not set')
    env_path = Path(env)
    if not env_path.exists():
        raise ValueError(f'{env_path} not a valid path')
    logger.debug(f'Loading environment from {env_path}')
    return env_path


def get_wsdl():
    res = Path(cast(Path, files('parcelforce_expresslink').joinpath('expresslink_api.wsdl'))) # resource files returns Traversable (subset of path)
    if not res.exists():
        raise FileNotFoundError('WSDL file not found')
    logger.info(f'Using WSDL file at {res}')
    return str(res.resolve())


class ParcelforceSettings(BaseSettings):
    """Load Parcelforce ExpressLink configuration from environment variables / .env file.
    location of environment file is set by the environment variable PARCELFORCE_ENV.
    """

    pf_ac_num_1: str
    pf_contract_num_1: str
    pf_expr_usr: SecretStr
    pf_expr_pwd: SecretStr

    department_id: int = 1
    pf_ac_num_2: str | None
    pf_contract_num_2: str | None

    pf_endpoint: str = r'https://expresslink.parcelforce.net/ws'
    pf_wsdl: str = Field(default_factory=get_wsdl)
    pf_binding: str = r'{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding'
    tracking_url_stem: str = r'https://www.royalmail.com/track-your-item#/tracking-results/'

    model_config = SettingsConfigDict()

    def get_auth_secrets(self) -> tuple[str, str]:
        return self.pf_expr_usr.get_secret_value(), self.pf_expr_pwd.get_secret_value()

    @classmethod
    @functools.lru_cache
    def from_env(cls, env_name: str = 'PARCELFORCE_ENV') -> Self:
        return cls(_env_file=get_env(env_name))

    def tracking_link(self, shipment_num: str) -> str:
        stem = self.tracking_url_stem
        tlink = f'{stem}PB{shipment_num}001'
        return tlink



