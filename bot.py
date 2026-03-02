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
MIN_WITHDRAW = 20 # সর্বনিম্ন ২০ টাকা হলে উইথড্র করা যাবে

# ডাটাবেস
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    await update.message.reply_text("👋 স্বাগতম! কাজ শুরু করতে নিচের বাটনগুলো ব্যবহার করুন।", reply_markup=get_main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == 'bal':
        cursor.execute("SELECT balance FROM users WHERE id=?", (query.from_user.id,))
        bal = cursor.fetchone()[0]
        await query.edit_message_text(f"💰 আপনার বর্তমান ব্যালেন্স: {bal:.2f} টাকা", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]]))
    
    elif data == 'withdraw':
        cursor.execute("SELECT balance FROM users WHERE id=?", (query.from_user.id,))
        bal = cursor.fetchone()[0]
        if bal < MIN_WITHDRAW:
            await query.answer(f"❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! (মিনিমাম {MIN_WITHDRAW} টাকা)", show_alert=True)
        else:
            await query.edit_message_text(f"💸 আপনার ব্যালেন্স {bal:.2f} টাকা।\nউইথড্র করতে আপনার বিকাশ/নগদ নম্বরটি এখানে লিখুন।", 
                                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]]))
            context.user_data['waiting_for_number'] = True

    elif data == 'main_menu':
        await query.edit_message_text("👋 মেইন মেনু: কাজ শুরু করতে নিচে ক্লিক করুন।", reply_markup=get_main_menu())

    elif data == 'submit_proof':
        await query.edit_message_text("📸 অনুগ্রহ করে আপনার কাজের স্ক্রিনশটটি এখানে পাঠান।", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]]))

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

# মেসেজ হ্যান্ডেলার (নম্বর গ্রহণ করার জন্য)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_number'):
        user = update.effective_user
        number = update.message.text
        cursor.execute("SELECT balance FROM users WHERE id=?", (user.id,))
        bal = cursor.fetchone()[0]
        
        # অ্যাডমিন চ্যানেলে রিকোয়েস্ট পাঠানো
        await context.bot.send_message(chat_id=LOG_CHANNEL_ID, 
                                     text=f"💸 **পেমেন্ট রিকোয়েস্ট!**\n👤 নাম: {user.first_name}\n🆔 আইডি: `{user.id}`\n💰 পরিমাণ: {bal:.2f} TK\n📞 নম্বর: `{number}`")
        
        cursor.execute("UPDATE users SET balance = 0 WHERE id=?", (user.id,))
        conn.commit()
        context.user_data['waiting_for_number'] = False
        await update.message.reply_text("✅ আপনার পেমেন্ট রিকোয়েস্ট পাঠানো হয়েছে! অ্যাডমিন চেক করে টাকা পাঠিয়ে দেবেন।", reply_markup=get_main_menu())

async def handle_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo_id = update.message.photo[-1].file_id
    keyboard = [[InlineKeyboardButton("✅ Approve 5 TK", callback_data=f"app_{user.id}_5")],
                [InlineKeyboardButton("❌ Reject", callback_data=f"rej_{user.id}")]]
    
    try:
        await context.bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo_id, 
                                   caption=f"📩 **প্রুফ সাবমিশন**\n👤 নাম: {user.first_name}\n🆔 আইডি: `{user.id}`", 
                                   reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        await update.message.reply_text("✅ আপনার প্রুফটি জমা হয়েছে।", reply_markup=get_main_menu())
    except:
        await update.message.reply_text("⚠️ এরর: বটকে আপনার চ্যানেলে অ্যাডমিন করুন।")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_proof))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.run_polling()
