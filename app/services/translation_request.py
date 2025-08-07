from dataclasses import dataclass
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.transaction import Transaction
from models.translation import Translation
from models.user import User

import uuid




@dataclass
class TextValidationResult:
    is_valid: bool
    errors: List[str]


@dataclass
class Model:
    SUPPORTED_MODELS = {
        ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
        ("fr", "en"): "Helsinki-NLP/opus-mt-fr-en"
    }

    def translate(self, origin_text: str, source_lang: str, target_lang: str) -> str:
        from transformers import pipeline

        if (source_lang, target_lang) not in self.SUPPORTED_MODELS:
            raise ValueError("Модель перевода не поддерживается")

        model_name = self.SUPPORTED_MODELS[(source_lang, target_lang)]
        translator = pipeline("translation", model=model_name)
        return translator(origin_text)[0]["translation_text"]


@dataclass
class TranslationRequest:
    user: User
    input_text: str
    source_lang: str
    target_lang: str
    model: Model
    cost: int = 1

    async def process(self, db: AsyncSession) -> str:
        if self.user.wallet is None or self.user.wallet.balance < self.cost:
            raise ValueError("Недостаточно средств на балансе")

        output_text = self.model.translate(
            origin_text=self.input_text,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
        )

        self.user.wallet.balance -= self.cost
        db.add(self.user.wallet)

        translation = Translation(
            user_id=self.user.id,
            input_text=self.input_text,
            output_text=output_text,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            cost=self.cost,
        )
        db.add(translation)

        await db.commit()
        return output_text




async def process_translation_request(db: AsyncSession, user_id: str, data) -> dict:
    """
    Обёртка для роутера:
    - ищет пользователя
    - вызывает TranslationRequest.process(...)
    - пишет Transaction (Списание)
    - возвращает payload для ответа
    """
    # 1) достаём пользователя
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    # 2) собираем запрос и обрабатываем
    req = TranslationRequest(
        user=user,
        input_text=data.input_text if hasattr(data, "input_text") else data["input_text"],
        source_lang=data.source_lang if hasattr(data, "source_lang") else data["source_lang"],
        target_lang=data.target_lang if hasattr(data, "target_lang") else data["target_lang"],
        model=Model(),
        cost=1,
    )
    output_text = await req.process(db)

    # 3) логируем транзакцию (история списаний)
    tx = Transaction(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        user_id=user_id,
        amount=req.cost,
        type="Списание",
    )
    db.add(tx)
    await db.commit()

    # 4) отдаём ответ
    return {
        "output_text": output_text,
        "cost": req.cost,
        "timestamp": datetime.utcnow().isoformat(),
    }