from dataclasses import dataclass
from models.user import User
from models.transaction import Transaction
from models.translation import Translation

@dataclass
class Admin(User):
    def approve_bonus(self, user_id: str, amount: int, wallet):
        wallet.add_credits(user_id, amount, type="Бонус")

    def view_transactions(self, transaction_history, user=None):
        if user:
            return transaction_history.get_by_user(user_id=user)
        return transaction_history.get_all()

    def view_translations(self, translation_history, user=None):
        if user:
            return translation_history.get_by_user(user_id=user)
        return translation_history.get_all()
