
from sqlalchemy.orm import Session
from models.transaction import Transaction

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, transaction: Transaction):
        self.db.add(transaction)
        self.db.commit()

    def get_by_user(self, user_id: str):
        return self.db.query(Transaction).filter(Transaction.user_id == user_id).all()

    def get_all(self):
        return self.db.query(Transaction).all()
