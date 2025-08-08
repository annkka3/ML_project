import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне текст для перевода в формате:\n\nтекст | en | fr")

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Ожидаем формат: "текст | source | target"
        parts = update.message.text.split("|")
        if len(parts) != 3:
            await update.message.reply_text("Неверный формат. Пример: Hello world | en | fr")
            return

        text, source_lang, target_lang = [p.strip() for p in parts]

        response = requests.post(API_URL, json={
            "input_text": text,
            "source_lang": source_lang,
            "target_lang": target_lang
        })

        if response.status_code == 200:
            data = response.json()
            translated = data.get("output_text", "<нет перевода>")
            await update.message.reply_text(f"Перевод: {translated}")
        else:
            await update.message.reply_text(f"Ошибка API: {response.status_code}")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Произошла ошибка при переводе.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))

    app.run_polling()

if __name__ == "__main__":
    main()
