import sqlite3
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler,ConversationHandler, ContextTypes, filters
from API import weather, currencies, get_random_image, fact, news
from api_tokens import TOKEN
DB_FILE = "users.db"

ASK_CITY, ASK_TIME = 0, 1  #это флаги для состояний



# ф-я для определения правильного формата времени
def time_ask(s):
    parts = s.split(":")
    if len(parts) != 2:
        return False
    left, right = parts
    if int(left) < 0 or int(left) > 24:
        return False
    if int(right) < 0 or int(right) > 59:
        return False
    return True

# ---------- БД ----------

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id  INTEGER PRIMARY KEY,
            username TEXT,
            city     TEXT,
            time     TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user(user_id, username, city, time_str):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO users (user_id, username, city, time) VALUES (?, ?, ?, ?)",
        (user_id, username, city, time_str)
    )
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT city, time FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row



# ---------- КЛАВА ----------

keyboard = [[KeyboardButton("погода"), KeyboardButton("валюты")], [KeyboardButton("мемчик"), KeyboardButton("факт")], [KeyboardButton("новость")], [KeyboardButton("настройки")]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ---------- Команды ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = get_user(user.id)

    if db_user:
        city, time_str = db_user
        await update.message.reply_text(f"Снова привет, {user.first_name or ''}!\nТы уже зарегистрирован.\nГород: {city}\nВремя отправки: {time_str}",reply_markup=reply_markup,)
        return ConversationHandler.END

    await update.message.reply_text("Привет! Напиши свой город:")
    return ASK_CITY




async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = (update.message.text or "").strip()
    if not city:
        await update.message.reply_text("Напиши город текстом:")
        return ASK_CITY

    context.user_data["city"] = city
    await update.message.reply_text(f"Отлично! Теперь напиши время в формате ЧЧ:ММ \n Например 19:30")
    return ASK_TIME

async def ask_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = (update.message.text or "").strip()
    print(time_str)

    if not time_ask(time_str):
        await update.message.reply_text(
            "Неверный формат. Введи время как ЧЧ:ММ, например 09:30:"
        )
        return ASK_TIME

    user = update.effective_user
    city = context.user_data.get("city", "")

    save_user(user.id, user.username, city, time_str)

    await update.message.reply_text(
        f"Сохранил:\nГород: {city}\nВремя: {time_str}",
        reply_markup=reply_markup,
    )

    context.user_data.clear()
    return ConversationHandler.END


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    # Достаём город и время из БД
    db_user = get_user(user.id)  # возвращает (city, time) или None

    if not db_user: #если ещё не зареган
        await update.message.reply_text("Сначала зарегистрируйся командой /start, чтобы я знал для какого города тебе нужна информация.")
        return

    city, time_str = db_user
    if text == "погода":
        await update.message.reply_text(weather(city))
    elif text == "валюты":
        await update.message.reply_text(currencies())
    elif text == "мемчик":
        await update.message.reply_text(get_random_image())
    elif text == "факт":
        await update.message.reply_text(fact())
    elif text == "новость":
        await update.message.reply_text(news(f"НОВОСТИ {city.upper()}"))
    elif text == "настройки":
        await update.message.reply_text(f"Ещё не сделал, но посмотреть какой город и время вы выбрали можно пвторно вызвав команду /start, я ещё нубчик(")
    else:
        await update.message.reply_text("Я тебя не понял. Нажми одну из кнопок или напиши /start.")


# ---------- ЗАПУСК ----------

def main():
    init_db()

    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_city)],
            ASK_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_time)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    app.run_polling()

if __name__ == "__main__":
    main()
