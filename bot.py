import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# --- ১. কনফিগারেশন ---
TOKEN = "8629892440:AAFg8jGPFc9UTzFj1CaBNlMqdrjnq38nGzg" 
ADMIN_ID = 6578678699 
ADMIN_USERNAME = "Molla019" 
LOG_CHANNEL_ID = -1003732172008 # আপনার চ্যানেল আইডি

YT_LINK = "https://www.youtube.com/@skFarhan-u7z" 
TIKTOK_LINK = "https://www.tiktok.com/@user469378505" 

# ডাটাবেস
conn = sqlite3.connect("income_master.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)")
conn.commit()

# মেনু কিবোর্ড (যাতে বারবার ব্যবহার করা যায়)
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🔴 Subscribe YouTube", url=YT_LINK)],
        [InlineKeyboardButton("🎵 Follow TikTok", url=TIKTOK_LINK)],
        [InlineKeyboardButton("📸 Submit Screenshot", callback_data='submit_proof')],
        [InlineKeyboardButton("💰 Balance", callback_data='bal')],
        [InlineKeyboardButton("❓ Help (Contact Admin)", url=f"https://t.me/{ADMIN_USERNAME}")]
    ]
    return InlineKeyboardMarkup(keyboard)

# স্টার্ট কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    
    await update.message.reply_text(
        "👋 স্বাগতম! কাজ শুরু করতে আমাদের সোশ্যাল মিডিয়া ফলো করুন।\nসব কাজ শেষ করে স্ক্রিনশট দিন।",
        reply_markup=get_main_menu()
    )

# বাটন ক্লিক হ্যান্ডেলার (মেসেজ এডিট হবে)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == 'bal':
        cursor.execute("SELECT balance FROM users WHERE id=?", (query.from_user.id,))
        bal = cursor.fetchone()[0]
        # এখানে মেসেজটি এডিট হয়ে ব্যালেন্স দেখাবে এবং নিচে ব্যাক বাটন থাকবে
        back_button = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data='main_menu')]]
        await query.edit_message_text(
            f"💰 আপনার বর্তমান ব্যালেন্স: {bal:.2f} টাকা",
            reply_markup=InlineKeyboardMarkup(back_button)
        )
    
    elif data == 'main_menu':
        # আবার মূল মেনুতে ফিরে আসবে (মেসেজ এডিট হবে)
        await query.edit_message_text(
            "👋 মেইন মেনু: কাজ শুরু করতে নিচে ক্লিক করুন।",
            reply_markup=get_main_menu()
        )

    elif data == 'submit_proof':
        await query.edit_message_text(
            "📸 অনুগ্রহ করে আপনার কাজের স্ক্রিনশটটি এখানে পাঠান।",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]])
        )

    # অ্যাডমিন পার্ট (চ্যানেল থেকে)
    elif data.startswith(("app_", "rej_")):
        if query.from_user.id != ADMIN_ID: return
        info = data.split("_")
        user_id = int(info[1])
        if data.startswith("app_"):
            amount = float(info[2])
            cursor.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amount, user_id))
            conn.commit()
            await query.edit_message_caption(caption=query.message.caption + f"\n\n✅ Approved!")
            await context.bot.send_message(chat_id=user_id, text=f"💰 অভিনন্দন! {amount} টাকা যোগ হয়েছে।")
        elif data.startswith("rej_"):
            await query.edit_message_caption(caption=query.message.caption + f"\n\n❌ Rejected!")
            await context.bot.send_message(chat_id=user_id, text="❌ আপনার প্রুফটি সঠিক নয়।")

# স্ক্রিনশট হ্যান্ডেলার
async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo_id = update.message.photo[-1].file_id
    keyboard = [[InlineKeyboardButton("✅ Approve 5 TK", callback_data=f"app_{user.id}_5")],
                [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user.id}")]]
    
    try:
        await context.bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo_id, 
                                   caption=f"📩 নতুন প্রুফ!\n👤 নাম: {user.first_name}\n🆔 আইডি: `{user.id}`", 
                                   reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        # ইউজারের ইনবক্সে কনফার্মেশন দিবে
        await update.message.reply_text("✅ আপনার প্রুফটি পাঠানো হয়েছে!", reply_markup=get_main_menu())
    except:
        await update.message.reply_text("⚠️ এরর: বট আপনার প্রুফ চ্যানেলে অ্যাডমিন নয়।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_proof))
    app.run_polling()
