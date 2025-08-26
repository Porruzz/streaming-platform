# services/playback-service/app/settings.py
from common.config.settings import BaseServiceSettings

class Settings(BaseServiceSettings):
    service_name: str = "playback-service"

settings = Settings()
