from dotenv import load_dotenv
import requests
import datetime
import os
import sys
import asyncio
import discord
from discord import Webhook
import aiohttp
import json

load_dotenv()

LOGIN_URL = os.getenv("LOGIN_URL")
CLAIM_URL = os.getenv("CLAIM_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

status = {
    "last_claim_response": "Not yet claimed.",
    "last_claim_time": "N/A",
    "next_claim_in": "N/A"
}

def get_accounts():
    """Reads accounts from .env in format USERNAME_1, PASSWORD_1, USERNAME_2, PASSWORD_2..."""
    accounts = []
    i = 1
    while True:
        username = os.getenv(f"USERNAME_{i}")
        password = os.getenv(f"PASSWORD_{i}")
        if not username or not password:
            break
        accounts.append({"username": username, "password": password})
        i += 1
    return accounts

def login(username, password):
    session = requests.Session()
    login_data = {
        "login": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0"
    }
    response = session.post(LOGIN_URL, headers=headers, data=login_data)

    if "Logout" in response.text or response.ok:
        print(f"✅ [{username}] Logged in successfully.")
        return session
    else:
        print(f"❌ [{username}] Login failed.")
        print(response.text)
        return None

def claim_gift(session, username):
    claim_data = {
        "category": "gifts",
        "action": "claim_gift",
        "buy": "2"
    }
    response = session.post(CLAIM_URL, headers={"User-Agent": "Mozilla/5.0"}, data=claim_data)
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    response_text = response.text.strip()

    print(f"🎁 [{username}] Claim response: {response_text}")
    print(f"🕒 Time: {timestamp}")

    status['last_claim_response'] = response_text.replace("\n", " | ")
    status['last_claim_time'] = timestamp
    return response

async def webhookSend(url, response, username):
    response_txt = response.text.strip()
    try:
        response_data = json.loads(response_txt)
    except json.JSONDecodeError:
        response_data = {"status": "error", "message": "Invalid response from server"}

    status_val = response_data.get("status", "unknown")
    message = response_data.get("message", "No message")
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, session=session)
        if "success" in status_val:
            embed = discord.Embed(title=f"{username} - Shroom bot ✅", colour=0x35f500)
        else:
            embed = discord.Embed(title=f"{username} - Shroom bot ❌", colour=0xf50000)
        embed.add_field(name="Status", value=status_val)
        embed.add_field(name="Message", value=message)
        await webhook.send(embed=embed, username="Shroom Dealer")

def mushroom_bot(username, password):
    session = login(username, password)
    if not session:
        print(f"❌ [{username}] Could not log in. Skipping.")
        return

    res = claim_gift(session, username)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(webhookSend(WEBHOOK_URL, res, username))
    loop.close()

    if "Unauthorized" in res.text:
        print(f"🔁 [{username}] Re-authenticating due to 'Unauthorized'...")
        session = login(username, password)
        if session:
            claim_gift(session, username)

    print(f"✅ [{username}] Claim attempt complete.")

if __name__ == "__main__":
    accounts = get_accounts()
    if not accounts:
        print("❌ No accounts found in .env")
        sys.exit(1)

    for account in accounts:
        mushroom_bot(account["username"], account["password"])
