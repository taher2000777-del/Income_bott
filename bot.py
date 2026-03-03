import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# --- ১. কনফিগারেশন ---
TOKEN = "8629892440:AAFg8jGPFc9UTzFj1CaBNlMqdrjnq38nGzg" 
ADMIN_ID = 6578678699 
ADMIN_USERNAME = "Molla019" 
LOG_CHANNEL_ID = -1003732172008  # আপনার চ্যানেল আইডি

YT_LINK = "https://www.youtube.com/@skFarhan-u7z" 
TIKTOK_LINK = "https://www.tiktok.com/@user469378505" 
MIN_WITHDRAW = 20 

# --- ২. ডাটাবেস সেটআপ ---
conn = sqlite3.connect("income_master.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)")
conn.commit()

def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🔴 Subscribe YouTube", url=YT_LINK)],
        [InlineKeyboardButton("🎵 Follow TikTok", url=TIKTOK_LINK)],
        [InlineKeyboardButton("📸 Submit Screenshot", callback_data='submit_proof')],
        [InlineKeyboardButton("💰 Balance", callback_data='bal'), InlineKeyboardButton("💸 Withdraw", callback_data='withdraw')],
        [InlineKeyboardButton("❓ Help (Contact Admin)", url=f"https://t.me/{ADMIN_USERNAME}")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- ৪. ফাংশনসমূহ ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    await update.message.reply_text("👋 স্বাগতম!", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id # আপনার সংশোধনী অনুযায়ী
    await query.answer()

    if data == 'bal':
        cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
        result = cursor.fetchone()
        bal = result[0] if result else 0
        await query.edit_message_text(f"💰 বর্তমান ব্যালেন্স: {bal:.2f} টাকা", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]]))
    
    elif data == 'withdraw':
        cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
        result = cursor.fetchone()
        bal = result[0] if result else 0
        if bal < MIN_WITHDRAW:
            await query.message.reply_text(f"❌ মিনিমাম {MIN_WITHDRAW} টাকা লাগবে।")
        else:
            await query.edit_message_text(f"💸 ব্যালেন্স {bal:.2f} টাকা।\nনম্বরটি মেসেজ করুন।", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]]))
            context.user_data['waiting_for_number'] = True

    elif data == 'main_menu':
        await query.edit_message_text("👋 মেইন মেনু:", reply_markup=get_main_menu())

    elif data == 'submit_proof':
        await query.edit_message_text("📸 স্ক্রিনশট পাঠান।", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]]))

    elif data.startswith("app_") or data.startswith("rej_"):
        if query.from_user.id != ADMIN_ID: return
        parts = data.split("_")
        action, target_id = parts[0], int(parts[1])

        if action == "app":
            amount = float(parts[2])
            cursor.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, target_id))
            conn.commit()
            await query.edit_message_caption(caption=f"✅ Approved! {amount} TK Added.")
            try: await context.bot.send_message(chat_id=target_id, text=f"💰 {amount} টাকা যোগ হয়েছে।")
            except: pass
        elif action == "rej":
            await query.edit_message_caption(caption="❌ Rejected!")
            try: await context.bot.send_message(chat_id=target_id, text="❌ প্রুফ সঠিক নয়।")
            except: pass

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get('waiting_for_number'):
        text = update.message.text
        cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
        bal = cursor.fetchone()[0]
        await context.bot.send_message(chat_id=LOG_CHANNEL_ID, 
                                     text=f"💸 **উইথড্র রিকোয়েস্ট!**\n🆔 `{user_id}`\n💰 পরিমাণ: {bal:.2f}\n📞 নম্বর: `{text}`")
        cursor.execute("UPDATE users SET balance = 0 WHERE id=?", (user_id,))
        conn.commit()
        context.user_data['waiting_for_number'] = False
        await update.message.reply_text("✅ রিকোয়েস্ট পাঠানো হয়েছে!", reply_markup=get_main_menu())

async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo_id = update.message.photo[-1].file_id
    keyboard = [[InlineKeyboardButton("✅ Approve 5 TK", callback_data=f"app_{user.id}_5")],
                [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user.id}")]]
    try:
        await context.bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo_id, 
                                   caption=f"📩 **নতুন প্রুফ**\n👤 {user.first_name}\n🆔 `{user.id}`", 
                                   reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.reply_text("✅ জমা হয়েছে।", reply_markup=get_main_menu())
    except:
        await update.message.reply_text("⚠️ এরর: বটকে চ্যানেলে এডমিন করুন।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_proof))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.run_polling()
