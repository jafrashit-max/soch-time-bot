import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = "8578169848:AAF3r_7tienkbAb4afBe9W63wz2wGxDtkCo"
ADMIN_ID = 1314440253

MASTERS = {
    "salohiddin": {"name": "Салохидин", "emoji": "✂️", "spec": "Барбер • стаж 5 лет", "phone": "+998 94 676 29 09"},
    "jasur": {"name": "Жасур", "emoji": "💈", "spec": "Стилист • стаж 6 лет", "phone": "+998 90 123 45 67"},
    "bobur": {"name": "Бобур", "emoji": "🪒", "spec": "Барбер • стаж 4 года", "phone": "+998 93 987 65 43"},
}

SERVICES = {
    "haircut": {"name": "✂️ Стрижка", "price": 80000, "time": "40 мин"},
    "haircut_beard": {"name": "💈 Стрижка + борода", "price": 80000, "time": "60 мин"},
    "beard": {"name": "🪒 Борода", "price": 80000, "time": "30 мин"},
}

CARD = "5614 6814 2496 1377"
CLICK_URL = "https://my.click.uz/services/pay?service_id=12345&merchant_id=12345"
PAYME_URL = "https://checkout.paycom.uz"

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
        status = "💳 Оплачено" if b.get("paid") else "💵 Оплата в салоне"
        lines.append(f"┌ *{bid}*\n│ 👤 {b['client_name']}\n│ 👨‍💼 {b['master']}\n│ 💇 {b['service']}\n│ 📅 {b['day']} в {b['time']}\n│ 💰 {b['price']:,} сум\n└ {status}")
    return "\n\n".join(lines)

async def send_reminder(bot, user_id, bid, booking):
    await asyncio.sleep(3600)
    if bid in bookings:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=(
                    f"⏰ *Напоминание!*\n\n"
                    f"Через 1 час у вас запись:\n\n"
                    f"👨‍💼 {booking['master']}\n"
                    f"💇 {booking['service']}\n"
                    f"🕐 {booking['time']}\n\n"
                    f"Ждём вас в *Soch Time* ✂️"
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass

async def start(u, c):
    usr = u.effective_user
    c.user_data.clear()
    if usr.id == ADMIN_ID:
        total = sum(b["price"] for b in bookings.values())
        paid = sum(1 for b in bookings.values() if b.get("paid"))
        kb = [[InlineKeyboardButton("📋 Все записи", callback_data="admin_list")],[InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]]
        await u.message.reply_text(
            f"🔐 *Панель администратора*\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"📅 Записей: *{len(bookings)}*\n"
            f"💳 Оплачено онлайн: *{paid}*\n"
            f"💰 Выручка: *{total:,} сум*\n"
            f"━━━━━━━━━━━━━━━━",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        return
    kb = [[InlineKeyboardButton("✂️  Записаться", callback_data="book")],[InlineKeyboardButton("📋  Мои записи", callback_data="my_bookings")]]
    await u.message.reply_text(
        f"〰️〰️〰️〰️〰️〰️〰️〰️〰️\n"
        f"✂️  *SOCH TIME*\n"
        f"〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\n"
        f"Привет, *{usr.first_name}*! 👋\n\n"
        f"Запишись к мастеру онлайн —\n"
        f"без звонков и очередей!\n\n"
        f"⏰ *09:00 – 21:00*\n"
        f"📍 г. Ташкент\n"
        f"⭐️ Рейтинг: 4.9/5",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def admin_cmd(u, c):
    if u.effective_user.id != ADMIN_ID:
        await u.message.reply_text("⛔️ Нет доступа.")
        return
    total = sum(b["price"] for b in bookings.values())
    paid = sum(1 for b in bookings.values() if b.get("paid"))
    kb = [[InlineKeyboardButton("📋 Все записи", callback_data="admin_list")],[InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]]
    await u.message.reply_text(
        f"🔐 *Панель администратора*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📅 Записей: *{len(bookings)}*\n"
        f"💳 Оплачено онлайн: *{paid}*\n"
        f"💰 Выручка: *{total:,} сум*\n"
        f"━━━━━━━━━━━━━━━━",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

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
        total = sum(b["price"] for b in bookings.values())
        paid = sum(b["price"] for b in bookings.values() if b.get("paid"))
        lines.append(f"\n💰 Итого: *{total:,} сум*")
        lines.append(f"💳 Оплачено онлайн: *{paid:,} сум*")
        await q.edit_message_text("\n".join(lines), parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="admin_back")]]))

    elif d == "admin_back":
        total = sum(b["price"] for b in bookings.values())
        paid = sum(1 for b in bookings.values() if b.get("paid"))
        await q.edit_message_text(
            f"🔐 *Панель администратора*\n━━━━━━━━━━━━━━━━\n"
            f"📅 Записей: *{len(bookings)}*\n"
            f"💳 Оплачено онлайн: *{paid}*\n"
            f"💰 Выручка: *{total:,} сум*\n━━━━━━━━━━━━━━━━",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Все записи", callback_data="admin_list")],[InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")]]))

    elif d.startswith("del_"):
        bid = d.replace("del_", "")
        if bid in bookings:
            del bookings[bid]
        text = "📋 *Все записи:*\n\n" + fmt()
        rows = [[InlineKeyboardButton(f"🗑 Удалить {bid}", callback_data=f"del_{bid}")] for bid in bookings]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="admin_back")])
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d == "my_bookings":
        my = [(bid, b) for bid, b in bookings.items() if b.get("user_id") == usr.id]
        if not my:
            text = "📭 У вас пока нет записей."
            rows = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_start")]]
        else:
            lines = ["📋 *Ваши записи:*\n"]
            for bid, b in my:
                status = "💳 Оплачено" if b.get("paid") else "💵 Оплата в салоне"
                lines.append(f"▪️ *{b['day']} в {b['time']}*\n   {b['master']} — {b['service']}\n   {status} | 🔖 {bid}\n")
            text = "\n".join(lines)
            rows = [[InlineKeyboardButton(f"❌ Отменить {bid}", callback_data=f"cancel_{bid}")] for bid, b in my]
            rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_start")])
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d.startswith("cancel_"):
        bid = d.replace("cancel_", "")
        if bid in bookings and bookings[bid].get("user_id") == usr.id:
            b = bookings[bid]
            del bookings[bid]
            await q.edit_message_text(
                f"❌ *Запись отменена*\n\n🔖 {bid}\n👨‍💼 {b['master']}\n📅 {b['day']} в {b['time']}\n\nЖдём вас в следующий раз! 🙏",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📅 Записаться снова", callback_data="book")]]))
            try:
                await q.get_bot().send_message(chat_id=ADMIN_ID, text=f"❌ *Отмена {bid}*\n\n👤 {b['client_name']}\n👨‍💼 {b['master']}\n📅 {b['day']} в {b['time']}", parse_mode="Markdown")
            except Exception:
                pass
        else:
            await q.edit_message_text("❌ Запись не найдена.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="my_bookings")]]))

    elif d == "back_start":
        await q.edit_message_text(
            "〰️〰️〰️〰️〰️〰️〰️〰️〰️\n✂️  *SOCH TIME*\n〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\nВыберите действие:",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✂️ Записаться", callback_data="book")],[InlineKeyboardButton("📋 Мои записи", callback_data="my_bookings")]]))

    elif d == "book":
        rows = []
        for key, m in MASTERS.items():
            rows.append([InlineKeyboardButton(f"{m['emoji']} {m['name']} — {m['spec']}", callback_data=f"master_{key}")])
        rows.append([InlineKeyboardButton("❌ Отмена", callback_data="back_start")])
        await q.edit_message_text("👨‍💼 *Шаг 1 из 4 — Выберите мастера:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d.startswith("master_"):
        k = d[7:]
        m = MASTERS[k]
        context.user_data["mk"] = k
        context.user_data["master"] = f"{m['emoji']} {m['name']}"
        context.user_data["master_phone"] = m["phone"]
        rows = [[InlineKeyboardButton(f"{s['name']} • {s['price']:,} сум • {s['time']}", callback_data=f"service_{sk}")] for sk, s in SERVICES.items()]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data="book")])
        await q.edit_message_text(
            f"💇 *Шаг 2 из 4 — Выберите услугу:*\n\n"
            f"Мастер: *{m['emoji']} {m['name']}*\n"
            f"📞 {m['phone']}",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d.startswith("service_"):
        sk = d[8:]
        s = SERVICES[sk]
        context.user_data["sk"] = sk
        context.user_data["service"] = s["name"]
        context.user_data["price"] = s["price"]
        rows = [[InlineKeyboardButton(f"📅 {dy}", callback_data=f"day_{dy}")] for dy in DAYS]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"master_{context.user_data['mk']}")])
        await q.edit_message_text(
            f"📅 *Шаг 3 из 4 — Выберите день:*\n\n"
            f"Мастер: *{context.user_data['master']}*\n"
            f"Услуга: *{s['name']}* — {s['price']:,} сум",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d.startswith("day_"):
        day = d[4:]
        context.user_data["day"] = day
        rows = [[InlineKeyboardButton(f"🕐 {t}", callback_data=f"time_{t}") for t in TIMES[i:i+3]] for i in range(0, len(TIMES), 3)]
        rows.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"service_{context.user_data['sk']}")])
        cd = context.user_data
        await q.edit_message_text(
            f"🕐 *Шаг 4 из 4 — Выберите время:*\n\n"
            f"Мастер: *{cd['master']}*\n"
            f"Услуга: *{cd['service']}*\n"
            f"День: *{day}*",
            parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(rows))

    elif d.startswith("time_"):
        t = d[5:]
        context.user_data["time"] = t
        cd = context.user_data
        await q.edit_message_text(
            f"📋 *Проверьте запись:*\n\n"
            f"〰️〰️〰️〰️〰️〰️〰️〰️\n"
            f"👨‍💼 *{cd['master']}*\n"
            f"📞 {cd['master_phone']}\n"
            f"💇 *{cd['service']}*\n"
            f"📅 *{cd['day']}*\n"
            f"🕐 *{t}*\n"
            f"💰 *{cd['price']:,} сум*\n"
            f"〰️〰️〰️〰️〰️〰️〰️〰️\n\n"
            f"Всё верно?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm")],
                [InlineKeyboardButton("⬅️ Изменить", callback_data=f"day_{cd['day']}")],
            ]))

    elif d == "confirm":
        cd = context.user_data
        bid = f"#{bc()}"
        now = datetime.now().strftime("%d.%m %H:%M")
        bookings[bid] = {"user_id": usr.id, "client_name": usr.full_name, "username": usr.username, "master": cd["master"], "master_phone": cd["master_phone"], "service": cd["service"], "price": cd["price"], "day": cd["day"], "time": cd["time"], "created_at": now, "paid": False}
        await q.edit_message_text(
            f"🎉 *Запись подтверждена!*\n\n"
            f"〰️〰️〰️〰️〰️〰️〰️〰️\n"
            f"🔖 *{bid}*\n"
            f"👨‍💼 {cd['master']}\n"
            f"📞 {cd['master_phone']}\n"
            f"💇 {cd['service']}\n"
            f"📅 {cd['day']} в {cd['time']}\n"
            f"💰 {cd['price']:,} сум\n"
            f"〰️〰️〰️〰️〰️〰️〰️〰️\n\n"
            f"💳 *Оплатите онлайн или в салоне:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 Оплатить через Click", url=f"https://my.click.uz/pay/12345?amount=80000&comment={bid}")],
                [InlineKeyboardButton("💚 Оплатить через Payme", url=f"https://checkout.paycom.uz/12345?amount=8000000")],
                [InlineKeyboardButton("💵 Оплачу в салоне", callback_data="pay_salon")],
                [InlineKeyboardButton("📋 Мои записи", callback_data="my_bookings")],
            ]))
        try:
            await q.get_bot().send_message(
                chat_id=ADMIN_ID,
                text=f"🔔 *Новая запись {bid}!*\n\n👤 {usr.full_name}" + (f" (@{usr.username})" if usr.username else "") + f"\n👨‍💼 {cd['master']}\n💇 {cd['service']}\n📅 {cd['day']} в {cd['time']}\n💰 {cd['price']:,} сум\n💳 Ожидает оплаты",
                parse_mode="Markdown"
            )
        except Exception:
            pass
        asyncio.create_task(send_reminder(q.get_bot(), usr.id, bid, bookings[bid]))

    elif d == "pay_salon":
        await q.edit_message_text(
            f"✅ *Отлично!*\n\nОплата в салоне. Ждём вас!\n\n⏰ Напомним за 1 час до визита. ✂️",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📅 Записаться снова", callback_data="book")],
                [InlineKeyboardButton("📋 Мои записи", callback_data="my_bookings")],
            ]))

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
