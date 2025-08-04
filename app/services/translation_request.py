from dataclasses import dataclass
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from models.translation import Translation
from models.user import User


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
