# app/api/v1/routes_health.py
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health", summary="Liveness/Readiness")
async def health():
    return {"status": "ok"}
