# repositories/translation_repository.py
from sqlalchemy.orm import Session
from models.translation import Translation

class TranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, translation: Translation):
        self.db.add(translation)
        self.db.commit()

    def get_by_user(self, user_id: str):
        return self.db.query(Translation).filter(Translation.user_id == user_id).all()

    def get_all(self):
        return self.db.query(Translation).all()
