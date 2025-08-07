from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from database.database import get_db
from deps import require_user_id
from models.wallet import Wallet
from models.transaction import Transaction

router = APIRouter(prefix="/wallet", tags=["Wallet"])

class BalanceOut(BaseModel):
    balance: int

class TopUpIn(BaseModel):
    amount: int = Field(..., gt=0)

@router.get("/", response_model=BalanceOut)
async def get_balance(db: AsyncSession = Depends(get_db), user_id: str = Depends(require_user_id)):
    wallet = (await db.execute(select(Wallet).where(Wallet.user_id == user_id))).scalar_one_or_none()
    if not wallet: raise HTTPException(status_code=404, detail="Счет не найден")
    return BalanceOut(balance=wallet.balance)

@router.post("/topup")
async def topup(data: TopUpIn, db: AsyncSession = Depends(get_db), user_id: str = Depends(require_user_id)):
    wallet = (await db.execute(select(Wallet).where(Wallet.user_id == user_id))).scalar_one_or_none()
    if not wallet: raise HTTPException(status_code=404, detail="Счет не найден")
    wallet.balance += data.amount
    db.add(Transaction(id=str(uuid.uuid4()), timestamp=datetime.utcnow(), user_id=user_id, amount=data.amount, type="Пополнение"))
    await db.commit()
    return {"message": "Баланс пополнен", "Новый баланс": wallet.balance}
