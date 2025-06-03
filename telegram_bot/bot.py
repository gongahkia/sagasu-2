# ----- REQUIRED IMPORTS -----

import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

from core import helper
from core.scraper_service import scrape_task  
from core.models import UserCredentials  

# ---- TELEGRAM BOT CONFIGURATION ----

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SETTING_EMAIL, SETTING_PASSWORD = range(2)

# ---- BOT HANDLERS ----

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initial command with inline keyboard"""
    keyboard = [
        [InlineKeyboardButton("🔍 Scrape Now", callback_data="scrape_now")],
        [InlineKeyboardButton("⚙ Settings", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to Sagasu 2 - SMU Room Availability Bot\n"
        "Choose an action:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    if query.data == "scrape_now":
        await handle_scrape(update, context)
    elif query.data == "settings":
        await show_settings_menu(query)
    elif query.data == "set_creds":
        await query.edit_message_text("Please enter your SMU email:")
        return SETTING_EMAIL

async def handle_scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle scraping request through shared service"""
    query = update.callback_query
    chat_id = query.message.chat_id
    try:
        creds = await helper.get_redis_credentials(chat_id)
        if not creds:
            await context.bot.send_message(chat_id, "❌ No credentials set! Configure in settings first.")
            return
        task = scrape_task.delay({
            "buildings": ["Li Ka Shing Library"],  
            "floors": ["Level 1"],
            "email": creds.email,
            "password": creds.password
        })
        await query.answer("⏳ Scraping started...")
        while not task.ready():
            await asyncio.sleep(2)
            await query.edit_message_text(f"⏳ Status: {task.state}")
        result = task.get()
        if result['status'] == 'success':
            formatted = json.dumps(result['data'], indent=2)
            await helper.send_large_message(context, chat_id, f"✅ Scraping complete!\nResults:\n{formatted}")
        else:
            await context.bot.send_message(chat_id, f"❌ Error: {result['message']}")
    except Exception as e:
        await context.bot.send_message(chat_id, f"❌ Scraping failed: {str(e)}")

async def settings_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store email and prompt for password"""
    context.user_data["email"] = update.message.text
    await update.message.reply_text("Please enter your SMU password:")
    return SETTING_PASSWORD

async def settings_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store credentials in Redis"""
    chat_id = update.message.chat_id
    password = update.message.text
    email = context.user_data["email"]
    await helper.store_credentials(
        chat_id=chat_id,
        credentials=UserCredentials(email=email, password=password)
    )
    await update.message.reply_text("✅ Credentials updated successfully!")
    return ConversationHandler.END

# ---- MAIN APPLICATION SETUP ----

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    helper.init_redis(REDIS_URL)
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="set_creds")],
        states={
            SETTING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, settings_email)],
            SETTING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, settings_password)]
        },
        fallbacks=[CommandHandler("cancel", helper.cancel)],
        per_message=True  
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running in hybrid mode...")
    app.run_polling()

# ----- EXECUTION CODE ----

if __name__ == "__main__":
    main()