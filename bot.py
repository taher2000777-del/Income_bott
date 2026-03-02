import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# --- কনফিগারেশন ---
TOKEN = "8629892440:AAFg8jGPFc9UTzFj1CaBNlMqdrjnq38nGzg" 
ADMIN_ID = 6578678699 # আপনার টেলিগ্রাম আইডি
ADMIN_LINK = "https://t.me/Molla019" # আপনার প্রোফাইল লিংক

# সোশ্যাল মিডিয়া লিংক (পরে পরিবর্তন করতে পারবেন)
YT_LINK = "https://www.youtube.com/@skFarhan-u7z" 
FB_LINK = "https://facebook.com/yourpage"

# ডাটাবেস সেটআপ
conn = sqlite3.connect("income_master.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)")
conn.commit()

# ১. স্টার্ট কমান্ড - এখানে বাধ্যতামূলক কাজ দেওয়া হয়েছে
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    
    keyboard = [
        [InlineKeyboardButton("🔴 Subscribe YouTube", url=YT_LINK)],
        [InlineKeyboardButton("🔵 Follow Facebook", url=FB_LINK)],
        [InlineKeyboardButton("📸 Submit Screenshot", callback_data='submit_proof')],
        [InlineKeyboardButton("✅ Check / Main Menu", callback_data='main_menu')]
    ]
    await update.message.reply_text(
        "👋 স্বাগতম! কাজ শুরু করতে উপরের ইউটিউব ও ফেসবুক পেজ ফলো করে স্ক্রিনশট দিন।\n\n"
        "স্ক্রিনশট দিতে 'Submit Screenshot' বাটনে ক্লিক করুন।",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ২. বাটন হ্যান্ডেলার
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'submit_proof':
        await query.message.reply_text("📸 অনুগ্রহ করে আপনার সাবস্ক্রাইব ও ফলো করার স্ক্রিনশটটি এখানে পাঠান।")
    
    elif query.data == 'main_menu':
        # এখানে আপনি মেনু বাটনগুলো রাখতে পারেন
        keyboard = [
            [InlineKeyboardButton("💰 Balance", callback_data='bal'), InlineKeyboardButton("🎁 Bonus", callback_data='bonus')],
            [InlineKeyboardButton("🚀 Start Earning", callback_data='earn')],
            [InlineKeyboardButton("💳 Withdraw", callback_data='withdraw'), InlineKeyboardButton("❓ Help", callback_data='help')]
        ]
        await query.message.edit_text("🎮 **মেইন মেনু**\nঅ্যাডমিন আপনার স্ক্রিনশট চেক করলে ব্যালেন্স যোগ হবে।", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'bal':
        cursor.execute("SELECT balance FROM users WHERE id=?", (query.from_user.id,))
        bal = cursor.fetchone()[0]
        await query.message.reply_text(f"💰 আপনার বর্তমান ব্যালেন্স: {bal:.2f} টাকা")

# ৩. স্ক্রিনশট বা প্রুফ হ্যান্ডেলার (এটি আপনার কাছে ছবি পাঠাবে)
async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # ইউজারের পাঠানো স্ক্রিনশট অ্যাডমিনকে পাঠিয়ে দেওয়া
    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    await update.message.reply_text(f"✅ ধন্যবাদ {user.first_name}! আপনার স্ক্রিনশট অ্যাডমিনের কাছে পাঠানো হয়েছে। চেক করার পর আপনার ব্যালেন্স আপডেট করা হবে।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    # ইউজার কোনো ছবি পাঠালে সেটি এই ফাংশন ধরবে
    app.add_handler(MessageHandler(filters.PHOTO, handle_proof))
    
    app.run_polling()
