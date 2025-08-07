from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.database import Base
from utils.hasher import PasswordHasher
from utils.validator import UserValidator
from models.wallet import Wallet


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    _password_hash: Mapped[str] = mapped_column("password_hash", String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Связи
    wallet: Mapped["Wallet"] = relationship(
        "Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )
    translations: Mapped[list["Translation"]] = relationship(
        "Translation", back_populates="user", cascade="all, delete-orphan"
    )

    @classmethod
    def create_instance(cls, id: str, email: str, password: str, is_admin: bool = False, initial_balance: int = 0):
        UserValidator.validate_email(email)
        UserValidator.validate_password(password)

        return cls(
            id=id,
            email=email,
            _password_hash=PasswordHasher.hash(password),
            is_admin=is_admin,
            wallet=Wallet(balance=initial_balance)
        )

    def check_password(self, password: str) -> bool:
        return PasswordHasher.check(password, self._password_hash)
