import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# --- ১. কনফিগারেশন (এগুলো পরে পাল্টাতে পারবেন) ---
TOKEN = "8629892440:AAFg8jGPFc9UTzFj1CaBNlMqdrjnq38nGzg" # আপনার টোকেন
ADMIN_ID = 6578678699 # আপনার আইডি
ADMIN_LINK = "https://t.me/Molla019" # আপনার মেসেজ লিংক

# সোশ্যাল মিডিয়া লিংক (পরে পাল্টাতে পারবেন)
YT_LINK = "https://youtube.com/@yourchannel" 
FB_LINK = "https://facebook.com/yourpage"

# --- ২. ইনকাম রেট সেটআপ ---
REFER_BONUS = 2.00  # প্রতি রেফারে ২ টাকা
VIDEO_BONUS = 0.50  # ভিডিও দেখলে ৫০ পয়সা
DAILY_BONUS = 1.00  # প্রতিদিন ১ টাকা

# ডেটাবেস কানেকশন
conn = sqlite3.connect("income_master.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, referred_by INTEGER)")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # রেফারেল চেক
    args = context.args
    referred_by = int(args[0]) if args and args[0].isdigit() else None
    
    cursor.execute("INSERT OR IGNORE INTO users (id, referred_by) VALUES (?, ?)", (user_id, referred_by))
    conn.commit()

    keyboard = [
        [InlineKeyboardButton("🔴 Subscribe YouTube", url=YT_LINK)],
        [InlineKeyboardButton("🔵 Follow Facebook", url=FB_LINK)],
        [InlineKeyboardButton("✅ Check / Join Menu", callback_data='main_menu')]
    ]
    await update.message.reply_text("👋 স্বাগতম! কাজ শুরু করতে আমাদের সোশ্যাল মিডিয়া ফলো করে 'Check' বাটনে ক্লিক করুন।", reply_markup=InlineKeyboardMarkup(keyboard))

async def main_menu(query):
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data='bal'), InlineKeyboardButton("🎁 Bonus", callback_data='bonus')],
        [InlineKeyboardButton("🚀 Start Earning", callback_data='earn')],
        [InlineKeyboardButton("👥 Refer & Earn", callback_data='refer'), InlineKeyboardButton("💳 Withdraw", callback_data='withdraw')],
        [InlineKeyboardButton("❓ Help & Support", callback_data='help')]
    ]
    await query.message.edit_text("🎮 **মেইন মেনু**\nনিচের বাটনগুলো ব্যবহার করে ইনকাম শুরু করুন।", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == 'main_menu':
        await main_menu(query)
    
    elif query.data == 'bal':
        cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
        bal = cursor.fetchone()[0]
        await query.message.reply_text(f"💰 আপনার বর্তমান ব্যালেন্স: **{bal:.2f} টাকা**", parse_mode='Markdown')

    elif query.data == 'bonus':
        # এখানে টাকা যোগ করার লজিক (অটোমেটিক)
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id=?", (DAILY_BONUS, user_id))
        conn.commit()
        await query.message.reply_text(f"🎁 অভিনন্দন! আপনি আজকের ডেইলি বোনাস {DAILY_BONUS} টাকা পেয়েছেন।")

    elif query.data == 'earn':
        # ভিডিও টাস্ক বাটন
        earn_btn = [[InlineKeyboardButton("📺 ভিডিও দেখুন (টাকা পাবেন)", url=YT_LINK)],
                    [InlineKeyboardButton("✅ কাজ শেষ (টাকা নিন)", callback_data='add_video_money')]]
        await query.message.reply_text("🚀 ভিডিওটি ১ মিনিট দেখুন এবং টাকা সংগ্রহ করুন।", reply_markup=InlineKeyboardMarkup(earn_btn))

    elif query.data == 'add_video_money':
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id=?", (VIDEO_BONUS, user_id))
        conn.commit()
        await query.message.reply_text(f"✅ ভিডিও দেখার জন্য {VIDEO_BONUS} টাকা আপনার ব্যালেন্সে যোগ হয়েছে!")

    elif query.data == 'refer':
        bot_username = context.bot.username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        await query.message.reply_text(f"👥 **আপনার রেফার লিংক:**\n{ref_link}\n\nপ্রতি রেফারে পাবেন {REFER_BONUS} টাকা।")

    elif query.data == 'help':
        help_btn = [[InlineKeyboardButton("💬 সরাসরি মেসেজ দিন", url=ADMIN_LINK)]]
        await query.message.reply_text("❓ যেকোনো সমস্যার জন্য অ্যাডমিনকে মেসেজ দিন।", reply_markup=InlineKeyboardMarkup(help_btn))

    elif query.data == 'withdraw':
        await query.message.reply_text("💳 মিনিমাম উইথড্র ৫০ টাকা। আপনার ব্যালেন্স পর্যাপ্ত হলে অ্যাডমিনকে জানান।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
