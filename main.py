import csv
import logging
import re
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, Message
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pyrogram.errors import FloodWait

from time import sleep
import asyncio
import os

# Bot credentials
API_ID = 22108239
API_HASH = "72b103fb198143c9b8e739784eb5d557"
BOT_TOKEN = "6417942588:AAEE86o9kKFj6nt4O10ZQqwnWJT_Y8MvYWQ"  # Replace with your Bot Token
MONGO_URI = "mongodb+srv://akg:akg8894@cluster0.ajoin.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB connection string

# Initialize the bot
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client["telegram_bot"]
users_collection = db["users"]

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_message(filters.command(["start"]))
async def start(client, message):
    user_id = message.from_user.id

    # Check if user is already in the database
    if not users_collection.find_one({"user_id": user_id}):
        # Add user to the database
        users_collection.insert_one({"user_id": user_id})

    # Inline keyboard with web app and help buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Open Web App", web_app=WebAppInfo(url="https://codex-ml.github.io/vehicle/"))],
        [InlineKeyboardButton("Help", callback_data="help"), InlineKeyboardButton("Support", url="https://t.me/how_to_use_source")]
    ])

    # Send the video with the caption and keyboard
    sent_message = await client.send_video(
        chat_id=user_id,
        video="http://codex-ml.tech/videos/vehi.mp4",
        caption=(
            "Welcome to the bot! Click the buttons below for more options.\n\n"
            "**How to use this BOT**\n"
            "**इस रोबोट का उपयोग कैसे करें**"
        ),
        reply_markup=keyboard
    )

    # Wait for 10 seconds
    await asyncio.sleep(10)

    # Replace the button with a "Restart" button
    restart_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Restart", callback_data="restart")]
    ])
    await client.edit_message_reply_markup(
        chat_id=sent_message.chat.id,
        message_id=sent_message.id,
        reply_markup=restart_keyboard
    )

@app.on_callback_query(filters.regex("help"))
async def help_callback(client, callback_query):
    await callback_query.answer()
    await callback_query.message.reply_text(
        "Here is how you can use this bot:\n\n"
        "1. Use the 'Open Web App' button to access the vehicle info.\n"
        "3. Use the /stats command to check user statistics.\n\n"
        "For further assistance, contact [Support](https://t.me/+Y9O5ptuPEFs3NGE1).",
        disable_web_page_preview=True
    )

@app.on_callback_query(filters.regex("restart"))
async def restart_callback(client, callback_query):
    await callback_query.answer("Restarting...")
    await callback_query.message.reply_text("Click /start to begin again.")

@app.on_message(filters.command(["stats"]))
async def stats(client, message):
    total_users = users_collection.count_documents({})
    await message.reply_text(f"Total number of users: {total_users}")

@app.on_message(filters.command(["check"]))
async def check_duplicates(client, message: Message):
    # Find duplicate user IDs
    duplicates = users_collection.aggregate([
        {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ])

    duplicates_to_remove = []
    for duplicate in duplicates:
        user_id = duplicate["_id"]
        entries = list(users_collection.find({"user_id": user_id}))
        if len(entries) > 1:
            duplicates_to_remove.extend(entry["_id"] for entry in entries[1:])

    if duplicates_to_remove:
        users_collection.delete_many({"_id": {"$in": duplicates_to_remove}})
        await message.reply_text(f"Removed {len(duplicates_to_remove)} duplicate user entries.")
    else:
        await message.reply_text("No duplicate user entries found.")

@app.on_message(filters.command(["broadcast"]))
async def broadcast(client, message: Message):
    if not message.text.startswith("/broadcast "):
        return

    broadcast_message = message.text[len("/broadcast "):].strip()
    users = users_collection.find()
    total_sent, total_failed = 0, 0

    for user in users:
        try:
            await client.send_message(user["user_id"], broadcast_message)
            total_sent += 1
        except Exception as e:
            total_failed += 1

    await message.reply_text(
        f"Broadcast completed!\nTotal Sent: {total_sent}\nTotal Failed: {total_failed}"
    )



@app.on_message(filters.text & filters.regex(r'^[A-Za-z0-9]{10}$'))
async def handle_vehicle_request(client, message: Message):
    regno = message.text.strip()
    api_url = f"https://a182-20-244-44-82.ngrok-free.app/?regno={regno}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and 'detail' in data['data']:
            full_details = data['data']['detail']['full_details']
            details_dict = eval(full_details)  # Convert the string to a dictionary

            # Format the details into a table
            details_table = "\n".join([f"{key}: {value}" for key, value in details_dict.items()])

            await message.reply_text(f"Vehicle Details:\n\n{details_table}")
        else:
            await message.reply_text("No vehicle details found.")
    except requests.RequestException as e:
        await message.reply_text(f"Error fetching vehicle details: {str(e)}")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app.run()
