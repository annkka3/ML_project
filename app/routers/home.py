from typing import Dict
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Home"])

@router.get("/", response_model=Dict[str, str])
async def index() -> Dict[str, str]:
    return {"message": "Добро пожаловать в сервис по переводу с английского на французский и наоборот"}

@router.get("/health", response_model=Dict[str, str])
async def health() -> Dict[str, str]:
    try:
        return {"status": "healthy"}
    except Exception:
        raise HTTPException(status_code=503, detail="Service unavailable")
