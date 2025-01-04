from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from osint import app
from osint.core.db import get_user_count

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """
    Sends a help message with user details, bot statistics, and commands.
    Usage: /help
    """
    user_name = message.from_user.first_name or "User"
    user_id = message.from_user.id
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    user_count = get_user_count()

    help_message = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **Welcome, {user_name}!** ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 **User Details:**
╭───────────────╮
├ 🆔 User ID: `{user_id}`
├ ⏰ Time: `{current_time}`
├ 📅 Date: `{current_date}`
╰───────────────╯

📊 **Bot Statistics:**
👥 Total Users: `{user_count}`

📖 **How to Use the Bot:**
╭───────────────╮
├ ✉️ **/info <vehicle_number>**:To get Vehicle details .
├ 📊 **/stats**: View bot statistics.
├ 📢 **/broadcast <message>**: Send a custom message to all users. *(Admin only)*
├ 🔄 **/start**: Restart the bot interaction.
├ 📜 **/help**: View this help message.
╰───────────────╯

🔗 **Join Us:** 
[Click here to join our channel/group!](#)

━━━━━━━━━━━━━━━━━━━━━━━━━━
😊 Enjoy your experience with the bot!
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    await message.reply_text(help_message)
