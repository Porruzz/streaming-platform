# services/reco-service/app/settings.py
from common.config.settings import BaseServiceSettings

class Settings(BaseServiceSettings):
    service_name: str = "reco-service"

settings = Settings()
