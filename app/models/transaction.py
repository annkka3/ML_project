from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import List

@dataclass
class Transaction:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: str = ""
    amount: int = 0
    type: str = "Списание"

class TransactionHistory:
    def __init__(self):
        self._transactions: List[Transaction] = []

    def add(self, transaction: Transaction):
        self._transactions.append(transaction)

    def get_by_user(self, user_id: str) -> List[Transaction]:
        return [t for t in self._transactions if t.user_id == user_id]

    def get_all(self) -> List[Transaction]:
        return self._transactions
