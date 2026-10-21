import os
import asyncio

from google import genai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Проверяем ключи
telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
gemini_key = os.environ.get("GEMINI_API_KEY")

if not telegram_token or not gemini_key:
    raise RuntimeError(
        "Не заданы ключи! Проверь переменные в CMD."
    )

client = genai.Client(api_key=gemini_key)


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "Привет! Я твой ИИ-помощник! 🤖\n"
        "Задавай любой вопрос."
    )


async def chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message or not update.message.text:
        return

    try:
        await update.message.chat.send_action("typing")

        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-3.5-flash-lite",
            contents=update.message.text,
        )

        answer = response.text or "Пустой ответ от ИИ."

        for i in range(0, len(answer), 4000):
            await update.message.reply_text(
                answer[i:i + 4000]
            )

    except Exception as error:
        print("Ошибка Gemini:", repr(error))

        await update.message.reply_text(
            "ИИ сейчас не ответил. Подробности "
            "ошибки смотри в окне CMD."
        )


def main():
    app = (
        Application.builder()
        .token(telegram_token)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat
        )
    )

    print("Бот запущен! Открой Telegram и напиши /start.")
    app.run_polling()


if __name__ == "__main__":
    main()