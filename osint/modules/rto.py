import json
import logging
import aiohttp  # For asynchronous HTTP requests
from pyrogram import Client, filters
from pyrogram.types import Message
from osint import app  # Assuming `osint.app` is properly configured
from osint import 
# Configure logging
logger = logging.getLogger("vehicle_request")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("vehicle_request.log")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)




@app.on_message(filters.command("info") & filters.private)
async def handle_vehicle_request(client, message: Message):
    user_id = message.from_user.id
    
    # Check rate limit
    can_proceed, remaining = check_rate_limit(user_id)
    if not can_proceed:
        reset_time = get_reset_time(user_id)
        time_remaining = reset_time - datetime.utcnow()
        minutes_remaining = int(time_remaining.total_seconds() / 60)
        
        await message.reply_text(
            f"❌ You have reached your hourly query limit.\n"
            f"Your limit will reset in approximately {minutes_remaining} minutes."
        )
        logger.warning(f"User {user_id} attempted to exceed rate limit")
        return

    command_args = message.text.split(maxsplit=1)
    
    # Check if registration number is provided
    if len(command_args) < 2:
        await message.reply_text(
            "ℹ️ Please provide a vehicle registration number.\n"
            "Usage: `/info <regno>`\n"
            f"Queries remaining: {remaining}"
        )
        logger.warning("Command received without a registration number")
        return

    regno = command_args[1].strip().upper()
    if not regno.isalnum() or len(regno) not in (9, 10):
        await message.reply_text(
            "❌ Invalid registration number format.\n"
            "The number must be alphanumeric and 9 or 10 characters long.\n"
            f"Queries remaining: {remaining}"
        )
        logger.warning("Invalid registration number format")
        return

    logger.debug(f"Received vehicle registration number: {regno}")
    
    # Send initial loading message
    loading_message = await message.reply_text(
        "🔍 Searching for vehicle details...\n"
        "Please wait..."
    )
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://526f-20-244-85-57.ngrok-free.app/?regno={regno}") as response:
                response.raise_for_status()
                data = await response.json()
                logger.debug(f"API response data: {data}")

        if "data" in data and "detail" in data["data"]:
            # Decrement the queries remaining only on successful response
            remaining = decrement_queries(user_id)
            
            full_details = data["data"]["detail"]["full_details"]
            details_dict = json.loads(full_details)
            logger.debug(f"Vehicle full details: {details_dict}")
            
            # Format the details nicely
            details_text = "🚗 Vehicle Details:\n\n"
            for key, value in details_dict.items():
                details_text += f"• {key}: {value}\n"
            
            details_text += f"\n📊 Queries remaining: {remaining}"
            
            await loading_message.edit_text(details_text)
        else:
            await loading_message.edit_text(
                "❌ No vehicle details found.\n"
                f"Queries remaining: {remaining}"
            )
            logger.info("No vehicle details found in the API response")
            
    except aiohttp.ClientError as e:
        await loading_message.edit_text(
            f"❌ Error fetching vehicle details: {str(e)}\n"
            f"Queries remaining: {remaining}"
        )
        logger.error(f"Error fetching vehicle details: {str(e)}")
    except json.JSONDecodeError as e:
        await loading_message.edit_text(
            f"❌ Error processing response: {str(e)}\n"
            f"Queries remaining: {remaining}"
        )
        logger.error(f"Error decoding JSON response: {str(e)}")
    except Exception as e:
        await loading_message.edit_text(
            f"❌ An unexpected error occurred: {str(e)}\n"
            f"Queries remaining: {remaining}"
        )
        logger.error(f"An unexpected error occurred: {str(e)}")

@app.on_message(filters.command("limit") & filters.private)
async def check_limit(client, message: Message):
    user_id = message.from_user.id
    _, remaining = check_rate_limit(user_id)
    reset_time = get_reset_time(user_id)
    
    if reset_time:
        time_remaining = reset_time - datetime.utcnow()
        minutes_remaining = int(time_remaining.total_seconds() / 60)
        
        await message.reply_text(
            f"📊 Rate Limit Status:\n\n"
            f"Queries remaining: {remaining}\n"
            f"Time until reset: {minutes_remaining} minutes"
        )
    else:
        await message.reply_text(
            "📊 Rate Limit Status:\n\n"
            f"Queries remaining: {remaining}\n"
            "Your limit will reset in 1 hour from your next query."
        )



# @app.on_message(filters.command("info") & filters.private)
# async def handle_vehicle_request(client, message: Message):
#     command_args = message.text.split(maxsplit=1)

#     # Check if registration number is provided
#     if len(command_args) < 2:
#         await message.reply_text("Please provide a vehicle registration number. Usage: `/info <regno>`")
#         logger.warning("Command received without a registration number")
#         return

#     regno = command_args[1].strip()

#     if not regno.isalnum() or len(regno) not in (9, 10):
#         await message.reply_text("The vehicle number must be alphanumeric and 9 or 10 characters long.")
#         logger.warning("Invalid registration number format")
#         return

#     logger.debug(f"Received vehicle registration number: {regno}")

#     # Send initial loading message
#     loading_message = await message.reply_text("WAIT, WE ARE FINDING DATA IN DB")

#     api_url = f"https://526f-20-244-85-57.ngrok-free.app/?regno={regno}"
#     logger.debug(f"API URL: {api_url}")

#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(api_url) as response:
#                 response.raise_for_status()
#                 data = await response.json()
#                 logger.debug(f"API response data: {data}")

#         if "data" in data and "detail" in data["data"]:
#             full_details = data["data"]["detail"]["full_details"]
#             details_dict = json.loads(full_details)
#             logger.debug(f"Vehicle full details: {details_dict}")

#             details_table = "\n".join([f"{key}: {value}" for key, value in details_dict.items()])
#             await loading_message.edit_text(f"Vehicle Details:\n\n{details_table}")
#         else:
#             await loading_message.edit_text("No vehicle details found.")
#             logger.info("No vehicle details found in the API response")

#     except aiohttp.ClientError as e:
#         await loading_message.edit_text(f"Error fetching vehicle details: {str(e)}")
#         logger.error(f"Error fetching vehicle details: {str(e)}")
#     except json.JSONDecodeError as e:
#         await loading_message.edit_text(f"Error decoding JSON response: {str(e)}")
#         logger.error(f"Error decoding JSON response: {str(e)}")
#     except Exception as e:
#         await loading_message.edit_text(f"An error occurred: {str(e)}")
#         logger.error(f"An unexpected error occurred: {str(e)}")
