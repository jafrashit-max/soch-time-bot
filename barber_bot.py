import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8578169848:AAHYCONiST92PsFVhy_IRzmfdQpK1jHwQjs"

MASTERS = ["✂️ Алибек", "💈 Рустам", "🪒 Санжар"]
SERVICES = {"Стрижка": 80000, "Стрижка + борода": 80000, "Укладка": 80000}
TIMES = ["10:00", "11:00", "13:00", "14:00", "15:00", "17:00", "18:00", "19:00"]
DAYS = ["1 мая", "2 мая", "3 мая", "5 мая", "6 мая", "7 мая", "8 мая"]
bookings = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()
    keyboard = [[InlineKeyboardButton("📅 Записаться", callback_data="book")]]
    await update.message.reply_text(f"👋 Привет, {user.first_name}!\n\nДобро пожаловать в *Soch Time* — онлайн запись к мастеру.\n\nНикаких очередей — выбери мастера, услугу и удобное время! ✂️", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "book":
        keyboard = [[InlineKeyboardButton(m, callback_data=f"master_{m}")] for m in MASTERS]
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])
        await query.edit_message_text("👨‍💼 *Выберите мастера:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("master_"):
        master = data.replace("master_", "")
        context.user_data["master"] = master
        keyboard = [[InlineKeyboardButton(f"{s} — {p} сум", callback_data=f"service_{s}")] for s, p in SERVICES.items()]
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="book")])
        await query.edit_message_text(f"✅ Мастер: *{master}*\n\n💇 *Выберите услугу:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("service_"):
        service = data.replace("service_", "")
        context.user_data["service"] = service
        context.user_data["price"] = SERVICES[service]
        keyboard = [[InlineKeyboardButton(f"📅 {d}", callback_data=f"day_{d}")] for d in DAYS]
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"master_{context.user_data['master']}")])
        await query.edit_message_text(f"✅ Мастер: *{context.user_data['master']}*\n✅ Услуга: *{service}* — {SERVICES[service]} сум\n\n📅 *Выберите день:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("day_"):
        day = data.replace("day_", "")
        context.user_data["day"] = day
        keyboard = [[InlineKeyboardButton(f"🕐 {t}", callback_data=f"time_{t}") for t in TIMES[i:i+3]] for i in range(0, len(TIMES), 3)]
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"service_{context.user_data['service']}")])
        await query.edit_message_text(f"✅ Мастер: *{context.user_data['master']}*\n✅ Услуга: *{context.user_data['service']}*\n✅ День: *{day}*\n\n🕐 *Выберите время:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("time_"):
        time = data.replace("time_", "")
        context.user_data["time"] = time
        d = context.user_data
        keyboard = [[InlineKeyboardButton("✅ Подтвердить запись", callback_data="confirm")], [InlineKeyboardButton("⬅️ Назад", callback_data=f"day_{d['day']}")]]
        await query.edit_message_text(f"📋 *Ваша запись:*\n\n👨‍💼 Мастер: *{d['master']}*\n💇 Услуга: *{d['service']}*\n📅 Дата: *{d['day']}*\n🕐 Время: *{time}*\n💰 Цена: *{d['price']} сум*\n\nВсё верно?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "confirm":
        d = context.user_data
        user = update.effective_user
        booking_id = f"#{len(bookings)+1001}"
        bookings[booking_id] = {**d, "user": user.full_name}
        await query.edit_message_text(f"🎉 *Запись подтверждена!*\n\nНомер записи: *{booking_id}*\n\n👨‍💼 Мастер: *{d['master']}*\n💇 Услуга: *{d['service']}*\n📅 Дата: *{d['day']}*\n🕐 Время: *{d['time']}*\n💰 Оплата в салоне: *{d['price']} сум*\n\n⏰ Ждём вас в *Soch Time* ✂️", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📅 Записаться снова", callback_data="book")]]))
    elif data == "cancel":
        await query.edit_message_text("❌ Запись отменена.\n\nНапишите /start чтобы начать заново.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("✅ Бот запущен! @Soch_time01bot")
    app.run_polling()

if __name__ == "__main__":
    main()
