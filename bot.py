import requests
import re
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

BOT_TOKEN = "8906698752:AAGTOoFa7YPH_H2pOwiQQp58034aIy_B9C8"

COUNTRIES = {
    "MM": "Myanmar",
    "TH": "Thailand",
    "PH": "Philippines",
    "ID": "Indonesia",
    "MY": "Malaysia",
    "SG": "Singapore",
    "VN": "Vietnam"
}

# ========== Flask Web Server (Keep Alive အတွက်) ==========
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is alive! 🤖"

def run():
    flask_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Region Checker Bot**\n\n"
        "Send me MLBB ID like:\n"
        "• `1220968187 8948`\n"
        "• `1220968187(8948)`\n\n"
        "I'll detect automatically! 😍"
    )

async def check_region(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id, server_id):
    try:
        checking_msg = await update.message.reply_text(
            "⏳ **Checking region...**",
            parse_mode="Markdown"
        )
        
        url = "https://xpreloads.com/api/api/mlbb"
        headers = {"x-custom-token": "narbu-frontend"}
        params = {"user_id": user_id, "server_id": server_id}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        username = data.get("username", "Unknown")
        country_code = data.get("country", "Unknown")
        country_name = COUNTRIES.get(country_code, country_code)
        
        msg = (
            f"🎮 **Mobile Legends Information**\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Name**: `{username.replace('+', ' ')}`\n"
            f"🆔 **ID**: `{user_id}` ({server_id})\n"
            f"🌍 **Region**: {country_name}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📋 `{user_id} ({server_id})`"
        )
        
        keyboard = [[InlineKeyboardButton("📋 Copy", callback_data=f"copy_{user_id}_{server_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await checking_msg.edit_text(
            msg,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        pass

async def auto_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ""
    if update.message.text:
        text = update.message.text
    elif update.message.caption:
        text = update.message.caption
    
    if not text:
        return
    
    text = text.strip()
    
    patterns = [
        r'(\d{9,10})\s*[\(\s]?(\d{4})[\)\s]?',
        r'(\d{9,10})\s+(\d{4})',
    ]
    
    user_id = None
    server_id = None
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            user_id = match.group(1)
            server_id = match.group(2)
            break
    
    if not user_id or not server_id:
        return
    
    await check_region(update, context, user_id, server_id)

async def copy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

# ========== Main Function ==========
def main():
    # Keep Alive ကို အရင်ခေါ်ပါ (Web Server စဖွင့်မယ်)
    keep_alive()
    
    # ပြီးမှ Bot ကို Start လုပ်ပါ
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(copy_callback, pattern="^copy_"))
    
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.CAPTION, 
        auto_check
    ))
    
    print("🤖 Bot Started... Auto-detect mode enabled!")
    app.run_polling()
# ==================================

if __name__ == "__main__":
    main()
