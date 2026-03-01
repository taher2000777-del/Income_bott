import sqlite3
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# ১. আপনার নতুন টোকেনটি এখানে বসান
TOKEN = "8629892440:AAFg8jGPFc9UTzFj1CaBNlMqdrjnq38nGzg"
# ২. আপনার টেলিগ্রাম ইউজারনেম এখানে দিন (যেমন: @YourUsername)
MY_USERNAME = "@Molla019" 

# ডেটাবেস কানেকশন
conn = sqlite3.connect("income_bot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()

    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data='bal'), InlineKeyboardButton("📊 Rank", callback_data='rank')],
        [InlineKeyboardButton("🚀 Start Earning", callback_data='earn')],
        [InlineKeyboardButton("💳 Withdraw", callback_data='withdraw'), InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"👋 স্বাগতম {update.effective_user.first_name}!\nনিচের মেনু থেকে বাটন ক্লিক করে কাজ শুরু করুন।"
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'bal':
        await query.message.reply_text("💰 আপনার ব্যালেন্স: **০.০০ টাকা**", parse_mode='Markdown')
    elif query.data == 'earn':
        await query.message.reply_text("🚀 ইনকাম শুরু করতে নিচের লিংকে ক্লিক করুন!\n(লিংক এখানে বসান)")
    elif query.data == 'withdraw':
        await query.message.reply_text("💳 মিনিমাম উইথড্র ৫০ টাকা।")
    elif query.data == 'help':
        await query.message.reply_text(f"❓ সাহায্যের জন্য অ্যাডমিনকে মেসেজ দিন: {MY_USERNAME}")
    elif query.data == 'rank':
        await query.message.reply_text("📊 আপনি বর্তমানে মেম্বার তালিকায় আছেন!")

async def message_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ইউজার কিছু লিখলে এই রিপ্লাই দেবে
    await update.message.reply_text("👋 আপনি চাইলে নিচের মেনু বাটনগুলো ব্যবহার করতে পারেন। নতুন মেনু পেতে /start লিখুন।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # হ্যান্ডেলারগুলো যোগ করা
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_reply))
    
    print("বটটি এখন সচল...")
    app.run_polling()
