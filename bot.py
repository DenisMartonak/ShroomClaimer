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
from playwright.sync_api import sync_playwright

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

def login_with_playwright(username, password):
    """Logs in via Playwright to bypass Cloudflare and returns a requests.Session() with cookies."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"🌐 [{username}] Opening login page...")
        page.goto(LOGIN_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)  # Wait for Cloudflare challenge

        print(f"🔑 [{username}] Filling login form...")
        page.fill("input[name='login']", username)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")  # Adjust selector to match site's login button
        page.wait_for_timeout(3000)  # Wait for login to process

        # Extract cookies and put into requests.Session
        cookies = context.cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie["name"], cookie["value"], domain=cookie.get("domain"))

        browser.close()

        print(f"✅ [{username}] Logged in via Playwright.")
        return session

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
    session = login_with_playwright(username, password)
    if not session:
        print(f"❌ [{username}] Could not log in. Skipping.")
        return

    res = claim_gift(session, username)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(webhookSend(WEBHOOK_URL, res, username))
    loop.close()

    if "Unauthorized" in res.text:
        print(f"🔁 [{username}] Re-authenticating due to 'Unauthorized'...")
        session = login_with_playwright(username, password)
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
