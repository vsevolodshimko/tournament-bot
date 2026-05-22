import json
import time
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Настройка логов — будет видно в консоли что происходит
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ========================
# НАСТРОЙКИ БОТА
# ========================

TOKEN = "8842476005:AAFpOY9lJ1TDUiV0i0vaFJ1HHS_WCfvw6_U"  # <-- Вставьте токен от BotFather

# Задержка между одинаковыми ответами (в секундах).
# Бот не будет отвечать на одно и то же чаще чем раз в X секунд.
COOLDOWN_SECONDS = 10

# ========================
# ЗАГРУЗКА ВОПРОСОВ И ОТВЕТОВ
# ========================

def load_qa():
    """Загружает вопросы и ответы из файла qa.json"""
    try:
        with open("qa.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("Файл qa.json не найден!")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка в формате qa.json: {e}")
        return []

# Словарь для хранения времени последнего ответа по каждому правилу
# Ключ: (chat_id, rule_id), Значение: timestamp
last_reply_time = {}

# ========================
# ОБРАБОТЧИК СООБЩЕНИЙ
# ========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Игнорируем сообщения без текста (фото, стикеры и т.д.)
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()  # Переводим в нижний регистр
    chat_id = update.message.chat_id

    qa_list = load_qa()  # Загружаем актуальные правила при каждом сообщении

    for i, rule in enumerate(qa_list):
        keywords = rule.get("keywords", [])
        answer = rule.get("answer", "")

        # Проверяем, есть ли хотя бы одно ключевое слово в сообщении
        matched = any(kw.lower() in text for kw in keywords)

        if matched:
            rule_key = (chat_id, i)
            now = time.time()
            last_time = last_reply_time.get(rule_key, 0)

            # Антиспам: проверяем кулдаун
            if now - last_time < COOLDOWN_SECONDS:
                logging.info(f"Кулдаун активен для правила #{i} в чате {chat_id}")
                return

            # Отправляем ответ
            await update.message.reply_text(answer)
            last_reply_time[rule_key] = now
            logging.info(f"Ответил на правило #{i} в чате {chat_id}")
            return  # Отвечаем только на первое совпавшее правило

# ========================
# ЗАПУСК БОТА
# ========================

if __name__ == "__main__":
    print("Бот запускается...")
    print(f"Кулдаун между ответами: {COOLDOWN_SECONDS} секунд")

    app = ApplicationBuilder().token(TOKEN).build()

    # Слушаем все текстовые сообщения (личные и групповые)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен! Нажмите Ctrl+C для остановки.")
    app.run_polling()
