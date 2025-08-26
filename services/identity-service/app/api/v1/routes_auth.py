# services/identity-service/app/api/v1/routes_auth.py
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
