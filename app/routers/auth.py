from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from models.user import User
from schemas.auth import UserAuth, SignResponse
import uuid

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=SignResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: UserAuth, db: AsyncSession = Depends(get_db)):
    if (await db.execute(select(User).where(User.email == data.email))).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Пользователь уже существует")
    user = User.create_instance(id=str(uuid.uuid4()), email=data.email, password=data.password, initial_balance=10)
    db.add(user); await db.commit()
    return SignResponse(message="Пользователь зарегистрирован", user_id=user.id)

@router.post("/signin", response_model=SignResponse)
async def signin(data: UserAuth, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.email == data.email))
    user = res.scalar_one_or_none()
    if not user or not user.check_password(data.password):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    return SignResponse(message="User signed in", user_id=user.id)