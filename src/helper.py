# ----- REQUIRED IMPORTS -----

import os
import json
import itertools
from dotenv import load_dotenv

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