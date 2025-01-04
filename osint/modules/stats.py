from pyrogram.client import Client
from pyrogram import Client, filters
from osint import app
from osint.core.db import get_user_count
from pyrogram.types import Message

@app.on_message(filters.command("stats") & filters.user(6621610889))
async def stats(client: Client, message: Message):
    """
    Provides statistics about the bot.
    Usage: /stats
    """
    from osint.core.db import get_user_count

    user_count = get_user_count()
    await message.reply_text(text=f"📊 **Bot Statistics**\n\n👥 Total Users: {user_count}")
