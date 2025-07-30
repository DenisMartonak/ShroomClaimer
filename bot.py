from dotenv import load_dotenv
import requests
import datetime
import os
import sys
import asyncio
import discord
from discord import Webhook
import aiohttp

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
LOGIN_URL = os.getenv("LOGIN_URL")
CLAIM_URL = os.getenv("CLAIM_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

status = {
    "last_claim_response": "Not yet claimed.",
    "last_claim_time": "N/A",
    "next_claim_in": "N/A"
}

def login():
    session = requests.Session()
    login_data = {
        "login": USERNAME,
        "password": PASSWORD
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0"
    }
    response = session.post(LOGIN_URL, headers=headers, data=login_data)

    if "Logout" in response.text or response.ok:
        print("✅ Logged in successfully.")
        return session
    else:
        print("❌ Login failed.")
        print(response.text)
        return None

def claim_gift(session):
    claim_data = {
        "category": "gifts",
        "action": "claim_gift",
        "buy": "2"
    }
    response = session.post(CLAIM_URL, headers={"User-Agent": "Mozilla/5.0"}, data=claim_data)
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    response_text = response.text.strip()

    print(f"🎁 Claim response: {response_text}")
    print(f"🕒 Time: {timestamp}")

    status['last_claim_response'] = response_text.replace("\n", " | ")
    status['last_claim_time'] = timestamp
    return response

async def webhookSend(url, response):
    response_txt = response.text.strip()
    async with aiohttp.ClientSession() as session:
        if "success" in response.text:
            webhook = Webhook.from_url(url, session=session)
            embed = discord.Embed(title="Shroom bot response ✅", description=response_txt, colour=0xf500b4)
            await webhook.send(embed=embed, username="Shroom Dealer")
        else:
            webhook = Webhook.from_url(url, session=session)
            embed = discord.Embed(title="Shroom bot response ❌", description=response_txt, colour=0xf500b4)
            embed.set_image(url="https://media1.tenor.com/m/pWbYdRvbuvsAAAAd/sheiken.gif")
            await webhook.send(embed=embed, username="Shroom Dealer")

def mushroom_bot():
    session = login()
    if not session:
        print("❌ Could not log in. Exiting.")
        sys.exit(1)

    res = claim_gift(session)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(webhookSend(WEBHOOK_URL, res))
    loop.close()

    if "Unauthorized" in res.text:
        print("🔁 Re-authenticating due to 'Unauthorized'...")
        session = login()
        if session:
            claim_gift(session)

    print("✅ Claim attempt complete. Done for this run.")

if __name__ == "__main__":
    mushroom_bot()
