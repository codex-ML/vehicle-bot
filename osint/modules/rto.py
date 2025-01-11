import json
import logging
import aiohttp
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from osint import app
from fake_useragent import UserAgent

# Configure logging
logger = logging.getLogger("vehicle_request")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()  # Logs to console for debugging
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Load proxies from the given URL
async def load_proxies():
    proxy_url = "https://raw.githubusercontent.com/codex-ML/proxy/refs/heads/main/abc.txt"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(proxy_url) as response:
                if response.status == 200:
                    proxies = await response.text()
                    proxy_list = proxies.splitlines()  # Split proxies by lines
                    logger.debug(f"Loaded proxies: {len(proxy_list)} proxies found.")
                    return proxy_list
                else:
                    logger.error(f"Failed to fetch proxies. HTTP status code: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error loading proxies: {e}")
        return []

# Get vehicle data through a proxy
async def get_vehicle_info_with_proxy(session, regno, proxy):
    api_url = f"https://saadhanapi.cars24.team/api/v1/vahan/{regno}"
    try:
        ua = UserAgent()
        headers = {
            'Host': 'saadhanapi.cars24.team',
            'Content-Type': 'application/json',
            'Device-ID': '[object Object]',
            'Platform': 'android',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImJiMjUyMWRmLTAzYjktNGU2MS1hMzNlLTQzZDBiZTRjOGUwMiIsInV1aWQiOiIzYjlhMGZhOC1hODlkLTRhYjctYjM4Ny1jNTljODhhNWJkNjgiLCJpYXQiOjE3MzQ5NTcxODgsImV4cCI6MTczNzU0OTE4OH0.G4aiNOPkMXahu4BIhWxGit3hCkhXTW3kRoklbPWJWSM',
            'Accept-Encoding': 'gzip',
            'Cookie': '__cf_bm=_WkTk0O1X65vvLDxuBZnD1Vm2.LSfVXWHHmxyTcEAqI-1734957156-1.0.1.1-LHemmQ.HpwLTffi8KV1fYvIo3P2vCIj0oDqlJxDHWIvXTrA752ZC6vBrenioCvIdZkBuZhiF4DE5HQe9jdVdA',
            'User-Agent': ua.random  # Use random user-agent
        }

        # Set proxy for the request
        proxies = {
            'http': proxy,
            'https': proxy
        }

        logger.info(f"Using proxy: {proxy}")
        async with session.get(api_url, headers=headers, proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                logger.debug(f"Response received for {regno}: {data}")
                return data
            else:
                logger.error(f"Failed to fetch vehicle data, status code: {response.status}")
                return {"Error": f"Failed to fetch data, status code: {response.status}"}
    except Exception as e:
        logger.error(f"Error fetching vehicle info with proxy {proxy}: {e}")
        return {"Error": str(e)}

# Handler to process vehicle request
@app.on_message(filters.command("info"))
async def handle_vehicle_request(client, message: Message):
    command_args = message.text.split(maxsplit=1)

    # Check if registration number is provided
    if len(command_args) < 2:
        await message.reply_text("Please provide a vehicle registration number. Usage: /info <regno>")
        logger.warning("Command received without a registration number")
        return

    regno = command_args[1].strip()

    # Validate registration number format
    if not regno.isalnum() or len(regno) not in (9, 10):
        await message.reply_text("The vehicle number must be alphanumeric and 9 or 10 characters long.")
        logger.warning("Invalid registration number format")
        return

    logger.debug(f"Received vehicle registration number: {regno}")

    # Load proxies
    proxies = await load_proxies()
    if not proxies:
        await message.reply_text("No proxies available.")
        logger.warning("No proxies available, request not sent.")
        return

    # Pick a random proxy from the list
    random_proxy = random.choice(proxies)
    logger.debug(f"Using proxy: {random_proxy}")

    # Send initial loading message
    loading_message = await message.reply_text("WAIT, WE ARE FINDING DATA IN DB")

    # Fetch vehicle data using the proxy
    async with aiohttp.ClientSession() as session:
        vehicle_info = await get_vehicle_info_with_proxy(session, regno, random_proxy)

        if 'Error' in vehicle_info:
            await loading_message.edit_text(vehicle_info['Error'])
            return

        # Extract and process the vehicle details
        try:
            detail = vehicle_info['data']['detail']
            model_image_url = detail.get('modelImageUrl', 'https://cdn.24c.in/prod/new-car-cms/Saadhan-Test/2024/04/20/2fc95276-2134-42f7-8232-19423152a51c-default_make_logo.png')

            vehicle_details = (
                f"🚗 **Vehicle Registration Number:** {detail.get('registrationNumber', 'N/A')}\n"
                f"📍 **Registered Place:** {detail.get('registeredPlace', 'N/A')}\n"
                f"⛽ **Fuel Type:** {detail.get('fuelType', 'N/A')}\n"
                f"💡 **Model:** {detail.get('model_display', 'N/A')}\n"
                f"🏢 **Brand:** {detail.get('brand', {}).get('make_display', 'N/A')}\n"
                f"📅 **Registration Year:** {detail.get('regn_year', 'N/A')}\n"
                f"🎨 **Color:** {detail.get('color', 'N/A')}\n"
                f"🏷️ **Vehicle Category:** {detail.get('vehicleClassDesc', 'N/A')}\n"
                f"🛠️ **Engine Number:** {detail.get('engineNo', 'N/A')}\n"
                f"🔑 **Chassis Number:** {detail.get('chassisNo', 'N/A')}\n"
                f"💼 **Insurance Company:** {detail.get('insuranceCompany', 'N/A')}\n"
                f"📆 **Insurance Expiry:** {detail.get('insuranceUpTo', 'N/A')}\n"
                f"🗓️ **Fitness Up To:** {detail.get('fitnessUpTo', 'N/A')}\n"
                f"💰 **Tax Up To:** {detail.get('taxUpTo', 'N/A')}\n"
                f"📝 **Insurance Policy Number:** {detail.get('insurancePolicyNo', 'N/A')}\n"
                f"⚖️ **Unladen Weight:** {detail.get('unladenWt', 'N/A')} kg\n"
                f"🏠 **Financier:** {detail.get('financier', 'N/A')}\n"
                f"🚙 **Vehicle Class:** {detail.get('vehicleClassDesc', 'N/A')}\n"
                f"🏷️ **RC Status:** {detail.get('rcStatus', 'N/A')}\n"
                f"🛣️ **RTO NOC Issued:** {detail.get('rtoNocIssued', 'N/A')}\n"
                f"📅 **Manufacturing Date:** {detail.get('manufacturingMonthYr', 'N/A')}\n"
            )

            # Send the message with vehicle details and image
            try:
                await loading_message.edit_text(vehicle_details)
                await client.send_photo(message.chat.id, model_image_url, caption=vehicle_details)
            except Exception as e:
                logger.error(f"Error sending photo: {e}")
                await loading_message.edit_text("Error sending the vehicle details image.")
        except Exception as e:
            logger.error(f"Error parsing vehicle data: {e}")
            await loading_message.edit_text("Failed to fetch or parse vehicle details.")
