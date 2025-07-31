from typing import Dict
from models.transaction import Transaction

class Wallet:
    def __init__(self, transactions_history):
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
