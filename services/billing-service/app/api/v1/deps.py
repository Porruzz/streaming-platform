# app/api/v1/deps.py
# Aquí irán dependencias comunes: auth, paginación, etc.
from typing import Optional
from fastapi import Depends, HTTPException, status
from common.auth.jwt import decode_jwt_rs256
from ..settings import settings

def get_current_user(token: Optional[str] = None):
    # Stub: en dev podrías inyectar token por header Authorization "Bearer ..."
    # Implementación real se hará después (ver identity-service).
    return {"sub": "demo-user", "plan": "free"}
