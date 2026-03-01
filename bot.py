import sqlite3
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# আপনার সঠিক টোকেন ও আইডি
TOKEN = "8629892440:AAFg8jGPFc9UTzFj1CaBNlMqdrjnq38nGzg"
ADMIN_ID = 6578678699

# ডেটাবেস সেটআপ
conn = sqlite3.connect("income_bot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()

    # প্রফেশনাল মেনু বাটন ডিজাইন
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data='bal'), InlineKeyboardButton("📊 Rank", callback_data='rank')],
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
    
    if query.data == 'bal':
        await query.message.reply_text("💰 আপনার ব্যালেন্স: **০.০০ টাকা**", parse_mode='Markdown')
    elif query.data == 'earn':
        await query.message.reply_text("🚀 ইনকাম করতে আমাদের নতুন টাস্কগুলো সম্পন্ন করুন!")
    elif query.data == 'withdraw':
        await query.message.reply_text("💳 মিনিমাম উইথড্র ৫০ টাকা।")
    elif query.data == 'help':
        await query.message.reply_text(f"❓ সাহায্যের জন্য অ্যাডমিনকে (@{ADMIN_ID}) মেসেজ দিন।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
