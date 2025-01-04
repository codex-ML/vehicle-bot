import os
import asyncio
import importlib
import logging
import random
from pyrogram import idle
from pyrogram.client import Client
from osint import app
from osint.modules import ALL_MODULES
from osint.core.db import add_user, get_user_count, user_exists
from pyrogram import filters, errors
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, CallbackQuery, WebAppInfo
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from pyrogram.errors import FloodWait, PeerIdInvalid
from config import CHANNEL
from osint import app
import subprocess
import shlex
from pyrogram.errors import FloodWait
import time
import threading
from datetime import datetime

loop = asyncio.get_event_loop()


async def init():
  await app.start()
  for all_module in ALL_MODULES:
    importlib.import_module("osint.modules." + all_module)
    print(f"LOADING {all_module} ...")
  # await app.start()

  print(f"""OSINT """)
  await idle()


def send_heartbeat():
  logging.info("Worker is alive.")
  print("Worker is alive.")


def main_worker_logic():
  while True:
    print("AKG OP ")
    send_heartbeat()
    time.sleep(300)


print(f"""\n
  ___           _     _                       
 |   \ ___ _ __| |___(_)_ _  __ _             
 | |) / -_) '_ \ / _ \ | ' \/ _` |  _   _   _ 
 |___/\___| .__/_\___/_|_||_\__, | (_) (_) (_)
          |_|               |___/             
""")

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format=
    '%(asctime)s - %(levelname)s - %(message)s',  # Define log message format
    filename='app.log',  # Log file name
    filemode='w')  # Set log file mode to 'write'

# Create a logger
logger = logging.getLogger()

# Log messages at different levels
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')


def check_user_in_channel(func):

  async def wrapper(_, message: Message):

    channel_id = CHANNEL
    user_id = message.from_user.id
    try:
      await app.get_chat_member(channel_id, user_id)
      await func(_, message)
    except Exception as e:
      abtbtn = InlineKeyboardMarkup([[
          InlineKeyboardButton("JOIN CHANNEL FOR UPDATES",
                               url="https://t.me/+hSIRZreoC1dkODg9")
      ]])
      join_message = """
      🌟 **Welcome to the Bot!** 🌟

      🇬🇧 **English**: First, you have to join our support group. Then you can use the bot.

      🇮🇳 **हिंदी**: सबसे पहले आपको हमारे सहायता समूह से जुड़ना होगा। उसके बाद आप इस बॉट का उपयोग कर सकते हैं.

      🔗 **Join Now:** [Support Group](https://t.me/source_code_network)
      """
      await message.reply_text(join_message, reply_markup=abtbtn)

  return wrapper


@app.on_message(filters.command("start"))
async def start(client, msg):
  user_id = msg.from_user.id
  username = msg.from_user.username
  user_name = msg.from_user.first_name or "User"
  user_id = msg.from_user.id
  current_time = datetime.now().strftime("%H:%M:%S")
  current_date = datetime.now().strftime("%Y-%m-%d")

  welcome_message = f"""
  ━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✨ **Welcome, {user_name}!** ✨
  ━━━━━━━━━━━━━━━━━━━━━━━━━━

  👤 **User Details:**
  ╭───────────────╮
  ├ 🆔 User ID: `{user_id}`
  ├ ⏰ Time: `{current_time}`
  ├ 📅 Date: `{current_date}`
  ╰───────────────╯

  📖 **Commands:**
  ╭───────────────╮
  ├ 📜 **/help**: View all available commands
  ├ 🔄 **/start**: Restart the bot
  ├ 🔄 **//info**:To get Vehicle info 
  ╰───────────────╯

      🇬🇧 **English**: First, you have to join our support group. Then you can use the bot.

      🇮🇳 **हिंदी**: सबसे पहले आपको हमारे सहायता समूह से जुड़ना होगा। उसके बाद आप इस बॉट का उपयोग कर सकते हैं.

  🔗 **Join Us:** 
  [Click here to join our channel/group!](https://t.me/source_code_network)

  ━━━━━━━━━━━━━━━━━━━━━━━━━━
  😊 Enjoy your experience with the bot!
  ━━━━━━━━━━━━━━━━━━━━━━━━━━
  """
  if not user_exists(user_id):
    add_user(user_id, username)

  keyboard = InlineKeyboardMarkup(
      [[InlineKeyboardButton("Support",
                             url="https://t.me/+hSIRZreoC1dkODg9")]])
  try:
    await app.get_chat_member(CHANNEL, user_id)
    await msg.reply_text(welcome_message, reply_markup=keyboard)
  except Exception as e:
    abtbtn = InlineKeyboardMarkup([[
        InlineKeyboardButton("JOIN CHANNEL FOR UPDATES",
                             url="https://t.me/+hSIRZreoC1dkODg9")
    ]])
    await msg.reply_text(welcome_message,
        reply_markup=abtbtn)


@app.on_message(filters.new_chat_members)
async def welcome_message(client, message):
  for member in message.new_chat_members:
    # Send a private message to the new member
    user_name = message.from_user.first_name or "User"
    user_id = message.from_user.id
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")

    welcome_message = f"""
    ━━━━━━━━━━━━━━━━━━━━━━━━━━
    ✨ **Welcome, {user_name}!** ✨
    ━━━━━━━━━━━━━━━━━━━━━━━━━━

    👤 **User Details:**
    ╭───────────────╮
    ├ 🆔 User ID: `{user_id}`
    ├ ⏰ Time: `{current_time}`
    ├ 📅 Date: `{current_date}`
    ╰───────────────╯

    📖 **Commands:**
    ╭───────────────╮
    ├ 📜 **/help**: View all available commands
    ├ 🔄 **/start**: Restart the bot
    ╰───────────────╯

    🔗 **Join Us:** 
    [Click here to join our channel/group!](https://t.me/source_code_network)

    ━━━━━━━━━━━━━━━━━━━━━━━━━━
    😊 Enjoy your experience with the bot!
    ━━━━━━━━━━━━━━━━━━━━━━━━━━
    """
    await client.send_message(chat_id=member.id, text=welcome_message)





        
        
if __name__ == "__main__":
  loop.run_until_complete(init())
  print("Stopping Bot! GoodBye")
