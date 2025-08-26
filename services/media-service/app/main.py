# services/media-service/app/main.py
from fastapi import FastAPI
from common.middleware.correlation import CorrelationIdMiddleware
from common.logging.logger import setup_logging
from .settings import settings
from .api.v1.routes_health import router as health_router

# Routers extra se agregan aquí (p.ej. auth en identity)
try:
    from .api.v1.routes_auth import router as auth_router  # solo identity
except Exception:
    auth_router = None

def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    app = FastAPI(title=settings.service_name, version="1.0.0")
    app.add_middleware(CorrelationIdMiddleware)
    app.include_router(health_router, prefix="/v1")
    if auth_router:
        app.include_router(auth_router, prefix="/v1")
    return app

app = create_app()
