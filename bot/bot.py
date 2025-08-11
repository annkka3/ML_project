import os
import logging
from typing import Tuple

import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("API_URL", "").strip()
API_USER_ID = os.getenv("API_USER_ID", "").strip()

# Нормализуем URL: нужен конечный слэш и сам путь /translate/
if API_URL:
    # если дали базу типа http://ml-api-2:8080 — добавим путь
    if "/translate" not in API_URL:
        API_URL = API_URL.rstrip("/") + "/translate/"
    else:
        API_URL = API_URL.rstrip("/") + "/"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _parse_message(text: str) -> Tuple[str, str, str]:
    """
    Ожидаем формат: "текст | source | target"
    Возвращаем: (text, source, target) или бросаем ValueError.
    """
    parts = [p.strip() for p in text.split("|")]
    if len(parts) != 3:
        raise ValueError("Неверный формат. Пример: Hello world | en | fr")
    msg, src, tgt = parts
    if not msg or not src or not tgt:
        raise ValueError("Пустые значения недопустимы. Пример: Hello world | en | fr")
    return msg, src.lower(), tgt.lower()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь мне текст для перевода в формате:\n\nтекст | en | fr")


async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверим обязательные переменные окружения
    if not API_URL:
        await update.message.reply_text("Не задан API_URL в переменных окружения.")
        return
    if not API_USER_ID:
        await update.message.reply_text("Не задан API_USER_ID в переменных окружения.")
        return

    try:
        text, source_lang, target_lang = _parse_message(update.message.text)
    except ValueError as e:
        await update.message.reply_text(str(e))
        return

    payload = {
        "input_text": text,
        "source_lang": source_lang,
        "target_lang": target_lang,
    }
    headers = {"X-User-Id": API_USER_ID, "Accept": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.post(API_URL, json=payload, headers=headers)

        if resp.status_code == 200:
            data = resp.json()
            translated = data.get("output_text") or "<нет перевода>"
            cost = data.get("cost")
            if cost is not None:
                await update.message.reply_text(f"Перевод: {translated}\nСписано: {cost}")
            else:
                await update.message.reply_text(f"Перевод: {translated}")
        else:
            # Попробуем прочитать причину
            detail = None
            try:
                j = resp.json()
                detail = j.get("detail")
            except Exception:
                try:
                    detail = resp.text
                except Exception:
                    detail = None
            msg = f"Ошибка API: {resp.status_code}"
            if detail:
                msg += f"\n{detail}"
            await update.message.reply_text(msg)

    except httpx.RequestError as e:
        logger.exception("HTTP error")
        await update.message.reply_text(f"Сеть/HTTP ошибка: {e}")
    except Exception as e:
        logger.exception("Unexpected error")
        await update.message.reply_text(f"Неожиданная ошибка: {e}")


def main():
    if not TOKEN:
        raise RuntimeError("Не задан TELEGRAM_TOKEN в переменных окружения.")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_text))
    app.run_polling()


if __name__ == "__main__":
    main()
