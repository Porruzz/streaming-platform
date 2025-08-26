# services/catalog-service/app/settings.py
from common.config.settings import BaseServiceSettings

class Settings(BaseServiceSettings):
    service_name: str = "catalog-service"

settings = Settings()
