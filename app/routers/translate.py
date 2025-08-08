
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from database.database import get_db
from deps import require_user_id
from services.translation_request import process_translation_request

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
    try:
        return await process_translation_request(db, user_id, data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))