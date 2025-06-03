# ----- REQUIRED IMPORTS -----

import os
import json
import redis
import itertools
from dotenv import load_dotenv
from typing import Optional
from core.models import UserCredentials

# ----- REDIS CONFIGURATION -----

_redis = None

# ----- HELPER FUNCTIONS -----

def remove_duplicates_preserve_order(lst):
    """Remove duplicates from a list while preserving order"""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def pretty_print_json(obj):
    print(json.dumps(obj, indent=4))

def write_json(obj, filename):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=4)
    print(f"JSON file written to: {filename}")

def read_credentials():
    """Read credentials from a .env file"""
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    if not username or not password:
        print("Missing USERNAME or PASSWORD in .env file.")
        return None
    print("Credentials loaded.")
    return {"username": username, "password": password}

def format_date(date_input):
    """Convert various date formats to DD-MMM-YYYY"""
    try:
        date_obj = parse(date_input)
        return date_obj.strftime("%d-%b-%Y")
    except ValueError:
        return "Invalid date format"

def split_message(text: str, max_length: int = 4096) -> list:
    """Split long messages for Telegram"""
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

async def send_large_message(context, chat_id, text):
    """Handle Telegram's message length limits"""
    for part in split_message(text):
        await context.bot.send_message(chat_id=chat_id, text=part)

def init_redis(redis_url: str):
    global _redis
    _redis = redis.Redis.from_url(redis_url)

async def get_redis_credentials(chat_id: int) -> Optional[UserCredentials]:
    if not _redis:
        return None
    creds_json = _redis.get(f"creds:{chat_id}")
    return UserCredentials(**json.loads(creds_json)) if creds_json else None

async def store_credentials(chat_id: int, credentials: UserCredentials):
    if _redis:
        _redis.set(f"creds:{chat_id}", credentials.json())

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END