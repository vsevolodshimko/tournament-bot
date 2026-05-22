import json
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

TOKEN = "8842476005:AAFpOY9lJ1TDUiV0i0vaFJ1HHS_WCfvw6_U"

COOLDOWN_SECONDS = 10

last_trigger_time = 0


def load_qa():
    with open("qa.json", "r", encoding="utf-8") as f:
        return json.load(f)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_trigger_time

    if not update.message or not update.message.text:
        return

    current_time = time.time()

    if current_time - last_trigger_time < COOLDOWN_SECONDS:
        return

    text = update.message.text.lower()

    qa_data = load_qa()

    for item in qa_data:
        for keyword in item["keywords"]:
            if keyword.lower() in text:
                await update.message.reply_text(item["answer"])
                last_trigger_time = current_time
                return


print("Бот запускается...")
print(f"Кулдаун между ответами: {COOLDOWN_SECONDS} секунд")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

print("Бот запущен!")

app.run_polling()