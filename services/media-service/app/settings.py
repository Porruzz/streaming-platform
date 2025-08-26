# services/media-service/app/settings.py
from common.config.settings import BaseServiceSettings

class Settings(BaseServiceSettings):
    service_name: str = "media-service"

settings = Settings()
