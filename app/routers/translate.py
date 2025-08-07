
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from deps import require_user_id

from services.translation_request import process_translation_request  # <-- этого теперь хватит

from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/translate", tags=["Translate"])

class TranslationIn(BaseModel):
    input_text: str
    source_lang: str
    target_lang: str

@router.post("/")
async def translate_endpoint(
    data: TranslationIn,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_user_id),
):
    return await process_translation_request(db, user_id, data)
