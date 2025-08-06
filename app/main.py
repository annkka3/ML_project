
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from datetime import datetime

from sqlalchemy import select, delete

from database.database import get_db, Base, engine
from models.user import User
from models.wallet import Wallet
from models.translation import Translation
from models.transaction import Transaction
from services.translation_request import TranslationRequest, Model
from services.admin_actions import AdminActions


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "API started"}


@app.get("/translate-test")
async def translate_test(db: AsyncSession = Depends(get_db)):
    # Очистка всех данных
    await db.execute(delete(Transaction))
    await db.execute(delete(Translation))
    await db.execute(delete(Wallet))
    await db.execute(delete(User))
    await db.commit()

    # Создание пользователей
    user1 = User.create_instance(
        id=str(uuid4()), email="user@example.com", password="secure123", is_admin=False, initial_balance=0
    )
    user2 = User.create_instance(
        id=str(uuid4()), email="user2@example.com", password="secure123", is_admin=False, initial_balance=0
    )
    admin = User.create_instance(
        id=str(uuid4()), email="admin@example.com", password="adminpass", is_admin=True, initial_balance=0
    )

    db.add_all([user1, user2, admin])
    await db.commit()

    # Бонусы
    await AdminActions.approve_bonus(db, user_id=user1.id, amount=10)
    await AdminActions.approve_bonus(db, user_id=user2.id, amount=5)

    await db.refresh(user1.wallet)
    await db.refresh(user2.wallet)

    # Переводы
    model = Model()
    request1 = TranslationRequest(
        user=user1,
        input_text="Hello",
        source_lang="en",
        target_lang="fr",
        model=model,
    )
    request2 = TranslationRequest(
        user=user2,
        input_text="Bonjour",
        source_lang="fr",
        target_lang="en",
        model=model,
    )

    result1 = await request1.process(db)
    result2 = await request2.process(db)

    return {
        "result1": result1,
        "result2": result2,
        "balance_user1": user1.wallet.balance,
        "balance_user2": user2.wallet.balance,
    }


@app.get("/test-translations")
async def test_translations(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Translation))

    # Создание пользователя
    user = User.create_instance(
        id=str(uuid4()), email="test@translations.com", password="test12345678", is_admin=False, initial_balance=0
    )
    db.add(user)
    await db.commit()

    # Добавление перевода
    translation = Translation(
        id=str(uuid4()),
        user_id=user.id,
        input_text="Test translation input",
        output_text="Test translation output",
        source_lang="en",
        target_lang="de",
        cost=3,
        timestamp=datetime.utcnow()
    )
    db.add(translation)
    await db.commit()

    result = await db.execute(select(Translation))
    translations = result.scalars().all()

    return {
        "translations": [t.__dict__ for t in translations]
    }


@app.get("/test-transactions")
async def test_transactions(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Transaction))

    # Создание пользователя
    user = User.create_instance(
        id=str(uuid4()), email="test@transactions.com", password="test12345678", is_admin=False, initial_balance=0
    )
    db.add(user)
    await db.commit()

    # Добавление транзакции
    transaction = Transaction(
        id=str(uuid4()),
        user_id=user.id,
        amount=7,
        type="BONUS",
        timestamp=datetime.utcnow()
    )
    db.add(transaction)
    await db.commit()

    result = await db.execute(select(Transaction))
    transactions = result.scalars().all()

    return {
        "transactions": [t.__dict__ for t in transactions]
    }
