# ----- REQUIRED IMPORTS -----

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from core.core_helpers import split_message

# ----- MESSAGE HANDLING -----

async def send_large_message(context, chat_id: int, text: str):
    """Handle Telegram's message length limits"""
    for part in split_message(text):
        await context.bot.send_message(chat_id=chat_id, text=part)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END