import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8578169848:AAF3r_7tienkbAb4afBe9W63wz2wGxDtkCo"

# ⚠️ Замени на свой Telegram ID (узнать можно у @userinfobot)
ADMIN_ID = 1314440253

MASTERS = {
    "alibekk": {"name": "Алибек", "emoji": "✂️", "spec": "Барбер • стаж 5 лет"},
    "rustam":  {"name": "Рустам",  "emoji": "💈", "spec": "Стилист • стаж 7 лет"},
    "sanzhar": {"name": "Санжар", "emoji": "🪒", "spec": "Барбер • стаж 3 года"},
}

SERVICES = {
    "haircut":       {"name": "Стрижка",         "price": 80000, "time": "40 мин"},
    "haircut_beard": {"name": "Стрижка + борода", "price": 80000, "time": "60 мин"},
    "styling":       {"name": "Укладка",          "price": 80000, "time": "30 мин"},
    "beard":         {"name": "Борода",            "price": 80000, "time": "30 мин"},
}

TIMES = ["09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00"]
DAYS  = ["Сегодня","Завтра","2 мая","3 мая","5 мая","6 мая","7 мая","8 мая","9 мая","10 мая"]

bookings = {}

def booking_counter():
    return len(bookings) + 1001

def fmt_bookings_for_admin():
    if not bookings:
        return "📭 Записей пока нет."
    lines = []
    for bid, b in sorted(bookings.items()):
        lines.append(
            f"┌ *Запись {bid}*\n"
            f"│ 👤 {b['client_name']} (@{b.get('username') or '—'})\n"
            f"│ 👨‍💼 {b['master']}\n"
            f"│ 💇 {b['service']}\n"
            f"│ 📅 {b['day']} в {b['time']}\n"
            f"│ 💰 {b['price']:,} сум\n"
            f"└ 🕐 {b['created_at']}\n"
        )
    return "\n".join(lines)
return "\n".join(lines)



async def my_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_bookings = [
        (bid, b) for bid, b in bookings.items() if b["user_id"] == user_id
    ]

    if not user_bookings:
        await update.message.reply_text("Sizda yozuvlar yo‘q ❌")
        return

    for bid, b in user_bookings:
        text = (
            f"✂️ {b['service']}\n"
            f"👨‍🔧 {b['master']}\n"
            f"📅 {b['day']} {b['time']}"
        )

    
        await update.message.reply_text(text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()
    if user.id == ADMIN_ID:
        await show_admin_msg(update, context)
        return
    keyboard = [
        [InlineKeyboardButton("✂️  Записаться", callback_data="book")],
        [InlineKeyboardButton("📋  Мои записи", callback_data="my_bookings")],
    ]
    await update.message.reply_text(
        f"━━━━━━━━━━━━━━━━━━\n"
        f"✂️  *SOCH TIME*\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"Привет, *{user.first_name}*! 👋\n\n"
        f"Запишись к мастеру онлайн —\nбез звонков и очередей.\n\n"
        f"⏰ Работаем: 09:00 – 21:00\n"
        f"📍 г. Ташкент",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔️ Нет доступа.")
        return
    await show_admin_msg(update, context)

async def show_admin_msg(update, context):
    total = sum(b["price"] for b in bookings.values())
    keyboard = [
        [InlineKeyboardButton("📋 Все записи", callback_data="admin_list")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
    ]
    text = (
        f"🔐 *Панель администратора*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📅 Всего записей: *{len(bookings)}*\n"
        f"💰 Ожидаемая выручка: *{total:,} сум*\n"
        f"━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user

    # ADMIN callbacks
    if data == "admin_list":
        text = "📋 *Все записи:*\n\n" + fmt_bookings_for_admin()
        rows = [[InlineKeyboardButton(f"🗑 Удалить {bid}", callback_data=f"del_{bid}")] for bid in bookings]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="admin_back")])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))
        return

    elif data == "admin_stats":
        by_master = {}
        for b in bookings.values():
            by_master[b["master"]] = by_master.get(b["master"], 0) + 1
        lines = ["📊 *Статистика по мастерам:*\n"]
        for master, count in by_master.items():
            lines.append(f"• {master}: *{count}* записей")
        lines.append(f"\n💰 Итого: *{sum(b['price'] for b in bookings.values()):,} сум*")
        rows = [[InlineKeyboardButton("⬅️ Назад", callback_data="admin_back")]]
        await query.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))
        return

    elif data == "admin_back":
        total = sum(b["price"] for b in bookings.values())
        keyboard = [
            [InlineKeyboardButton("📋 Все записи", callback_data="admin_list")],
            [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        ]
        await query.edit_message_text(
            f"🔐 *Панель администратора*\n━━━━━━━━━━━━━━━━\n"
            f"📅 Записей: *{len(bookings)}*\n"
            f"💰 Выручка: *{total:,} сум*\n━━━━━━━━━━━━━━━━",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    elif data.startswith("del_"):
        bid = data.replace("del_", "")
        if bid in bookings:
            del bookings[bid]
        text = "📋 *Все записи:*\n\n" + fmt_bookings_for_admin()
        rows = [[InlineKeyboardButton(f"🗑 Удалить {bid}", callback_data=f"del_{bid}")] for bid in bookings]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="admin_back")])
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))
        return

    # CLIENT callbacks
    if data == "my_bookings":
        my = [b for b in bookings.values() if b.get("user_id") == user.id]
        if not my:
            text = "📭 У вас пока нет записей."
        else:
            lines = ["📋 *Ваши записи:*\n"]
            for b in my:
                lines.append(f"▪️ *{b['day']} в {b['time']}*\n   {b['master']} — {b['service']}\n")
            text = "\n".join(lines)
        await query.edit_message_text(text, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_start")]]))

    elif data == "back_start":
        keyboard = [
            [InlineKeyboardButton("✂️  Записаться", callback_data="book")],
            [InlineKeyboardButton("📋  Мои записи", callback_data="my_bookings")],
        ]
        await query.edit_message_text(
            "━━━━━━━━━━━━━━━━━━\n✂️  *SOCH TIME*\n━━━━━━━━━━━━━━━━━━\n\nВыберите действие:",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "book":
        rows = []
        for key, m in MASTERS.items():
            rows.append([InlineKeyboardButton(f"{m['emoji']} {m['name']}  —  {m['spec']}", callback_data=f"master_{key}")])
        rows.append([InlineKeyboardButton("❌ Отмена", callback_data="back_start")])
        await query.edit_message_text(
            "👨‍💼 *Шаг 1 из 4 — Выберите мастера:*",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif data.startswith("master_"):
        key = data.replace("master_", "")
        m = MASTERS[key]
        context.user_data["master_key"] = key
        context.user_data["master"] = f"{m['emoji']} {m['name']}"
        rows = []
        for skey, s in SERVICES.items():
            rows.append([InlineKeyboardButton(f"{s['name']}  •  {s['price']:,} сум  •  {s['time']}", callback_data=f"service_{skey}")])
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="book")])
        await query.edit_message_text(
            f"💇 *Шаг 2 из 4 — Выберите услугу:*\n\nМастер: *{m['emoji']} {m['name']}*",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif data.startswith("service_"):
        skey = data.replace("service_", "")
        s = SERVICES[skey]
        context.user_data["service_key"] = skey
        context.user_data["service"] = s["name"]
        context.user_data["price"] = s["price"]
        rows = [[InlineKeyboardButton(f"📅 {d}", callback_data=f"day_{d}")] for d in DAYS]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"master_{context.user_data['master_key']}")])
        await query.edit_message_text(
            f"📅 *Шаг 3 из 4 — Выберите день:*\n\n"
            f"Мастер: *{context.user_data['master']}*\n"
            f"Услуга: *{s['name']}* — {s['price']:,} сум",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif data.startswith("day_"):
        day = data.replace("day_", "")
        context.user_data["day"] = day
        rows = [[InlineKeyboardButton(f"🕐 {t}", callback_data=f"time_{t}") for t in TIMES[i:i+3]] for i in range(0, len(TIMES), 3)]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"service_{context.user_data['service_key']}")])
        d = context.user_data
        await query.edit_message_text(
            f"🕐 *Шаг 4 из 4 — Выберите время:*\n\n"
            f"Мастер: *{d['master']}*\nУслуга: *{d['service']}*\nДень: *{day}*",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif data.startswith("time_"):
        time = data.replace("time_", "")
        context.user_data["time"] = time
        d = context.user_data
        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить запись", callback_data="confirm")],
            [InlineKeyboardButton("⬅️ Изменить", callback_data=f"day_{d['day']}")],
        ]
        await query.edit_message_text(
            f"📋 *Проверьте запись:*\n\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"👨‍💼 Мастер:  *{d['master']}*\n"
            f"💇 Услуга:   *{d['service']}*\n"
            f"📅 Дата:     *{d['day']}*\n"
            f"🕐 Время:   *{time}*\n"
            f"💰 Цена:     *{d['price']:,} сум*\n"
            f"━━━━━━━━━━━━━━━━\n\nВсё верно?",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "confirm":
        d = context.user_data
        bid = f"#{booking_counter()}"
        now = datetime.now().strftime("%d.%m %H:%M")
        bookings[bid] = {
            "user_id": user.id,
            "client_name": user.full_name,
            "username": user.username,
            "master": d["master"],
            "service": d["service"],
            "price": d["price"],
            "day": d["day"],
            "time": d["time"],
            "created_at": now,
        }
        await query.edit_message_text(
            f"🎉 *Запись подтверждена!*\n\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🔖 Номер: *{bid}*\n"
            f"👨‍💼 Мастер: *{d['master']}*\n"
            f"💇 Услуга: *{d['service']}*\n"
            f"📅 Дата: *{d['day']}*\n"
            f"🕐 Время: *{d['time']}*\n"
            f"💰 Оплата в салоне: *{d['price']:,} сум*\n"
            f"━━━━━━━━━━━━━━━━\n\n"
            f"⏰ Напомним за 1 час!\nЖдём вас в *Soch Time* ✂️",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Записаться снова", callback_data="book")],
                [InlineKeyboardButton("📋 Мои записи", callback_data="my_bookings")],
            ]))
        # Уведомление администратору
        try:
            await query.get_bot().send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"🔔 *Новая запись {bid}!*\n\n"
                    f"👤 Клиент: *{user.full_name}*"
                    + (f" (@{user.username})" if user.username else "") + "\n"
                    f"👨‍💼 Мастер: *{d['master']}*\n"
                    f"💇 Услуга: *{d['service']}*\n"
                    f"📅 Дата: *{d['day']}*\n"
                    f"🕐 Время: *{d['time']}*\n"
                    f"💰 Сумма: *{d['price']:,} сум*"
                ),
           try:
    pass
except Exception:
    pass

     if query.data.startswith("cancel_"):
        bid = int(query.data.split("_")[1])

        if bid in bookings:
            del bookings[bid]
            await query.edit_message_text("❌ Запись отменена")
        else:
            await query.edit_message_text("❌ Запись не найдена")
   
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("✅ Бот запущен! @Soch_time01bot")
    app.run_polling()

if __name__ == "__main__":
    main()

