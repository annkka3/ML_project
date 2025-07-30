from fastapi import FastAPI
import uvicorn

from models.user import User
from models.admin import Admin
from models.transaction import TransactionHistory
from models.translation import TranslationHistory
from services.wallet import Wallet
from services.translation_request import TranslationRequest, Model

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API started"}

@app.get("/translate-test")
async def translate_test():
    user1 = User.create(id="1", email="user@example.com", password="secure123")
    user2 = User.create(id="2", email="user2@example.com", password="secure123")
    admin = Admin.create(id="0", email="admin@example.com", password="adminpass")

    transactions = TransactionHistory()
    wallet = Wallet(transactions_history=transactions)
    translations = TranslationHistory()

    admin.approve_bonus(user_id="1", amount=10, wallet=wallet)
    admin.approve_bonus(user_id="2", amount=5, wallet=wallet)

    model = Model()
    request1 = TranslationRequest(
        user=user1,
        input_text="Hello",
        source_lang="en",
        target_lang="fr",
        model=model,
        wallet=wallet,
        translation_history=translations,
    )
    request2 = TranslationRequest(
        user=user2,
        input_text="Bonjour",
        source_lang="fr",
        target_lang="en",
        model=model,
        wallet=wallet,
        translation_history=translations,
    )

    result1 = request1.process()
    result2 = request2.process()

    return {
        "result1": result1,
        "result2": result2,
        "balance_user1": wallet.get_balance(user1.id),
        "balance_user2": wallet.get_balance(user2.id),
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

