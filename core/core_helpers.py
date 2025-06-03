# ----- REQUIRED IMPORTS -----

import os
import json
import redis
from typing import Optional, List
from dotenv import load_dotenv
from core.models import UserCredentials

# ----- REDIS CONFIGURATION -----

_redis = None

def init_redis(redis_url: str):
    global _redis
    _redis = redis.Redis.from_url(redis_url)

def get_redis_connection():
    """Get shared Redis connection"""
    return redis.Redis.from_url(os.getenv("REDIS_URL"))

# ----- CORE UTILITIES -----

def remove_duplicates_preserve_order(lst: List) -> List:
    """Remove duplicates from a list while preserving order"""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]

def pretty_print_json(obj: dict):
    print(json.dumps(obj, indent=4))

def write_json(obj: dict, filename: str):
    with open(filename, "w") as f:
        json.dump(obj, f, indent=4)
    print(f"JSON file written to: {filename}")

def format_date(date_input: str) -> str:
    """Convert various date formats to DD-MMM-YYYY"""
    from dateutil.parser import parse  
    try:
        date_obj = parse(date_input)
        return date_obj.strftime("%d-%b-%Y")
    except ValueError:
        return "Invalid date format"

# ----- CREDENTIAL MANAGEMENT -----

def read_credentials() -> Optional[dict]:
    """Read credentials from a .env file"""
    load_dotenv()
    username = os.getenv("SMU_FBS_USERNAME")
    password = os.getenv("SMU_FBS_PASSWORD")
    if not username or not password:
        print("Missing USERNAME or PASSWORD in .env file.")
        return None
    print("Credentials loaded.")
    return {"username": username, "password": password}

def validate_credentials(email: str, password: str) -> bool:
    """Basic SMU credential validation"""
    return "@smu.edu.sg" in email and len(password) >= 8

def store_credentials(chat_id: int, credentials: UserCredentials):
    if _redis:
        _redis.set(f"creds:{chat_id}", credentials.json())

def get_redis_credentials(chat_id: int) -> Optional[UserCredentials]:
    if not _redis:
        return None
    creds_json = _redis.get(f"creds:{chat_id}")
    return UserCredentials(**json.loads(creds_json)) if creds_json else None

# ----- MESSAGE HANDLING -----

def split_message(text: str, max_length: int = 4096) -> List[str]:
    """Split long messages into chunks"""
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]