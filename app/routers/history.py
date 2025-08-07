from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from deps import require_user_id
from models.translation import Translation
from models.transaction import Transaction



router = APIRouter(prefix="/history", tags=["History"])

class TranslationItem(BaseModel):
    id: str
    timestamp: datetime
    input_text: str
    output_text: str
    source_lang: str
    target_lang: str
    cost: int
    class Config: from_attributes = True

@router.get("/translations", response_model=List[TranslationItem])
async def list_translations(db: AsyncSession = Depends(get_db), user_id: str = Depends(require_user_id)):
    q = await db.execute(select(Translation).where(Translation.user_id == user_id).order_by(Translation.timestamp.desc()))
    return q.scalars().all()

class TransactionItem(BaseModel):
    id: str
    timestamp: datetime
    amount: int
    type: str
    class Config:
        from_attributes = True

@router.get("/transactions", response_model=List[TransactionItem])
async def list_transactions(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_user_id),
    tx_type: Optional[str] = Query(default=None, description="Фильтр по типу: 'Пополнение' или 'Списание'"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = select(Transaction).where(Transaction.user_id == user_id)
    if tx_type:
        stmt = stmt.where(Transaction.type == tx_type)
    stmt = stmt.order_by(Transaction.timestamp.desc()).limit(limit).offset(offset)

    res = await db.execute(stmt)
    return res.scalars().all()
