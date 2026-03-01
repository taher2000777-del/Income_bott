import sqlite3, time, random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# আপনার টোকেন ও আইডি
TOKEN = "8629892440:AAHdMFBKf8UmV4XfBb3iaLOrImINb8sbH6c"
ADMIN_ID = 6578678699

# ডেটাবেস সেটআপ
conn = sqlite3.connect("income_bot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, last_earn INTEGER DEFAULT 0, daily_count INTEGER DEFAULT 0)")
conn.commit()

# ইনকাম লিংক
AD_LINKS = [
    "https://www.effectivegatecpm.com/c5bkk9ri?key=c8f7c78728555572c9078a0a2fa04107",
    "https://www.effectivegatecpm.com/d1fbg3v9?key=23c7dd7b9f21469d099225a717c8f556"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()

    # সুন্দর বাটন ডিজাইন
    keyboard = [
        [InlineKeyboardButton("💰 My Balance", callback_data='bal'), InlineKeyboardButton("📊 Rank", callback_data='rank')],
        [InlineKeyboardButton("🚀 Start Earning", callback_data='earn')],
        [InlineKeyboardButton("💳 Withdraw", callback_data='withdraw'), InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"👋 **স্বাগতম, {update.effective_user.first_name}!**\n\n"
        "নিচের মেনু থেকে বাটন ক্লিক করে কাজ শুরু করুন।"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == 'bal':
        cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        balance = cursor.fetchone()[0]
        await query.message.reply_text(f"💰 আপনার বর্তমান ব্যালেন্স: **{balance:.2f} TK**", parse_mode='Markdown')

    elif query.data == 'earn':
        link = random.choice(AD_LINKS)
        await query.message.reply_text(f"🚀 **আপনার আজকের লিংক:**\n{link}\n\n✅ ৩০ সেকেন্ড দেখে ব্যাক করুন!", parse_mode='Markdown')

    elif query.data == 'rank':
        await query.message.reply_text("📊 বর্তমানে আপনি **Top 100** মেম্বারের তালিকায় আছেন!")

    elif query.data == 'help':
        await query.message.reply_text("❓ সাহায্য প্রয়োজন? আমাদের অ্যাডমিনকে মেসেজ দিন।")
    
    elif query.data == 'withdraw':
        await query.message.reply_text("💳 মিনিমাম উইথড্র **৫০ টাকা**। কাজ চালিয়ে যান!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()
