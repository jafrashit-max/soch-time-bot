import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = "8578169848:AAF3r_7tienkbAb4afBe9W63wz2wGxDtkCo"
ADMIN_ID = 1314440253
MASTERS = {
    "alibekk": {"name": "Алибек", "emoji": "✂️", "spec": "Барбер • стаж 5 лет"},
    "rustam": {"name": "Рустам", "emoji": "💈", "spec": "Стилист • стаж 7 лет"},
    "sanzhar": {"name": "Санжар", "emoji": "🪒", "spec": "Барбер • стаж 3 года"},
}
SERVICES = {
    "haircut": {"name": "Стрижка", "price": 80000, "time": "40 мин"},
    "haircut_beard": {"name": "Стрижка + борода", "price": 80000, "time": "60 мин"},
    "styling": {"name": "Укладка", "price": 80000, "time": "30 мин"},
    "beard": {"name": "Борода", "price": 80000, "time": "30 мин"},
}
TIMES = ["09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00"]
DAYS = ["Сегодня","Завтра","2 мая","3 мая","5 мая","6 мая","7 мая","8 мая","9 мая","10 мая"]
bookings = {}

def bc():
    return len(bookings) + 1001

def fmt():
    if not bookings:
        return "📭 Записей пока нет."
    lines = []
    for bid, b in sorted(bookings.items()):
        lines.append(f"┌ *{bid}*\n│ 👤 {b['client_name']}\n│ 👨‍💼 {b['master']}\n│ 💇 {b['service']}\n│ 📅 {b['day']} в {b['time']}\n└ 💰 {b['price']:,} сум")
    return "\n\n".join(lines)

async def start(u, c):
    usr = u.effective_user
    c.user_data.clear()
    if usr.id == ADMIN_ID:
        total = sum(b["price"] for b in bookings.values())
        kb = [[InlineKeyboardButton("📋 Все записи", callback_data="admin_list")],[InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]]
        await u.message.reply_text(f"🔐 *Панель администратора*\n━━━━━━━━━━━━━━━━\n📅 Записей: *{len(bookings)}*\n💰 Выручка: *{total:,} сум*\n━━━━━━━━━━━━━━━━", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        return
    kb = [[InlineKeyboardButton("✂️ Записаться", callback_data="book")],[InlineKeyboardButton("📋 Мои записи", callback_data="my_bookings")]]
    await u.message.reply_text(f"━━━━━━━━━━━━━━━━━━\n✂️ *SOCH TIME*\n━━━━━━━━━━━━━━━━━━\n\nПривет, *{usr.first_name}*! 👋\n\nЗапишись онлайн — без очередей!\n\n⏰ 09:00–21:00  📍 Ташкент", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def admin_cmd(u, c):
    if u.effective_user.id != ADMIN_ID:
        await u.message.reply_text("⛔️ Нет доступа.")
        return
    total = sum(b["price"] for b in bookings.values())
    kb = [[InlineKeyboardButton("📋 Все записи", callback_data="admin_list")],[InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]]
    await u.message.reply_text(f"🔐 *Панель администратора*\n━━━━━━━━━━━━━━━━\n📅 Записей: *{len(bookings)}*\n💰 Выручка: *{sum(b['price'] for b in bookings.values()):,} сум*\n━━━━━━━━━━━━━━━━", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def cb(update, context):
    q = update.callback_query
    await q.answer()
    d = q.data
    usr = update.effective_user

    if d == "admin_list":
        text = "📋 *Все записи:*\n\n" + fmt()
        rows = [[InlineKeyboardButton(f"🗑 Удалить {bid}", callback_data=f"del_{bid}")] for bid in bookings]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="admin_back")])
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d == "admin_stats":
        bm = {}
        for b in bookings.values():
            bm[b["master"]] = bm.get(b["master"], 0) + 1
        lines = ["📊 *Статистика:*\n"] + [f"• {m}: *{n}* записей" for m, n in bm.items()]
        lines.append(f"\n💰 Итого: *{sum(b['price'] for b in bookings.values()):,} сум*")
        await q.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="admin_back")]]))

    elif d == "admin_back":
        total = sum(b["price"] for b in bookings.values())
        await q.edit_message_text(f"🔐 *Панель администратора*\n━━━━━━━━━━━━━━━━\n📅 Записей: *{len(bookings)}*\n💰 Выручка: *{total:,} сум*\n━━━━━━━━━━━━━━━━", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Все записи", callback_data="admin_list")],[InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]]))

    elif d.startswith("del_"):
        bid = d.replace("del_", "")
        if bid in bookings:
            del bookings[bid]
        text = "📋 *Все записи:*\n\n" + fmt()
        rows = [[InlineKeyboardButton(f"🗑 Удалить {bid}", callback_data=f"del_{bid}")] for bid in bookings]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="admin_back")])
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d == "my_bookings":
        my = [b for b in bookings.values() if b.get("user_id") == usr.id]
        text = "📭 Записей нет." if not my else "📋 *Ваши записи:*\n\n" + "".join([f"▪️ *{b['day']} в {b['time']}*\n   {b['master']} — {b['service']}\n\n" for b in my])
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back_start")]]))

    elif d == "back_start":
        await q.edit_message_text("━━━━━━━━━━━━━━━━━━\n✂️ *SOCH TIME*\n━━━━━━━━━━━━━━━━━━\n\nВыберите действие:", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✂️ Записаться", callback_data="book")],[InlineKeyboardButton("📋 Мои записи", callback_data="my_bookings")]]))

    elif d == "book":
        rows = [[InlineKeyboardButton(f"{m['emoji']} {m['name']} — {m['spec']}", callback_data=f"master_{k}")] for k, m in MASTERS.items()]
        rows.append([InlineKeyboardButton("❌ Отмена", callback_data="back_start")])
        await q.edit_message_text("👨‍💼 *Шаг 1 из 4 — Выберите мастера:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d.startswith("master_"):
        k = d[7:]
        m = MASTERS[k]
        context.user_data["mk"] = k
        context.user_data["master"] = f"{m['emoji']} {m['name']}"
        rows = [[InlineKeyboardButton(f"{s['name']} • {s['price']:,} сум • {s['time']}", callback_data=f"service_{sk}")] for sk, s in SERVICES.items()]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="book")])
        await q.edit_message_text(f"💇 *Шаг 2 из 4 — Услуга:*\n\nМастер: *{m['emoji']} {m['name']}*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d.startswith("service_"):
        sk = d[8:]
        s = SERVICES[sk]
        context.user_data["sk"] = sk
        context.user_data["service"] = s["name"]
        context.user_data["price"] = s["price"]
        rows = [[InlineKeyboardButton(f"📅 {dy}", callback_data=f"day_{dy}")] for dy in DAYS]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"master_{context.user_data['mk']}")])
        await q.edit_message_text(f"📅 *Шаг 3 из 4 — День:*\n\nМастер: *{context.user_data['master']}*\nУслуга: *{s['name']}*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d.startswith("day_"):
        day = d[4:]
        context.user_data["day"] = day
        rows = [[InlineKeyboardButton(f"🕐 {t}", callback_data=f"time_{t}") for t in TIMES[i:i+3]] for i in range(0, len(TIMES), 3)]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"service_{context.user_data['sk']}")])
        cd = context.user_data
        await q.edit_message_text(f"🕐 *Шаг 4 из 4 — Время:*\n\nМастер: *{cd['master']}*\nУслуга: *{cd['service']}*\nДень: *{day}*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d.startswith("time_"):
        t = d[5:]
        context.user_data["time"] = t
        cd = context.user_data
        await q.edit_message_text(f"📋 *Проверьте запись:*\n\n━━━━━━━━━━━━━━━━\n👨‍💼 *{cd['master']}*\n💇 *{cd['service']}*\n📅 *{cd['day']}*\n🕐 *{t}*\n💰 *{cd['price']:,} сум*\n━━━━━━━━━━━━━━━━\n\nВсё верно?", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Подтвердить", callback_data="confirm")],[InlineKeyboardButton("⬅️ Изменить", callback_data=f"day_{cd['day']}")]]))

    elif d == "confirm":
        cd = context.user_data
        bid = f"#{bc()}"
        now = datetime.now().strftime("%d.%m %H:%M")
        bookings[bid] = {"user_id": usr.id, "client_name": usr.full_name, "username": usr.username, "master": cd["master"], "service": cd["service"], "price": cd["price"], "day": cd["day"], "time": cd["time"], "created_at": now}
        await q.edit_message_text(f"🎉 *Запись подтверждена!*\n\n━━━━━━━━━━━━━━━━\n🔖 *{bid}*\n👨‍💼 {cd['master']}\n💇 {cd['service']}\n📅 {cd['day']} в {cd['time']}\n💰 {cd['price']:,} сум (в салоне)\n━━━━━━━━━━━━━━━━\n\n⏰ Напомним за 1 час!\nЖдём вас! ✂️", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📅 Записаться снова", callback_data="book")],[InlineKeyboardButton("📋 Мои записи", callback_data="my_bookings")]]))
        try:
            await q.get_bot().send_message(chat_id=ADMIN_ID, text=f"🔔 *Новая запись {bid}!*\n\n👤 {usr.full_name}" + (f" (@{usr.username})" if usr.username else "") + f"\n👨‍💼 {cd['master']}\n💇 {cd['service']}\n📅 {cd['day']} в {cd['time']}\n💰 {cd['price']:,} сум", parse_mode="Markdown")
        except Exception:
            pass

    elif d == "cancel":
        await q.edit_message_text("❌ Запись отменена.\n\nНапишите /start чтобы начать заново.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CallbackQueryHandler(cb))
    print("✅ Бот запущен! @Soch_time01bot")
    app.run_polling()

if __name__ == "__main__":
    main()
