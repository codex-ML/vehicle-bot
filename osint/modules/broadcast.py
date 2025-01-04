from pyrogram import Client, filters
from pyrogram.types import Message
from osint.core.db import get_all_users
import os
import platform
from osint import app

@app.on_message(filters.command("broadcast") & filters.user(6621610889))
async def broadcast(client: Client, message: Message):
    """
    Broadcasts a custom message to all users.
    Usage: /broadcast <your message here>
    """
    # Ensure the command has additional text
    if len(message.command) < 2:
        await message.reply_text("Usage: /broadcast <message>")
        return

    # Extract the broadcast message
    broadcast_message = message.text.split(' ', 1)[1].strip()

    if not broadcast_message:
        await message.reply_text("Please provide a message to broadcast.")
        return

    # Fetch all users from the database
    users_cursor = get_all_users()

    total_sent, total_failed = 0, 0

    # Iterate over each user and send the broadcast message
    for user in users_cursor:
        try:
            await client.send_message(chat_id=user["user_id"], text=broadcast_message)
            total_sent += 1
        except Exception as e:
            total_failed += 1
            print(f"Failed to send message to {user['user_id']}: {e}")

    # Send a summary of the broadcast
    await message.reply_text(
        f"📢 Broadcast completed!\n\n✅ Total Sent: {total_sent}\n❌ Total Failed: {total_failed}"
    )


@app.on_message(filters.command("replybroadcast") & filters.user(6621610889))
async def reply_broadcast(client: Client, message: Message):
    """
    Broadcasts a custom message to all users, even when replying to another message.
    Usage: /replybroadcast <your message here>
    """
    # Ensure the command has additional text
    if len(message.command) < 2:
        await message.reply_text("Usage: /replybroadcast <message>")
        return

    # Extract the broadcast message explicitly provided
    broadcast_message = message.text.split(' ', 1)[1].strip()

    if not broadcast_message:
        await message.reply_text("Please provide a message to broadcast.")
        return

    # Fetch all users from the database
    users_cursor = get_all_users()

    total_sent, total_failed = 0, 0

    # Iterate over each user and send the broadcast message
    for user in users_cursor:
        try:
            await client.send_message(chat_id=user["user_id"], text=broadcast_message)
            total_sent += 1
        except Exception as e:
            total_failed += 1
            print(f"Failed to send message to {user['user_id']}: {e}")

    # Send a summary of the broadcast
    await message.reply_text(
        f"📢 Reply Broadcast completed!\n\n✅ Total Sent: {total_sent}\n❌ Total Failed: {total_failed}"
    )


