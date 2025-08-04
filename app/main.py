from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from database.database import get_db
from models.user import User
from services.translation_request import TranslationRequest, Model
from services.admin_actions import AdminActions
from database.database import Base, engine

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

    # Бонус от админа
    await AdminActions.approve_bonus(db, user_id=user1.id, amount=10)
    await AdminActions.approve_bonus(db, user_id=user2.id, amount=5)

    # Загрузка пользователей с кошельками из БД (после коммита)
    user1 = await db.get(User, user1.id)
    user2 = await db.get(User, user2.id)

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

    # Обновлённые балансы
    await db.refresh(user1.wallet)
    await db.refresh(user2.wallet)

    return {
        "result1": result1,
        "result2": result2,
        "balance_user1": user1.wallet.balance,
        "balance_user2": user2.wallet.balance,
    }
