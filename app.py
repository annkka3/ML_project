from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
from transformers import pipeline
import uuid
import re
import bcrypt


class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def check(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())


class UserValidator:
    @staticmethod
    def validate_email(email: str):
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not pattern.match(email):
            raise ValueError("Неверный формат email")

    @staticmethod
    def validate_password(password: str):
        if len(password) < 8:
            raise ValueError("Пароль должен быть не меньше 8 символов")


@dataclass
class Transaction:

    """
    Класс для представления транзакции в системе.
        Attributes:
        id (str): Идентификатор операции
        timestamp: (datetime): Время операции
        user_id (str): Уникальный идентификатор пользователя
        amount (int): Стоимость операции
        type (str): Тип операции "Пополнение", "Списание", "Бонус"
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""
    amount: int = 0
    type: str = "Списание"

class TransactionHistory:

    """
    Класс для представления истории транзакций.

    Attributes:
    _transactions (List): Журнал транзакций
    """

    def __init__(self):
        self._transactions: List[Transaction] = []

    def add(self, transaction: Transaction):
        self._transactions.append(transaction)

    def get_by_user(self, user_id: str) -> List[Transaction]:
        return [t for t in self._transactions if t.user_id == user_id]

    def get_all(self) -> List[Transaction]:
        return self._transactions


@dataclass
class Translation:

    """
    Класс для представления перевода в системе.

    Attributes:
    id (str): Идентификатор операции
    timestamp (datetime): Время опреции
    input_text (str): Оригинальный текст
    output_text (str): Переведенный текст
    source_lang (str): Язык оригинала
    target_lang (str): Язык для перевода
    cost (int): Стоимость перевода
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""
    input_text: str = ""
    output_text: str = ""
    source_lang: str = ""
    target_lang: str = ""
    cost: int = 1


class TranslationHistory:

    """
    Класс для представления истории переводов.

    Attributes:
    _translations (List): Журнал переводов
    """

    def __init__(self):
        self._translations: List[Translation] = []

    def add(self, translation: Translation):
        self._translations.append(translation)

    def get_by_user(self, user_id: str) -> List[Translation]:
        return [t for t in self._translations if t.user_id == user_id]

    def get_all(self) -> List[Translation]:
        return self._translations

@dataclass
class User:
    """
    Класс для представления пользователя в системе.
    Attributes:
    id (int): Уникальный идентификатор пользователя
    email (str): Email пользователя
    _password_hash (str): Пароль пользователя будет храниться в виде хэша
    """
    id: str
    email: str
    _password_hash: str

    @classmethod
    def create(cls, id: str, email: str, password: str) -> 'User':
        UserValidator.validate_email(email)
        UserValidator.validate_password(password)
        return cls(id=id, email=email, _password_hash=PasswordHasher.hash(password))

    def check_password(self, password: str) -> bool:
        return PasswordHasher.check(password, self._password_hash)


@dataclass
class Admin(User):

    """
    Класс администратора системы.

    """

    def approve_bonus(self, user_id: str, amount: int, wallet):
        wallet.add_credits(user_id, amount, type="Бонус")

    def view_transactions(self, transaction_history, user=None) -> List[Transaction]:
        if user:
            return transaction_history.get_by_user(user_id=user)
        return transaction_history.get_all()

    def view_translations(self, translation_history, user=None) -> List[Translation]:
        if user:
            return translation_history.get_by_user(user_id=user)
        return translation_history.get_all()


class Wallet:

    def __init__(self, transactions_history=TransactionHistory):
        self._balances: Dict[str, int] = {}
        self._transactions = transactions_history

    def get_balance(self, user_id: str) -> int:
        return self._balances.get(user_id, 0)

    def can_afford(self, user_id: str, amount: int) -> bool:
        return self.get_balance(user_id) >= amount

    def add_credits(self, user_id: str, amount: int, type="Пополнение"):
        self._balances[user_id] = self.get_balance(user_id) + amount
        self._transactions.add(Transaction(user_id=user_id, amount=amount, type=type))

    def charge(self, user_id: str, amount: int, type="Списание"):
        if not self.can_afford(user_id, amount):
            raise ValueError("Недостаточно средств")
        self._balances[user_id] -= amount
        self._transactions.add(Transaction(user_id=user_id, amount=-amount, type=type))


@dataclass
class Model:
    """
    Класс для модели перевода.

    """
    SUPPERTED_MODELS: Dict[tuple, str] = field(
        default_factory=lambda: {
        ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
        ("fr", "en"): "Helsinki-NLP/opus-mt-fr-en"})

    def translate(self, origin_text: str, source_lang: str, target_lang: str) -> str:
        if (source_lang, target_lang) not in self.SUPPERTED_MODELS:
            raise ValueError(f"Перевод с {origin_text} на {source_lang} не поддерживается")
        model = self.SUPPERTED_MODELS[(source_lang, target_lang)]
        translator = pipeline('translation', model=model)
        return translator(origin_text, src_lang=source_lang, tgt_lang=target_lang)[0]["translation_text"]


@dataclass
class TextValidationResult:
    is_valid: bool
    errors: List[str]


@dataclass
class TranslationRequest:
    """
    Класс для выполнения запроса по переводу.

    Attributes:
    user (User): Идентификатор пользователя
    input_text (str): Оригинальный текст
    source_lang (str): Язык оригинала
    target_lang (str): Язык для перевода
    model (Model): Модель для перевода
    wallet (Wallet): Кошелек пользователя
    transaction_history (TransactionHistory): История транзакций
    translation_history (TranslationHistory): История переводов
    cost_per_traslation (int): Стоимость перевода

    """

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

        user_id = self.user.id
        if not self.wallet.can_afford(user_id, self.cost_per_translation):
            raise ValueError("Недостаточный баланс")

        self.wallet.charge(user_id, self.cost_per_translation, type="Списание за перевод")
        output = self.model.translate(self.input_text, self.source_lang, self.target_lang)

        translation = Translation(
            user_id=user_id,
            input_text=self.input_text,
            output_text=output,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            cost=self.cost_per_translation
        )
        self.translation_history.add(translation)
        return output


# Проверка работы
user1 = User.create(id="1", email="user@example.com", password="secure123")
user2 = User.create(id="2", email="user2@example.com", password="secure123")
admin = Admin.create(id="0", email="admin@example.com", password="adminpass")
transactions=TransactionHistory()
wallet = Wallet(transactions_history=transactions)
translations = TranslationHistory()

# Админ начисляет бонус
admin.approve_bonus(user_id="1", amount=10, wallet=wallet)
admin.approve_bonus(user_id="2", amount=5, wallet=wallet)

# Запрос на перевод
model = Model()
request1 = TranslationRequest(
    user=user1,
    input_text="Hello. How are you?",
    source_lang="en",
    target_lang="fr",
    model=model,
    wallet=wallet,
    translation_history=translations
)

request2 = TranslationRequest(
    user=user2,
    input_text="Bonjour",
    source_lang="fr",
    target_lang="en",
    model=model,
    wallet=wallet,
    translation_history=translations
)

result1 = request1.process()
result2 = request2.process()

# Результаты
print("Результат перевода 1:", result1)
print("Результат перевода 2:", result2)

print(f"Баланс пользователя {user1.id}: {wallet.get_balance(user1.id)} монет")
print(f"Баланс пользователя {user2.id}: {wallet.get_balance(user2.id)} монет")

print("Транзакции пользователя 1:", admin.view_transactions(transaction_history=transactions, user='1'))
print("Транзакции всех пользователей:", admin.view_transactions(transaction_history=transactions))

print("История перевода пользователя 1:", admin.view_translations(translation_history=translations, user='1'))
print("История переводов всех пользователей:", admin.view_translations(translation_history=translations))
