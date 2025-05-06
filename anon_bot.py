import asyncio
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

# 🔐 تنظیمات اولیه
ADMIN_ID = 167764826
BOT_TOKEN = "7632920897:AAEJ3GwF6XJXLd3t1D8qAlF8_7XLotqkWDI"
MEDIA_CHANNEL = "@nashhhenasprt"

# 💾 دیتاهای ضروری
active_chats = {}
message_log = []
blocked_users = set()

# دکمه زیر پیام‌ها
def reply_markup_buttons(uid):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ پاسخ", callback_data=f"reply_{uid}"),
            InlineKeyboardButton("❌ انصراف", callback_data=f"cancel_{uid}")
        ]
    ])

# ارسال منو اصلی
async def send_main_menu(user, context):
    keyboard = [
        [KeyboardButton("📬 لینک ناشناس من"), KeyboardButton("📖 راهنما")],
        [KeyboardButton("💌 وصلم کن به مخاطب خاصم!")]
    ]
    if user.id == ADMIN_ID:
        keyboard.append([KeyboardButton("🛠 پنل ادمین")])
    await context.bot.send_message(
        chat_id=user.id,
        text="🏠 منوی اصلی:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    if args:
        target = int(args[0])
        if user.id == target:
            await update.message.reply_text("اینکه آدم با خودش حرف بزنه خوبه، ولی اینجا نمیشه به خودت پیام ناشناس بدی 😅")
            await send_main_menu(user, context)
            return

        context.user_data["target"] = target
        target_user = await context.bot.get_chat(target)
        name = target_user.full_name
        await update.message.reply_text(
            f"در حال ارسال پیام ناشناس به {name} هستی! 🕊️\n\n"
            "با خیال راحت هر حرف یا انتقادی که تو دلت هست بنویس، این پیام بصورت کاملاً ناشناس ارسال میشه 🙂"
        )
    else:
        await send_main_menu(user, context)

# دریافت پیام متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    text = msg.text

    # لیست دستورات فیلتر شده در حین ارسال پیام
    blocked_texts = [
        "📖 راهنما", "📬 لینک ناشناس من", "💌 وصلم کن به مخاطب خاصم!", "🛠 پنل ادمین",
        "/again", "/neewmsg", "/link"
    ]
    if 'target' in context.user_data or user.id in active_chats:
        if text in blocked_texts:
            return await msg.reply_text("⛔️ در حالت ارسال پیام ناشناس نمی‌تونی از این دکمه‌ها استفاده کنی.")

    # پاسخ به پیام ناشناس
    if user.id in active_chats:
        peer = active_chats.pop(user.id)
        await context.bot.send_message(chat_id=peer, text=text, reply_markup=reply_markup_buttons(user.id))
        await context.bot.send_message(chat_id=MEDIA_CHANNEL,
            text=f"📨 پیام از {user.full_name} (ID: {user.id}, @{user.username}) → {peer}:\n{text}")
        await msg.reply_text("✅ پیام شما ارسال شد 😊\n\nجهت ارسال پیام دوباره به این شخص دستور /again را لمس کنید.")
        return

    # ارسال پیام ناشناس
    if 'target' in context.user_data:
        target = context.user_data.pop('target')
        context.bot_data.setdefault("pending_messages", {})[target] = {
            "type": "text", "content": text, "from_id": user.id}
        await context.bot.send_message(chat_id=target, text="📬 یک پیام ناشناس دارید!\nبرای مشاهده 👈 /neewmsg")
        await context.bot.send_message(chat_id=MEDIA_CHANNEL,
            text=f"📨 پیام از {user.full_name} (ID: {user.id}, @{user.username}) → {target}:\n{text}")
        await msg.reply_text("✅ پیام شما ارسال شد 😊\n\nجهت ارسال پیام دوباره به این شخص دستور /again را لمس کنید.")
        return

    # دستورات متنی
    if text == "📬 لینک ناشناس من" or text == "/link":
        link = f"https://t.me/{context.bot.username}?start={user.id}"
        await msg.reply_text(
            f"سلام {user.first_name} هستم ✋️\n\n"
            "لینک زیر رو لمس کن و هر حرفی که تو دلت هست یا هر انتقادی که نسبت به من داری رو با خیال راحت بنویس و بفرست. "
            "بدون اینکه از اسمت باخبر بشم پیامت به من می‌رسه.\n\n"
            f"👇👇\n{link}\n\n"
            "☝️ این پیامو برای دوستات یا گروه‌هایی که می‌شناسی فوروارد کن یا لینک داخلش رو تو بیوی اینستاگرامت بذار، "
            "تا بقیه بتونن راحت و ناشناس بهت پیام بدن 😉"
        )
    elif text == "📖 راهنما":
        await msg.reply_text(
            "🤖 «ربات ناشناس سوشی» محبوب‌ترین ربات برای دریافت پیام‌های ناشناس در تلگرامه!\n\n"
            "🔹 پیام ناشناس بگیر از دوستات و فالوور‌هات\n"
            "🔹 به مخاطب خاصت یا گروه‌ها پیام ناشناس بفرست\n"
            "🔹 همه‌چیز کاملاً امن و بدون نمایش اسم و شماره طرف\n\n"
            "برای دریافت لینک ناشناس، دستور /link رو لمس کن ✨"
        )
    elif text == "💌 وصلم کن به مخاطب خاصم!":
        await msg.reply_text("🔧 این بخش در حال توسعه است و فعلاً امکان استفاده نداره.")
    elif text == "🛠 پنل ادمین" and user.id == ADMIN_ID:
        await show_admin_panel(update, context)
    elif text == "/again":
        peer = context.user_data.get("last_target")
        if peer:
            peer_info = await context.bot.get_chat(peer)
            context.user_data['target'] = peer
            await msg.reply_text(
                f"در حال ارسال پیام ناشناس به {peer_info.full_name} هستی! 🕊️\n\n"
                "با خیال راحت هر حرف یا انتقادی که تو دلت هست بنویس، این پیام بصورت کاملاً ناشناس ارسال میشه 🙂"
            )
    else:
        await send_main_menu(user, context)

# رسانه‌ها
async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message

    file_id, media_type = None, None
    if msg.photo:
        file_id, media_type = msg.photo[-1].file_id, "photo"
    elif msg.animation:
        file_id, media_type = msg.animation.file_id, "animation"
    elif msg.sticker:
        file_id, media_type = msg.sticker.file_id, "sticker"
    else:
        return

    if user.id in active_chats:
        peer = active_chats.pop(user.id)
        await send_any_message(context, media_type, peer, file_id=file_id, markup=reply_markup_buttons(user.id))
        await context.bot.send_message(chat_id=MEDIA_CHANNEL,
            text=f"📷 رسانه از {user.full_name} (ID: {user.id}, @{user.username}) → {peer}")
        await send_any_message(context, media_type, MEDIA_CHANNEL, file_id=file_id)
        await msg.reply_text("✅ پیام رسانه‌ای شما ارسال شد.")
        return

    if 'target' in context.user_data:
        target = context.user_data.pop('target')
        context.user_data['last_target'] = target
        context.bot_data.setdefault("pending_messages", {})[target] = {
            "type": media_type, "file_id": file_id, "from_id": user.id}
        await context.bot.send_message(chat_id=target, text="📬 یک پیام ناشناس دارید!\nبرای مشاهده 👈 /neewmsg")
        await context.bot.send_message(chat_id=MEDIA_CHANNEL,
            text=f"📷 رسانه از {user.full_name} (ID: {user.id}, @{user.username}) → {target}")
        await send_any_message(context, media_type, MEDIA_CHANNEL, file_id=file_id)
        await msg.reply_text("✅ پیام رسانه‌ای شما ارسال شد.")
        return

# ارسال پیام
async def send_any_message(context, method, target_id, file_id=None, text=None, markup=None):
    kwargs = {'chat_id': target_id}
    if markup:
        kwargs['reply_markup'] = markup
    if method == "text":
        kwargs['text'] = text
        await context.bot.send_message(**kwargs)
    elif method == "photo":
        kwargs['photo'] = file_id
        await context.bot.send_photo(**kwargs)
    elif method == "animation":
        kwargs['animation'] = file_id
        await context.bot.send_animation(**kwargs)
    elif method == "sticker":
        kwargs['sticker'] = file_id
        await context.bot.send_sticker(**kwargs)

# دریافت پیام معلق
async def neewmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = context.bot_data.get("pending_messages", {}).pop(user.id, None)
    if not data:
        return await update.message.reply_text("📭 پیامی موجود نیست.")

    frm = data["from_id"]
    active_chats[user.id] = frm
    context.user_data['last_target'] = frm
    markup = reply_markup_buttons(frm)

    if data["type"] == "text":
        await context.bot.send_message(chat_id=user.id, text=data["content"], reply_markup=markup)
    else:
        await send_any_message(context, data["type"], user.id, file_id=data["file_id"], markup=markup)

    try:
        await context.bot.send_message(chat_id=frm, text="👁 پیام شما توسط گیرنده خوانده شد.")
    except Exception as e:
        print(f"خطا در خواندن: {e}")

# پنل ادمین
async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return

    total = len(message_log)
    unique = len({m['from_id'] for m in message_log})
    latest_users = list({m['from_id'] for m in reversed(message_log)})[:10]

    text = f"🛠 پنل ادمین\n👥 کاربران: {unique}\n📨 پیام‌ها: {total}\n\n🔟 ۱۰ کاربر آخر:\n"
    for uid in latest_users:
        try:
            u = await context.bot.get_chat(uid)
            text += f"• {u.full_name} - ID: {uid} - @{u.username or 'بدون آیدی'}\n"
        except:
            continue

    await context.bot.send_message(chat_id=user.id, text=text)

# دکمه‌های پاسخ و انصراف
async def handle_reply_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    await query.answer()

    if data.startswith("reply_"):
        peer = int(data.split("_")[1])
        active_chats[user.id] = peer
        await context.bot.send_message(chat_id=user.id, text="✏️ پاسخ بده:")

    elif data.startswith("cancel_"):
        peer = int(data.split("_")[1])
        active_chats.pop(user.id, None)
        await context.bot.send_message(chat_id=user.id, text="📴 چت بسته شد.")
        await context.bot.send_message(chat_id=peer, text="📴 چت توسط طرف مقابل بسته شد.")

# اجرای بات
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("neewmsg", neewmsg))
    app.add_handler(CommandHandler("link", handle_message))
    app.add_handler(CommandHandler("again", handle_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO | filters.ANIMATION | filters.Sticker.ALL, handle_media))
    app.add_handler(CallbackQueryHandler(handle_reply_buttons, pattern=r"^(reply_|cancel_)"))
    app.add_handler(CommandHandler("admin_panel", show_admin_panel))

    print("🤖 ربات سوشی در حال اجراست...")
    app.run_polling()
