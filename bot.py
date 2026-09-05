#!/usr/bin/env python3
"""
Telegram Number Info Bot
A complete Telegram bot for fetching mobile number information from an API.
"""

import json
import logging
import re
import time
from typing import Dict, List, Optional, Any

import requests
import telebot
from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton

# ===================================================
# CONFIGURATION
# ===================================================
BOT_TOKEN = "8936205112:AAFniSWYU_I0kJFfUi0pEK8_OMOR9Zp2ECE"

API_URL = "https://ansh-apis.is-dev.org/api/creta?key=ansh&num="

# ===================================================
# LOGGING SETUP
# ===================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================================================
# BOT INITIALIZATION
# ===================================================
try:
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
    bot.get_me()
    logger.info("✅ Bot connected successfully!")
except Exception as e:
    logger.error(f"❌ Bot initialization failed: {e}")
    exit(1)

# ===================================================
# KEYBOARD FUNCTIONS
# ===================================================
def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=False,
        row_width=1
    )
    btn_get_info = KeyboardButton("🔍 Get Info")
    keyboard.add(btn_get_info)
    return keyboard


# ===================================================
# UTILITY FUNCTIONS
# ===================================================
def is_valid_mobile_number(number: str) -> bool:
    number = number.strip()
    return bool(re.match(r'^\d{10}$', number))


def format_record(record: Dict[str, Any], index: int) -> str:
    """
    Format a single record into a beautiful message.
    """
    # Extract data - try both possible field names
    spell = record.get("Spell") or record.get("mobile") or record.get("number") or "Not Available"
    name = record.get("Name") or record.get("name") or record.get("full_name") or "Not Available"
    father_name = record.get("FatherName") or record.get("father_name") or record.get("father") or "Not Available"
    address = record.get("Address") or record.get("address") or record.get("full_address") or "Not Available"
    circle = record.get("Circle") or record.get("circle") or record.get("operator") or "Not Available"
    alternate_num = record.get("AlternateNum") or record.get("alternate_num") or record.get("alternate") or "Not Available"
    aadhar = record.get("Aadhar") or record.get("aadhar") or record.get("aadhar_number") or "Not Available"
    email = record.get("Email") or record.get("email") or record.get("email_id") or "Not Available"
    used_count = record.get("Used_count") or record.get("used_count") or record.get("count") or "Not Available"
    server_time = record.get("Server_Time_IST") or record.get("server_time") or record.get("timestamp") or "Not Available"

    # Clean up address
    if address != "Not Available":
        address = str(address).replace("!!", "\n").replace("!", "\n")

    # Format the message
    message = f"""
╭━━━〔 📱 NUMBER INFO 〕━━━⬣

👤 <b>Name</b>        : {name}
👨 <b>Father</b>      : {father_name}
📞 <b>Mobile</b>      : {spell}
📱 <b>Alternate</b>   : {alternate_num}
📡 <b>Circle</b>      : {circle}
🆔 <b>Aadhar</b>      : {aadhar}
📧 <b>Email</b>       : {email}
📊 <b>Used Count</b>  : {used_count}

🏠 <b>Address</b> :
{address}

⏰ <b>Server Time</b> : {server_time}

━━━━━━━━━━━━━━━━━━━"""
    return message.strip()


def format_no_data(number: str) -> str:
    return f"""
╭━━━〔 ❌ NO DATA FOUND 〕━━━⬣

📞 Number : {number}

⚠️ Is Number Ka Koi Data Nahi Hai.

Please Try Another Number.

╰━━━━━━━━━━━━━━━━━━⬣"""


def format_api_error(error_msg: str) -> str:
    return f"""
╭━━━〔 ⚠️ API ERROR 〕━━━⬣

❌ Error: {error_msg}

Please try again later or use a different number.

╰━━━━━━━━━━━━━━━━━━⬣"""


def fetch_number_info(number: str) -> Optional[Dict[str, Any]]:
    """
    Fetch number information from the API.
    Returns the JSON response as dictionary or None on error.
    """
    try:
        url = f"{API_URL}{number}"
        logger.info(f"Calling API: {url}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=15)
        
        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Content: {response.text[:500]}")  # Log first 500 chars
        
        if response.status_code == 404:
            logger.warning(f"Number {number} not found (404)")
            return {"status": "error", "message": "Not found"}
            
        response.raise_for_status()

        data = response.json()
        logger.info(f"API Response received: {json.dumps(data, indent=2)[:500]}")
        
        return data

    except requests.exceptions.Timeout:
        logger.error(f"Timeout error while fetching number {number}")
        return {"status": "error", "message": "Timeout"}
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error while fetching number {number}")
        return {"status": "error", "message": "Connection Error"}
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e} while fetching number {number}")
        return {"status": "error", "message": str(e)}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response: {e}")
        return {"status": "error", "message": "Invalid JSON Response"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"status": "error", "message": str(e)}


def extract_records(data: Any) -> List[Dict[str, Any]]:
    """
    Extract records from various API response formats.
    """
    records = []
    
    # If data is None or not a dict/list
    if not data:
        return records
    
    # Case 1: Direct list of records
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                records.append(item)
        return records
    
    # Case 2: Dict response
    if isinstance(data, dict):
        # Check for status/error
        if data.get("status") == "error" or data.get("error"):
            logger.warning(f"API returned error: {data}")
            return records
        
        # Check if data itself is a record
        if any(key in data for key in ["Name", "name", "Spell", "mobile", "MobileNum"]):
            records.append(data)
            return records
        
        # Check common data keys
        for key in ["data", "result", "results", "records", "items", "Data", "Result", "Records"]:
            if key in data and data[key]:
                if isinstance(data[key], list):
                    for item in data[key]:
                        if isinstance(item, dict):
                            records.append(item)
                    return records
                elif isinstance(data[key], dict):
                    records.append(data[key])
                    return records
        
        # If no records found, check if any value is a list of dicts
        for key, value in data.items():
            if isinstance(value, list) and value:
                for item in value:
                    if isinstance(item, dict):
                        records.append(item)
                if records:
                    return records
    
    return records


def handle_number_lookup(message: Message, number: str) -> None:
    chat_id = message.chat.id

    searching_msg = bot.send_message(chat_id, "🔍 Searching Information...")

    data = fetch_number_info(number)

    if data is None:
        bot.edit_message_text(
            format_api_error("API Server not responding"),
            chat_id,
            searching_msg.message_id
        )
        return

    # Extract records from the response
    records = extract_records(data)

    if not records:
        no_data_msg = format_no_data(number)
        bot.edit_message_text(no_data_msg, chat_id, searching_msg.message_id)
        return

    # Delete the searching message
    bot.delete_message(chat_id, searching_msg.message_id)

    # Send each record as a separate message
    for idx, record in enumerate(records):
        if isinstance(record, dict):
            formatted_record = format_record(record, idx)
            bot.send_message(chat_id, formatted_record, parse_mode="HTML")
        else:
            bot.send_message(chat_id, f"📊 Data {idx+1}: {str(record)}")

    # Send total records count
    if len(records) > 1:
        bot.send_message(chat_id, f"📊 Total Records Found : {len(records)}")


# ===================================================
# BOT HANDLERS
# ===================================================
@bot.message_handler(commands=['start'])
def handle_start(message: Message) -> None:
    chat_id = message.chat.id
    welcome_message = """
🌟 <b>Welcome to Number Info Bot!</b>

Get detailed information about any Indian mobile number instantly.

Simply press the button below to get started.

━━━━━━━━━━━━━━━━━━━
<b>📌 How it works:</b>
1️⃣ Press <code>🔍 Get Info</code>
2️⃣ Send any 10-digit mobile number
3️⃣ Get detailed information

<i>Powered by Number Info API</i>
"""

    bot.send_message(
        chat_id,
        welcome_message,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@bot.message_handler(func=lambda message: message.text == "🔍 Get Info")
def handle_get_info(message: Message) -> None:
    chat_id = message.chat.id

    info_message = """
📱 <b>Please Send Mobile Number</b>

Example:
<code>1234567890</code>

✅ Send Any Valid 10 Digit Mobile Number.
"""

    bot.send_message(
        chat_id,
        info_message,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@bot.message_handler(content_types=['text'])
def handle_text_messages(message: Message) -> None:
    chat_id = message.chat.id
    user_input = message.text.strip()

    if user_input.startswith('/'):
        return

    if is_valid_mobile_number(user_input):
        handle_number_lookup(message, user_input)
    else:
        error_message = """
❌ <b>Invalid Mobile Number.</b>

Please send a valid 10-digit mobile number.
Example: <code>1234567890</code>
"""

        bot.send_message(
            chat_id,
            error_message,
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )


# ===================================================
# POLLING WITH ERROR HANDLING
# ===================================================
def run_bot() -> None:
    logger.info("Starting Number Info Bot...")
    logger.info(f"Bot Token: {BOT_TOKEN[:10]}...")
    logger.info(f"API URL: {API_URL}")

    while True:
        try:
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=1, timeout=60)
        except telebot.apihelper.ApiTelegramException as e:
            if "404" in str(e):
                logger.error("❌ INVALID BOT TOKEN!")
                break
            else:
                logger.error(f"Telegram API error: {e}")
                time.sleep(5)
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise