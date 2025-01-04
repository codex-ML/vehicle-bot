import json
import logging
import aiohttp  # For asynchronous HTTP requests
from pyrogram import Client, filters
from pyrogram.types import Message
from osint import app  # Assuming `osint.app` is properly configured

# Configure logging
logger = logging.getLogger("vehicle_request")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("vehicle_request.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.on_message(filters.command("info") & filters.private)
async def handle_vehicle_request(client, message: Message):
    command_args = message.text.split(maxsplit=1)

    # Check if registration number is provided
    if len(command_args) < 2:
        await message.reply_text("Please provide a vehicle registration number. Usage: `/info <regno>`")
        logger.warning("Command received without a registration number")
        return

    regno = command_args[1].strip()

    if not regno.isalnum() or len(regno) not in (9, 10):
        await message.reply_text("The vehicle number must be alphanumeric and 9 or 10 characters long.")
        logger.warning("Invalid registration number format")
        return

    logger.debug(f"Received vehicle registration number: {regno}")

    # Send initial loading message
    loading_message = await message.reply_text("WAIT, WE ARE FINDING DATA IN DB")

    api_url = f"https://526f-20-244-85-57.ngrok-free.app/?regno={regno}"
    logger.debug(f"API URL: {api_url}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                response.raise_for_status()
                data = await response.json()
                logger.debug(f"API response data: {data}")

        if "data" in data and "detail" in data["data"]:
            full_details = data["data"]["detail"]["full_details"]
            details_dict = json.loads(full_details)
            logger.debug(f"Vehicle full details: {details_dict}")

            details_table = "\n".join([f"{key}: {value}" for key, value in details_dict.items()])
            await loading_message.edit_text(f"Vehicle Details:\n\n{details_table}")
        else:
            await loading_message.edit_text("No vehicle details found.")
            logger.info("No vehicle details found in the API response")

    except aiohttp.ClientError as e:
        await loading_message.edit_text(f"Error fetching vehicle details: {str(e)}")
        logger.error(f"Error fetching vehicle details: {str(e)}")
    except json.JSONDecodeError as e:
        await loading_message.edit_text(f"Error decoding JSON response: {str(e)}")
        logger.error(f"Error decoding JSON response: {str(e)}")
    except Exception as e:
        await loading_message.edit_text(f"An error occurred: {str(e)}")
        logger.error(f"An unexpected error occurred: {str(e)}")
