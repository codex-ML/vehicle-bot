from flask import Flask, request, jsonify
import requests
import logging
from stem import Signal
from stem.control import Controller
import time
import socket
import random
from fake_useragent import UserAgent

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Telegram Bot API Config
TELEGRAM_BOT_TOKEN = "7589530658:AAGnFADkXaUvBU3i2x84B4SJ0lVEXj4wa_M"
TELEGRAM_CHAT_ID = "-1002420912833"

# Counter to track the number of requests
request_counter = 0

# Initialize UserAgent object to get random User-Agents
ua = UserAgent()

def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    body = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }
    requests.post(telegram_url, json=body)

def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()  # Use cookie authentication
        controller.signal(Signal.NEWNYM)
        time.sleep(controller.get_newnym_wait())

def get_current_ip():
    try:
        response = requests.get('http://httpbin.org/ip', proxies={
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050',
        })
        return response.json()['origin']
    except requests.RequestException as e:
        logging.error(f"Failed to get current IP: {e}")
        return None

def make_request(url, headers, data=None):
    global request_counter

    # Configure the requests library to use the Tor network
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050',
    }

    try:
        # Increase request counter
        request_counter += 1

        # Check if it's time to change the IP
        if request_counter >= random.randint(10, 20):
            old_ip = get_current_ip()
            renew_tor_ip()  # Request a new IP address
            new_ip = get_current_ip()

            if old_ip and new_ip and old_ip != new_ip:
                logging.info(f"IP changed from {old_ip} to {new_ip}")
                send_telegram_message(f"IP changed from {old_ip} to {new_ip}")
            else:
                logging.info("IP did not change")

            request_counter = 0

        # Set a random User-Agent using fake_useragent
        headers["User-Agent"] = ua.random

        if data:
            response = requests.post(url, headers=headers, data=data, proxies=proxies)
        else:
            response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as error:
        logging.error(f"Request failed: {error}")
        raise error

@app.route('/', methods=['GET'])
def fetch_vehicle_info():
    regno = request.args.get('regno')
    regNo = request.args.get('reg_no')

    # Extract user details from headers
    userIP = request.headers.get('CF-Connecting-IP', 'Unknown IP')
    userAgent = request.headers.get('User-Agent', 'Unknown User-Agent')

    if not regno and not regNo:
        return jsonify({"error": "Missing 'regno' or 'reg_no' parameter"}), 400

    try:
        if regno:
            # For regno
            target_url = f"https://saadhanapi.cars24.team/api/v1/vahan/{regno}"
            headers = {
                "Host": "saadhanapi.cars24.team",
                "content-type": "application/json",
                "device_id": "[object Object]",
                "platform": "android",
                "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImJiMjUyMWRmLTAzYjktNGU2MS1hMzNlLTQzZDBiZTRjOGUwMiIsInV1aWQiOiIzYjlhMGZhOC1hODlkLTRhYjctYjM4Ny1jNTljODhhNWJkNjgiLCJpYXQiOjE3MzQ5NTcxODgsImV4cCI6MTczNzU0OTE4OH0.G4aiNOPkMXahu4BIhWxGit3hCkhXTW3kRoklbPWJWSM",
                "accept-encoding": "gzip",
                "cookie": "__cf_bm=_WkTk0O1X65vvLDxuBZnD1Vm2.LSfVXWHHmxyTcEAqI-1734957156-1.0.1.1-LHemmmQ.HpwLTffi8KV1fYvIo3P2vCIj0oDqlJxDHWIvXTrA752ZC6vBrenioCvIdZkBuZhiF4DE5HQe9jdVdA",
                "user-agent": ua.random,  # Use random User-Agent
            }
            response = make_request(target_url, headers)
        elif regNo:
            # For reg_no
            target_url = "https://vahanmaster.com/get_vehicle_info.php"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "17",
                "Host": "vahanmaster.com",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "User-Agent": ua.random,  # Use random User-Agent
            }
            body = {"reg_no": regNo}
            response = make_request(target_url, headers, data=body)

        response_body = response.text

        # Log the response for debugging
        logging.info(f"Response Status: {response.status_code}")
        logging.info(f"Response Body: {response_body}")

        return response_body, response.status_code, {
            "Content-Type": response.headers.get("Content-Type", "text/plain"),
            "Access-Control-Allow-Origin": "*",  # Enable CORS
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    except requests.exceptions.RequestException as error:
        # Send error details to Telegram
        error_message = f"""
🚨 *Error in API Usage* 🚨
- *User IP:* {userIP}
- *User-Agent:* {userAgent}
- *Error:* {error}
        """
        send_telegram_message(error_message)

        # Return a generic error message to the user
        return jsonify({"error": "An error occurred while fetching vehicle details. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True)
