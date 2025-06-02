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

import helper
from helper import (
   format_date, 
)
from scraper import (
    scrape_smu_fbs,
    VALID_BUILDING,
    VALID_FLOOR,
    VALID_FACILITY_TYPE,
    convert_room_capacity
)

# ---- TELEGRAM BOT CONFIGURATION ----

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TARGET_URL = "https://fbs.intranet.smu.edu.sg/home"
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
        await query.edit_message_text(
            text="⚙ Settings Menu:\n"
                 "1. Set SMU Credentials\n"
                 "2. Configure Filters\n"
                 "3. Back to Main",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 Set Credentials", callback_data="set_creds")],
                [InlineKeyboardButton("⚙ Configure Filters", callback_data="config_filters")],
                [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
            ])
        )
    elif query.data == "set_creds":
        await query.edit_message_text("Please enter your SMU email:")
        return SETTING_EMAIL

async def handle_scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle scraping request"""
    query = update.callback_query
    chat_id = query.message.chat_id
    try:
        loop = asyncio.get_event_loop()
        errors = await loop.run_in_executor(None, scrape_smu_fbs, TARGET_URL)
        if errors:
            await helper.send_large_message(context, chat_id, f"⚠ Errors occurred:\n{json.dumps(errors, indent=2)}")
        else:
            with open("./booking_log/scraped_log.json") as f:
                data = json.load(f)
                formatted = json.dumps(data["scraped"]["result"], indent=2)
                await helper.send_large_message(context, chat_id, f"✅ Scraping complete!\nResults:\n{formatted}")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Scraping failed: {str(e)}")

async def settings_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store email and prompt for password"""
    context.user_data["email"] = update.message.text
    await update.message.reply_text("Please enter your SMU password:")
    return SETTING_PASSWORD

async def settings_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store password and complete setup"""
    context.user_data["password"] = update.message.text
    os.environ["SMU_FBS_USERNAME"] = context.user_data["email"]
    os.environ["SMU_FBS_PASSWORD"] = context.user_data["password"]
    await update.message.reply_text("✅ Credentials updated successfully!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# ---- MAIN APPLICATION SETUP ----

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="set_creds")],
        states={
            SETTING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, settings_email)],
            SETTING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, settings_password)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()

# ----- EXECUTION CODE ----

if __name__ == "__main__":
    main()