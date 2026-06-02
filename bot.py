import json
import os
from threading import Thread
from flask import Flask

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = "8842476005:AAErC0IaMd1AlLG-LiXzQuXe5yq-dGcyPQ8"
CURRENT_SEASON = "25/26"

# =========================
# Flask
# =========================

app_web = Flask("")


@app_web.route("/")
def home():
    return "Bot is running"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)


Thread(target=run_web).start()


# =========================
# Ratings
# =========================

def load_ratings():
    with open("ratings.json", "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_score(player):
    return (
        player["gold"] * 4
        + player["silver"] * 2
        + player["bronze"]
    )


def format_rating(players):
    result = []

    sorted_players = sorted(
        players.items(),
        key=lambda x: (
            calculate_score(x[1]),
            x[1]["gold"],
            x[1]["silver"],
            x[1]["bronze"]
        ),
        reverse=True
    )

    for index, (username, data) in enumerate(sorted_players, start=1):

        total = (
            data["gold"]
            + data["silver"]
            + data["bronze"]
        )

        line = (
            f"{index}. {total} медалей "
            f"({data['gold']}🥇, "
            f"{data['silver']}🥈, "
            f"{data['bronze']}🥉)\n"
            f"{username}"
        )

        result.append(line)

    return "\n\n".join(result)


# =========================
# Commands
# =========================

async def seasons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📚 Доступные сезоны:\n\n"
        "🔴 25/26\n"
        "🔴 24/25\n"
        "🔴 23/24\n"
        "🔴 22/23"
    )

    await update.message.reply_text(text)


async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ratings = load_ratings()

    season = CURRENT_SEASON

    if context.args:
        season = context.args[0]

    if season not in ratings:
        await update.message.reply_text("❌ Сезон не найден")
        return

    text = f"🔴 СЕЗОН {season} 🔴\n\n"

    if "solo" in ratings[season]:
        text += "🏆 1x1\n\n"

        if ratings[season]["solo"]:
            text += format_rating(
                ratings[season]["solo"]
            )
        else:
            text += "Нет данных"

    if "duo" in ratings[season]:
        text += "\n\n🤝 2x2\n\n"

        if ratings[season]["duo"]:
            text += format_rating(
                ratings[season]["duo"]
            )
        else:
            text += "Нет данных"

    await update.message.reply_text(text)


# =========================
# Start bot
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    CommandHandler("seasons", seasons)
)

app.add_handler(
    CommandHandler("rating", rating)
)

print("Bot started")

app.add_handler(
    CommandHandler("gold1v1", gold1v1)
)

app.add_handler(
    CommandHandler("silver1v1", silver1v1)
)

app.add_handler(
    CommandHandler("bronze1v1", bronze1v1)
)

app.add_handler(
    CommandHandler("gold2v2", gold2v2)
)

app.add_handler(
    CommandHandler("silver2v2", silver2v2)
)

app.add_handler(
    CommandHandler("bronze2v2", bronze2v2)
)
app.run_polling()
def save_ratings(data):
    with open("ratings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


async def add_medal(update: Update,
                    context: ContextTypes.DEFAULT_TYPE,
                    mode,
                    medal):

    ADMIN_ID = 509816654

    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text(
            "Использование:\n/gold1v1 @username"
        )
        return

    username = context.args[0]

    if not username.startswith("@"):
        username = "@" + username

    ratings = load_ratings()

    season = ratings["25/26"]

    if username not in season[mode]:
        season[mode][username] = {
            "gold": 0,
            "silver": 0,
            "bronze": 0
        }

    season[mode][username][medal] += 1

    save_ratings(ratings)

    await update.message.reply_text(
        f"✅ {username} получил {medal}"
    )


async def gold1v1(update, context):
    await add_medal(update, context, "solo", "gold")


async def silver1v1(update, context):
    await add_medal(update, context, "solo", "silver")


async def bronze1v1(update, context):
    await add_medal(update, context, "solo", "bronze")


async def gold2v2(update, context):
    await add_medal(update, context, "duo", "gold")


async def silver2v2(update, context):
    await add_medal(update, context, "duo", "silver")


async def bronze2v2(update, context):
    await add_medal(update, context, "duo", "bronze")