# bootstrap_scaffold.py
from pathlib import Path

ROOT = Path(".").resolve()

services = [
    ("identity-service", 8010),
    ("catalog-service", 8011),
    ("media-service", 8012),
    ("playback-service", 8013),
    ("billing-service", 8014),
    ("analytics-service", 8015),
    ("reco-service", 8016),
]

gitignore = r"""
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so
*.egg-info/
dist/
build/
.mypy_cache/
.pytest_cache/
.coverage
htmlcov/
# venv
.venv/
# IDE
.vscode/
.idea/
# OS
.DS_Store
Thumbs.db
"""

# ---------- COMMON LIB ----------
common_init = """# libs/common-py/common/__init__.py
__all__ = ["config", "auth", "logging", "middleware", "http", "events"]
"""

common_config = """# libs/common-py/common/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseServiceSettings(BaseSettings):
    service_name: str = "service"
    env: str = "dev"
    log_level: str = "INFO"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
"""

common_jwt = """# libs/common-py/common/auth/jwt.py
from typing import Optional
import jwt
from jwt import PyJWKClient

class JWTError(Exception):
    pass

def decode_jwt_rs256(token: str, jwks_url: Optional[str] = None, public_key_pem: Optional[str] = None, audience: Optional[str] = None) -> dict:
    try:
        if public_key_pem:
            return jwt.decode(token, public_key_pem, algorithms=["RS256"], audience=audience)
        if not jwks_url:
            raise JWTError("Provide jwks_url or public_key_pem")
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        return jwt.decode(token, signing_key, algorithms=["RS256"], audience=audience)
    except Exception as e:
        raise JWTError(str(e))
"""

common_logging = """# libs/common-py/common/logging/logger.py
import logging, structlog

def setup_logging(level: str = "INFO"):
    logging.basicConfig(level=level)
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)))
"""

common_mw_correlation = """# libs/common-py/common/middleware/correlation.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

CORRELATION_HEADER = "X-Correlation-ID"

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        cid = request.headers.get(CORRELATION_HEADER) or str(uuid.uuid4())
        response = await call_next(request)
        response.headers[CORRELATION_HEADER] = cid
        return response
"""

common_http = """# libs/common-py/common/http/client.py
import httpx
from typing import Callable, Optional

def client(timeout=10.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout)
"""

common_events = """# libs/common-py/common/events/kafka.py
# Stubs de productor/consumidor; se implementarán luego.
class EventPublisher:
    async def publish(self, topic: str, payload: dict): ...
"""

common_pyproject = """# libs/common-py/pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "common-py"
version = "0.1.0"
description = "Librería compartida (settings, auth, logging, middleware, http, eventos)"
requires-python = ">=3.12"
dependencies = [
  "pydantic>=2",
  "pydantic-settings>=2",
  "structlog>=24",
  "PyJWT[crypto]>=2.8",
  "httpx>=0.27",
]
"""

# ---------- SERVICE TEMPLATES ----------
def service_pyproject(name: str) -> str:
    return f"""# services/{name}/pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.111",
  "uvicorn[standard]>=0.30",
  "pydantic>=2",
  "pydantic-settings>=2",
  "structlog>=24",
  "httpx>=0.27",
  "sqlalchemy>=2",
  "alembic>=1.13",
  "asyncpg>=0.29",
  "redis>=5",
  "aiokafka>=0.10",
  "common-py @ file://{(ROOT / 'libs' / 'common-py').resolve().as_posix()}",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio", "ruff", "black", "mypy", "types-PyYAML"]
"""

def service_dockerfile() -> str:
    return """# services/*/Dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml /app/
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .
COPY app /app/app
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
"""

service_settings_tpl = """# services/{name}/app/settings.py
from common.config.settings import BaseServiceSettings

class Settings(BaseServiceSettings):
    service_name: str = "{name}"

settings = Settings()
"""

service_main_tpl = """# services/{name}/app/main.py
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
"""

routes_health = """# app/api/v1/routes_health.py
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health", summary="Liveness/Readiness")
async def health():
    return {"status": "ok"}
"""

deps_tpl = """# app/api/v1/deps.py
# Aquí irán dependencias comunes: auth, paginación, etc.
from typing import Optional
from fastapi import Depends, HTTPException, status
from common.auth.jwt import decode_jwt_rs256
from ..settings import settings

def get_current_user(token: Optional[str] = None):
    # Stub: en dev podrías inyectar token por header Authorization "Bearer ..."
    # Implementación real se hará después (ver identity-service).
    return {"sub": "demo-user", "plan": "free"}
"""

# Domain / Application / Infra placeholders
domain_entities = """# app/domain/entities.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Entity:
    id: str
"""

domain_values = """# app/domain/value_objects.py
# Aquí defines Value Objects (Email, Plan, etc.)
"""

domain_errors = """# app/domain/errors.py
class DomainError(Exception): ...
"""

domain_ports = """# app/domain/ports/__init__.py
# Define interfaces (puertos) como UserRepository, EventPublisher, etc.
"""

application_uc = """# app/application/use_cases/__init__.py
# Casos de uso: coordinan puertos/repos y reglas.
"""

infra_models = """# app/infra/db/models.py
# SQLAlchemy ORM models (se definen luego).
"""

infra_repos = """# app/infra/db/repositories.py
# Implementaciones de repositorios (puertos) contra SQLAlchemy.
"""

infra_migrations_readme = """# app/infra/db/alembic/README
# Reservado para migraciones Alembic, se añade config más adelante.
"""

infra_messaging = """# app/infra/messaging/kafka_publisher.py
# Publisher de eventos (usará aiokafka + Outbox más adelante).
"""

schemas_init = """# app/schemas/__init__.py
# Pydantic DTOs (entrada/salida) - no mezclar con Entidades de Dominio.
"""

tests_health = """# tests/unit/test_health.py
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    c = TestClient(app)
    r = c.get("/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
"""

# Identity-only routes
routes_auth_identity = """# services/identity-service/app/api/v1/routes_auth.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterIn(BaseModel):
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

@router.post("/register", summary="Registro (stub)")
async def register(payload: RegisterIn):
    # TODO: guardar usuario, hash Argon2, emitir eventos…
    return {"ok": True, "email": payload.email}

@router.post("/login", summary="Login (stub)")
async def login(payload: LoginIn):
    # TODO: validar, emitir JWT RS256
    return {"access_token": "stub.jwt.token", "token_type": "bearer"}
"""

def write(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def create_common():
    base = ROOT / "libs" / "common-py"
    write(ROOT / ".gitignore", gitignore.strip() + "\n")
    write(base / "common" / "__init__.py", common_init)
    write(base / "common" / "config" / "settings.py", common_config)
    write(base / "common" / "auth" / "jwt.py", common_jwt)
    write(base / "common" / "logging" / "logger.py", common_logging)
    write(base / "common" / "middleware" / "correlation.py", common_mw_correlation)
    write(base / "common" / "http" / "client.py", common_http)
    write(base / "common" / "events" / "kafka.py", common_events)
    write(base / "pyproject.toml", common_pyproject.strip() + "\n")
    write(base / "README.md", "# common-py\nUtilidades compartidas.\n")

def create_service(name: str, port: int):
    base = ROOT / "services" / name / "app"
    # API
    write(base / "api" / "v1" / "routes_health.py", routes_health)
    write(base / "api" / "v1" / "deps.py", deps_tpl)
    # Application / Domain / Infra / Schemas
    write(base / "application" / "use_cases" / "__init__.py", application_uc)
    write(base / "domain" / "entities.py", domain_entities)
    write(base / "domain" / "value_objects.py", domain_values)
    write(base / "domain" / "errors.py", domain_errors)
    write(base / "domain" / "ports" / "__init__.py", domain_ports)
    write(base / "infra" / "db" / "models.py", infra_models)
    write(base / "infra" / "db" / "repositories.py", infra_repos)
    write(base / "infra" / "db" / "alembic" / "README", infra_migrations_readme)
    write(base / "infra" / "messaging" / "kafka_publisher.py", infra_messaging)
    write(base / "schemas" / "__init__.py", schemas_init)
    # Settings & main
    write(base / "settings.py", service_settings_tpl.replace("{name}", name))
    write(base / "main.py", service_main_tpl.replace("{name}", name))
    # Tests, Docker, pyproject
    write(ROOT / "services" / name / "tests" / "unit" / "test_health.py", tests_health)
    write(ROOT / "services" / name / "Dockerfile", service_dockerfile())
    write(ROOT / "services" / name / "pyproject.toml", service_pyproject(name))

    # identity: rutas extra
    if name == "identity-service":
        write(ROOT / "services" / name / "app" / "api" / "v1" / "routes_auth.py", routes_auth_identity)

def main():
    create_common()
    for name, port in services:
        create_service(name, port)
    # docs, docker, gateway (placeholders mínimos)
    (ROOT / "docs").mkdir(parents=True, exist_ok=True)
    (ROOT / "docker").mkdir(parents=True, exist_ok=True)
    (ROOT / "gateway").mkdir(parents=True, exist_ok=True)
    (ROOT / "infra" / "k8s").mkdir(parents=True, exist_ok=True)
    (ROOT / "scripts").mkdir(parents=True, exist_ok=True)
    (ROOT / "workers" / "transcode-worker").mkdir(parents=True, exist_ok=True)
    (ROOT / "README.md").write_text("# Streaming Platform (backend-first)\n", encoding="utf-8")
    print("✅ Estructura generada.")

if __name__ == "__main__":
    main()
