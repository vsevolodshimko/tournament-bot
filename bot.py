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
ADMIN_ID = 509816654
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


Thread(target=run_web, daemon=True).start()


# =========================
# Ratings
# =========================

def load_ratings():
    with open("ratings.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_ratings(data):
    with open("ratings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def score(data):
    return data["gold"] * 4 + data["silver"] * 2 + data["bronze"]


def format_rating(players):
    sorted_players = sorted(
        players.items(),
        key=lambda x: (
            score(x[1]),
            x[1]["gold"],
            x[1]["silver"],
            x[1]["bronze"]
        ),
        reverse=True
    )

    text = ""

    for pos, (username, medals) in enumerate(sorted_players, start=1):

        total = (
            medals["gold"]
            + medals["silver"]
            + medals["bronze"]
        )

        if pos == 1:
            place = "🥇"
        elif pos == 2:
            place = "🥈"
        elif pos == 3:
            place = "🥉"
        else:
            place = f"{pos}."

        text += (
            f"{place} {total} медалей "
            f"({medals['gold']}🥇, "
            f"{medals['silver']}🥈, "
            f"{medals['bronze']}🥉)\n"
            f"{username}\n\n"
        )

    return text


# =========================
# Commands
# =========================

async def seasons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Сезоны:\n\n"
        "/rating 25/26\n"
        "/rating 24/25\n"
        "/rating 23/24\n"
        "/rating 22/23"
    )


async def rating(update: Update, context: ContextTypes.DEFAULT_TYPE):

    ratings = load_ratings()

    season = CURRENT_SEASON

    if context.args:
        season = context.args[0]

    if season not in ratings:
        await update.message.reply_text("❌ Сезон не найден")
        return

    text = f"🔴 {season} СЕЗОН 🔴\n\n"

    if "solo" in ratings[season]:

        text += "🏆 1×1\n\n"

        if ratings[season]["solo"]:
            text += format_rating(
                ratings[season]["solo"]
            )

    if "duo" in ratings[season]:

        text += "\n🤝 2×2\n\n"

        if ratings[season]["duo"]:
            text += format_rating(
                ratings[season]["duo"]
            )

    await update.message.reply_text(text)


# =========================
# выдача медалей
# =========================

async def add_medal(update, context, mode, medal):

    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 1:

        await update.message.reply_text(
            "Пример:\n/gold1v1 @nickname"
        )
        return

    username = context.args[0]

    if not username.startswith("@"):
        username = "@" + username

    ratings = load_ratings()

    season = ratings[CURRENT_SEASON]

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


# =========================
# Start
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("seasons", seasons))
app.add_handler(CommandHandler("rating", rating))

app.add_handler(CommandHandler("gold1v1", gold1v1))
app.add_handler(CommandHandler("silver1v1", silver1v1))
app.add_handler(CommandHandler("bronze1v1", bronze1v1))

app.add_handler(CommandHandler("gold2v2", gold2v2))
app.add_handler(CommandHandler("silver2v2", silver2v2))
app.add_handler(CommandHandler("bronze2v2", bronze2v2))

print("BOT STARTED")

app.run_polling()