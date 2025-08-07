# init_db.py
import asyncio
from database import engine, Base, async_session
from models.user import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

async def init():
    async with engine.begin() as conn:
        print("Создание таблицы...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        try:
            print("Добавление пользователя...")

            admin = User.create_instance(
                email="admin@example.com",
                password="adminpass",
                is_admin=True,
                initial_balance=100
            )

            user = User.create_instance(
                email="user@example.com",
                password="userpass",
                initial_balance=50
            )

            session.add_all([admin, user])
            await session.commit()

            print("Пользователь создан.")

        except IntegrityError:
            print("Пользователь уже существует")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(init())
