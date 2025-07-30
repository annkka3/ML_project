from dataclasses import dataclass
from typing import List
from models.translation import Translation, TranslationHistory
from models.user import User
from services.wallet import Wallet

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
        model = self.SUPPORTED_MODELS[(source_lang, target_lang)]
        translator = pipeline('translation', model=model)
        return translator(origin_text)[0]["translation_text"]

@dataclass
class TranslationRequest:
    user: User
    input_text: str
    source_lang: str
    target_lang: str
    model: Model
    wallet: Wallet
    translation_history: TranslationHistory
    cost_per_translation: int = 1

    def validate_text(self) -> TextValidationResult:
        if not self.input_text.strip():
            return TextValidationResult(False, ["Empty input text."])
        return TextValidationResult(True, [])

    def process(self) -> str:
        validation = self.validate_text()
        if not validation.is_valid:
            raise ValueError(f"Не пройдена проверка текста: {validation.errors}")

        if not self.wallet.can_afford(self.user.id, self.cost_per_translation):
            raise ValueError("Недостаточный баланс")

        self.wallet.charge(self.user.id, self.cost_per_translation, type="Списание за перевод")
        output = self.model.translate(self.input_text, self.source_lang, self.target_lang)

        translation = Translation(
            user_id=self.user.id,
            input_text=self.input_text,
            output_text=output,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            cost=self.cost_per_translation
        )
        self.translation_history.add(translation)
        return output
