from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import List

@dataclass
class Translation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""
    input_text: str = ""
    output_text: str = ""
    source_lang: str = ""
    target_lang: str = ""
    cost: int = 1

class TranslationHistory:
    def __init__(self):
        self._translations: List[Translation] = []

    def add(self, translation: Translation):
        self._translations.append(translation)

    def get_by_user(self, user_id: str) -> List[Translation]:
        return [t for t in self._translations if t.user_id == user_id]

    def get_all(self) -> List[Translation]:
        return self._translations
