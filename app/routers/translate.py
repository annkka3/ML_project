
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from deps_auth import get_current_user
from models.user import User
from schemas.classes import TranslationIn, TranslationOut
from services.translation_request import process_translation_request

router = APIRouter(prefix="/translate", tags=["Translate"])

@router.post("/", response_model=TranslationOut)
async def translate_endpoint(
    data: TranslationIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await process_translation_request(db, current_user.id, data)