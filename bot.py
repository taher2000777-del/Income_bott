import sqlite3, time, random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# আপনার নতুন টোকেনটি এখানে বসান (BotFather থেকে নেওয়া)
TOKEN = "8629892440:AAHdMFBKf8UmV4XfBb3iaLOrImINb8sbH6c"
ADMIN_ID = 6578678699

AD_LINKS = [
    "https://www.effectivegatecpm.com/c5bkk9ri?key=e70ce0917c41f2b210097d5e180434ff",
    "https://www.effectivegatecpm.com/d1fbg3v9?key=c57248232f041c52fb2315142ba1b831",
    "https://www.effectivegatecpm.com/w3gjaezfm?key=c8f7c78728555572c9078a0a2fa04107",
    "https://www.effectivegatecpm.com/r66djn1h?key=23c7dd7b9f21469d099225a717c8f556",
    "https://www.effectivegatecpm.com/n5biffq8m?key=9bb4f41a938d9ec6b8437244aa6c12cc"
]

EXTRA_SITES = [
    {"name": "🔥 Free Crypto Faucet", "url": "https://faucetcrypto.com/"},
    {"name": "🚀 Best Survey Site", "url": "https://www.swagbucks.com/"}
]

conn = sqlite3.connect("income_bot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, lang TEXT DEFAULT "bn")')
conn.commit()

strings = {
    'bn': {
        'main_menu': "┏━━━━━━━━━━━━━━━━━━┓\n   💎  **S u p e r  I n c o m e** 💎\n┗━━━━━━━━━━━━━━━━━━┛\n\nসেরা সব ইনকাম সুযোগ এখানে!",
        'earn': "💰 এডেস্টেরা আয়",
        'sites': "🔥 সেরা ইনকাম সাইট",
        'profile': "👤 প্রোফাইল",
        'withdraw': "💳 উইথড্র (Binance)",
        'link_msg': "🎁 **Reward Link Ready!**\n\n🔗 [এখানে ক্লিক করুন]({})\n\n⚠️ ৩০ সেকেন্ড পর **০.০১ USDT** পাবেন!"
    },
    'en': {
        'main_menu': "┏━━━━━━━━━━━━━━━━━━┓\n   💎  **S u p e r  I n c o m e** 💎\n┗━━━━━━━━━━━━━━━━━━┛\n\nBest earning opportunities here!",
        'earn': "💰 Adsterra Earning",
        'sites': "🔥 Best Income Sites",
        'profile': "👤 My Profile",
        'withdraw': "💳 Withdraw (Binance)",
        'link_msg': "🎁 **Reward Link Ready!**\n\n🔗 [Click Here]({})\n\n⚠️ Stay 30s to get **0.01 USDT**!"
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    keyboard = [[InlineKeyboardButton("বাংলা 🇧🇩", callback_data='set_bn'), InlineKeyboardButton("English 🇺🇸", callback_data='set_en')]]
    await update.message.reply_text("✨ Choose Language:", reply_markup=InlineKeyboardMarkup(keyboard))

async def menu(update: Update, lang):
    keyboard = [
        [InlineKeyboardButton(strings[lang]['earn'], callback_data='earn')],
        [InlineKeyboardButton(strings[lang]['sites'], callback_data='extra_sites')],
        [InlineKeyboardButton(strings[lang]['profile'], callback_data='profile'), InlineKeyboardButton(strings[lang]['withdraw'], callback_data='withdraw')],
        [InlineKeyboardButton("🌐 Change Language", callback_data='start_lang')]
    ]
    await update.callback_query.edit_message_text(strings[lang]['main_menu'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cursor.execute("SELECT lang, balance FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()
    lang, balance = data if data else ('bn', 0.0)

    if query.data.startswith('set_'):
        new_lang = query.data.split('_')[1]
        cursor.execute("UPDATE users SET lang=? WHERE user_id=?", (new_lang, user_id))
        conn.commit()
        await menu(update, new_lang)
    elif query.data == 'extra_sites':
        btns = [[InlineKeyboardButton(site['name'], url=site['url'])] for site in EXTRA_SITES]
        btns.append([InlineKeyboardButton("⬅️ Back", callback_data='set_'+lang)])
        await query.edit_message_text("🚀 **Best Income Sites:**", reply_markup=InlineKeyboardMarkup(btns), parse_mode='Markdown')
    elif query.data == 'earn':
        link = random.choice(AD_LINKS)
        cursor.execute("UPDATE users SET balance = balance + 0.01 WHERE user_id=?", (user_id,))
        conn.commit()
        await query.message.reply_text(strings[lang]['link_msg'].format(link), parse_mode='Markdown', disable_web_page_preview=True)
    elif query.data == 'profile':
        await query.edit_message_text(f"💰 **Balance:** {balance:.4f} USDT", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='set_'+lang)]]), parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()
