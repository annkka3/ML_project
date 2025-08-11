# app/routers/wallet.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from deps_auth import get_current_user
from models.user import User
from models.wallet import Wallet
from models.transaction import Transaction
from schemas.classes import TopUpIn, BalanceOut
from schemas.auth import UserAuth, SignResponse

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("/", response_model=BalanceOut)
async def get_balance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить текущий баланс кошелька пользователя.
    Если кошелёк ещё не создан — считаем баланс равным 0.
    """
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet: Wallet | None = result.scalar_one_or_none()

    if wallet is None:
        return BalanceOut(balance=0)

    return BalanceOut(balance=wallet.balance)


@router.post("/topup", response_model=BalanceOut)
async def topup(
    data: TopUpIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Пополнение баланса. Создаёт кошелёк, если его ещё нет.
    Пишет запись в таблицу транзакций.
    """
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet: Wallet | None = result.scalar_one_or_none()

    if wallet is None:
        wallet = Wallet(user_id=current_user.id, balance=0)
        db.add(wallet)
        await db.flush()

    if data.amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be > 0")

    wallet.balance += data.amount

    txn = Transaction(
        user_id=current_user.id,
        amount=data.amount,
        type="topup",
    )
    db.add(txn)

    await db.commit()
    await db.refresh(wallet)

    return BalanceOut(balance=wallet.balance)
