# libs/common-py/common/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseServiceSettings(BaseSettings):
    service_name: str = "service"
    env: str = "dev"
    log_level: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
